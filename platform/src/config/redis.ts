import Redis from 'ioredis';
import { logger } from '../utils/logger';

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';

class RedisClient {
  private client: Redis;
  private isConnected: boolean = false;

  constructor() {
    this.client = new Redis(REDIS_URL, {
      maxRetriesPerRequest: 3,
      lazyConnect: true,
    });

    this.client.on('connect', () => {
      this.isConnected = true;
      logger.info('Redis client connected');
    });

    this.client.on('error', (error) => {
      this.isConnected = false;
      logger.error('Redis client error:', error);
    });

    this.client.on('close', () => {
      this.isConnected = false;
      logger.info('Redis client disconnected');
    });
  }

  async connect(): Promise<void> {
    if (!this.isConnected) {
      await this.client.connect();
    }
  }

  async disconnect(): Promise<void> {
    if (this.isConnected) {
      await this.client.disconnect();
    }
  }

  // Session management methods
  async setSession(sessionId: string, userId: string, tenantId: string, expiresIn: number): Promise<void> {
    const sessionData = {
      userId,
      tenantId,
      createdAt: new Date().toISOString(),
    };

    const key = `platform:session:${sessionId}`;
    await this.client.setex(key, expiresIn, JSON.stringify(sessionData));
  }

  async getSession(sessionId: string): Promise<{ userId: string; tenantId: string; createdAt: string } | null> {
    const key = `platform:session:${sessionId}`;
    const data = await this.client.get(key);
    
    if (!data) {
      return null;
    }

    try {
      return JSON.parse(data);
    } catch (error) {
      logger.error('Error parsing session data:', error);
      return null;
    }
  }

  async deleteSession(sessionId: string): Promise<void> {
    const key = `platform:session:${sessionId}`;
    await this.client.del(key);
  }

  async deleteUserSessions(userId: string): Promise<void> {
    const pattern = `platform:session:*`;
    const keys = await this.client.keys(pattern);
    
    for (const key of keys) {
      const sessionData = await this.client.get(key);
      if (sessionData) {
        try {
          const parsed = JSON.parse(sessionData);
          if (parsed.userId === userId) {
            await this.client.del(key);
          }
        } catch (error) {
          logger.error('Error parsing session data during cleanup:', error);
        }
      }
    }
  }

  // Rate limiting methods
  async incrementRateLimit(key: string, windowSeconds: number): Promise<number> {
    const rateLimitKey = `platform:rate_limit:${key}`;
    const current = await this.client.incr(rateLimitKey);
    
    if (current === 1) {
      await this.client.expire(rateLimitKey, windowSeconds);
    }
    
    return current;
  }

  async getRateLimit(key: string): Promise<number> {
    const rateLimitKey = `platform:rate_limit:${key}`;
    const current = await this.client.get(rateLimitKey);
    return current ? parseInt(current) : 0;
  }

  // Cache methods
  async setCache(key: string, value: any, expiresIn: number): Promise<void> {
    const cacheKey = `platform:cache:${key}`;
    await this.client.setex(cacheKey, expiresIn, JSON.stringify(value));
  }

  async getCache(key: string): Promise<any> {
    const cacheKey = `platform:cache:${key}`;
    const data = await this.client.get(cacheKey);
    
    if (!data) {
      return null;
    }

    try {
      return JSON.parse(data);
    } catch (error) {
      logger.error('Error parsing cache data:', error);
      return null;
    }
  }

  async deleteCache(key: string): Promise<void> {
    const cacheKey = `platform:cache:${key}`;
    await this.client.del(cacheKey);
  }

  // Raw Redis methods for rate limiting
  async incr(key: string): Promise<number> {
    return this.client.incr(key);
  }

  async expire(key: string, seconds: number): Promise<number> {
    return this.client.expire(key, seconds);
  }

  async keys(pattern: string): Promise<string[]> {
    return this.client.keys(pattern);
  }

  async del(...keys: string[]): Promise<number> {
    return this.client.del(...keys);
  }

  async pipeline() {
    return this.client.pipeline();
  }

  // Health check
  async ping(): Promise<string> {
    return this.client.ping();
  }

  get connected(): boolean {
    return this.isConnected;
  }
}

export const redisClient = new RedisClient();
export default redisClient;