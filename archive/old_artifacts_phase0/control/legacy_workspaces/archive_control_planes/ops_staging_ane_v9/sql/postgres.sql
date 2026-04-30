CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS repos (
  repo_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  repo_root TEXT NOT NULL,
  default_branch TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS doc_registry (
  doc_id TEXT PRIMARY KEY,
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  rel_path TEXT NOT NULL,
  canonical_kind TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  latest_summary TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS benchmark_runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  git_commit TEXT,
  machine_name TEXT,
  chip TEXT,
  ram_gb INTEGER,
  macos_version TEXT,
  model_name TEXT,
  precision_mode TEXT,
  workload_name TEXT,
  params_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  metrics_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  raw_artifact_path TEXT,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS benchmark_summaries (
  summary_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES benchmark_runs(run_id) ON DELETE CASCADE,
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  title TEXT,
  summary TEXT NOT NULL,
  findings JSONB NOT NULL DEFAULT '[]'::jsonb,
  regressions JSONB NOT NULL DEFAULT '[]'::jsonb,
  recommendations JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence REAL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  source_type TEXT NOT NULL,
  source_ref TEXT,
  event_type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  importance REAL DEFAULT 0.5,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS semantic_memories (
  memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  memory_kind TEXT NOT NULL,
  subject TEXT NOT NULL,
  summary TEXT NOT NULL,
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  supersedes UUID REFERENCES semantic_memories(memory_id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS beads_tasks (
  bead_id TEXT PRIMARY KEY,
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  priority INTEGER,
  assignee TEXT,
  parent_bead_id TEXT,
  depends_on JSONB NOT NULL DEFAULT '[]'::jsonb,
  summary TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS retrieval_memories (
  item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL REFERENCES repos(repo_id),
  source_kind TEXT NOT NULL,
  source_ref TEXT,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ltm_threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ltm_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES ltm_threads(id) ON DELETE CASCADE,
  actor TEXT NOT NULL,
  content TEXT NOT NULL,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  importance_score INTEGER NOT NULL DEFAULT 0,
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ltm_thread_summaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES ltm_threads(id) ON DELETE CASCADE,
  summary TEXT NOT NULL,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding vector(1536),
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ltm_master_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  bucket TEXT NOT NULL,
  content TEXT NOT NULL,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ltm_master_evidence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  master_item_id UUID NOT NULL REFERENCES ltm_master_items(id) ON DELETE CASCADE,
  thread_id UUID REFERENCES ltm_threads(id) ON DELETE SET NULL,
  event_id UUID REFERENCES ltm_events(id) ON DELETE SET NULL,
  summary_id UUID REFERENCES ltm_thread_summaries(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE TABLE IF NOT EXISTS authority_snapshots (
  snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL,
  authority_kind TEXT NOT NULL, -- standards, settings, procedures, startup
  subject TEXT NOT NULL,
  content JSONB NOT NULL DEFAULT '{}'::jsonb,
  version_tag TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_authority_snapshots_repo_kind ON authority_snapshots(repo_id, authority_kind, created_at DESC);

CREATE TABLE IF NOT EXISTS authority_events (
  event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL,
  event_type TEXT NOT NULL, -- upgrade, deprecate, startup_hydration, drift_detected
  subject TEXT NOT NULL,
  body JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS changed_files_state (
  doc_id TEXT PRIMARY KEY,
  repo_id TEXT NOT NULL,
  rel_path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  last_embedded_at TIMESTAMPTZ,
  embedding_status TEXT NOT NULL DEFAULT 'pending'
);


CREATE TABLE IF NOT EXISTS memory_atoms (
  atom_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL,
  atom_kind TEXT NOT NULL, -- fact, rule, preference, procedure_step, decision, warning
  subject TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_text TEXT NOT NULL,
  canonical_weight REAL NOT NULL DEFAULT 1.0,
  validity TEXT NOT NULL DEFAULT 'active', -- active, deprecated, tentative
  source_type TEXT NOT NULL,
  source_ref TEXT,
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_memory_atoms_repo_kind ON memory_atoms(repo_id, atom_kind, created_at DESC);

CREATE TABLE IF NOT EXISTS drift_reports (
  drift_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL,
  rel_path TEXT NOT NULL,
  drift_kind TEXT NOT NULL, -- settings_mismatch, standards_mismatch, procedure_gap
  expected TEXT NOT NULL,
  observed TEXT NOT NULL,
  severity TEXT NOT NULL DEFAULT 'medium',
  suggested_fix TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_drift_reports_repo_path ON drift_reports(repo_id, rel_path, created_at DESC);


CREATE TABLE IF NOT EXISTS atom_conflicts (
  conflict_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id TEXT NOT NULL,
  subject TEXT NOT NULL,
  predicate TEXT NOT NULL,
  canonical_atom_id UUID,
  conflicting_source_type TEXT NOT NULL,
  conflicting_source_ref TEXT,
  conflicting_value TEXT NOT NULL,
  resolution_status TEXT NOT NULL DEFAULT 'open', -- open,resolved,ignored
  resolution_note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_atom_conflicts_repo_subject ON atom_conflicts(repo_id, subject, predicate, created_at DESC);
