import request from 'supertest';
import app from '../../src/main';
import { prisma } from '../../src/config/database';
import { redisClient } from '../../src/config/redis';
import { hashPassword } from '../../src/utils/password';
import { UserRole, TenantStatus, UserStatus } from '@prisma/client';

describe('Authentication API', () => {
  let testTenant: any;
  let testUser: any;
  let accessToken: string;

  beforeAll(async () => {
    // Connect to Redis
    await redisClient.connect();

    // Create test tenant
    testTenant = await prisma.tenant.create({
      data: {
        name: 'Test Company',
        slug: 'test-company',
        status: TenantStatus.ACTIVE,
      },
    });

    // Create test user
    const hashedPassword = await hashPassword('TestPassword123!');
    testUser = await prisma.user.create({
      data: {
        email: 'test@test.com',
        tenantId: testTenant.id,
        firstName: 'Test',
        lastName: 'User',
        role: UserRole.ADMIN,
        passwordHash: hashedPassword,
        status: UserStatus.ACTIVE,
      },
    });
  });

  afterAll(async () => {
    // Clean up test data
    await prisma.user.deleteMany({
      where: { tenantId: testTenant.id },
    });
    await prisma.tenant.delete({
      where: { id: testTenant.id },
    });

    // Disconnect Redis
    await redisClient.disconnect();
  });

  describe('POST /api/v1/auth/login', () => {
    it('should login user successfully with valid credentials', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'test@test.com',
          password: 'TestPassword123!',
        });

      expect(response.status).toBe(200);
      expect(response.body.access_token).toBeDefined();
      expect(response.body.refresh_token).toBeDefined();
      expect(response.body.expires_in).toBeDefined();
      expect(response.body.user).toMatchObject({
        id: testUser.id,
        email: testUser.email,
        role: testUser.role,
        tenant: {
          id: testTenant.id,
          name: testTenant.name,
          slug: testTenant.slug,
        },
      });

      // Store token for other tests
      accessToken = response.body.access_token;
    });

    it('should reject login with invalid email', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'wrong@test.com',
          password: 'TestPassword123!',
        });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('Invalid credentials');
    });

    it('should reject login with invalid password', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'test@test.com',
          password: 'WrongPassword123!',
        });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('Invalid credentials');
    });

    it('should reject login with missing credentials', async () => {
      const response = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'test@test.com',
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toBe('Email and password are required');
    });
  });

  describe('GET /api/v1/auth/me', () => {
    it('should return user profile with valid token', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        id: testUser.id,
        email: testUser.email,
        firstName: testUser.firstName,
        lastName: testUser.lastName,
        role: testUser.role,
        status: testUser.status,
        tenant: {
          id: testTenant.id,
          name: testTenant.name,
          slug: testTenant.slug,
        },
      });
    });

    it('should reject request without token', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me');

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('No authentication token provided');
    });

    it('should reject request with invalid token', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', 'Bearer invalid_token');

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('Invalid token');
    });
  });

  describe('POST /api/v1/auth/refresh', () => {
    let refreshToken: string;

    beforeAll(async () => {
      // Get fresh tokens
      const loginResponse = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'test@test.com',
          password: 'TestPassword123!',
        });

      refreshToken = loginResponse.body.refresh_token;
    });

    it('should refresh access token with valid refresh token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/refresh')
        .send({
          refresh_token: refreshToken,
        });

      expect(response.status).toBe(200);
      expect(response.body.access_token).toBeDefined();
      expect(response.body.expires_in).toBeDefined();
    });

    it('should reject refresh with invalid token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/refresh')
        .send({
          refresh_token: 'invalid_refresh_token',
        });

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('Invalid');
    });

    it('should reject refresh without token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/refresh')
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.error).toBe('Refresh token is required');
    });
  });

  describe('POST /api/v1/auth/logout', () => {
    it('should logout successfully with valid token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/logout')
        .set('Authorization', `Bearer ${accessToken}`);

      expect(response.status).toBe(200);
      expect(response.body.message).toBe('Logged out successfully');
    });

    it('should reject logout without token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/logout');

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('No authentication token provided');
    });
  });

  describe('POST /api/v1/auth/validate', () => {
    let validToken: string;

    beforeAll(async () => {
      // Get fresh token
      const loginResponse = await request(app)
        .post('/api/v1/auth/login')
        .send({
          email: 'test@test.com',
          password: 'TestPassword123!',
        });

      validToken = loginResponse.body.access_token;
    });

    it('should validate token successfully for internal service', async () => {
      const response = await request(app)
        .post('/api/v1/auth/validate')
        .set('X-Service-Token', process.env.SERVICE_TOKEN || 'internal-service-secret')
        .send({
          token: validToken,
        });

      expect(response.status).toBe(200);
      expect(response.body.valid).toBe(true);
      expect(response.body.tenant_id).toBe(testTenant.id);
      expect(response.body.user_id).toBe(testUser.id);
      expect(response.body.role).toBe(testUser.role);
    });

    it('should reject validation without service token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/validate')
        .send({
          token: validToken,
        });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('Invalid service token');
    });

    it('should return invalid for bad token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/validate')
        .set('X-Service-Token', process.env.SERVICE_TOKEN || 'internal-service-secret')
        .send({
          token: 'invalid_token',
        });

      expect(response.status).toBe(200);
      expect(response.body.valid).toBe(false);
    });
  });
});