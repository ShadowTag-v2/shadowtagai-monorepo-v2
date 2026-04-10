# Cor.LawTrack MVP Execution Framework

This document outlines the technical execution plan for the "BEST" deployment pathway of Cor.LawTrack (6-8 weeks for demo + full security), strictly adhering to the "Business Judgment Rule" parameters and the ShadowTag-v2 Zero-Trust security paradigm.

## User Review Required
> [!IMPORTANT]
> The architectural baseline enforces **no unencrypted databases** and **no local-only tracking**. The resulting Terraform configurations will mandate Google Cloud KMS, encrypted Cloud SQL (PostgreSQL), and S3/GCS Object Lock. These strictly increase initial operational costs. Please confirm that the Zero-Trust mandate remains non-negotiable for Phase 1 MVP.

## Proposed Changes

### Database & Infrastructure (Zero-Trust)
#### [NEW] [schema.sql](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/core/lawtrack/schema.sql)
*(Drafted)* Multi-tenant PostgreSQL schema with pgcrypto capabilities, RLS, and an immutable audit ledger.
#### [NEW] [main.tf](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/infra/terraform/main.tf)
Terraform skeleton enforcing KMS, secure RDS/CloudSQL deployment, VPC isolation, and immutable storage buckets.

### Core Backend Services (FastAPI / Python)
The backend leverages Python to inherently support Gemini 3.1 Pro inference and Apple Neural Engine integration as established in the ShadowTag-v2 architecture.

#### [NEW] [main.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/core/lawtrack/api/main.py)
FastAPI root containing the SSO/OIDC middleware and role-based access control (RBAC) gates.
#### [NEW] [ingestion.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/core/lawtrack/services/ingestion.py)
The primary webhook receiver for email ingestion. Converts unstructured email payloads into the standardized Internal Event JSON.
#### [NEW] [timeline.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/core/lawtrack/services/timeline.py)
The core engine loop. Pulls the relevant Rule Pack (e.g., FRCP, Academic Syllabus) and mathematically generates the deadlines based on the ingested event date.
#### [NEW] [help_on_demand.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/core/lawtrack/services/help_on_demand.py)
The Academic/Professional crossover assistance plugin. Routes requests between the AI Tutor context window or pings the designated human expert/teacher.

### Pnkln Prompt Execution Integration
The core logic for parsing court documents will be re-wired to use the battle-tested Pnkln code compendium.
#### [MODIFY] [gemini_parser.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/src/legaltrack/parsing/gemini_parser.py)
Will import `run` from `control/pnkln/pnkln_studio_bundle/scripts/runners.py` to execute the `lawcal` prompt template natively via Vertex AI. This abstracts away the generative model initialization and relies on the 15 years of prompt engineering captured in the Pnkln `lawcal.prompt.txt`.

### Schiznit Prodding Engine (CEOTrack)
The active ambient orchestrator that converts LegalTrack deadlines into physical/digital nudges.
#### [NEW] [prodding_engine.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/src/legaltrack/ceo_track/prodding_engine.py)
The continuous async loop that monitors the CEO's active schedule.
#### [NEW] [tesla_api.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/src/legaltrack/ceo_track/integrations/tesla_api.py)
Wrapper around the Tesla Owner API to wake vehicle, check charge limits, pre-condition cabin, and set navigation targets based on calendar events.
#### [NEW] [calendar_sync.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/src/legaltrack/calendar/google_sync.py)
Idempotent Google Calendar writer that establishes the shared truth layer for LegalTrack and Schiznit.

### Frontend Application (React/Vite)
The user interface follows a "Dark Luxury" aesthetic and focuses exclusively on rapid, high-stakes decision making.
#### [NEW] [apps/legaltrack/ui/src/App.tsx](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/ui/src/App.tsx)
The main entry point, featuring a responsive split: full-screen critical tiles on mobile, and a timeline view on desktop.
#### [NEW] [apps/legaltrack/ui/src/components/CriticalTile.tsx](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/ui/src/components/CriticalTile.tsx)
A full-screen, tap-to-act component. Adheres to NY SB S7263 (UPL AI ban) by acting strictly as a procedural router (displaying calculated deadlines and rule text) rather than generating legal advice.

### Infrastructure as Code (OpenTofu / Terraform)
Adheres to the 2026 Branko-proof "infrastructure-live" pattern using Cloud Run Gen2, KMS, and CloudSQL.
#### [NEW] [apps/legaltrack/infra/main.tf](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/infra/main.tf)
Defines the Cloud Run Serverless environment with `execution_environment = "EXECUTION_ENVIRONMENT_GEN2"`, explicit VPC egress for the CloudSQL Zero-Trust connection, and KMS-encrypted state.
#### [NEW] [apps/legaltrack/infra/variables.tf](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/legaltrack/infra/variables.tf)
Strictly typed input variables for the environment.

## Production-Wiring (Closed Beta Gaps)
The initial MVP scaffolding defined the API interfaces. To achieve Closed Beta status, the following 5 gaps will be fully executed:
1. **Webhooks (`webhooks.py` / `ingestion.py`)**: Implement the ECF/TrueFiling raw parsing pipeline instead of the background task comment stub.
2. **Calendar Sync (`google_sync.py`)**: Replace the `print()` stub with the actual Google Calendar API idempotent upsert calls.
3. **Memory DB (`memory_as_a_service.py`)**: Replace the class shell with actual `pgvector` insert and contextual retrieval queries.
4. **Agent Routing (`zt_legal_router.py` / `glicko_router.py`)**: Physically wire the Glicko-2 engine into the `agents/legal.py` extraction layer to route dynamically between DTE and MAD.
5. **Hardware Enforcement (`tesla_oem.py` / `device_sdk.py`)**: Replace the slider stubs with actual HTTP outbound requests to Twilio (SMS metrics) and the Tesla Owner API wrapper.

## Verification Plan

### Automated Tests
*   **API E2E Tests:** Execute `pytest core/lawtrack/tests/` to validate the webhook ingestion routes respond with `202 Accepted` and cleanly reject malformed payloads without leaking environment traces.
*   **Rules DB Math Validation:** Re-utilize the `test_frcp_calculator.py` regression suite against the new timeline generator to mathematically guarantee strict compliance with rolling federal/academic deadlines.

### Infrastructure Validation
*   **Security Configuration Check:** Run `terraform validate` and `tfsec` (if available locally) against the deployment scripts to mathematically prove that KMS encryption is forced `true` on all resources.
