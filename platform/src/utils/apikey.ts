import crypto from 'crypto';
import bcrypt from 'bcryptjs';

export interface GeneratedApiKey {
  key: string;
  keyHash: string;
  keyPrefix: string;
}

export function generateApiKey(prefix: string = 'sk'): GeneratedApiKey {
  // Generate a unique prefix for the key (first 8 chars after prefix)
  const uniqueId = crypto.randomBytes(4).toString('hex');
  const keyPrefix = `${prefix}_${uniqueId}`;
  
  // Generate the actual secret part (32 bytes = 64 hex chars)
  const secretPart = crypto.randomBytes(32).toString('hex');
  
  // Combine prefix and secret
  const key = `${keyPrefix}_${secretPart}`;
  
  // Hash the key for storage
  const keyHash = bcrypt.hashSync(key, 12);
  
  return {
    key,
    keyHash,
    keyPrefix,
  };
}

export function verifyApiKey(key: string, hash: string): boolean {
  return bcrypt.compareSync(key, hash);
}

export function extractKeyPrefix(key: string): string | null {
  // Expected format: sk_12345678_64-char-secret
  const parts = key.split('_');
  if (parts.length !== 3) {
    return null;
  }
  
  return `${parts[0]}_${parts[1]}`;
}

export function validateApiKeyFormat(key: string): boolean {
  // Check if key matches expected format
  const apiKeyRegex = /^sk_[a-f0-9]{8}_[a-f0-9]{64}$/;
  return apiKeyRegex.test(key);
}

export function maskApiKey(key: string): string {
  const prefix = extractKeyPrefix(key);
  if (!prefix) {
    return '***';
  }
  
  return `${prefix}_${'*'.repeat(16)}`;
}

export function generateApiKeyName(baseName: string, existingNames: string[]): string {
  let name = baseName;
  let counter = 1;
  
  while (existingNames.includes(name)) {
    name = `${baseName} (${counter})`;
    counter++;
  }
  
  return name;
}