Module: AiYou

## Problem
Implement the RagGraph.retrieve with structured tag filtering before ANN search, followed by reranking, ensuring end-to-end p95 ≤ 120ms retrieval.

## Constraints
- DB: Postgres 16 + pgvector
- Retrieval sequence: exact tag match (via ShadowTag API) -> ANN query -> contextual rerank
- Observability: counter(aiyou.retrieve), timer(aiyou.retrieve_ms)

## IO Examples
input:
  query: "connector design"
  filter: {"topic": "ingest"}
  k: 3
output:
  hits: [{artifactId, snippet, score, tags}]

## Target Stack
- TypeScript (Node 20), pgvector, LangChain bindings

## Acceptance Tests
- RAG retrieves node successfully filtering out irrelevant topics.
- Retrieval pipeline executes ≤ 120ms under load testing.
- Missing embeddings gracefully trigger backfill or fallback logic.

## Non-Goals
- Building raw custom reranker (use adapter to external/local standard reranker initially)

## Preferences
- Fast early pruning via explicit tag filtering to reduce vector ANN compute load.
