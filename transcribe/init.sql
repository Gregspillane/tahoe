-- PostgreSQL initialization script for Transcription Service
-- This script sets up the database with proper permissions

-- Ensure the database exists
SELECT 'CREATE DATABASE transcription'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'transcription');

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE transcription TO transcription_user;