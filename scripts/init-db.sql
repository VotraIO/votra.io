-- VotraIO Database Initialization Script
-- This script runs automatically when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS consulting;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions
GRANT USAGE ON SCHEMA consulting TO postgres;
GRANT USAGE ON SCHEMA audit TO postgres;

-- Set search path
ALTER DATABASE votraio_db SET search_path TO consulting, public;

-- Create audit table for financial compliance
CREATE TABLE IF NOT EXISTS audit.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    user_id UUID,
    changes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster audit queries
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit.audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit.audit_log(table_name);

-- Grant audit table access
GRANT SELECT ON audit.audit_log TO postgres;

-- Log initialization
INSERT INTO audit.audit_log (table_name, operation, user_id, changes)
VALUES ('audit.audit_log', 'INIT', NULL, '{"message": "Database initialized"}');
