import { PrismaClient, ApiKey, Prisma } from '@prisma/client';
import { ApiKeyRequest, PaginationParams } from '../types';
import { Permission } from '../utils/permissions';

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
        permissions: data.permissions as Prisma.JsonArray,
        expiresAt: data.expiresAt || null,
      },
      include: {
        tenant: {
          select: {
            id: true,
            name: true,
            slug: true,
          },
        },
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

  async update(
    keyId: string,
    tenantId: string,
    data: Partial<{ name: string; permissions: Permission[]; expiresAt: Date | null }>
  ): Promise<ApiKey | null> {
    try {
      return await this.prisma.apiKey.update({
        where: {
          id: keyId,
          tenantId,
          revokedAt: null,
        },
        data: {
          ...data,
          ...(data.permissions && { permissions: data.permissions as Prisma.JsonArray }),
        },
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
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError && error.code === 'P2025') {
        return null;
      }
      throw error;
    }
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

  async findByTenant(
    tenantId: string, 
    params: PaginationParams = {}
  ): Promise<{ apiKeys: ApiKey[]; total: number; page: number; totalPages: number }> {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = params;
    const skip = (page - 1) * limit;

    const where: Prisma.ApiKeyWhereInput = {
      tenantId,
      revokedAt: null,
    };

    const [apiKeys, total] = await Promise.all([
      this.prisma.apiKey.findMany({
        where,
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
      }),
      this.prisma.apiKey.count({ where }),
    ]);

    return {
      apiKeys,
      total,
      page,
      totalPages: Math.ceil(total / limit),
    };
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