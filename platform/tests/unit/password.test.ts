import { hashPassword, verifyPassword, validatePasswordStrength, generateSecurePassword } from '../../src/utils/password';

describe('Password Utilities', () => {
  const testPassword = 'TestPassword123!';
  const weakPassword = '123';

  describe('hashPassword', () => {
    it('should hash password successfully', async () => {
      const hash = await hashPassword(testPassword);
      
      expect(hash).toBeDefined();
      expect(typeof hash).toBe('string');
      expect(hash).not.toBe(testPassword);
      expect(hash.length).toBeGreaterThan(50); // bcrypt hashes are typically 60 chars
    });

    it('should generate different hashes for same password', async () => {
      const hash1 = await hashPassword(testPassword);
      const hash2 = await hashPassword(testPassword);
      
      expect(hash1).not.toBe(hash2);
    });

    it('should throw error for short password', async () => {
      await expect(hashPassword('short')).rejects.toThrow('Password must be at least 8 characters long');
    });

    it('should throw error for empty password', async () => {
      await expect(hashPassword('')).rejects.toThrow('Password must be at least 8 characters long');
    });
  });

  describe('verifyPassword', () => {
    it('should verify correct password', async () => {
      const hash = await hashPassword(testPassword);
      const isValid = await verifyPassword(testPassword, hash);
      
      expect(isValid).toBe(true);
    });

    it('should reject incorrect password', async () => {
      const hash = await hashPassword(testPassword);
      const isValid = await verifyPassword('WrongPassword123!', hash);
      
      expect(isValid).toBe(false);
    });

    it('should return false for empty password', async () => {
      const hash = await hashPassword(testPassword);
      const isValid = await verifyPassword('', hash);
      
      expect(isValid).toBe(false);
    });

    it('should return false for empty hash', async () => {
      const isValid = await verifyPassword(testPassword, '');
      
      expect(isValid).toBe(false);
    });
  });

  describe('validatePasswordStrength', () => {
    it('should validate strong password', () => {
      const result = validatePasswordStrength(testPassword);
      
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject weak password', () => {
      const result = validatePasswordStrength(weakPassword);
      
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should require minimum length', () => {
      const result = validatePasswordStrength('Short1!');
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must be at least 8 characters long');
    });

    it('should require lowercase letter', () => {
      const result = validatePasswordStrength('PASSWORD123!');
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one lowercase letter');
    });

    it('should require uppercase letter', () => {
      const result = validatePasswordStrength('password123!');
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one uppercase letter');
    });

    it('should require number', () => {
      const result = validatePasswordStrength('TestPassword!');
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one number');
    });

    it('should require special character', () => {
      const result = validatePasswordStrength('TestPassword123');
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one special character');
    });

    it('should handle empty password', () => {
      const result = validatePasswordStrength('');
      
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password is required');
    });
  });

  describe('generateSecurePassword', () => {
    it('should generate password with default length', () => {
      const password = generateSecurePassword();
      
      expect(password).toBeDefined();
      expect(password.length).toBe(16);
    });

    it('should generate password with custom length', () => {
      const password = generateSecurePassword(20);
      
      expect(password).toBeDefined();
      expect(password.length).toBe(20);
    });

    it('should generate valid password', () => {
      const password = generateSecurePassword();
      const validation = validatePasswordStrength(password);
      
      expect(validation.valid).toBe(true);
    });

    it('should generate different passwords each time', () => {
      const password1 = generateSecurePassword();
      const password2 = generateSecurePassword();
      
      expect(password1).not.toBe(password2);
    });
  });
});