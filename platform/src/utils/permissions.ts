import { UserRole } from '@prisma/client';

export const PERMISSIONS = {
  // Tenant management
  TENANT_READ: 'tenant:read',
  TENANT_UPDATE: 'tenant:update',
  TENANT_DELETE: 'tenant:delete',
  
  // User management
  USER_READ: 'user:read',
  USER_CREATE: 'user:create',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
  USER_INVITE: 'user:invite',
  
  // API key management
  API_KEY_READ: 'api_key:read',
  API_KEY_CREATE: 'api_key:create',
  API_KEY_UPDATE: 'api_key:update',
  API_KEY_DELETE: 'api_key:delete',
  
  // Session management
  SESSION_READ: 'session:read',
  SESSION_DELETE: 'session:delete',
  
  // Feature flags
  FEATURE_FLAG_READ: 'feature_flag:read',
  FEATURE_FLAG_UPDATE: 'feature_flag:update',
  
  // Events and audit
  EVENT_READ: 'event:read',
  
  // Analytics and usage
  ANALYTICS_READ: 'analytics:read',
  USAGE_READ: 'usage:read',
  
  // Service operations
  SERVICE_STATUS: 'service:status',
  SERVICE_HEALTH: 'service:health',
} as const;

export type Permission = typeof PERMISSIONS[keyof typeof PERMISSIONS];

export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  [UserRole.ADMIN]: [
    // Admins have all permissions
    PERMISSIONS.TENANT_READ,
    PERMISSIONS.TENANT_UPDATE,
    PERMISSIONS.TENANT_DELETE,
    PERMISSIONS.USER_READ,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_UPDATE,
    PERMISSIONS.USER_DELETE,
    PERMISSIONS.USER_INVITE,
    PERMISSIONS.API_KEY_READ,
    PERMISSIONS.API_KEY_CREATE,
    PERMISSIONS.API_KEY_UPDATE,
    PERMISSIONS.API_KEY_DELETE,
    PERMISSIONS.SESSION_READ,
    PERMISSIONS.SESSION_DELETE,
    PERMISSIONS.FEATURE_FLAG_READ,
    PERMISSIONS.FEATURE_FLAG_UPDATE,
    PERMISSIONS.EVENT_READ,
    PERMISSIONS.ANALYTICS_READ,
    PERMISSIONS.USAGE_READ,
    PERMISSIONS.SERVICE_STATUS,
    PERMISSIONS.SERVICE_HEALTH,
  ],
  
  [UserRole.MANAGER]: [
    // Managers can manage users and view most data
    PERMISSIONS.TENANT_READ,
    PERMISSIONS.USER_READ,
    PERMISSIONS.USER_CREATE,
    PERMISSIONS.USER_UPDATE,
    PERMISSIONS.USER_INVITE,
    PERMISSIONS.API_KEY_READ,
    PERMISSIONS.API_KEY_CREATE,
    PERMISSIONS.SESSION_READ,
    PERMISSIONS.FEATURE_FLAG_READ,
    PERMISSIONS.EVENT_READ,
    PERMISSIONS.ANALYTICS_READ,
    PERMISSIONS.USAGE_READ,
    PERMISSIONS.SERVICE_STATUS,
    PERMISSIONS.SERVICE_HEALTH,
  ],
  
  [UserRole.USER]: [
    // Users have read access to basic data
    PERMISSIONS.TENANT_READ,
    PERMISSIONS.USER_READ,
    PERMISSIONS.SESSION_READ,
    PERMISSIONS.FEATURE_FLAG_READ,
    PERMISSIONS.SERVICE_STATUS,
  ],
};

export function getRolePermissions(role: UserRole): Permission[] {
  return ROLE_PERMISSIONS[role] || [];
}

export function hasPermission(userPermissions: Permission[], requiredPermission: Permission): boolean {
  return userPermissions.includes(requiredPermission);
}

export function hasAnyPermission(userPermissions: Permission[], requiredPermissions: Permission[]): boolean {
  return requiredPermissions.some(permission => hasPermission(userPermissions, permission));
}

export function hasAllPermissions(userPermissions: Permission[], requiredPermissions: Permission[]): boolean {
  return requiredPermissions.every(permission => hasPermission(userPermissions, permission));
}

export function validateApiKeyPermissions(permissions: string[]): boolean {
  const validPermissions = Object.values(PERMISSIONS);
  return permissions.every(permission => validPermissions.includes(permission as Permission));
}

export function getDefaultApiKeyPermissions(userRole: UserRole): Permission[] {
  // API keys get a subset of user permissions by default
  const userPermissions = getRolePermissions(userRole);
  
  // Exclude sensitive permissions for API keys
  const excludedPermissions = [
    PERMISSIONS.USER_DELETE,
    PERMISSIONS.TENANT_DELETE,
    PERMISSIONS.API_KEY_DELETE,
    PERMISSIONS.SESSION_DELETE,
  ];
  
  return userPermissions.filter(permission => !excludedPermissions.includes(permission));
}