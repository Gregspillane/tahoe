import { getDatabase } from '../config/database';
import { redisClient } from '../config/redis';
import { logger } from './logger';

export interface UsageEvent {
  tenantId: string;
  userId?: string;
  eventType: string;
  resource?: string;
  quantity?: number;
  metadata?: Record<string, any>;
  timestamp?: Date;
}

export interface UsageMetrics {
  tenantId: string;
  period: 'hour' | 'day' | 'week' | 'month';
  startDate: Date;
  endDate: Date;
  events: Record<string, number>;
  totalEvents: number;
  uniqueUsers: number;
}

export class UsageTracker {
  private static readonly USAGE_EVENTS = {
    // Authentication events
    LOGIN: 'auth.login',
    LOGOUT: 'auth.logout',
    API_KEY_USED: 'auth.api_key_used',
    
    // API usage
    API_REQUEST: 'api.request',
    API_ERROR: 'api.error',
    
    // Resource usage
    TRANSCRIPTION_CREATED: 'transcription.created',
    TRANSCRIPTION_COMPLETED: 'transcription.completed',
    TRANSCRIPTION_MINUTES: 'transcription.minutes',
    
    // File operations
    FILE_UPLOADED: 'file.uploaded',
    FILE_DOWNLOADED: 'file.downloaded',
    FILE_DELETED: 'file.deleted',
    
    // User management
    USER_CREATED: 'user.created',
    USER_INVITED: 'user.invited',
    USER_ACTIVATED: 'user.activated',
    
    // Feature usage
    FEATURE_USED: 'feature.used',
    DASHBOARD_VIEW: 'dashboard.view',
  } as const;

  static get EVENTS() {
    return this.USAGE_EVENTS;
  }

  static async track(event: UsageEvent): Promise<void> {
    try {
      const timestamp = event.timestamp || new Date();
      const eventData = {
        tenantId: event.tenantId,
        userId: event.userId || null,
        eventType: event.eventType,
        resource: event.resource || null,
        quantity: event.quantity || 1,
        metadata: event.metadata || {},
        timestamp,
      };

      // Store in database for long-term analytics
      await this.storeInDatabase(eventData);
      
      // Store in Redis for real-time metrics
      await this.storeInRedis(eventData);
      
      logger.debug('Usage event tracked', {
        tenantId: event.tenantId,
        eventType: event.eventType,
        quantity: event.quantity,
      });
    } catch (error) {
      logger.error('Failed to track usage event:', error);
    }
  }

  private static async storeInDatabase(event: UsageEvent & { timestamp: Date }): Promise<void> {
    const db = getDatabase();
    
    await db.event.create({
      data: {
        tenantId: event.tenantId,
        userId: event.userId,
        eventType: event.eventType,
        payload: {
          resource: event.resource,
          quantity: event.quantity,
          metadata: event.metadata,
        },
        createdAt: event.timestamp,
      },
    });
  }

  private static async storeInRedis(event: UsageEvent & { timestamp: Date }): Promise<void> {
    const date = event.timestamp.toISOString().split('T')[0]; // YYYY-MM-DD
    const hour = event.timestamp.getHours();
    
    // Increment daily counter
    const dailyKey = `usage:daily:${event.tenantId}:${date}:${event.eventType}`;
    await redisClient.incr(dailyKey);
    await redisClient.expire(dailyKey, 30 * 24 * 60 * 60); // 30 days
    
    // Increment hourly counter
    const hourlyKey = `usage:hourly:${event.tenantId}:${date}:${hour}:${event.eventType}`;
    await redisClient.incr(hourlyKey);
    await redisClient.expire(hourlyKey, 7 * 24 * 60 * 60); // 7 days
    
    // Track unique users per day
    if (event.userId) {
      const userKey = `usage:users:${event.tenantId}:${date}`;
      const userSet = await redisClient.getCache(userKey) || new Set();
      userSet.add(event.userId);
      await redisClient.setCache(userKey, Array.from(userSet), 30 * 24 * 60 * 60);
    }
    
    // Track quantity if specified
    if (event.quantity && event.quantity > 1) {
      const quantityKey = `usage:quantity:${event.tenantId}:${date}:${event.eventType}`;
      const current = await redisClient.getCache(quantityKey) || 0;
      await redisClient.setCache(quantityKey, current + event.quantity, 30 * 24 * 60 * 60);
    }
  }

  static async getUsageMetrics(
    tenantId: string,
    period: 'hour' | 'day' | 'week' | 'month',
    eventTypes?: string[]
  ): Promise<UsageMetrics> {
    const now = new Date();
    let startDate: Date;
    let endDate: Date = now;
    
    switch (period) {
      case 'hour':
        startDate = new Date(now.getTime() - 60 * 60 * 1000);
        break;
      case 'day':
        startDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
    }

    try {
      const db = getDatabase();
      
      const whereClause: any = {
        tenantId,
        createdAt: {
          gte: startDate,
          lte: endDate,
        },
      };
      
      if (eventTypes && eventTypes.length > 0) {
        whereClause.eventType = { in: eventTypes };
      }
      
      const events = await db.event.findMany({
        where: whereClause,
        select: {
          eventType: true,
          userId: true,
          payload: true,
          createdAt: true,
        },
      });

      const eventCounts: Record<string, number> = {};
      const uniqueUsers = new Set<string>();
      let totalEvents = 0;

      events.forEach(event => {
        eventCounts[event.eventType] = (eventCounts[event.eventType] || 0) + 1;
        totalEvents++;
        
        if (event.userId) {
          uniqueUsers.add(event.userId);
        }
      });

      return {
        tenantId,
        period,
        startDate,
        endDate,
        events: eventCounts,
        totalEvents,
        uniqueUsers: uniqueUsers.size,
      };
    } catch (error) {
      logger.error('Failed to get usage metrics:', error);
      throw error;
    }
  }

  static async getRealTimeMetrics(tenantId: string): Promise<{
    today: Record<string, number>;
    thisHour: Record<string, number>;
    activeUsers: number;
  }> {
    try {
      const today = new Date().toISOString().split('T')[0];
      const currentHour = new Date().getHours();
      
      // Get today's metrics from Redis
      const todayPattern = `usage:daily:${tenantId}:${today}:*`;
      const todayKeys = await redisClient.keys(todayPattern);
      
      const today: Record<string, number> = {};
      for (const key of todayKeys) {
        const eventType = key.split(':').pop() || '';
        const count = await redisClient.getCache(key) || 0;
        today[eventType] = count;
      }
      
      // Get this hour's metrics
      const hourPattern = `usage:hourly:${tenantId}:${today}:${currentHour}:*`;
      const hourKeys = await redisClient.keys(hourPattern);
      
      const thisHour: Record<string, number> = {};
      for (const key of hourKeys) {
        const eventType = key.split(':').pop() || '';
        const count = await redisClient.getCache(key) || 0;
        thisHour[eventType] = count;
      }
      
      // Get active users today
      const userKey = `usage:users:${tenantId}:${today}`;
      const activeUsersArray = await redisClient.getCache(userKey) || [];
      const activeUsers = Array.isArray(activeUsersArray) ? activeUsersArray.length : 0;
      
      return {
        today,
        thisHour,
        activeUsers,
      };
    } catch (error) {
      logger.error('Failed to get real-time metrics:', error);
      return {
        today: {},
        thisHour: {},
        activeUsers: 0,
      };
    }
  }

  static async trackApiRequest(
    req: { tenantId?: string; userId?: string; method: string; path: string },
    responseTime: number,
    statusCode: number
  ): Promise<void> {
    if (!req.tenantId) return;

    await this.track({
      tenantId: req.tenantId,
      userId: req.userId,
      eventType: statusCode >= 400 ? this.EVENTS.API_ERROR : this.EVENTS.API_REQUEST,
      metadata: {
        method: req.method,
        path: req.path,
        responseTime,
        statusCode,
      },
    });
  }

  static async getTopResources(
    tenantId: string,
    days: number = 7
  ): Promise<Array<{ resource: string; count: number }>> {
    try {
      const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      const db = getDatabase();
      
      const events = await db.event.findMany({
        where: {
          tenantId,
          createdAt: { gte: startDate },
          payload: {
            path: ['resource'],
            not: null,
          },
        },
        select: {
          payload: true,
        },
      });

      const resourceCounts: Record<string, number> = {};
      
      events.forEach(event => {
        const resource = (event.payload as any)?.resource;
        if (resource) {
          resourceCounts[resource] = (resourceCounts[resource] || 0) + 1;
        }
      });

      return Object.entries(resourceCounts)
        .map(([resource, count]) => ({ resource, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 10);
    } catch (error) {
      logger.error('Failed to get top resources:', error);
      return [];
    }
  }
}

// Middleware for automatic API usage tracking
export function trackApiUsage() {
  return (req: any, res: any, next: any) => {
    const startTime = Date.now();
    
    res.on('finish', () => {
      const responseTime = Date.now() - startTime;
      
      UsageTracker.trackApiRequest(
        {
          tenantId: req.tenantId,
          userId: req.userId,
          method: req.method,
          path: req.path,
        },
        responseTime,
        res.statusCode
      ).catch(error => {
        logger.error('Failed to track API usage:', error);
      });
    });
    
    next();
  };
}