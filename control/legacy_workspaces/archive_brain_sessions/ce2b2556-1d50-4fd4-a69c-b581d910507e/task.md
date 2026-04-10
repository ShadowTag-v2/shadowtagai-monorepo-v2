# ShadowTag-Omega-V6 Tasks (Intelligence Synthesis)

## Phase 1: Source & Global Setup
- [x] Commit all open git changes.
- [x] Execute `hunter_killer_docker_snippet.md` equivalents so we have Ripgrep, AST-grep, and Ugrep locally.

## Phase 2: Database Re-Alignment
- [x] Revert DB to `postgres` (from `alloydbomni`) as we lack GC credits.
- [x] Ensure `shadowtag_hippocampus.sql` does not use AlloyDB native embeddings.
- [x] Execute `shadowtag_hippocampus.sql` against the database.
- [x] Load `shadowtag-laws.md` into the `shadowtag_hippocampus` index.

## Phase 3: Research & Grounding
- [x] Use Developer Knowledge MCP to pull Next.js 14 docs. (Using web search fallback)
- [x] Generate `sg` (ast-grep) script to swap frontend nav bar based on Next.js 14 docs.
- [x] Initialize `LlmAgent` using Deep Research Beta, ground it with `read_url_content` against vLLM benchmarks for Cloud Run.

## Phase 4: Code Implementations (The Ex Toto Synthesis)
- [x] Map these instructions into `src/brain/orchestrator.py` system prompts.
- [x] Inject OTLP Telemetry to `src/brain/orchestrator.py`.
- [x] Implement Visual Quant Engine in `src/citadels/omniscience_quant.py`.
- [x] Execute Visual Quant: write local test script returning PNG to disk.
- [x] Implement Pomelli Aegis UI in `src/frontend/app/components/AegisLock.tsx`.
- [x] The Firestore Pipeline Migration: Python script using Firestore aggregation pipelines to count queued tasks.
- [x] The Antigravity SDK Skill: Write `.agent/skills/genai_v1_expert.md` teaching the new `google-genai` SDK and `code_execution` tool.

## Phase 5: Infrastructure
- [x] Write Terraform config `infrastructure/monitoring.tf` for OTLP Dashboard tracking `judge6_strikes`.
- [x] Run `terraform init` and `terraform apply` in `infrastructure/terraform` (State bucket temporarily disabled for local processing).

## Phase 6: Capstone Doctrine Assimilation & Protocol 22
- [x] Execute Doctrine Ingest (`scripts/ingest_public_doctrine.py`).
- [x] Wire Protocol 22 MILDEC (`src/citadels/honeypot_synthetic_engine.py`).
- [x] Upgrade FM 2-0 Intelligence Loop (`src/citadels/omniscience_quant.py`).

## Phase 8: Final Atomic Vectors (Completed)
- [x] Write script to apply 12 atomic blocks.
- [x] Run script to update monorepo codebase entirely.
- [x] Create scripts/deploy_apex_matrix.sh and deploy tf architecture.
- [x] Create scripts/setup_copilotkit.sh to initialize src/frontend copilot dependencies.
- [x] Execute Visual Quant tests with code execution sandboxing resolving issues.
- [x] Write .agent/skills/genai_v1_expert.md.

## Phase 9: Split-Brain Zero-ETL Architecture (Completed)
- [x] BigQuery Sovereign Infrastructure (Terraform).
- [x] BigQuery Autonomous Embedding Vector Schema (SQL).
- [x] Python Data Router (Local AlloyDB vs Uphillsnowball BQ).
- [x] Swarm Native Vector Search (Python tool & FastMCP).
- [x] Validate Ingestion and Semantic Retrieval in BQ backend.
