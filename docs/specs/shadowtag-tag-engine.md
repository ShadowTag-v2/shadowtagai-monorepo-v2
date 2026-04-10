Module: ShadowTag

## Problem

Implement TagEngine.query with AND/OR/NOT tag filters, pagination (limit ≤ 50 + cursor), optional textContains; p95 ≤ 10ms @ 1M artifacts on dev data. Incorporate ShadowTag v2 dual-layer steganographic provenance hashing.

## Constraints

- DB: Postgres 16 + pgvector (available), pg_trgm optional
- Memory: ≤ 256MB per service pod
- Max deps: 1 DB client, no Redis (for now)
- Observability: counter(tag.query), timer(tag.query_ms)

## IO Examples

input:
allOf: {"topic":"ingest"} anyOf: {"stage":"raw","stage":"clean"} not: {"pii":true}
output:
items: [{artifactId, tags, score?, shadow?}], nextCursor?

## Target Stack

- TypeScript (Node 20), pg + zod for validation

## Acceptance Tests

- AND only; OR only; NOT only; combos; limit & cursor rollover; textContains
- latency harness passes p95 ≤ 10ms on seeded dataset
- Cross-layer ShadowTag check extracts prompt 32-byte hash reliably.

## Non-Goals

- external caches; distributed transactions

## Preferences

- jsonb tags with normalized keys; GIN indexes; query planner hints
