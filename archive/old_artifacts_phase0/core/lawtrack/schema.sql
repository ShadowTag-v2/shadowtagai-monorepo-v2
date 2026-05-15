-- Cor.LawTrack Zero-Trust Schema MVP
-- Requires PostgreSQL with pgcrypto extension for field-level encryption (if needed beyond EBS volume encryption)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Tenants / Orgs (Supports multi-vertical routing)
CREATE TABLE tenants (
    tenant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vertical text NOT NULL, -- e.g., 'academic', 'legal', 'tax'
    name text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb, -- Enforcment intensity limits, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Rules Packages (The Domain Logic)
CREATE TABLE rule_packs (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vertical text NOT NULL,
    jurisdiction text NOT NULL,
    trigger_event_type text NOT NULL,
    deadline_math_json jsonb NOT NULL, -- e.g., {"add_days": 30, "exclude_weekends": true}
    nagging_profile jsonb NOT NULL
);

-- 3. Matters / Academic Courses
CREATE TABLE matters (
    matter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id),
    title text NOT NULL,
    encrypted_description bytea, -- Sensitive context
    status text DEFAULT 'active'
);

-- 4. Ingested Events (The Triggers)
CREATE TABLE ingested_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    matter_id UUID REFERENCES matters(matter_id),
    source text NOT NULL, -- e.g., 'email_webhook', 'manual'
    raw_payload jsonb NOT NULL,
    parsed_date TIMESTAMP WITH TIME ZONE,
    is_processed boolean DEFAULT false
);

-- 5. Timelines & Deadlines
CREATE TABLE deadlines (
    deadline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    matter_id UUID REFERENCES matters(matter_id),
    event_id UUID REFERENCES ingested_events(event_id),
    rule_id UUID REFERENCES rule_packs(rule_id),
    calculated_due_date TIMESTAMP WITH TIME ZONE NOT NULL,
    enforcement_status text DEFAULT 'pending', -- pending, nagging, escalated, completed
    completion_date TIMESTAMP WITH TIME ZONE
);

-- 6. Immutable Audit Ledger
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(tenant_id),
    actor_id UUID, -- User or AI Agent ID
    action_type text NOT NULL,
    target_record_id UUID,
    metadata jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Security Policies (Row-Level Security setup)
ALTER TABLE matters ENABLE ROW LEVEL SECURITY;
ALTER TABLE deadlines ENABLE ROW LEVEL SECURITY;
-- (Policies would be applied here linking tenant_id to the requesting auth token)
