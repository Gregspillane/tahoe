import { Request, Response } from 'express';
import { UserRepository } from '../repositories/user.repository';
import { generateTokens, verifyRefreshToken, extractTokenFromHeader } from '../utils/jwt';
import { verifyPassword } from '../utils/password';
import { redisClient } from '../config/redis';
import { LoginRequest, LoginResponse, AuthRequest } from '../types';
import { logger } from '../utils/logger';
import { getDatabase } from '../config/database';

export class AuthController {
  async login(req: Request, res: Response): Promise<void> {
    try {
      const { email, password }: LoginRequest = req.body;

      if (!email || !password) {
        res.status(400).json({ error: 'Email and password are required' });
        return;
      }

      // Find user by email
      const userRepository = new UserRepository(getDatabase());
      const user = await userRepository.findByEmail(email);
      if (!user) {
        res.status(401).json({ error: 'Invalid credentials' });
        return;
      }

      // Check if user is active
      if (user.status !== 'ACTIVE') {
        res.status(401).json({ error: 'Account is not active' });
        return;
      }

      // Verify password
      const isValidPassword = await verifyPassword(password, user.passwordHash);
      if (!isValidPassword) {
        res.status(401).json({ error: 'Invalid credentials' });
        return;
      }

      // Get tenant information
      const db = getDatabase();
      const tenant = await db.tenant.findUnique({
        where: { id: user.tenantId }
      });

      if (!tenant || tenant.status !== 'ACTIVE') {
        res.status(401).json({ error: 'Tenant account is not active' });
        return;
      }

      // Generate tokens
      const tokens = generateTokens(
        user.id,
        user.tenantId,
        user.role,
        [] // TODO: Implement proper permissions
      );

      // Store session in Redis
      await redisClient.setSession(
        user.id,
        user.id,
        user.tenantId,
        tokens.expires_in
      );

      // Update last login
      await userRepository.updateLastLogin(user.id);

      // Prepare response
      const response: LoginResponse = {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        expires_in: tokens.expires_in,
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
          tenant: {
            id: tenant.id,
            name: tenant.name,
            slug: tenant.slug
          }
        }
      };

      logger.info('User logged in successfully', {
        userId: user.id,
        tenantId: user.tenantId,
        email: user.email
      });

      res.json(response);
    } catch (error) {
      logger.error('Login error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async logout(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.userId) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      // Delete session from Redis
      await redisClient.deleteSession(req.userId);

      logger.info('User logged out successfully', {
        userId: req.userId,
        tenantId: req.tenantId
      });

      res.json({ message: 'Logged out successfully' });
    } catch (error) {
      logger.error('Logout error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async refresh(req: Request, res: Response): Promise<void> {
    try {
      const { refresh_token } = req.body;

      if (!refresh_token) {
        res.status(400).json({ error: 'Refresh token is required' });
        return;
      }

      // Verify refresh token
      const refreshPayload = verifyRefreshToken(refresh_token);

      // Check if user still exists and is active
      const userRepository = new UserRepository(getDatabase());
      const user = await userRepository.findById(refreshPayload.sub);
      if (!user || user.status !== 'ACTIVE') {
        res.status(401).json({ error: 'User not found or inactive' });
        return;
      }

      // Check if tenant is still active
      const db = getDatabase();
      const tenant = await db.tenant.findUnique({
        where: { id: user.tenantId }
      });

      if (!tenant || tenant.status !== 'ACTIVE') {
        res.status(401).json({ error: 'Tenant account is not active' });
        return;
      }

      // Generate new access token
      const tokens = generateTokens(
        user.id,
        user.tenantId,
        user.role,
        [] // TODO: Implement proper permissions
      );

      // Update session in Redis
      await redisClient.setSession(
        user.id,
        user.id,
        user.tenantId,
        tokens.expires_in
      );

      logger.info('Token refreshed successfully', {
        userId: user.id,
        tenantId: user.tenantId
      });

      res.json({
        access_token: tokens.access_token,
        expires_in: tokens.expires_in
      });
    } catch (error) {
      logger.error('Token refresh error:', error);
      
      if (error instanceof Error) {
        if (error.message.includes('expired') || error.message.includes('Invalid')) {
          res.status(401).json({ error: error.message });
          return;
        }
      }
      
      res.status(500).json({ error: 'Internal server error' });
    }
  }

  async validate(req: Request, res: Response): Promise<void> {
    try {
      const { token } = req.body;
      const serviceToken = req.headers['x-service-token'];
      
      // Validate service token for internal calls
      if (!serviceToken || serviceToken !== process.env.SERVICE_TOKEN) {
        res.status(401).json({ error: 'Invalid service token' });
        return;
      }

      if (!token) {
        res.status(400).json({ error: 'Token is required' });
        return;
      }

      // Verify the token
      const payload = verifyRefreshToken(token);
      
      // Check session
      const sessionData = await redisClient.getSession(payload.sub);
      if (!sessionData) {
        res.json({ valid: false, error: 'Session not found' });
        return;
      }

      // Get user data
      const userRepository = new UserRepository(getDatabase());
      const user = await userRepository.findById(payload.sub);
      if (!user || user.status !== 'ACTIVE') {
        res.json({ valid: false, error: 'User not found or inactive' });
        return;
      }

      res.json({
        valid: true,
        tenant_id: user.tenantId,
        user_id: user.id,
        role: user.role,
        permissions: [] // TODO: Implement proper permissions
      });
    } catch (error) {
      logger.error('Token validation error:', error);
      res.json({ valid: false, error: 'Invalid token' });
    }
  }

  async me(req: AuthRequest, res: Response): Promise<void> {
    try {
      if (!req.userId) {
        res.status(401).json({ error: 'Authentication required' });
        return;
      }

      const userRepository = new UserRepository(getDatabase());
      const user = await userRepository.findById(req.userId);
      if (!user) {
        res.status(404).json({ error: 'User not found' });
        return;
      }

      const db = getDatabase();
      const tenant = await db.tenant.findUnique({
        where: { id: user.tenantId }
      });

      res.json({
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        status: user.status,
        lastLoginAt: user.lastLoginAt,
        tenant: tenant ? {
          id: tenant.id,
          name: tenant.name,
          slug: tenant.slug,
          status: tenant.status,
          planTier: tenant.planTier
        } : null
      });
    } catch (error) {
      logger.error('Get user profile error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
}