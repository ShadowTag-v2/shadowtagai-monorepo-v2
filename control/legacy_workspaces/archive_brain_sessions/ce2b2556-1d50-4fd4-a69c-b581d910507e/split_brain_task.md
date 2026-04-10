# Split-Brain Architecture (Zero-ETL) Tasks

## Phase 1: Atomic Blocks
- [x] Create `infrastructure/terraform/bigquery_omniscience.tf`.
- [x] Create `schema/bq_autonomous_lake.sql`.
- [x] Create `src/brain/data_router.py`.
- [x] Create `src/tools/bq_omni_search.py`.

## Phase 2: Action Vectors
- [x] Vector 1 (Deploy Infra): Create `scripts/deploy_bigquery.sh`.
- [x] Vector 2 (Test Zero-ETL Router): Create `scripts/test_zero_etl_router.py`.
- [x] Vector 3 (Wire BQ Search): Modify `.vscode/settings.json` and tool scripts to register the `search_uphillsnowball` MCP server.

## Phase 3: Verification
- [x] Run deployment scripts.
- [x] Execute `scripts/test_zero_etl_router.py`.
