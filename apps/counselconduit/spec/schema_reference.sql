-- schema_reference.sql
-- REFERENCE ONLY — Canonical runtime is Firestore (per AGENTS.md doctrine).
-- This SQL schema documents the logical data model and maps to Firestore collections.
--
-- Firestore Collection Mapping:
--   law_firms              → Firestore: beta_accounts (existing)
--   seu_ephemeral_tokens   → Firestore: seu_tokens (existing)
--   kovel_telemetry        → Firestore: kovel_telemetry (existing)
--   murder_board_sessions  → Firestore: murder_board_sessions (new)
--   verb_ledger            → Firestore: verb_ledger (new)
--   kovel_billing_telemetry → Firestore: kovel_billing_telemetry (new)
--   brief_exports          → Firestore: brief_exports (new — 30-day TTL)
--   advance_fee_rules      → Firestore: advance_fee_rules (new — read-only ref)
--
-- This file exists for:
--   1. Court-admissible documentation of data architecture
--   2. PostgreSQL reference if enterprise customers require SQL (Phase 4: BYOC)
--   3. Schema validation tooling

-- Block 1: The Zero-Data Telemetry & Financial Ledger

CREATE TABLE law_firms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  stripe_connect_account_id TEXT NOT NULL,
  subscription_tier TEXT DEFAULT 'professional',
  oauth_vault_token TEXT -- Encrypted AES-256 (Clio/OneDrive API keys)
);

-- The S.E.U. Token Ledger (Defeating the Perplexity Hack)
CREATE TABLE seu_ephemeral_tokens (
  token_hash TEXT PRIMARY KEY,
  firm_id UUID REFERENCES law_firms(id),
  client_ip TEXT NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  is_active BOOLEAN DEFAULT TRUE
);

-- The Kovel Audit Log & Billing Telemetry (NO CHAT TEXT STORED)
CREATE TABLE kovel_telemetry (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  firm_id UUID REFERENCES law_firms(id),
  client_stripe_charge_id TEXT NOT NULL,
  attorney_directive_hash TEXT NOT NULL,
  zdr_enterprise_enforced BOOLEAN DEFAULT TRUE,
  client_upfront_payment_cents INT NOT NULL,
  tokens_consumed INT NOT NULL,
  model_routed TEXT NOT NULL,
  search_queries_executed INT DEFAULT 0,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Block 2: War Room Pipeline (NEW — v2.2)

-- Murder Board Session State
CREATE TABLE murder_board_sessions (
  session_id TEXT PRIMARY KEY,
  firm_id UUID REFERENCES law_firms(id),
  status TEXT NOT NULL DEFAULT 'intake',
  -- Valid statuses: intake, osint, verb_audit, oracle, citations, brief, vault, complete, failed
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  -- Stage outputs (JSON blobs in Firestore, TEXT here for reference)
  intake_data JSONB,
  osint_queries JSONB,
  osint_results TEXT,
  verb_audit JSONB,
  oracle_memo TEXT,
  citations JSONB,
  brief_content TEXT,
  error TEXT,
  -- S.E.U. binding
  seu_token_hash TEXT NOT NULL,
  context_cache_id TEXT
);

-- Verb Ledger — Kinematic Action Verb Analysis (NO TRANSCRIPT STORED)
CREATE TABLE verb_ledger (
  session_id TEXT PRIMARY KEY,
  firm_id UUID REFERENCES law_firms(id),
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  verbs JSONB NOT NULL DEFAULT '[]',
  -- Each verb: {verb, context, kinematic_classification, cause_of_action, element_matched, confidence, strengthens_or_weakens}
  causes_of_action_summary JSONB NOT NULL DEFAULT '{}'
  -- {action: {count, avg_confidence}}
);

-- Extended Billing Telemetry for War Room Sessions
CREATE TABLE kovel_billing_telemetry (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  firm_id UUID REFERENCES law_firms(id),
  session_id TEXT NOT NULL,
  pipeline_type TEXT NOT NULL DEFAULT 'war_room',
  stages_completed INT NOT NULL DEFAULT 0,
  verb_count INT NOT NULL DEFAULT 0,
  citation_count INT NOT NULL DEFAULT 0,
  model_routed TEXT NOT NULL,
  client_upfront_payment_cents INT NOT NULL DEFAULT 0,
  tokens_consumed INT NOT NULL DEFAULT 0,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Brief Exports (30-day TTL for GDPR compliance)
CREATE TABLE brief_exports (
  session_id TEXT PRIMARY KEY,
  firm_id UUID REFERENCES law_firms(id),
  generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days'),
  kovel_attestation_hash TEXT NOT NULL,
  privilege_designation TEXT DEFAULT 'Attorney Work-Product',
  brief_content TEXT NOT NULL,
  page_count INT DEFAULT 0
);

-- Advance Fee State Rules (Read-Only Reference Data)
CREATE TABLE advance_fee_rules (
  state CHAR(2) PRIMARY KEY,
  state_name TEXT NOT NULL,
  default_destination TEXT NOT NULL DEFAULT 'trust',
  -- trust, operating, trust_with_exception
  allows_operating_deposit BOOLEAN DEFAULT FALSE,
  operating_conditions TEXT,
  disclosure_required TEXT DEFAULT 'trust_account_notice',
  -- none, written_notice, signed_agreement, trust_account_notice
  refund_required BOOLEAN DEFAULT TRUE,
  governing_rule TEXT NOT NULL,
  notes TEXT
);
