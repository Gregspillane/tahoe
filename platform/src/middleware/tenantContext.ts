import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { getDatabase } from '../config/database';
import { TenantRepository } from '../repositories/tenant.repository';
import { UserRepository } from '../repositories/user.repository';
import { logger } from '../utils/logger';
import { TenantStatus, UserStatus } from '@prisma/client';

export interface TenantInfo {
  id: string;
  name: string;
  slug: string;
  status: TenantStatus;
  planTier: string;
  settings: any;
}

export interface UserInfo {
  id: string;
  email: string;
  role: string;
  status: UserStatus;
  firstName: string;
  lastName: string;
}

export interface EnhancedAuthRequest extends AuthRequest {
  tenantInfo?: TenantInfo;
  userInfo?: UserInfo;
}

export async function enhanceTenantContext(
  req: EnhancedAuthRequest,
  res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const { tenantId, userId } = req;

    if (!tenantId || !userId) {
      // No authentication context, continue without enhancement
      next();
      return;
    }

    const db = getDatabase();
    const tenantRepo = new TenantRepository(db);
    const userRepo = new UserRepository(db);

    // Fetch tenant and user information in parallel
    const [tenant, user] = await Promise.all([
      tenantRepo.findById(tenantId),
      userRepo.findById(userId, tenantId),
    ]);

    // Validate tenant exists and is active
    if (!tenant) {
      logger.warn('Tenant not found', { tenantId, userId });
      res.status(403).json({ error: 'Tenant not found' });
      return;
    }

    if (tenant.status !== TenantStatus.ACTIVE && tenant.status !== TenantStatus.TRIAL) {
      logger.warn('Tenant account suspended', { 
        tenantId, 
        userId, 
        tenantStatus: tenant.status 
      });
      res.status(403).json({ 
        error: 'Tenant account suspended',
        tenantStatus: tenant.status
      });
      return;
    }

    // Validate user exists and is active
    if (!user) {
      logger.warn('User not found in tenant context', { tenantId, userId });
      res.status(403).json({ error: 'User not found' });
      return;
    }

    if (user.status !== UserStatus.ACTIVE) {
      logger.warn('User account suspended', { 
        tenantId, 
        userId, 
        userStatus: user.status 
      });
      res.status(403).json({ 
        error: 'User account suspended',
        userStatus: user.status
      });
      return;
    }

    // Validate user belongs to the tenant
    if (user.tenantId !== tenantId) {
      logger.error('User tenant mismatch', { 
        tenantId, 
        userId, 
        userTenantId: user.tenantId 
      });
      res.status(403).json({ error: 'Access denied' });
      return;
    }

    // Attach enhanced context to request
    req.tenantInfo = {
      id: tenant.id,
      name: tenant.name,
      slug: tenant.slug,
      status: tenant.status,
      planTier: tenant.planTier,
      settings: tenant.settings,
    };

    req.userInfo = {
      id: user.id,
      email: user.email,
      role: user.role,
      status: user.status,
      firstName: user.firstName,
      lastName: user.lastName,
    };

    logger.debug('Tenant context enhanced', {
      tenantId: tenant.id,
      tenantName: tenant.name,
      tenantStatus: tenant.status,
      userId: user.id,
      userEmail: user.email,
      userRole: user.role,
    });

    next();
  } catch (error) {
    logger.error('Failed to enhance tenant context:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}

export function requireActiveTenant(
  req: EnhancedAuthRequest,
  res: Response,
  next: NextFunction
): void {
  const { tenantInfo } = req;

  if (!tenantInfo) {
    res.status(401).json({ error: 'Tenant context required' });
    return;
  }

  if (tenantInfo.status !== TenantStatus.ACTIVE) {
    res.status(403).json({ 
      error: 'Active tenant required',
      tenantStatus: tenantInfo.status
    });
    return;
  }

  next();
}

export function requireTrialOrActiveTenant(
  req: EnhancedAuthRequest,
  res: Response,
  next: NextFunction
): void {
  const { tenantInfo } = req;

  if (!tenantInfo) {
    res.status(401).json({ error: 'Tenant context required' });
    return;
  }

  if (tenantInfo.status !== TenantStatus.ACTIVE && tenantInfo.status !== TenantStatus.TRIAL) {
    res.status(403).json({ 
      error: 'Active or trial tenant required',
      tenantStatus: tenantInfo.status
    });
    return;
  }

  next();
}

export function requirePlanTier(allowedTiers: string[]) {
  return (req: EnhancedAuthRequest, res: Response, next: NextFunction): void => {
    const { tenantInfo } = req;

    if (!tenantInfo) {
      res.status(401).json({ error: 'Tenant context required' });
      return;
    }

    if (!allowedTiers.includes(tenantInfo.planTier)) {
      res.status(403).json({ 
        error: 'Insufficient plan tier',
        currentTier: tenantInfo.planTier,
        requiredTiers: allowedTiers
      });
      return;
    }

    next();
  };
}

export function validateTenantScope(
  req: EnhancedAuthRequest,
  res: Response,
  next: NextFunction
): void {
  const { tenantId } = req.params;
  const { tenantInfo } = req;

  // If no tenant ID in params, continue
  if (!tenantId) {
    next();
    return;
  }

  // If no tenant context, require authentication
  if (!tenantInfo) {
    res.status(401).json({ error: 'Authentication required' });
    return;
  }

  // Validate tenant ID matches authenticated tenant
  if (tenantInfo.id !== tenantId) {
    logger.warn('Tenant scope violation', {
      authenticatedTenant: tenantInfo.id,
      requestedTenant: tenantId,
      userId: req.userId,
    });
    res.status(403).json({ error: 'Access to different tenant denied' });
    return;
  }

  next();
}

export function injectTenantHeaders(
  req: EnhancedAuthRequest,
  res: Response,
  next: NextFunction
): void {
  const { tenantInfo, userInfo } = req;

  if (tenantInfo) {
    res.set('X-Tenant-ID', tenantInfo.id);
    res.set('X-Tenant-Name', tenantInfo.name);
    res.set('X-Tenant-Status', tenantInfo.status);
  }

  if (userInfo) {
    res.set('X-User-ID', userInfo.id);
    res.set('X-User-Role', userInfo.role);
  }

  next();
}