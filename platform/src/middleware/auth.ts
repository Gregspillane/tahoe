import { Request, Response, NextFunction } from 'express';
import { verifyAccessToken, extractTokenFromHeader } from '../utils/jwt';
import { redisClient } from '../config/redis';
import { AuthRequest } from '../types';
import { logger } from '../utils/logger';

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

export function requirePermission(requiredPermission: string) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.permissions) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (!req.permissions.includes(requiredPermission)) {
      res.status(403).json({ error: 'Insufficient permissions' });
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