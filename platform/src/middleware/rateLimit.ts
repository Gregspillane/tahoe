import { Request, Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { redisClient } from '../config/redis';
import { logger } from '../utils/logger';

export interface RateLimitConfig {
  windowMs: number; // Time window in milliseconds
  max: number; // Maximum number of requests per window
  message?: string; // Custom error message
  keyGenerator?: (req: AuthRequest) => string; // Custom key generator
  skipSuccessfulRequests?: boolean; // Don't count successful requests
  skipFailedRequests?: boolean; // Don't count failed requests
}

export interface RateLimitInfo {
  limit: number;
  current: number;
  remaining: number;
  resetTime: Date;
}

export class RateLimiter {
  private config: Required<RateLimitConfig>;

  constructor(config: RateLimitConfig) {
    this.config = {
      windowMs: config.windowMs,
      max: config.max,
      message: config.message || 'Too many requests, please try again later',
      keyGenerator: config.keyGenerator || this.defaultKeyGenerator,
      skipSuccessfulRequests: config.skipSuccessfulRequests || false,
      skipFailedRequests: config.skipFailedRequests || false,
    };
  }

  private defaultKeyGenerator(req: AuthRequest): string {
    // Use tenant ID if authenticated, otherwise use IP
    if (req.tenantId) {
      return `rate_limit:tenant:${req.tenantId}`;
    }
    
    const ip = req.ip || req.socket.remoteAddress || 'unknown';
    return `rate_limit:ip:${ip}`;
  }

  async checkLimit(req: AuthRequest): Promise<RateLimitInfo> {
    const key = this.config.keyGenerator(req);
    const window = Math.floor(Date.now() / this.config.windowMs);
    const redisKey = `${key}:${window}`;

    try {
      // Increment the counter
      const current = await redisClient.incr(redisKey);
      
      // Set expiration on first increment
      if (current === 1) {
        await redisClient.expire(redisKey, Math.ceil(this.config.windowMs / 1000));
      }

      const resetTime = new Date((window + 1) * this.config.windowMs);
      
      return {
        limit: this.config.max,
        current,
        remaining: Math.max(0, this.config.max - current),
        resetTime,
      };
    } catch (error) {
      logger.error('Rate limit check failed:', error);
      // In case of Redis failure, allow the request
      return {
        limit: this.config.max,
        current: 0,
        remaining: this.config.max,
        resetTime: new Date(Date.now() + this.config.windowMs),
      };
    }
  }

  middleware() {
    return async (req: AuthRequest, res: Response, next: NextFunction): Promise<void> => {
      try {
        const info = await this.checkLimit(req);
        
        // Add rate limit headers
        res.set({
          'X-RateLimit-Limit': info.limit.toString(),
          'X-RateLimit-Remaining': info.remaining.toString(),
          'X-RateLimit-Reset': Math.ceil(info.resetTime.getTime() / 1000).toString(),
        });

        if (info.current > info.limit) {
          logger.warn('Rate limit exceeded', {
            key: this.config.keyGenerator(req),
            limit: info.limit,
            current: info.current,
            ip: req.ip,
            userAgent: req.get('User-Agent'),
            tenantId: req.tenantId,
            userId: req.userId,
          });

          res.status(429).json({
            error: this.config.message,
            limit: info.limit,
            resetTime: info.resetTime.toISOString(),
          });
          return;
        }

        // Store rate limit info for potential cleanup on response
        (req as any).rateLimitInfo = info;
        
        next();
      } catch (error) {
        logger.error('Rate limiting middleware error:', error);
        // On error, allow the request to proceed
        next();
      }
    };
  }
}

// Predefined rate limiters for common use cases
export const createTenantRateLimit = (requestsPerMinute: number) => {
  return new RateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: requestsPerMinute,
    keyGenerator: (req: AuthRequest) => `rate_limit:tenant:${req.tenantId || 'anonymous'}`,
    message: 'Too many requests from this tenant, please try again later',
  });
};

export const createUserRateLimit = (requestsPerMinute: number) => {
  return new RateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: requestsPerMinute,
    keyGenerator: (req: AuthRequest) => `rate_limit:user:${req.userId || req.ip}`,
    message: 'Too many requests from this user, please try again later',
  });
};

export const createIPRateLimit = (requestsPerMinute: number) => {
  return new RateLimiter({
    windowMs: 60 * 1000, // 1 minute
    max: requestsPerMinute,
    keyGenerator: (req: AuthRequest) => `rate_limit:ip:${req.ip || 'unknown'}`,
    message: 'Too many requests from this IP address, please try again later',
  });
};

export const createAuthRateLimit = (attemptsPerHour: number) => {
  return new RateLimiter({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: attemptsPerHour,
    keyGenerator: (req: AuthRequest) => {
      const email = req.body?.email;
      if (email) {
        return `rate_limit:auth:email:${email}`;
      }
      return `rate_limit:auth:ip:${req.ip || 'unknown'}`;
    },
    message: 'Too many authentication attempts, please try again later',
    skipSuccessfulRequests: true, // Only count failed attempts
  });
};

// Global rate limiter instances
export const globalRateLimit = createIPRateLimit(100); // 100 requests per minute per IP
export const tenantRateLimit = createTenantRateLimit(1000); // 1000 requests per minute per tenant
export const userRateLimit = createUserRateLimit(200); // 200 requests per minute per user
export const authRateLimit = createAuthRateLimit(10); // 10 auth attempts per hour

// Cleanup function for expired rate limit keys
export async function cleanupRateLimitKeys(): Promise<number> {
  try {
    const pattern = 'rate_limit:*';
    const keys = await redisClient.keys(pattern);
    
    if (keys.length === 0) {
      return 0;
    }

    // Get TTL for all keys and remove those that are expired
    const pipeline = redisClient.pipeline();
    keys.forEach(key => pipeline.ttl(key));
    
    const ttls = await pipeline.exec();
    const expiredKeys = keys.filter((_, index) => {
      const ttl = ttls?.[index]?.[1] as number;
      return ttl === -1; // Key exists but has no expiration
    });

    if (expiredKeys.length > 0) {
      await redisClient.del(...expiredKeys);
      logger.info(`Cleaned up ${expiredKeys.length} expired rate limit keys`);
    }

    return expiredKeys.length;
  } catch (error) {
    logger.error('Failed to cleanup rate limit keys:', error);
    return 0;
  }
}