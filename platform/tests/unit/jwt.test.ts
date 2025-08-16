import { generateTokens, verifyAccessToken, verifyRefreshToken, extractTokenFromHeader } from '../../src/utils/jwt';
import { UserRole } from '@prisma/client';

describe('JWT Utilities', () => {
  const testUserId = 'test-user-id';
  const testTenantId = 'test-tenant-id';
  const testRole = UserRole.ADMIN;
  const testPermissions = ['read', 'write'];

  describe('generateTokens', () => {
    it('should generate valid access and refresh tokens', () => {
      const tokens = generateTokens(testUserId, testTenantId, testRole, testPermissions);

      expect(tokens.access_token).toBeDefined();
      expect(tokens.refresh_token).toBeDefined();
      expect(tokens.expires_in).toBeDefined();
      expect(typeof tokens.access_token).toBe('string');
      expect(typeof tokens.refresh_token).toBe('string');
      expect(typeof tokens.expires_in).toBe('number');
    });

    it('should generate different tokens each time', () => {
      const tokens1 = generateTokens(testUserId, testTenantId, testRole, testPermissions);
      const tokens2 = generateTokens(testUserId, testTenantId, testRole, testPermissions);

      expect(tokens1.access_token).not.toBe(tokens2.access_token);
      expect(tokens1.refresh_token).not.toBe(tokens2.refresh_token);
    });
  });

  describe('verifyAccessToken', () => {
    it('should verify valid access token', () => {
      const tokens = generateTokens(testUserId, testTenantId, testRole, testPermissions);
      const payload = verifyAccessToken(tokens.access_token);

      expect(payload.sub).toBe(testUserId);
      expect(payload.tenant).toBe(testTenantId);
      expect(payload.role).toBe(testRole);
      expect(payload.permissions).toEqual(testPermissions);
    });

    it('should throw error for invalid token', () => {
      expect(() => {
        verifyAccessToken('invalid_token');
      }).toThrow('Invalid token');
    });

    it('should throw error for malformed token', () => {
      expect(() => {
        verifyAccessToken('not.a.jwt');
      }).toThrow('Invalid token');
    });
  });

  describe('verifyRefreshToken', () => {
    it('should verify valid refresh token', () => {
      const tokens = generateTokens(testUserId, testTenantId, testRole, testPermissions);
      const payload = verifyRefreshToken(tokens.refresh_token);

      expect(payload.sub).toBe(testUserId);
      expect(payload.tenant).toBe(testTenantId);
    });

    it('should throw error for invalid refresh token', () => {
      expect(() => {
        verifyRefreshToken('invalid_token');
      }).toThrow('Invalid refresh token');
    });

    it('should reject access token as refresh token', () => {
      const tokens = generateTokens(testUserId, testTenantId, testRole, testPermissions);
      
      expect(() => {
        verifyRefreshToken(tokens.access_token);
      }).toThrow('Invalid refresh token');
    });
  });

  describe('extractTokenFromHeader', () => {
    it('should extract token from Bearer header', () => {
      const token = 'test_token_123';
      const header = `Bearer ${token}`;
      
      const extracted = extractTokenFromHeader(header);
      expect(extracted).toBe(token);
    });

    it('should return null for missing header', () => {
      const extracted = extractTokenFromHeader(undefined);
      expect(extracted).toBeNull();
    });

    it('should return null for invalid format', () => {
      const extracted = extractTokenFromHeader('InvalidFormat token');
      expect(extracted).toBeNull();
    });

    it('should return null for Bearer without token', () => {
      const extracted = extractTokenFromHeader('Bearer ');
      expect(extracted).toBe('');
    });
  });
});