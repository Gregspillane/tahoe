import { PrismaClient } from '@prisma/client';
import { initializeDatabase } from '../src/config/database';

let prisma: PrismaClient;

beforeAll(async () => {
  process.env.DATABASE_URL = process.env.DATABASE_URL || 'postgresql://tahoe_user:tahoe_pass@localhost:5432/tahoe_test';
  prisma = initializeDatabase();
  await prisma.$connect();
});

afterAll(async () => {
  await prisma.$disconnect();
});

export { prisma };