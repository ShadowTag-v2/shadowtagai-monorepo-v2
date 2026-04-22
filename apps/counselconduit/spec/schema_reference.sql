-- schema_reference.sql
-- REFERENCE ONLY — Canonical runtime is Firestore (per AGENTS.md doctrine).
-- This SQL schema documents the logical data model and maps to Firestore collections.
--
-- Firestore Collection Mapping:
--   law_firms          → Firestore: beta_accounts (existing)
--   seu_ephemeral_tokens → Firestore: seu_tokens (new collection)
--   kovel_telemetry    → Firestore: kovel_telemetry (new collection)
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
