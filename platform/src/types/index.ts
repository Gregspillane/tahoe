import { Request } from 'express';
import { TenantStatus, UserStatus, UserRole } from '@prisma/client';

export interface AuthRequest extends Request {
  tenantId?: string;
  userId?: string;
  role?: UserRole;
  permissions?: string[];
}

export interface JWTPayload {
  sub: string;
  tenant: string;
  role: UserRole;
  permissions: string[];
  iat: number;
  exp: number;
}

export interface CreateTenantRequest {
  name: string;
  slug: string;
  planTier?: string;
  settings?: Record<string, any>;
}

export interface CreateUserRequest {
  email: string;
  firstName: string;
  lastName: string;
  role?: UserRole;
  password?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    role: UserRole;
    tenant: {
      id: string;
      name: string;
      slug: string;
    };
  };
}

export interface ApiKeyRequest {
  name: string;
  permissions: string[];
  expiresAt?: Date;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface EventPayload {
  eventType: string;
  tenantId?: string;
  userId?: string;
  payload: Record<string, any>;
}

export { TenantStatus, UserStatus, UserRole };