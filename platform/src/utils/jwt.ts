import jwt from 'jsonwebtoken';
import { JWTPayload } from '../types';
import { UserRole } from '@prisma/client';

const JWT_SECRET = process.env.JWT_SECRET || 'your-256-bit-secret';
const JWT_EXPIRY = process.env.JWT_EXPIRY || '3600';
const REFRESH_TOKEN_EXPIRY = process.env.REFRESH_TOKEN_EXPIRY || '604800';

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

export function generateTokens(
  userId: string,
  tenantId: string,
  role: UserRole,
  permissions: string[] = []
): TokenPair {
  const now = Math.floor(Date.now() / 1000);
  const expiresIn = parseInt(JWT_EXPIRY);
  
  const accessPayload: JWTPayload = {
    sub: userId,
    tenant: tenantId,
    role,
    permissions,
    iat: now,
    exp: now + expiresIn
  };

  const refreshPayload = {
    sub: userId,
    tenant: tenantId,
    type: 'refresh',
    iat: now,
    exp: now + parseInt(REFRESH_TOKEN_EXPIRY)
  };

  const access_token = jwt.sign(accessPayload, JWT_SECRET);
  const refresh_token = jwt.sign(refreshPayload, JWT_SECRET);

  return {
    access_token,
    refresh_token,
    expires_in: expiresIn
  };
}

export function verifyAccessToken(token: string): JWTPayload {
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as JWTPayload;
    
    if (!decoded.sub || !decoded.tenant || !decoded.role) {
      throw new Error('Invalid token payload');
    }
    
    return decoded;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new Error('Token expired');
    }
    if (error instanceof jwt.JsonWebTokenError) {
      throw new Error('Invalid token');
    }
    throw error;
  }
}

export function verifyRefreshToken(token: string): { sub: string; tenant: string } {
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as any;
    
    if (decoded.type !== 'refresh' || !decoded.sub || !decoded.tenant) {
      throw new Error('Invalid refresh token');
    }
    
    return {
      sub: decoded.sub,
      tenant: decoded.tenant
    };
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new Error('Refresh token expired');
    }
    if (error instanceof jwt.JsonWebTokenError) {
      throw new Error('Invalid refresh token');
    }
    throw error;
  }
}

export function extractTokenFromHeader(authHeader?: string): string | null {
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }
  return authHeader.substring(7);
}