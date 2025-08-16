import { PrismaClient, User, UserStatus, UserRole } from '@prisma/client';
import { CreateUserRequest, PaginationParams } from '../types';

export class UserRepository {
  constructor(private prisma: PrismaClient) {}

  async findById(userId: string, includeDeleted = false): Promise<User | null> {
    return this.prisma.user.findFirst({
      where: {
        id: userId,
        ...(!includeDeleted && { deletedAt: null }),
      },
      include: {
        tenant: true,
      },
    });
  }

  async findByEmail(email: string, includeDeleted = false): Promise<User | null> {
    return this.prisma.user.findFirst({
      where: {
        email,
        ...(!includeDeleted && { deletedAt: null }),
      },
      include: {
        tenant: true,
      },
    });
  }

  async findByTenantAndEmail(tenantId: string, email: string): Promise<User | null> {
    return this.prisma.user.findFirst({
      where: {
        tenantId,
        email,
        deletedAt: null,
      },
      include: {
        tenant: true,
      },
    });
  }

  async create(tenantId: string, data: CreateUserRequest): Promise<User> {
    return this.prisma.user.create({
      data: {
        tenantId,
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        role: data.role || UserRole.USER,
        passwordHash: data.password || '', // Will be hashed by service layer
        status: data.password ? UserStatus.ACTIVE : UserStatus.INVITED,
      },
      include: {
        tenant: true,
      },
    });
  }

  async update(userId: string, data: Partial<CreateUserRequest>): Promise<User> {
    return this.prisma.user.update({
      where: { id: userId },
      data: {
        ...data,
        updatedAt: new Date(),
      },
      include: {
        tenant: true,
      },
    });
  }

  async updatePassword(userId: string, passwordHash: string): Promise<User> {
    return this.prisma.user.update({
      where: { id: userId },
      data: {
        passwordHash,
        status: UserStatus.ACTIVE,
        updatedAt: new Date(),
      },
    });
  }

  async updateStatus(userId: string, status: UserStatus): Promise<User> {
    return this.prisma.user.update({
      where: { id: userId },
      data: {
        status,
        updatedAt: new Date(),
      },
    });
  }

  async updateLastLogin(userId: string): Promise<User> {
    return this.prisma.user.update({
      where: { id: userId },
      data: {
        lastLoginAt: new Date(),
        updatedAt: new Date(),
      },
    });
  }

  async softDelete(userId: string): Promise<User> {
    return this.prisma.user.update({
      where: { id: userId },
      data: {
        deletedAt: new Date(),
        updatedAt: new Date(),
      },
    });
  }

  async findByTenant(tenantId: string, params: PaginationParams = {}) {
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

  async countByTenant(tenantId: string): Promise<number> {
    return this.prisma.user.count({
      where: {
        tenantId,
        deletedAt: null,
      },
    });
  }
}