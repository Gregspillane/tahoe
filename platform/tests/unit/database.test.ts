import { PrismaClient } from '@prisma/client';
import { initializeDatabase, connectDatabase, getDatabase } from '../../src/config/database';

describe('Database Configuration', () => {
  let prisma: PrismaClient;

  beforeAll(() => {
    prisma = initializeDatabase();
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  it('should initialize database successfully', () => {
    expect(prisma).toBeInstanceOf(PrismaClient);
  });

  it('should get database instance', () => {
    const db = getDatabase();
    expect(db).toBeInstanceOf(PrismaClient);
    expect(db).toBe(prisma);
  });

  it('should connect to database successfully', async () => {
    await expect(connectDatabase()).resolves.not.toThrow();
  });

  it('should execute basic query', async () => {
    const result = await prisma.$queryRaw`SELECT 1 as test`;
    expect(result).toBeDefined();
  });
});