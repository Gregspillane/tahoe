import {
  PERMISSIONS,
  ROLE_PERMISSIONS,
  getRolePermissions,
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  validateApiKeyPermissions,
  getDefaultApiKeyPermissions,
} from '../../src/utils/permissions';
import { UserRole } from '@prisma/client';

describe('Permissions System', () => {
  describe('Role Permissions', () => {
    it('should return all permissions for ADMIN role', () => {
      const adminPermissions = getRolePermissions(UserRole.ADMIN);
      
      expect(adminPermissions).toContain(PERMISSIONS.TENANT_DELETE);
      expect(adminPermissions).toContain(PERMISSIONS.USER_DELETE);
      expect(adminPermissions).toContain(PERMISSIONS.API_KEY_DELETE);
      expect(adminPermissions.length).toBeGreaterThan(15);
    });

    it('should return limited permissions for MANAGER role', () => {
      const managerPermissions = getRolePermissions(UserRole.MANAGER);
      
      expect(managerPermissions).toContain(PERMISSIONS.USER_CREATE);
      expect(managerPermissions).toContain(PERMISSIONS.USER_UPDATE);
      expect(managerPermissions).not.toContain(PERMISSIONS.TENANT_DELETE);
      expect(managerPermissions).not.toContain(PERMISSIONS.USER_DELETE);
    });

    it('should return basic permissions for USER role', () => {
      const userPermissions = getRolePermissions(UserRole.USER);
      
      expect(userPermissions).toContain(PERMISSIONS.TENANT_READ);
      expect(userPermissions).toContain(PERMISSIONS.USER_READ);
      expect(userPermissions).not.toContain(PERMISSIONS.USER_CREATE);
      expect(userPermissions).not.toContain(PERMISSIONS.API_KEY_CREATE);
    });
  });

  describe('Permission Checking', () => {
    const userPermissions = [
      PERMISSIONS.TENANT_READ,
      PERMISSIONS.USER_READ,
      PERMISSIONS.API_KEY_READ,
    ];

    it('should correctly check single permission', () => {
      expect(hasPermission(userPermissions, PERMISSIONS.TENANT_READ)).toBe(true);
      expect(hasPermission(userPermissions, PERMISSIONS.TENANT_UPDATE)).toBe(false);
    });

    it('should correctly check any permission', () => {
      expect(hasAnyPermission(userPermissions, [
        PERMISSIONS.TENANT_READ,
        PERMISSIONS.TENANT_UPDATE,
      ])).toBe(true);

      expect(hasAnyPermission(userPermissions, [
        PERMISSIONS.TENANT_UPDATE,
        PERMISSIONS.TENANT_DELETE,
      ])).toBe(false);
    });

    it('should correctly check all permissions', () => {
      expect(hasAllPermissions(userPermissions, [
        PERMISSIONS.TENANT_READ,
        PERMISSIONS.USER_READ,
      ])).toBe(true);

      expect(hasAllPermissions(userPermissions, [
        PERMISSIONS.TENANT_READ,
        PERMISSIONS.TENANT_UPDATE,
      ])).toBe(false);
    });
  });

  describe('API Key Permissions', () => {
    it('should validate correct API key permissions', () => {
      const validPermissions = [
        PERMISSIONS.TENANT_READ,
        PERMISSIONS.USER_READ,
        PERMISSIONS.API_KEY_READ,
      ];

      expect(validateApiKeyPermissions(validPermissions)).toBe(true);
    });

    it('should reject invalid API key permissions', () => {
      const invalidPermissions = [
        PERMISSIONS.TENANT_READ,
        'invalid.permission',
      ];

      expect(validateApiKeyPermissions(invalidPermissions)).toBe(false);
    });

    it('should return default permissions for API keys', () => {
      const adminDefaults = getDefaultApiKeyPermissions(UserRole.ADMIN);
      const userDefaults = getDefaultApiKeyPermissions(UserRole.USER);

      // API keys should not have delete permissions
      expect(adminDefaults).not.toContain(PERMISSIONS.USER_DELETE);
      expect(adminDefaults).not.toContain(PERMISSIONS.TENANT_DELETE);
      expect(adminDefaults).not.toContain(PERMISSIONS.API_KEY_DELETE);

      // But should have other permissions based on role
      expect(adminDefaults).toContain(PERMISSIONS.USER_CREATE);
      expect(userDefaults).not.toContain(PERMISSIONS.USER_CREATE);
    });
  });
});