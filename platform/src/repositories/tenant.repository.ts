import { PrismaClient, Tenant, TenantStatus } from '@prisma/client';
import { CreateTenantRequest, PaginationParams } from '../types';

export class TenantRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(tenantId: string, includeDeleted = false): Promise<Tenant | null> {
    return this.prisma.tenant.findFirst({
      where: {
        id: tenantId,
        ...(!includeDeleted && { deletedAt: null }),
      },
    });
  }

  async findBySlug(slug: string, includeDeleted = false): Promise<Tenant | null> {
    return this.prisma.tenant.findFirst({
      where: {
        slug,
        ...(!includeDeleted && { deletedAt: null }),
      },
    });
  }

  async create(data: CreateTenantRequest): Promise<Tenant> {
    return this.prisma.tenant.create({
      data: {
        name: data.name,
        slug: data.slug,
        planTier: data.planTier || 'free',
        settings: data.settings || {},
      },
    });
  }

  async update(tenantId: string, data: Partial<CreateTenantRequest>): Promise<Tenant> {
    return this.prisma.tenant.update({
      where: { id: tenantId },
      data: {
        ...data,
        updatedAt: new Date(),
      },
    });
  }

  async updateStatus(tenantId: string, status: TenantStatus): Promise<Tenant> {
    return this.prisma.tenant.update({
      where: { id: tenantId },
      data: {
        status,
        updatedAt: new Date(),
      },
    });
  }

  async softDelete(tenantId: string): Promise<Tenant> {
    return this.prisma.tenant.update({
      where: { id: tenantId },
      data: {
        deletedAt: new Date(),
        updatedAt: new Date(),
      },
    });
  }

  async findMany(params: PaginationParams = {}): Promise<Tenant[]> {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = params;
    const skip = (page - 1) * limit;

    return this.prisma.tenant.findMany({
      where: { deletedAt: null },
      skip,
      take: limit,
      orderBy: { [sortBy]: sortOrder },
    });
  }

  async count(): Promise<number> {
    return this.prisma.tenant.count({
      where: { deletedAt: null },
    });
  }

  async findUsers(tenantId: string, params: PaginationParams = {}) {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = params;
    const skip = (page - 1) * limit;

    return this.prisma.user.findMany({
      where: {
        tenantId,
        deletedAt: null,
      },
      skip,
      take: limit,
      orderBy: { [sortBy]: sortOrder },
      select: {
        id: true,
        email: true,
        firstName: true,
        lastName: true,
        role: true,
        status: true,
        lastLoginAt: true,
        createdAt: true,
        updatedAt: true,
      },
    });
  }
}