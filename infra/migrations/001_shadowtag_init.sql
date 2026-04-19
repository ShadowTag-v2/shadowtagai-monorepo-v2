-- Migration: 001_shadowtag_init
-- Description: Core metadata spine and TagEngine backing table
-- Requires: Postgres 16+, pgvector, pg_trgm

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Table definition
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    tags JSONB NOT NULL DEFAULT '{}'::jsonb,
    shadow_hash TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for TagQuery performance (p95 <= 10ms target)
-- GIN index on the jsonb tags for @> (containment) filtering
CREATE INDEX IF NOT EXISTS idx_artifacts_tags_gin ON artifacts USING GIN (tags);

-- Optional gist/trigram index for textContains if we map a specific tag key like "content"
-- CREATE INDEX IF NOT EXISTS idx_artifacts_tags_trgm ON artifacts USING GIST ((tags->>'content') gist_trgm_ops);

-- Index for cursor pagination
CREATE INDEX IF NOT EXISTS idx_artifacts_id ON artifacts (id);
