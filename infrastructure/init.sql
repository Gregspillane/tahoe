-- Tahoe Infrastructure Database Initialization
-- This file initializes the shared PostgreSQL database for all Tahoe services

-- Create database if it doesn't exist (handled by POSTGRES_DB environment variable)
-- The database 'tahoe' will be created automatically by the postgres container

-- Enable UUID extension for consistent UUID generation across services
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone to UTC for consistency
SET timezone = 'UTC';

-- Create a comment documenting this database
COMMENT ON DATABASE tahoe IS 'Shared database for all Tahoe microservices';

-- Note: Individual service schemas and tables will be created by their respective migration systems
-- Service examples:
--   - Platform service: Uses Prisma to create auth/tenant tables (tenants, users, api_keys, etc.)
--   - Transcription service: Uses Prisma to create transcription tables (transcription_jobs, etc.)
--   - Future services: Each will create their own domain-specific tables