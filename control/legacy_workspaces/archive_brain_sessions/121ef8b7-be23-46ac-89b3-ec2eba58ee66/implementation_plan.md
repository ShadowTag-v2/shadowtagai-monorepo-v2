# SHADOWTAG OS vFINAL: Implementation Plan

## Core Objective

Convert the ShadowTag Engine from a MapReduce scraping batch job into a real-time **Streaming Cortex**. This requires injecting FAISS (for sub-millisecond RAM retrieval of streaming media/news), Time-Decayed `pgvector` (for the Hippocampus persistent memory), and Online Reinforcement Learning (RL) which modifies the CEO's affinity profile via Exponential Moving Average (EMA) per session. Limit operations to a "Tiny Teams" constraint of maximum 10 parallel agents, utilizing Sequential Attention for inference optimization, Gemini 3 Deep Research loops, and `scrapling` for resilient scraping. Add Edge Biometrics and Web3 Extortion loops to complete the Zero Trust mandate.

## Proposed Changes

### Configuration & Infrastructure

#### [MODIFY] .gitignore

Add exclusions for `browser_artifacts/`, `external_sdks/`, `node_modules/`, `*.webm`, `*.mp4`, etc.

#### [NEW] docs/marketing/the_shadowtag_manifesto.txt

Add the Steve Jobs typography mode manifesto.

#### [NEW] docs/pitch/Cap_Table.md

Add the strategic capitalization table and deal dynamics.

#### [MODIFY] .vscode/settings.json

Implement System Omega rules, including `antigravity.mcp.registry` additions, custom formatting, and the `shadowtag.constitution`.

#### [MODIFY] infrastructure/main.tf

Create the FedRAMP High Perimeter (VPC-SC), BeyondCorp Zero Trust Access Level, Honeypot routing, WORM Vault Storage Bucket, and the Cloud Run Gen 2 Service `shadowtag-nexus-api`.

#### [NEW] infrastructure/streaming.tf

Create `google_pubsub_topic` and `google_pubsub_subscription` for the Kinetic Stream (replacing Kafka).

#### [MODIFY] infrastructure/serverless.Dockerfile

Create the multi-stage artifact: install `ripgrep-all`, `ast-grep`, `libomp-dev`, `faiss-cpu`, `tesseract-ocr`, `postgresql-client`, `crawl4ai`, `scrapegraphai`, `scrapling`, and all Python dependencies in the final Gunicorn wrapper.

---

### The Active Hippocampus (Database Schema & Scraper)

#### [NEW] schema/streaming_cortex.sql

Implement the Adaptive Memory Matrix. Create the `executive_profiles` table with vector dynamic affinities, the `omniscience_stream` table with generated HNSW embeddings, and the custom `time_decay_search` PL/pgSQL function.

#### [NEW] schema/lean_hippocampus.sql

Create the 669 NIST Federal Catalog store (`nist_federal_catalog`) and the Operational WORM logs (`judge6_memories`).

#### [NEW] scripts/nist_kinetic_scraper.py

Create the Phase 9 scraper. Pulls from csrc.nist.gov, generates embeddings via Gemini, and arms the `nist_federal_catalog` in PostgreSQL.

---

### The High-Velocity Media Cortex (FAISS in RAM)

#### [NEW] src/core/faiss_streaming_cortex.py

Implement `HighVelocityMediaCortex` using `faiss.IndexHNSWFlat`. Handles high-churn streaming data ingest in RAM at sub-millisecond speeds. Includes `ingest_stream_batch` and `query_live_feed` methods.

---

### The Executive Feedback Engine (Online RL)

#### [NEW] src/core/online_inference.py

Implement `RLProfileEngine` (or `StreamingIntelligenceCortex`). Processes RL feedback by updating the CEO's profile vector directly using an Exponential Moving Average (EMA) mathematical shift `(1 - lr) * v_old + (lr * v_click)`.

---

### Kinetic Sensory Organs & Compliance (The Toolbelt)

#### [NEW] src/services/gemini_client.py

Implement the master `google-genai` SDK wrapper. Must support:

1. `generate_content` and `generate_embedding`.
2. **Deep Research Agent API**: Trigger long-running asynchronous context-gathering using `gemini-3-pro-interactions-exp`.
3. **Image Code Execution**: Enable analytical visual scripting on models where detail requires zoom/calculation logic.

#### [NEW] src/services/kinetic_systems.py

Implement `KineticSpecialOps` for Phase 3, 4, 5. Includes:

1. `execute_ciso_voice_extortion` (Twilio TwiML).
2. `mint_cryptographic_evidence` (Polygon/Pinata IPFS).
3. `extract_document` (PyMuPDF/Tesseract OCR).
4. `block_calendar_for_golf` (Google Calendar API).
5. `stealth_scrape` (Utilizes python `scrapling` for Turnstile bypass and ML-driven DOM relocation).

---

### The Tiny Teams Swarm (Intelligence Core)

#### [NEW] src/core/swarm_controller.py

Implement the 10-Agent Swarm Orchestrator. Completely replace the previous 650-unit structure. Synthesize x1xhlol (Cursor/Devin) meta-prompts. Utilize **Sequential Attention** concepts to adaptively pick subsets of context rather than flooding models via one-shot attention.

---

### Cloud Run Deployment & Authorization (The 4-Tier Matrix)

The final Cloud Run deployment will yield an auto-scaling, stateless, zero-latency container available via HTTPS. It will strictly enforce **Four Authentication Methods**:

1. **Google IAM / Service Accounts:** For sovereign internal service-to-service communication.
2. **Cloud IAP (Identity-Aware Proxy):** The front-door firewall for the Web Cockpit.
3. **Interactive OAuth / OIDC:** ADK-level Interactive user identity verification.
4. **ADK `AuthCredential` Integration:** Secure injection of external Tool APIs (Twilio, Web3).

---

### ShadowTag Web Cockpit: "Dark Luxury" Aesthetic

**Methodology:** Pure Gemini 3 Pro Orchestration (No Claude). We are bypassing standard syntax for macro-level intent.

- **Physics Engine:** Implement a custom HTML5 Canvas Neural Network `requestAnimationFrame` loop (Phases: Chaos -> Biology -> Architecture -> Focus).
- **Calibrator Tools:** We will build in-app React `Calibrator` components with sliders for real-time CSS/alignment tweaking, removing the "guess and reload" junior approach.
- **Tech Stack:** Next.js 14, Tailwind CSS, Framer Motion, `next-intl` (English/German).

---

### The Intelligence Engine & The Hunter-Killer (Judge 6)

#### [NEW] src/core/sentinel.py

Implement `JudgeSixSentinel` using `google-cloud-modelarmor` and Anthropic for governance, blocking Mindgard exploits.

#### [NEW] src/core/intelligence_engine.py

Implement `IntelligenceEngine`. Includes the Ghost Ship Supply Chain scanner, Kosmos Base Alternatives generator, and the `execute_recursive_hunter_killer` loop (Claude 3.5 auditing Gemini's `sg` rewrites natively).

---

### The Serverless Nexus (FastAPI Gateway)

#### [MODIFY] src/api/main.py

Implement FastAPI with Pydantic V2. Include `system_health_check` and the `/api/v1/csrmc/evaluate` Extortion Gate. Handle async background tasks for voice escalation and WORM token minting.

#### [NEW] src/api/streaming_router.py

Implement endpoints:

- `/api/internal/stream/ingest`: Pub/Sub micro-batch ingestion.
- `/api/v1/omniscience/radar`: Fetches the FAISS sub-millisecond adaptive radar.
- `/api/v1/omniscience/feedback`: Registers RL feedback to mutate the vector profile.

---

### The Glass Cockpit (Next.js UI)

#### [MODIFY] frontend/app/page.tsx

(Note: Assuming Next.js app is inside `apps/shadowtag-web/app/` based on prior context, path may vary).
Implement `CEOCommandCenter`. Include FAISS Live Kinetic Radar display with 'Investigate' vs 'Dismiss' RL actions. Integrate the Edge Biometrics (MediaPipe simulation) and the premium Extortion Gate pop-up payload.
