import { Request, Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { logger } from '../utils/logger';

export interface ServiceAuthRequest extends Request {
  serviceName?: string;
  serviceVersion?: string;
  tenantId?: string;
  userId?: string;
}

export interface ServiceTokenPayload {
  service: string;
  version?: string;
  tenant?: string;
  user?: string;
  permissions?: string[];
  iat: number;
  exp?: number;
}

export async function validateServiceAuthentication(
  req: ServiceAuthRequest,
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
      logger.warn('Invalid service token', {
        ip: req.ip,
        userAgent: req.get('User-Agent'),
        service: req.headers['x-service-name'],
      });
      res.status(401).json({ error: 'Invalid service token' });
      return;
    }

    // Extract service metadata from headers
    req.serviceName = req.headers['x-service-name'] as string;
    req.serviceVersion = req.headers['x-service-version'] as string;
    
    // Extract tenant context if provided
    const tenantId = req.headers['x-tenant-id'] as string;
    const userId = req.headers['x-user-id'] as string;
    
    if (tenantId) req.tenantId = tenantId;
    if (userId) req.userId = userId;

    logger.debug('Service authentication successful', {
      service: req.serviceName,
      version: req.serviceVersion,
      tenantId: req.tenantId,
      userId: req.userId,
    });
    
    next();
  } catch (error) {
    logger.error('Service authentication failed:', error);
    res.status(401).json({ error: 'Service authentication failed' });
  }
}

export function requireServiceHeader(headerName: string, required: boolean = true) {
  return (req: ServiceAuthRequest, res: Response, next: NextFunction): void => {
    const headerValue = req.headers[headerName.toLowerCase()];
    
    if (required && !headerValue) {
      res.status(400).json({ 
        error: `Missing required service header: ${headerName}` 
      });
      return;
    }
    
    next();
  };
}

export function validateServicePermissions(requiredPermissions: string[]) {
  return (req: ServiceAuthRequest, res: Response, next: NextFunction): void => {
    // For now, all services with valid tokens have all permissions
    // This can be enhanced later with service-specific permission systems
    const servicePermissions = req.headers['x-service-permissions'] as string;
    
    if (requiredPermissions.length > 0 && !servicePermissions) {
      res.status(403).json({ 
        error: 'Service permissions required',
        required: requiredPermissions
      });
      return;
    }
    
    next();
  };
}

export async function forwardTenantContext(
  req: AuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  // This middleware adds tenant context headers for service-to-service calls
  const { tenantId, userId, role, permissions } = req;
  
  if (tenantId) {
    res.set('X-Forwarded-Tenant-ID', tenantId);
  }
  
  if (userId) {
    res.set('X-Forwarded-User-ID', userId);
  }
  
  if (role) {
    res.set('X-Forwarded-User-Role', role);
  }
  
  if (permissions) {
    res.set('X-Forwarded-Permissions', JSON.stringify(permissions));
  }
  
  next();
}

export function createServiceClient(serviceName: string, serviceVersion?: string) {
  const serviceToken = process.env.SERVICE_TOKEN;
  
  if (!serviceToken) {
    throw new Error('SERVICE_TOKEN environment variable not set');
  }
  
  return {
    getAuthHeaders(tenantId?: string, userId?: string, permissions?: string[]) {
      const headers: Record<string, string> = {
        'X-Service-Token': serviceToken,
        'X-Service-Name': serviceName,
      };
      
      if (serviceVersion) {
        headers['X-Service-Version'] = serviceVersion;
      }
      
      if (tenantId) {
        headers['X-Tenant-ID'] = tenantId;
      }
      
      if (userId) {
        headers['X-User-ID'] = userId;
      }
      
      if (permissions && permissions.length > 0) {
        headers['X-Service-Permissions'] = JSON.stringify(permissions);
      }
      
      return headers;
    }
  };
}

// Service registry for tracking active services
export class ServiceRegistry {
  private static services = new Map<string, {
    name: string;
    version?: string;
    lastSeen: Date;
    endpoint?: string;
  }>();

  static registerService(
    name: string, 
    version?: string, 
    endpoint?: string
  ): void {
    this.services.set(name, {
      name,
      version,
      lastSeen: new Date(),
      endpoint,
    });
    
    logger.info('Service registered', { name, version, endpoint });
  }

  static updateServiceHeartbeat(name: string): void {
    const service = this.services.get(name);
    if (service) {
      service.lastSeen = new Date();
    }
  }

  static getServices(): Array<{
    name: string;
    version?: string;
    lastSeen: Date;
    endpoint?: string;
  }> {
    return Array.from(this.services.values());
  }

  static isServiceActive(name: string, timeoutMinutes: number = 5): boolean {
    const service = this.services.get(name);
    if (!service) return false;
    
    const timeout = new Date(Date.now() - timeoutMinutes * 60 * 1000);
    return service.lastSeen > timeout;
  }

  static removeInactiveServices(timeoutMinutes: number = 30): number {
    const timeout = new Date(Date.now() - timeoutMinutes * 60 * 1000);
    let removed = 0;
    
    for (const [name, service] of this.services.entries()) {
      if (service.lastSeen < timeout) {
        this.services.delete(name);
        removed++;
        logger.info('Removed inactive service', { name, lastSeen: service.lastSeen });
      }
    }
    
    return removed;
  }
}

// Middleware to automatically register and update service heartbeats
export function serviceHeartbeat(
  req: ServiceAuthRequest,
  res: Response,
  next: NextFunction
): void {
  const { serviceName, serviceVersion } = req;
  
  if (serviceName) {
    ServiceRegistry.updateServiceHeartbeat(serviceName);
  }
  
  next();
}