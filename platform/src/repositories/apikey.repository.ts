import { PrismaClient, ApiKey } from '@prisma/client';
import { ApiKeyRequest, PaginationParams } from '../types';

export class ApiKeyRepository {
  constructor(private prisma: PrismaClient) {}

  async findByPrefix(keyPrefix: string): Promise<ApiKey | null> {
    return this.prisma.apiKey.findFirst({
      where: {
        keyPrefix,
        revokedAt: null,
        OR: [
          { expiresAt: null },
          { expiresAt: { gt: new Date() } },
        ],
      },
      include: {
        tenant: true,
        user: true,
      },
    });
  }

  async findById(keyId: string): Promise<ApiKey | null> {
    return this.prisma.apiKey.findUnique({
      where: { id: keyId },
      include: {
        tenant: true,
        user: true,
      },
    });
  }

  async create(
    tenantId: string,
    userId: string,
    data: ApiKeyRequest,
    keyHash: string,
    keyPrefix: string
  ): Promise<ApiKey> {
    return this.prisma.apiKey.create({
      data: {
        tenantId,
        createdBy: userId,
        name: data.name,
        keyHash,
        keyPrefix,
        permissions: data.permissions,
        expiresAt: data.expiresAt || null,
      },
      include: {
        tenant: true,
        user: true,
      },
    });
  }

  async updateLastUsed(keyId: string): Promise<ApiKey> {
    return this.prisma.apiKey.update({
      where: { id: keyId },
      data: {
        lastUsedAt: new Date(),
      },
    });
  }

  async revoke(keyId: string): Promise<ApiKey> {
    return this.prisma.apiKey.update({
      where: { id: keyId },
      data: {
        revokedAt: new Date(),
      },
    });
  }

  async findByTenant(tenantId: string, params: PaginationParams = {}): Promise<ApiKey[]> {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = params;
    const skip = (page - 1) * limit;

    return this.prisma.apiKey.findMany({
      where: {
        tenantId,
        revokedAt: null,
      },
      skip,
      take: limit,
      orderBy: { [sortBy]: sortOrder },
      include: {
        user: {
          select: {
            id: true,
            email: true,
            firstName: true,
            lastName: true,
          },
        },
      },
    });
  }

  async countByTenant(tenantId: string): Promise<number> {
    return this.prisma.apiKey.count({
      where: {
        tenantId,
        revokedAt: null,
      },
    });
  }

  async findExpired(): Promise<ApiKey[]> {
    return this.prisma.apiKey.findMany({
      where: {
        expiresAt: { lt: new Date() },
        revokedAt: null,
      },
    });
  }
}