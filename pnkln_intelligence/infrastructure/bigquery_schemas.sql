-- PNKLN Intelligence Pipeline - BigQuery Schemas
-- Schema design for repositories, files, functions, and research papers

-- ============================================================================
-- REPOSITORIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.repositories` (
  repo_id STRING NOT NULL,
  repo_name STRING NOT NULL,
  repo_url STRING NOT NULL,
  organization STRING,
  primary_language STRING,
  category STRING,  -- multi-agent, inference, kubernetes, etc.
  priority STRING,  -- critical, high, medium, low
  stars INT64,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  last_ingested_at TIMESTAMP,
  metadata JSON,
  total_files INT64,
  total_lines INT64,
  total_functions INT64,
  ingestion_status STRING,  -- pending, processing, completed, failed
  error_message STRING
)
PARTITION BY DATE(updated_at)
CLUSTER BY primary_language, category, priority, repo_name
OPTIONS(
  description="Repository metadata and ingestion status",
  labels=[("component", "code-search")]
);

-- ============================================================================
-- FILES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.files` (
  file_id STRING NOT NULL,
  repo_id STRING NOT NULL,
  file_path STRING NOT NULL,
  file_name STRING,
  file_extension STRING,
  programming_language STRING,
  file_size_bytes INT64,
  line_count INT64,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  file_hash STRING,  -- SHA-256 hash for deduplication
  content STRING,  -- Full file content
  gcs_uri STRING,  -- GCS path to file
  metadata JSON
)
PARTITION BY DATE(updated_at)
CLUSTER BY programming_language, file_extension, repo_id
OPTIONS(
  description="Source code files with content and metadata",
  labels=[("component", "code-search")]
);

-- ============================================================================
-- FUNCTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.functions` (
  function_id STRING NOT NULL,
  file_id STRING NOT NULL,
  repo_id STRING NOT NULL,
  function_name STRING,
  function_signature STRING,
  function_body STRING,
  docstring STRING,
  start_line INT64,
  end_line INT64,
  line_count INT64,
  programming_language STRING,
  complexity_score FLOAT64,
  created_at TIMESTAMP,
  metadata JSON,
  -- Embedding for semantic search
  embedding_model STRING,
  embedding ARRAY<FLOAT64>  -- Will be migrated to Vertex AI Vector Search
)
PARTITION BY DATE(created_at)
CLUSTER BY programming_language, repo_id, function_name
OPTIONS(
  description="Extracted functions with embeddings for semantic search",
  labels=[("component", "code-search")]
);

-- ============================================================================
-- CODE CHUNKS TABLE (for embedding)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.code_chunks` (
  chunk_id STRING NOT NULL,
  file_id STRING NOT NULL,
  repo_id STRING NOT NULL,
  chunk_text STRING NOT NULL,
  chunk_type STRING,  -- function, class, file, block
  chunk_index INT64,  -- Position within file
  start_line INT64,
  end_line INT64,
  token_count INT64,
  programming_language STRING,
  created_at TIMESTAMP,
  metadata JSON,
  -- Embedding information
  embedding_model STRING,
  embedding_dimensions INT64,
  gcs_embedding_uri STRING  -- Path to embedding vector in GCS
)
PARTITION BY DATE(created_at)
CLUSTER BY programming_language, repo_id, chunk_type
OPTIONS(
  description="Code chunks for semantic search with embeddings",
  labels=[("component", "code-search")]
);

-- ============================================================================
-- RESEARCH PAPERS TABLE (arXiv)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.research_papers` (
  paper_id STRING NOT NULL,
  arxiv_id STRING NOT NULL,
  title STRING NOT NULL,
  authors ARRAY<STRING>,
  abstract STRING,
  categories ARRAY<STRING>,
  primary_category STRING,
  published TIMESTAMP,
  updated TIMESTAMP,
  pdf_url STRING,
  pdf_gcs_uri STRING,  -- GCS path to PDF
  doi STRING,
  journal_ref STRING,
  comment STRING,
  ingested_at TIMESTAMP,
  metadata JSON,
  -- Embedding for semantic search
  embedding_model STRING,
  embedding_dimensions INT64,
  gcs_embedding_uri STRING
)
PARTITION BY DATE(published)
CLUSTER BY primary_category, DATE(published)
OPTIONS(
  description="arXiv research papers with embeddings",
  labels=[("component", "research")]
);

-- ============================================================================
-- TECH NEWS TABLE (HN, Reddit)
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.tech_news` (
  news_id STRING NOT NULL,
  source STRING NOT NULL,  -- hackernews, reddit, paperswithcode
  source_id STRING,  -- Original ID from source
  title STRING NOT NULL,
  url STRING,
  author STRING,
  score INT64,
  num_comments INT64,
  content STRING,  -- Story text or selftext
  created_at TIMESTAMP,
  ingested_at TIMESTAMP,
  metadata JSON,
  -- For Reddit
  subreddit STRING,
  upvote_ratio FLOAT64,
  -- Embedding for semantic search
  embedding_model STRING,
  gcs_embedding_uri STRING
)
PARTITION BY DATE(created_at)
CLUSTER BY source, DATE(created_at)
OPTIONS(
  description="Tech news aggregated from HN, Reddit, and other sources",
  labels=[("component", "news")]
);

-- ============================================================================
-- EMBEDDINGS METADATA TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.embeddings_metadata` (
  embedding_id STRING NOT NULL,
  entity_type STRING NOT NULL,  -- code_chunk, function, paper, news
  entity_id STRING NOT NULL,
  embedding_model STRING NOT NULL,
  embedding_dimensions INT64,
  gcs_uri STRING NOT NULL,  -- GCS path to embedding vector
  vertex_ai_index_id STRING,  -- Vertex AI Vector Search index ID
  created_at TIMESTAMP,
  metadata JSON
)
PARTITION BY DATE(created_at)
CLUSTER BY entity_type, embedding_model
OPTIONS(
  description="Metadata for all embeddings stored in Vertex AI Vector Search",
  labels=[("component", "embeddings")]
);

-- ============================================================================
-- INGESTION LOGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS `{project_id}.code_search.ingestion_logs` (
  log_id STRING NOT NULL,
  ingestion_type STRING NOT NULL,  -- repository, paper, news
  entity_id STRING,
  status STRING NOT NULL,  -- started, processing, completed, failed
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_seconds FLOAT64,
  items_processed INT64,
  items_failed INT64,
  error_message STRING,
  metadata JSON
)
PARTITION BY DATE(started_at)
CLUSTER BY ingestion_type, status
OPTIONS(
  description="Logs for all ingestion operations",
  labels=[("component", "monitoring")]
);

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Active repositories with latest statistics
CREATE OR REPLACE VIEW `{project_id}.code_search.active_repositories` AS
SELECT
  repo_id,
  repo_name,
  repo_url,
  category,
  priority,
  stars,
  total_files,
  total_lines,
  total_functions,
  last_ingested_at,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), last_ingested_at, HOUR) as hours_since_last_ingest
FROM `{project_id}.code_search.repositories`
WHERE ingestion_status = 'completed'
ORDER BY last_ingested_at DESC;

-- Code search statistics
CREATE OR REPLACE VIEW `{project_id}.code_search.search_statistics` AS
SELECT
  programming_language,
  COUNT(DISTINCT repo_id) as num_repositories,
  COUNT(DISTINCT file_id) as num_files,
  COUNT(*) as num_chunks,
  SUM(token_count) as total_tokens,
  AVG(token_count) as avg_tokens_per_chunk
FROM `{project_id}.code_search.code_chunks`
GROUP BY programming_language
ORDER BY num_chunks DESC;

-- Recent research papers by category
CREATE OR REPLACE VIEW `{project_id}.code_search.recent_papers_by_category` AS
SELECT
  primary_category,
  COUNT(*) as paper_count,
  MAX(published) as latest_paper_date,
  MIN(published) as earliest_paper_date
FROM `{project_id}.code_search.research_papers`
WHERE published >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY primary_category
ORDER BY paper_count DESC;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Note: BigQuery doesn't support traditional indexes, but uses:
-- 1. Partitioning (already defined above)
-- 2. Clustering (already defined above)
-- 3. Search indexes for full-text search

-- Create search index on code content
CREATE SEARCH INDEX IF NOT EXISTS code_content_search_idx
ON `{project_id}.code_search.code_chunks`(chunk_text)
OPTIONS(
  analyzer='STANDARD'
);

-- Create search index on paper abstracts
CREATE SEARCH INDEX IF NOT EXISTS paper_abstract_search_idx
ON `{project_id}.code_search.research_papers`(abstract, title)
OPTIONS(
  analyzer='STANDARD'
);

-- Create search index on news content
CREATE SEARCH INDEX IF NOT EXISTS news_content_search_idx
ON `{project_id}.code_search.tech_news`(title, content)
OPTIONS(
  analyzer='STANDARD'
);
