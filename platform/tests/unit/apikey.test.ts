import {
  generateApiKey,
  verifyApiKey,
  extractKeyPrefix,
  validateApiKeyFormat,
  maskApiKey,
  generateApiKeyName,
} from '../../src/utils/apikey';

describe('API Key Utilities', () => {
  describe('generateApiKey', () => {
    it('should generate valid API key with default prefix', () => {
      const result = generateApiKey();
      
      expect(result.key).toBeDefined();
      expect(result.keyHash).toBeDefined();
      expect(result.keyPrefix).toBeDefined();
      expect(result.keyPrefix).toMatch(/^sk_[a-f0-9]{8}$/);
      expect(result.key).toMatch(/^sk_[a-f0-9]{8}_[a-f0-9]{64}$/);
    });

    it('should generate valid API key with custom prefix', () => {
      const result = generateApiKey('test');
      
      expect(result.keyPrefix).toMatch(/^test_[a-f0-9]{8}$/);
      expect(result.key).toMatch(/^test_[a-f0-9]{8}_[a-f0-9]{64}$/);
    });

    it('should generate unique keys each time', () => {
      const key1 = generateApiKey();
      const key2 = generateApiKey();
      
      expect(key1.key).not.toBe(key2.key);
      expect(key1.keyPrefix).not.toBe(key2.keyPrefix);
      expect(key1.keyHash).not.toBe(key2.keyHash);
    });
  });

  describe('verifyApiKey', () => {
    it('should verify correct API key', () => {
      const { key, keyHash } = generateApiKey();
      
      expect(verifyApiKey(key, keyHash)).toBe(true);
    });

    it('should reject incorrect API key', () => {
      const { keyHash } = generateApiKey();
      const wrongKey = generateApiKey().key;
      
      expect(verifyApiKey(wrongKey, keyHash)).toBe(false);
    });

    it('should reject tampered API key', () => {
      const { key, keyHash } = generateApiKey();
      const tamperedKey = key.replace(/.$/, 'x'); // Change last character
      
      expect(verifyApiKey(tamperedKey, keyHash)).toBe(false);
    });
  });

  describe('extractKeyPrefix', () => {
    it('should extract prefix from valid API key', () => {
      const { key, keyPrefix } = generateApiKey();
      
      expect(extractKeyPrefix(key)).toBe(keyPrefix);
    });

    it('should return null for invalid API key format', () => {
      expect(extractKeyPrefix('invalid_key')).toBeNull();
      expect(extractKeyPrefix('sk_12345678')).toBeNull();
      expect(extractKeyPrefix('sk_12345678_')).toBeNull();
    });
  });

  describe('validateApiKeyFormat', () => {
    it('should validate correct API key format', () => {
      const { key } = generateApiKey();
      
      expect(validateApiKeyFormat(key)).toBe(true);
    });

    it('should reject invalid API key formats', () => {
      expect(validateApiKeyFormat('invalid')).toBe(false);
      expect(validateApiKeyFormat('sk_12345678')).toBe(false);
      expect(validateApiKeyFormat('sk_xyz_abc')).toBe(false);
      expect(validateApiKeyFormat('test_12345678_' + 'a'.repeat(64))).toBe(false);
    });
  });

  describe('maskApiKey', () => {
    it('should mask API key correctly', () => {
      const { key, keyPrefix } = generateApiKey();
      const masked = maskApiKey(key);
      
      expect(masked).toContain(keyPrefix);
      expect(masked).toContain('*'.repeat(16));
      expect(masked).not.toContain(key.split('_')[2]); // Secret part should be hidden
    });

    it('should handle invalid keys gracefully', () => {
      expect(maskApiKey('invalid')).toBe('***');
    });
  });

  describe('generateApiKeyName', () => {
    it('should return base name when no conflicts', () => {
      const result = generateApiKeyName('Test Key', []);
      
      expect(result).toBe('Test Key');
    });

    it('should append number when conflicts exist', () => {
      const existingNames = ['Test Key', 'Test Key (1)'];
      const result = generateApiKeyName('Test Key', existingNames);
      
      expect(result).toBe('Test Key (2)');
    });

    it('should find next available number', () => {
      const existingNames = ['Test Key', 'Test Key (1)', 'Test Key (3)'];
      const result = generateApiKeyName('Test Key', existingNames);
      
      expect(result).toBe('Test Key (2)');
    });
  });
});