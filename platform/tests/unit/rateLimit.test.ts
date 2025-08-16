import { RateLimiter, createTenantRateLimit, createUserRateLimit, createIPRateLimit } from '../../src/middleware/rateLimit';
import { redisClient } from '../../src/config/redis';

// Mock Redis client for testing
jest.mock('../../src/config/redis');

describe('Rate Limiting', () => {
  let mockRedis: jest.Mocked<typeof redisClient>;

  beforeEach(() => {
    mockRedis = redisClient as jest.Mocked<typeof redisClient>;
    jest.clearAllMocks();
  });

  describe('RateLimiter', () => {
    it('should create rate limiter with correct config', () => {
      const limiter = new RateLimiter({
        windowMs: 60000,
        max: 100,
        message: 'Too many requests',
      });

      expect(limiter).toBeDefined();
    });

    it('should check rate limit and return info', async () => {
      mockRedis.incr.mockResolvedValue(1);
      mockRedis.expire.mockResolvedValue(1);

      const limiter = new RateLimiter({
        windowMs: 60000,
        max: 100,
      });

      const req = {
        tenantId: 'test-tenant',
        ip: '127.0.0.1',
      } as any;

      const info = await limiter.checkLimit(req);

      expect(info.limit).toBe(100);
      expect(info.current).toBe(1);
      expect(info.remaining).toBe(99);
      expect(mockRedis.incr).toHaveBeenCalled();
      expect(mockRedis.expire).toHaveBeenCalled();
    });

    it('should handle Redis failure gracefully', async () => {
      mockRedis.incr.mockRejectedValue(new Error('Redis error'));

      const limiter = new RateLimiter({
        windowMs: 60000,
        max: 100,
      });

      const req = {
        tenantId: 'test-tenant',
        ip: '127.0.0.1',
      } as any;

      const info = await limiter.checkLimit(req);

      expect(info.current).toBe(0);
      expect(info.remaining).toBe(100);
    });
  });

  describe('Predefined Rate Limiters', () => {
    it('should create tenant rate limiter', () => {
      const limiter = createTenantRateLimit(1000);
      expect(limiter).toBeDefined();
    });

    it('should create user rate limiter', () => {
      const limiter = createUserRateLimit(200);
      expect(limiter).toBeDefined();
    });

    it('should create IP rate limiter', () => {
      const limiter = createIPRateLimit(100);
      expect(limiter).toBeDefined();
    });
  });

  describe('Rate Limit Middleware', () => {
    it('should create middleware function', () => {
      const limiter = new RateLimiter({
        windowMs: 60000,
        max: 100,
      });

      const middleware = limiter.middleware();
      expect(typeof middleware).toBe('function');
    });

    it('should call next() when under limit', async () => {
      mockRedis.incr.mockResolvedValue(1);
      mockRedis.expire.mockResolvedValue(1);

      const limiter = new RateLimiter({
        windowMs: 60000,
        max: 100,
      });

      const req = { tenantId: 'test-tenant', ip: '127.0.0.1' } as any;
      const res = { 
        set: jest.fn(),
        status: jest.fn().mockReturnThis(),
        json: jest.fn(),
      } as any;
      const next = jest.fn();

      const middleware = limiter.middleware();
      await middleware(req, res, next);

      expect(next).toHaveBeenCalled();
      expect(res.set).toHaveBeenCalledWith({
        'X-RateLimit-Limit': '100',
        'X-RateLimit-Remaining': '99',
        'X-RateLimit-Reset': expect.any(String),
      });
    });

    it('should return 429 when over limit', async () => {
      mockRedis.incr.mockResolvedValue(101);
      mockRedis.expire.mockResolvedValue(1);

      const limiter = new RateLimiter({
        windowMs: 60000,
        max: 100,
        message: 'Rate limit exceeded',
      });

      const req = { tenantId: 'test-tenant', ip: '127.0.0.1' } as any;
      const res = { 
        set: jest.fn(),
        status: jest.fn().mockReturnThis(),
        json: jest.fn(),
      } as any;
      const next = jest.fn();

      const middleware = limiter.middleware();
      await middleware(req, res, next);

      expect(res.status).toHaveBeenCalledWith(429);
      expect(res.json).toHaveBeenCalledWith({
        error: 'Rate limit exceeded',
        limit: 100,
        resetTime: expect.any(String),
      });
      expect(next).not.toHaveBeenCalled();
    });
  });
});