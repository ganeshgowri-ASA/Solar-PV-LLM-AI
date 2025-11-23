-- =============================================================================
-- PostgreSQL Initialization Script
-- Create extensions for Solar PV LLM AI
-- =============================================================================

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgvector for vector embeddings (if using pgvector for RAG)
-- Uncomment if you install pgvector extension
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Enable pg_trgm for fuzzy text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Enable timescaledb for time-series data (optional)
-- Uncomment if you install TimescaleDB
-- CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Database extensions created successfully';
END $$;
