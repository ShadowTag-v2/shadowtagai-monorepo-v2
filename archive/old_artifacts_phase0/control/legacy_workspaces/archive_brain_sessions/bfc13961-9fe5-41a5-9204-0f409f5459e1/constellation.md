# The Omega Constellation: Connecting Biz & Code

This document maps the **ShadowTag Business Plan** (Strategy) directly to the **ShadowTag v2 Codebase** (Execution). This is the "God Mode" view of the system.

## 1. Sovereign Thesis (The Core)
*   **Business Goal**: Data Sovereignty, Local-First AI, "Wet Fleece/Dry Ground".
*   **Code Modules**:
    *   `src/pnkln/judge_six.py`: The Risk Engine (Validation Logic).
    *   `src/antigravity/memory_client.py`: The Sovereign Memory (Vector Store).
    *   `schema/memory.py`: The Data Structure of thoughts.

## 2. 1B MAU Model (Growth)
*   **Business Goal**: Viral loops, massive scale, consumer adoption.
*   **Code Modules**:
    *   `src/routes/growth_routes.py`: API endpoints for referral/viral features.
    *   `src/libs/ShadowTag-v2/agents/beads_agent.py`: The consumer-facing agent ("The Body").
    *   `external_memory/drive_ingest/formatted_docs`: The "Phase Docs" driving the growth strategy.

## 3. Wealth Strategy (Monetization)
*   **Business Goal**: AI-driven wealth accumulation.
*   **Code Modules**:
    *   `src/routes/swarms.py`: Managing the wealth-generating agent swarms.
    *   `legacy_ingest/ehanc69_fastapi_src/wealth/model.py`: The legacy financial models (imported).

## 4. Operational Infrastructure (The Machine)
*   **Business Goal**: 99.999% Uptime, Global Scale.
*   **Code Modules**:
    *   `bin/n-autoresearch/Kosmos/BioAgentss-server`: The Swarm Server (Cloud Run).
    *   `bin/antigravity-agent`: The Orchestrator.
    *   `.vscode/extensions.json`: Developer Environment Enforcement (Spell Check, etc.).
    *   `external_memory/local_ingest/aider_ollama`: Local AI Dev tools.

## 5. Deployment & Reliability
*   **Business Goal**: Constant "Ignition" (Always On).
*   **Status**:
    *   **Cloud Run**: `antigravity-agent` (Currently Recovering).
    *   **Ingestion**: `Google Drive` (Tunneled: `founder@shadowtagai.com`).
    *   **Governance**: `Code Spell Checker` (Enforced via Git Hooks).
