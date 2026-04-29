-- 1. Enable Vector Extension (Requires PG15+ and pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. The Main Decision Registry (The "Nodes")
CREATE TABLE IF NOT EXISTS decisions (
    decision_id VARCHAR(32) PRIMARY KEY, -- 'DEC-20260119-X7B9'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Metadata extracted for fast filtering
    decision_outcome VARCHAR(20), -- 'APPROVE', 'REJECT', 'ESCALATE'
    confidence_score FLOAT,
    authority_score FLOAT DEFAULT 0.0, -- The PageRank Score

    -- The Full AI Output (Flexible Storage)
    full_json JSONB NOT NULL,

    -- The Embedding (assuming 768 dims for now, adjust based on model)
    embedding vector(768)
);

-- 3. The Citation Network (The "Edges")
CREATE TABLE IF NOT EXISTS citations (
    id SERIAL PRIMARY KEY,
    source_decision_id VARCHAR(32) REFERENCES decisions(decision_id),
    cited_decision_id VARCHAR(32) REFERENCES decisions(decision_id),

    citation_weight FLOAT DEFAULT 1.0, -- Modified by success/failure outcome

    UNIQUE(source_decision_id, cited_decision_id)
);

-- 4. Outcomes (The Feedback Loop)
CREATE TABLE IF NOT EXISTS outcomes (
    id SERIAL PRIMARY KEY,
    decision_id VARCHAR(32) REFERENCES decisions(decision_id),
    outcome_type VARCHAR(20), -- 'LOAN_REPAID', 'DEFAULT', 'AUDIT_PASS'
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- INDEXES for Speed
CREATE INDEX IF NOT EXISTS idx_decisions_json ON decisions USING GIN (full_json);
CREATE INDEX IF NOT EXISTS idx_decisions_embedding ON decisions USING hnsw (embedding vector_cosine_ops);
