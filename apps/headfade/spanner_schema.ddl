-- HeadFade Spanner Schema v1.0
-- Phase 0: Analytical layer for high-throughput forensic telemetry
-- Firestore remains primary for user/video CRUD; Spanner handles scale reads.

-- ============================================================================
-- FORENSIC ANALYSIS EVENTS
-- High-volume event stream from Gemini forensic pipeline
-- ============================================================================
CREATE TABLE forensic_events (
  event_id        STRING(36) NOT NULL,   -- UUID v4
  video_id        STRING(36) NOT NULL,
  model_version   STRING(64) NOT NULL,   -- e.g., "gemini-3.1-flash-lite"
  verdict         STRING(16) NOT NULL,   -- "AI" | "REAL" | "INCONCLUSIVE"
  confidence      FLOAT64 NOT NULL,
  reasoning_hash  STRING(64),            -- SHA-256 of reasoning text
  latency_ms      INT64 NOT NULL,
  region          STRING(32),            -- GCP region of analysis
  created_at      TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (event_id);

CREATE INDEX idx_forensic_by_video ON forensic_events(video_id, created_at DESC);
CREATE INDEX idx_forensic_by_model ON forensic_events(model_version, created_at DESC);

-- ============================================================================
-- HUMAN TELEMETRY EVENTS
-- HDI (Human Deception Index) votes from the Global Turing Test swiper
-- ============================================================================
CREATE TABLE human_votes (
  vote_id       STRING(36) NOT NULL,
  video_id      STRING(36) NOT NULL,
  user_id       STRING(128),              -- NULL if anonymous
  user_vote     STRING(8) NOT NULL,       -- "AI" | "REAL"
  ground_truth  STRING(8) NOT NULL,       -- "AI" | "REAL"
  is_correct    BOOL NOT NULL,
  latency_ms    INT64 NOT NULL,
  device_type   STRING(16),               -- "mobile" | "desktop" | "tablet"
  country_code  STRING(2),                -- ISO 3166-1 alpha-2
  created_at    TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (vote_id);

CREATE INDEX idx_votes_by_video ON human_votes(video_id, created_at DESC);
CREATE INDEX idx_votes_by_user ON human_votes(user_id) WHERE user_id IS NOT NULL;

-- ============================================================================
-- EMBED ANALYTICS
-- Publisher embed impression/engagement tracking
-- ============================================================================
CREATE TABLE embed_impressions (
  impression_id   STRING(36) NOT NULL,
  video_id        STRING(36) NOT NULL,
  publisher_id    STRING(128) NOT NULL,
  domain          STRING(256) NOT NULL,
  referrer_url    STRING(1024),
  play_duration_s FLOAT64,
  is_play         BOOL NOT NULL DEFAULT (false),
  device_type     STRING(16),
  country_code    STRING(2),
  created_at      TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (impression_id);

CREATE INDEX idx_embed_by_publisher ON embed_impressions(publisher_id, created_at DESC);
CREATE INDEX idx_embed_by_video ON embed_impressions(video_id, created_at DESC);
CREATE INDEX idx_embed_by_domain ON embed_impressions(domain, created_at DESC);

-- ============================================================================
-- CONTENT PROVENANCE GRAPH (Remix Tree materialized view)
-- Denormalized for graph queries: ancestry lookups, depth calculations
-- ============================================================================
CREATE TABLE provenance_edges (
  edge_id       STRING(36) NOT NULL,
  parent_id     STRING(36) NOT NULL,      -- parent video_id
  child_id      STRING(36) NOT NULL,      -- child video_id
  edge_type     STRING(16) NOT NULL,      -- "REMIX" | "DERIVATIVE" | "COMPILATION"
  content_hash  STRING(64) NOT NULL,      -- SHA-256 of child content
  depth         INT64 NOT NULL,           -- Distance from original (0 = root)
  created_at    TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (edge_id);

CREATE INDEX idx_provenance_parent ON provenance_edges(parent_id);
CREATE INDEX idx_provenance_child ON provenance_edges(child_id);

-- ============================================================================
-- AGGREGATED METRICS (materialized daily by Cloud Scheduler + Dataflow)
-- ============================================================================
CREATE TABLE daily_metrics (
  metric_date     DATE NOT NULL,
  video_id        STRING(36) NOT NULL,
  total_votes     INT64 NOT NULL DEFAULT (0),
  correct_votes   INT64 NOT NULL DEFAULT (0),
  hdi_score       FLOAT64,               -- Human Deception Index (% fooled)
  total_embeds    INT64 NOT NULL DEFAULT (0),
  total_plays     INT64 NOT NULL DEFAULT (0),
  avg_play_sec    FLOAT64,
  forensic_count  INT64 NOT NULL DEFAULT (0),
  avg_confidence  FLOAT64,
  updated_at      TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (metric_date, video_id);

CREATE INDEX idx_metrics_by_video ON daily_metrics(video_id, metric_date DESC);

-- ============================================================================
-- CDC WATERMARKS (for Datastream change capture sync)
-- ============================================================================
CREATE TABLE cdc_watermarks (
  source_table  STRING(64) NOT NULL,
  last_ts       TIMESTAMP NOT NULL,
  row_count     INT64 NOT NULL DEFAULT (0),
  updated_at    TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY (source_table);
