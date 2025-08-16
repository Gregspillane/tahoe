import { Request, Response, NextFunction } from 'express';
import { verifyAccessToken, extractTokenFromHeader } from '../utils/jwt';
import { redisClient } from '../config/redis';
import { AuthRequest } from '../types';
import { logger } from '../utils/logger';
import { Permission, hasPermission, hasAnyPermission, hasAllPermissions } from '../utils/permissions';
import { getDatabase } from '../config/database';
import { ApiKeyRepository } from '../repositories/apikey.repository';
import { verifyApiKey, extractKeyPrefix } from '../utils/apikey';

export async function requireAuthentication(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const token = extractTokenFromHeader(req.headers.authorization);
    
    if (!token) {
      res.status(401).json({ error: 'No authentication token provided' });
      return;
    }

    // Verify JWT token
    const payload = verifyAccessToken(token);
    
    // Check if session exists in Redis
    const sessionData = await redisClient.getSession(payload.sub);
    if (!sessionData) {
      res.status(401).json({ error: 'Session expired or invalid' });
      return;
    }

    // Attach user context to request
    req.userId = payload.sub;
    req.tenantId = payload.tenant;
    req.role = payload.role;
    req.permissions = payload.permissions;

    logger.debug('Authentication successful', {
      userId: req.userId,
      tenantId: req.tenantId,
      role: req.role
    });

    next();
  } catch (error) {
    logger.error('Authentication failed:', error);
    
    if (error instanceof Error) {
      if (error.message === 'Token expired') {
        res.status(401).json({ error: 'Token expired' });
        return;
      }
      if (error.message === 'Invalid token') {
        res.status(401).json({ error: 'Invalid token' });
        return;
      }
    }
    
    res.status(401).json({ error: 'Authentication failed' });
  }
}

export function requireRole(allowedRoles: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.role) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (!allowedRoles.includes(req.role)) {
      res.status(403).json({ error: 'Insufficient permissions' });
      return;
    }

    next();
  };
}

export function requirePermission(requiredPermission: Permission) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.permissions) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (!hasPermission(req.permissions as Permission[], requiredPermission)) {
      res.status(403).json({ 
        error: 'Insufficient permissions',
        required: requiredPermission,
        userPermissions: req.permissions
      });
      return;
    }

    next();
  };
}

export function requireAnyPermission(requiredPermissions: Permission[]) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.permissions) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (!hasAnyPermission(req.permissions as Permission[], requiredPermissions)) {
      res.status(403).json({ 
        error: 'Insufficient permissions',
        requiredAny: requiredPermissions,
        userPermissions: req.permissions
      });
      return;
    }

    next();
  };
}

export function requireAllPermissions(requiredPermissions: Permission[]) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.permissions) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (!hasAllPermissions(req.permissions as Permission[], requiredPermissions)) {
      res.status(403).json({ 
        error: 'Insufficient permissions',
        requiredAll: requiredPermissions,
        userPermissions: req.permissions
      });
      return;
    }

    next();
  };
}

export async function optionalAuthentication(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const token = extractTokenFromHeader(req.headers.authorization);
    
    if (token) {
      const payload = verifyAccessToken(token);
      const sessionData = await redisClient.getSession(payload.sub);
      
      if (sessionData) {
        req.userId = payload.sub;
        req.tenantId = payload.tenant;
        req.role = payload.role;
        req.permissions = payload.permissions;
      }
    }
    
    next();
  } catch (error) {
    // For optional auth, we continue even if token is invalid
    logger.debug('Optional authentication failed, continuing without auth:', error);
    next();
  }
}

export async function validateInternalServiceToken(
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const serviceToken = req.headers['x-service-token'];
    const expectedToken = process.env.SERVICE_TOKEN;
    
    if (!serviceToken || !expectedToken) {
      res.status(401).json({ error: 'Service token required' });
      return;
    }
    
    if (serviceToken !== expectedToken) {
      res.status(401).json({ error: 'Invalid service token' });
      return;
    }
    
    next();
  } catch (error) {
    logger.error('Service token validation failed:', error);
    res.status(401).json({ error: 'Service authentication failed' });
  }
}

export async function requireApiKeyAuthentication(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      res.status(401).json({ error: 'API key required' });
      return;
    }

    const apiKey = authHeader.substring(7); // Remove 'Bearer ' prefix
    const keyPrefix = extractKeyPrefix(apiKey);
    
    if (!keyPrefix) {
      res.status(401).json({ error: 'Invalid API key format' });
      return;
    }

    // Find API key in database
    const db = getDatabase();
    const apiKeyRepo = new ApiKeyRepository(db);
    const apiKeyRecord = await apiKeyRepo.findByPrefix(keyPrefix);
    
    if (!apiKeyRecord) {
      res.status(401).json({ error: 'Invalid API key' });
      return;
    }

    // Verify the API key
    if (!verifyApiKey(apiKey, apiKeyRecord.keyHash)) {
      res.status(401).json({ error: 'Invalid API key' });
      return;
    }

    // Check if API key is expired
    if (apiKeyRecord.expiresAt && apiKeyRecord.expiresAt < new Date()) {
      res.status(401).json({ error: 'API key expired' });
      return;
    }

    // Check if tenant is active
    if (apiKeyRecord.tenant.status !== 'ACTIVE') {
      res.status(403).json({ error: 'Tenant account suspended' });
      return;
    }

    // Check if user is active
    if (apiKeyRecord.user.status !== 'ACTIVE') {
      res.status(403).json({ error: 'User account suspended' });
      return;
    }

    // Update last used timestamp (fire and forget)
    apiKeyRepo.updateLastUsed(apiKeyRecord.id).catch(error => {
      logger.error('Failed to update API key last used:', error);
    });

    // Attach API key context to request
    req.userId = apiKeyRecord.user.id;
    req.tenantId = apiKeyRecord.tenant.id;
    req.role = apiKeyRecord.user.role;
    req.permissions = apiKeyRecord.permissions as Permission[];

    logger.debug('API key authentication successful', {
      keyId: apiKeyRecord.id,
      keyPrefix,
      userId: req.userId,
      tenantId: req.tenantId,
      role: req.role
    });

    next();
  } catch (error) {
    logger.error('API key authentication failed:', error);
    res.status(401).json({ error: 'Authentication failed' });
  }
}

export async function requireJwtOrApiKey(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  const token = authHeader.substring(7);
  
  // Try JWT authentication first
  try {
    const payload = verifyAccessToken(token);
    const sessionData = await redisClient.getSession(payload.sub);
    
    if (sessionData) {
      req.userId = payload.sub;
      req.tenantId = payload.tenant;
      req.role = payload.role;
      req.permissions = payload.permissions;
      next();
      return;
    }
  } catch (jwtError) {
    // JWT failed, try API key authentication
    logger.debug('JWT authentication failed, trying API key:', jwtError);
  }

  // Try API key authentication
  try {
    await requireApiKeyAuthentication(req, res, next);
  } catch (apiKeyError) {
    logger.error('Both JWT and API key authentication failed:', apiKeyError);
    res.status(401).json({ error: 'Invalid authentication token' });
  }
}