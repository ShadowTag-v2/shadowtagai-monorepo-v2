# Enact Split-Brain Architecture & BigQuery Autonomous Embeddings

## Goal Description
Implement the "Split-Brain" architecture to leverage local AlloyDB for low-latency agentic thought, and Cloud BigQuery with Autonomous Embeddings for petabyte-scale Zero-ETL vectorization. This eliminates the "Python Tax" for high-volume data ingestion.

## Proposed Changes

### Infrastructure & Schema
#### [NEW] [bigquery_omniscience.tf](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/infrastructure/terraform/bigquery_omniscience.tf)
Terraform definitions for the BigQuery connection to Vertex AI, IAM permissions, and the `omniscience_lake` dataset.

#### [NEW] [bq_autonomous_lake.sql](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/schema/bq_autonomous_lake.sql)
BigQuery SQL DDL to create the remote model, the autonomous table with `ML.GENERATE_EMBEDDING` default column, and the vector index.

### Python Services
#### [NEW] [data_router.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/src/brain/data_router.py)
`AutonomousDataRouter` to inherently route unstructured intelligence ingestion to local AlloyDB in `development` and BQ Autonomous Lake in `production`.

#### [NEW] [bq_omni_search.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/src/tools/bq_omni_search.py)
`OmniscienceSearchEngine` to perform semantic search over the Uphillsnowball BigQuery lake using `VECTOR_SEARCH` and native Vertex AI embedding. It will also expose an MCP FastMCP server block for local agent queries.

### Action Vectors & Tooling
#### [NEW] [deploy_bigquery.sh](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/deploy_bigquery.sh)
Terminal commands to run `terraform apply` for the BigQuery infra and execute the SQL schema. (Vector 1)

#### [NEW] [test_zero_etl_router.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/scripts/test_zero_etl_router.py)
A local script to test `AutonomousDataRouter` by setting the environment to `production` and injecting a dummy payload. (Vector 2)

#### [MODIFY] [settings.json](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/.vscode/settings.json)
Wire `bq_omni_search.py` as a native MCP tool (`search_uphillsnowball`) into the Antigravity IDE configuration. (Vector 3)

## Verification Plan
### Automated Tests
- Execute `python3 scripts/test_zero_etl_router.py` to ensure the BigQuery backend successfully receives the payload and completes without timing out or crashing.
