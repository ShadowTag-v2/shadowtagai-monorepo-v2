# ⛏️ THREAD MINING REPORT: SOVEREIGN OS V8 & SINGULARITY V2.2

## A1. Existing Code Found (Live & Tracked in Workspace)
The following atomic scripts, Daemons, and configuration pieces from the "Cor.GPT Transfer Thread Script" lore have been located and verified as physically present in the `Monorepo-Uphillsnowball` repository:

1. **The Singularity Engine v2.2 & Hybrid Scraping (Located in `.agent/`)**
   - `boot_v2.2.sh` (The Core Bootstrapper)
   - `hybrid_scraper.py` (Firecrawl + Scrapling Triad)
   - `singularity_daemon.py` (BCI & Arbitrage Swarm Daemon)
   - `master_prompt_v2.2_singularity_engine.yaml` (The Unified Master Prompt)
   - `sovereign_indexer.py`, `sovereign_daemon.py`, `sovereign_patcher.py`

2. **The "Great Migration / Google3" Monolithic Roots (Partially Present)**
   - `apps/shadowtag-core/` (Present)
   - `tools/omega-scripts/` (Present)
   - `/.beads/` (Present, 128 bytes - empty or minimal footprint)
   - `third_party/ANE/` (Present)
   - `/.agent/`, `/.gemini/` (Present)
   - `Makefile` and `pyproject.toml` (Present at Root)

3. **Strategic Documentation**
   - `docs/legacy_shadowtag_v2/Strategic_Intelligence/Omega_Loop_Alpha_Omega_V8_Transfer_Manifest.md` (Constructed in current session)
   - PRISM / Pre-commit hooks for Dev Hygiene (`.pre-commit-config.yaml` with black/isort added in current session)

4. **BigQuery Zero-ETL / Splits (Located in `tools/legacy/_root_stash/`)**
   - `bq_autonomous_lake.sql`
   - `data_router.py`
   - `bq_omni_search.py`
   - `bigquery_omniscience.tf`

5. **AST Swarm / Kinetic Triad**
   - `apps/ShadowTag-v2_stack/cosmic-crab-payload/tools/ast_swarm_global.py` (Present)

---

## A2. Missing / Implied Code (Requires implementation or PR generation)
The following components were detailed heavily in the thread but are physically missing or incorrectly mapped in the current monorepo structure:

1. **The "ShadowTag Web / UphillSnowball" Next.js React UI**
   - **Missing:** The entirety of the A2UI React CopilotKit architecture described in the thread (`UphillSnowballCartWidget`, `NightlyBriefingWidget`, `ThreatRadarWidget`, `GlowButton.tsx`, `HeroContent.tsx`, `Navbar.tsx`, `page.tsx`).
   - **Impact:** High. The structural hijacking (The Pickle Protocol targeting unusualmachines.com) and the "Agentic OS" monetized frontend do not exist in the monorepo.
   - **Priority:** CRITICAL. We need the "Dark Luxury" Fiduciary Trap wedge.

2. **The "Great Migration" Missing Libs & Directories**
   - **Missing:** `apps/uphillsnowball/` (Node.js Relay Server)
   - **Missing:** `libs/cortex/`, `libs/telemetry/`, `libs/distribution/`, `libs/integrations/`.
   - **Impact:** Medium. The Python backend logic (`cinematic_studio.py`, `mxl_hotpath.cpp`) has not been cleanly separated into the Google3 / Bazel structure.

3. **The `SequentialAttentionSwarm` and `JudgeSixSentinel`**
   - **Missing:** `src/core/swarm_controller.py` and `src/core/sentinel.py`. The "Tiny Teams" and 6-Gate Fiduciary Extortion Gate logic are not in `src/core/`.
   - **Priority:** HIGH. These define the execution constraints of the Swarm.

4. **GDrive LangExtract Daemon**
   - **Missing:** The exact `scripts/ingest_drive_docs.py` daemon logic mapped to `gemini-3.1-flash-lite-preview`. The repository has local `.beads`, but the autonomous inbound RAG scraper script is missing.

---

## A3. Unaddressed Suggestions / Optionals
1. **BigQuery Implementation Gap:** The massive Zero-ETL embedding pipeline is banked strictly as *Legacy Stash* strings. It has not been applied via Terraform to the `shadowtag-omega-v4` GCP environment.
   - *Decision:* Leave banked until GCP provisioning is explicitly directed.
2. **"Pickle Protocol" against unusualmachines.com:** We possess the instruction prompts to structurally clone the site, but have not instantiated the React app.
   - *Decision:* Implement as PR Batch #1.
3. **Temporal Worker Pipeline:** The user mentioned fixing deployment pipelines for Temporal worker images, but no Temporal orchestration (`workflows.py`, `activities.py`) was actually provided or stored in the artifacts.
   - *Decision:* Acknowledge constraint. Defer until worker logic is provided.

---

## A4. Conflicts & Unknowns
1. **Bazel vs. Makefile Conflict:** The "Great Migration" refers strictly to `BUILD.bazel` mappings and a Google3 layout. However, the exact same thread also champions a `Makefile` bootstrap for environment consistency.
   - *Assumption:* The repo is currently transitioning. We will enforce the `Makefile` and `pre-commit` loop as the *local* edge dev experience, while `Bazel` structures the production multi-language builds.
2. **Missing `apps/uphillsnowball`:** We have `apps/ShadowTag-v2-fastapi-services` and `apps/ShadowTag-v2_stack` instead of the stated `apps/uphillsnowball/`.
   - *Assumption:* The namespace evolved. We will construct the missing A2UI UI assets inside a new `apps/shadowtag-web/` directory (which was the prefix used in the code strings).
