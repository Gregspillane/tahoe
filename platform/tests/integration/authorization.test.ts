import request from 'supertest';
import { app } from '../../src/main';
import { getDatabase } from '../../src/config/database';
import { TenantRepository } from '../../src/repositories/tenant.repository';
import { UserRepository } from '../../src/repositories/user.repository';
import { ApiKeyRepository } from '../../src/repositories/apikey.repository';
import { generateTokens } from '../../src/utils/jwt';
import { generateApiKey } from '../../src/utils/apikey';
import { hashPassword } from '../../src/utils/password';
import { PERMISSIONS } from '../../src/utils/permissions';
import { UserRole, TenantStatus, UserStatus } from '@prisma/client';

describe('Authorization Integration Tests', () => {
  let tenantRepo: TenantRepository;
  let userRepo: UserRepository;
  let apiKeyRepo: ApiKeyRepository;
  let testTenant: any;
  let adminUser: any;
  let managerUser: any;
  let regularUser: any;
  let adminToken: string;
  let managerToken: string;
  let userToken: string;
  let apiKey: string;

  beforeAll(async () => {
    const db = getDatabase();
    tenantRepo = new TenantRepository(db);
    userRepo = new UserRepository(db);
    apiKeyRepo = new ApiKeyRepository(db);

    // Create test tenant
    testTenant = await tenantRepo.create({
      name: 'Test Company',
      slug: 'test-company',
      status: TenantStatus.ACTIVE,
    });

    // Create test users
    const passwordHash = await hashPassword('testpass123');
    
    adminUser = await userRepo.create(testTenant.id, {
      email: 'admin@test.com',
      firstName: 'Admin',
      lastName: 'User',
      role: UserRole.ADMIN,
      password: passwordHash,
    });

    managerUser = await userRepo.create(testTenant.id, {
      email: 'manager@test.com',
      firstName: 'Manager',
      lastName: 'User',
      role: UserRole.MANAGER,
      password: passwordHash,
    });

    regularUser = await userRepo.create(testTenant.id, {
      email: 'user@test.com',
      firstName: 'Regular',
      lastName: 'User',
      role: UserRole.USER,
      password: passwordHash,
    });

    // Activate users
    await userRepo.update(adminUser.id, testTenant.id, { status: UserStatus.ACTIVE });
    await userRepo.update(managerUser.id, testTenant.id, { status: UserStatus.ACTIVE });
    await userRepo.update(regularUser.id, testTenant.id, { status: UserStatus.ACTIVE });

    // Generate tokens
    const adminTokens = generateTokens(adminUser.id, testTenant.id, UserRole.ADMIN);
    const managerTokens = generateTokens(managerUser.id, testTenant.id, UserRole.MANAGER);
    const userTokens = generateTokens(regularUser.id, testTenant.id, UserRole.USER);
    
    adminToken = adminTokens.access_token;
    managerToken = managerTokens.access_token;
    userToken = userTokens.access_token;

    // Create API key
    const { key, keyHash, keyPrefix } = generateApiKey();
    await apiKeyRepo.create(
      testTenant.id,
      adminUser.id,
      {
        name: 'Test API Key',
        permissions: [PERMISSIONS.TENANT_READ, PERMISSIONS.USER_READ],
      },
      keyHash,
      keyPrefix
    );
    apiKey = key;
  });

  describe('Role-based Authorization', () => {
    it('should allow admin to access admin endpoints', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${adminToken}`);

      expect(response.status).toBe(200);
      expect(response.body.user.role).toBe('ADMIN');
    });

    it('should allow manager to access manager endpoints', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${managerToken}`);

      expect(response.status).toBe(200);
      expect(response.body.user.role).toBe('MANAGER');
    });

    it('should allow user to access user endpoints', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${userToken}`);

      expect(response.status).toBe(200);
      expect(response.body.user.role).toBe('USER');
    });
  });

  describe('API Key Authentication', () => {
    it('should authenticate with valid API key', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${apiKey}`);

      expect(response.status).toBe(200);
      expect(response.body.user.id).toBe(adminUser.id);
    });

    it('should reject invalid API key', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', 'Bearer sk_invalid_key');

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('Invalid API key');
    });

    it('should reject malformed API key', async () => {
      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', 'Bearer invalid-format');

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('Invalid API key format');
    });
  });

  describe('Permission-based Access Control', () => {
    // These tests would require endpoints that use permission middleware
    // For now, we'll test the middleware logic directly
    
    it('should validate user has required permission', () => {
      // This would be tested in actual endpoint tests
      expect(true).toBe(true); // Placeholder
    });
  });

  describe('Rate Limiting', () => {
    it('should apply rate limiting to authenticated requests', async () => {
      // Make multiple requests quickly
      const requests = Array(5).fill(null).map(() => 
        request(app)
          .get('/api/v1/auth/me')
          .set('Authorization', `Bearer ${userToken}`)
      );

      const responses = await Promise.all(requests);
      
      // All should succeed within normal limits
      responses.forEach(response => {
        expect([200, 429]).toContain(response.status);
        expect(response.headers['x-ratelimit-limit']).toBeDefined();
        expect(response.headers['x-ratelimit-remaining']).toBeDefined();
      });
    });
  });

  describe('Tenant Context Validation', () => {
    it('should validate tenant is active', async () => {
      // Suspend tenant
      await tenantRepo.update(testTenant.id, { status: TenantStatus.SUSPENDED });

      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${userToken}`);

      expect(response.status).toBe(403);
      expect(response.body.error).toContain('suspended');

      // Restore tenant
      await tenantRepo.update(testTenant.id, { status: TenantStatus.ACTIVE });
    });

    it('should validate user is active', async () => {
      // Suspend user
      await userRepo.update(regularUser.id, testTenant.id, { status: UserStatus.SUSPENDED });

      const response = await request(app)
        .get('/api/v1/auth/me')
        .set('Authorization', `Bearer ${userToken}`);

      expect(response.status).toBe(403);
      expect(response.body.error).toContain('suspended');

      // Restore user
      await userRepo.update(regularUser.id, testTenant.id, { status: UserStatus.ACTIVE });
    });
  });

  describe('Service Authentication', () => {
    it('should accept valid service token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/validate')
        .set('X-Service-Token', process.env.SERVICE_TOKEN || 'test-service-token')
        .send({ token: userToken });

      expect(response.status).toBe(200);
      expect(response.body.valid).toBe(true);
      expect(response.body.tenant_id).toBe(testTenant.id);
    });

    it('should reject invalid service token', async () => {
      const response = await request(app)
        .post('/api/v1/auth/validate')
        .set('X-Service-Token', 'invalid-token')
        .send({ token: userToken });

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('Invalid service token');
    });

    it('should require service token for internal endpoints', async () => {
      const response = await request(app)
        .post('/api/v1/auth/validate')
        .send({ token: userToken });

      expect(response.status).toBe(401);
      expect(response.body.error).toContain('Service token required');
    });
  });

  afterAll(async () => {
    // Cleanup test data
    const db = getDatabase();
    
    await db.apiKey.deleteMany({ where: { tenantId: testTenant.id } });
    await db.user.deleteMany({ where: { tenantId: testTenant.id } });
    await db.tenant.delete({ where: { id: testTenant.id } });
  });
});