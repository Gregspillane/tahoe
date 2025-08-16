import { PrismaClient, TenantStatus, UserRole, UserStatus } from '@prisma/client';
import { TenantRepository } from '../../src/repositories/tenant.repository';
import { UserRepository } from '../../src/repositories/user.repository';
import { ApiKeyRepository } from '../../src/repositories/apikey.repository';
import { prisma } from '../setup';

describe('Repository Tests', () => {
  let tenantRepo: TenantRepository;
  let userRepo: UserRepository;
  let apiKeyRepo: ApiKeyRepository;
  let testTenantId: string;
  let testUserId: string;

  beforeAll(() => {
    tenantRepo = new TenantRepository(prisma);
    userRepo = new UserRepository(prisma);
    apiKeyRepo = new ApiKeyRepository(prisma);
  });

  afterEach(async () => {
    if (testUserId) {
      await prisma.user.deleteMany({ where: { id: testUserId } });
    }
    if (testTenantId) {
      await prisma.tenant.deleteMany({ where: { id: testTenantId } });
    }
  });

  describe('TenantRepository', () => {
    it('should create tenant successfully', async () => {
      const tenantData = {
        name: 'Test Company',
        slug: 'test-company',
        planTier: 'free',
      };

      const tenant = await tenantRepo.create(tenantData);
      testTenantId = tenant.id;

      expect(tenant).toBeDefined();
      expect(tenant.name).toBe(tenantData.name);
      expect(tenant.slug).toBe(tenantData.slug);
      expect(tenant.status).toBe(TenantStatus.TRIAL);
    });

    it('should find tenant by slug', async () => {
      const tenantData = {
        name: 'Test Company 2',
        slug: 'test-company-2',
      };

      const createdTenant = await tenantRepo.create(tenantData);
      testTenantId = createdTenant.id;

      const foundTenant = await tenantRepo.findBySlug(tenantData.slug);
      
      expect(foundTenant).toBeDefined();
      expect(foundTenant?.id).toBe(createdTenant.id);
    });
  });

  describe('UserRepository', () => {
    beforeEach(async () => {
      const tenant = await tenantRepo.create({
        name: 'Test Tenant for User',
        slug: 'test-tenant-user',
      });
      testTenantId = tenant.id;
    });

    it('should create user successfully', async () => {
      const userData = {
        email: 'test@example.com',
        firstName: 'John',
        lastName: 'Doe',
        role: UserRole.USER,
      };

      const user = await userRepo.create(testTenantId, userData);
      testUserId = user.id;

      expect(user).toBeDefined();
      expect(user.email).toBe(userData.email);
      expect(user.tenantId).toBe(testTenantId);
      expect(user.status).toBe(UserStatus.INVITED);
    });

    it('should find user by email', async () => {
      const userData = {
        email: 'findme@example.com',
        firstName: 'Jane',
        lastName: 'Doe',
      };

      const createdUser = await userRepo.create(testTenantId, userData);
      testUserId = createdUser.id;

      const foundUser = await userRepo.findByEmail(userData.email);
      
      expect(foundUser).toBeDefined();
      expect(foundUser?.id).toBe(createdUser.id);
      expect(foundUser?.tenant).toBeDefined();
    });
  });

  describe('ApiKeyRepository', () => {
    beforeEach(async () => {
      const tenant = await tenantRepo.create({
        name: 'Test Tenant for API Key',
        slug: 'test-tenant-apikey',
      });
      testTenantId = tenant.id;

      const user = await userRepo.create(testTenantId, {
        email: 'apiuser@example.com',
        firstName: 'API',
        lastName: 'User',
      });
      testUserId = user.id;
    });

    it('should create API key successfully', async () => {
      const keyData = {
        name: 'Test API Key',
        permissions: ['read', 'write'],
      };

      const apiKey = await apiKeyRepo.create(
        testTenantId,
        testUserId,
        keyData,
        'hashed_key_value',
        'test_prefix'
      );

      expect(apiKey).toBeDefined();
      expect(apiKey.name).toBe(keyData.name);
      expect(apiKey.tenantId).toBe(testTenantId);
      expect(apiKey.keyPrefix).toBe('test_prefix');

      await prisma.apiKey.delete({ where: { id: apiKey.id } });
    });
  });
});