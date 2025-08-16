import { Response } from 'express';
import { AuthRequest, ApiKeyRequest, PaginationParams } from '../types';
import { getDatabase } from '../config/database';
import { ApiKeyRepository } from '../repositories/apikey.repository';
import { UserRepository } from '../repositories/user.repository';
import { logger } from '../utils/logger';
import { generateApiKey, maskApiKey } from '../utils/apikey';
import { validateApiKeyPermissions, getDefaultApiKeyPermissions } from '../utils/permissions';

export class ApiKeyController {
  private apiKeyRepo: ApiKeyRepository;
  private userRepo: UserRepository;

  constructor() {
    const db = getDatabase();
    this.apiKeyRepo = new ApiKeyRepository(db);
    this.userRepo = new UserRepository(db);
  }

  async createApiKey(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { name, permissions, expiresAt } = req.body as ApiKeyRequest;
      const { tenantId, userId, role } = req;

      if (!tenantId || !userId || !role) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      // Validate request data
      if (!name || name.trim().length === 0) {
        res.status(400).json({ error: 'API key name is required' });
        return;
      }

      if (name.length > 100) {
        res.status(400).json({ error: 'API key name too long (max 100 characters)' });
        return;
      }

      // Validate permissions
      if (permissions && !validateApiKeyPermissions(permissions)) {
        res.status(400).json({ error: 'Invalid permissions specified' });
        return;
      }

      // Use provided permissions or default for user role
      const keyPermissions = permissions || getDefaultApiKeyPermissions(role);

      // Validate expiration date
      if (expiresAt && new Date(expiresAt) <= new Date()) {
        res.status(400).json({ error: 'Expiration date must be in the future' });
        return;
      }

      // Check if user exists and is active
      const user = await this.userRepo.findById(userId, tenantId);
      if (!user || user.status !== 'ACTIVE') {
        res.status(403).json({ error: 'User not found or inactive' });
        return;
      }

      // Generate API key
      const { key, keyHash, keyPrefix } = generateApiKey();

      // Create API key record
      const apiKey = await this.apiKeyRepo.create(
        tenantId,
        userId,
        {
          name: name.trim(),
          permissions: keyPermissions,
          expiresAt: expiresAt ? new Date(expiresAt) : undefined,
        },
        keyHash,
        keyPrefix
      );

      logger.info('API key created', {
        keyId: apiKey.id,
        tenantId,
        userId,
        keyPrefix,
        permissions: keyPermissions,
      });

      // Return the API key (only time we show the full key)
      res.status(201).json({
        id: apiKey.id,
        name: apiKey.name,
        key, // Full key - this is the only time we return it
        keyPrefix,
        permissions: apiKey.permissions,
        expiresAt: apiKey.expiresAt,
        createdAt: apiKey.createdAt,
        createdBy: {
          id: apiKey.user.id,
          email: apiKey.user.email,
          firstName: apiKey.user.firstName,
          lastName: apiKey.user.lastName,
        },
      });
    } catch (error) {
      logger.error('Failed to create API key:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async getApiKeys(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { tenantId } = req;
      const params: PaginationParams = {
        page: parseInt(req.query.page as string) || 1,
        limit: parseInt(req.query.limit as string) || 10,
        sortBy: req.query.sortBy as string || 'createdAt',
        sortOrder: (req.query.sortOrder as 'asc' | 'desc') || 'desc',
      };

      if (!tenantId) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      const result = await this.apiKeyRepo.findByTenant(tenantId, params);

      // Mask the API keys in the response
      const maskedApiKeys = result.apiKeys.map(apiKey => ({
        id: apiKey.id,
        name: apiKey.name,
        keyPrefix: apiKey.keyPrefix,
        maskedKey: maskApiKey(`${apiKey.keyPrefix}_${'x'.repeat(64)}`),
        permissions: apiKey.permissions,
        lastUsedAt: apiKey.lastUsedAt,
        expiresAt: apiKey.expiresAt,
        createdAt: apiKey.createdAt,
        createdBy: {
          id: apiKey.user.id,
          email: apiKey.user.email,
          firstName: apiKey.user.firstName,
          lastName: apiKey.user.lastName,
        },
      }));

      res.json({
        apiKeys: maskedApiKeys,
        pagination: {
          page: result.page,
          limit: params.limit,
          total: result.total,
          totalPages: result.totalPages,
        },
      });
    } catch (error) {
      logger.error('Failed to fetch API keys:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async getApiKey(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const { tenantId } = req;

      if (!tenantId) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      const apiKey = await this.apiKeyRepo.findById(id, tenantId);
      if (!apiKey) {
        res.status(404).json({ error: 'API key not found' });
        return;
      }

      res.json({
        id: apiKey.id,
        name: apiKey.name,
        keyPrefix: apiKey.keyPrefix,
        maskedKey: maskApiKey(`${apiKey.keyPrefix}_${'x'.repeat(64)}`),
        permissions: apiKey.permissions,
        lastUsedAt: apiKey.lastUsedAt,
        expiresAt: apiKey.expiresAt,
        createdAt: apiKey.createdAt,
        createdBy: {
          id: apiKey.user.id,
          email: apiKey.user.email,
          firstName: apiKey.user.firstName,
          lastName: apiKey.user.lastName,
        },
      });
    } catch (error) {
      logger.error('Failed to fetch API key:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async updateApiKey(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const { name, permissions, expiresAt } = req.body;
      const { tenantId } = req;

      if (!tenantId) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      // Validate request data
      if (name !== undefined) {
        if (!name || name.trim().length === 0) {
          res.status(400).json({ error: 'API key name cannot be empty' });
          return;
        }
        if (name.length > 100) {
          res.status(400).json({ error: 'API key name too long (max 100 characters)' });
          return;
        }
      }

      if (permissions !== undefined && !validateApiKeyPermissions(permissions)) {
        res.status(400).json({ error: 'Invalid permissions specified' });
        return;
      }

      if (expiresAt !== undefined && expiresAt !== null && new Date(expiresAt) <= new Date()) {
        res.status(400).json({ error: 'Expiration date must be in the future' });
        return;
      }

      const updateData: any = {};
      if (name !== undefined) updateData.name = name.trim();
      if (permissions !== undefined) updateData.permissions = permissions;
      if (expiresAt !== undefined) updateData.expiresAt = expiresAt ? new Date(expiresAt) : null;

      const apiKey = await this.apiKeyRepo.update(id, tenantId, updateData);
      if (!apiKey) {
        res.status(404).json({ error: 'API key not found' });
        return;
      }

      logger.info('API key updated', {
        keyId: apiKey.id,
        tenantId,
        updates: Object.keys(updateData),
      });

      res.json({
        id: apiKey.id,
        name: apiKey.name,
        keyPrefix: apiKey.keyPrefix,
        maskedKey: maskApiKey(`${apiKey.keyPrefix}_${'x'.repeat(64)}`),
        permissions: apiKey.permissions,
        lastUsedAt: apiKey.lastUsedAt,
        expiresAt: apiKey.expiresAt,
        createdAt: apiKey.createdAt,
        createdBy: {
          id: apiKey.user.id,
          email: apiKey.user.email,
          firstName: apiKey.user.firstName,
          lastName: apiKey.user.lastName,
        },
      });
    } catch (error) {
      logger.error('Failed to update API key:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async revokeApiKey(req: AuthRequest, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const { tenantId, userId } = req;

      if (!tenantId || !userId) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      const apiKey = await this.apiKeyRepo.revoke(id);
      if (!apiKey) {
        res.status(404).json({ error: 'API key not found' });
        return;
      }

      logger.info('API key revoked', {
        keyId: apiKey.id,
        tenantId,
        revokedBy: userId,
      });

      res.json({ message: 'API key revoked successfully' });
    } catch (error) {
      logger.error('Failed to revoke API key:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}