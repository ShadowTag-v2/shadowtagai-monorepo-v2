# Walkthrough - Self-Prompting n-autoresearch/Kosmos/BioAgents & Dual Sidecar

## Summary

The **Self-Prompting Monkey (SPM) Loop** and the **Dual Sidecar Architecture** have been fully implemented. The system now features a rigorous 4-iteration code generation loop backed by real browser automation (Jetski) and governance gating (Judge #6), all running on **Cloud Run** in verified "God Mode".

## Architecture Components

### 1. Jetski Sidecar (The Reality Check)

- **Engine**: `src/jetski/browser_engine.py`
  - Uses **Selenium Wire** for network interception and **Chrome CDP** for rendering checks.
- **Server**: `src/jetski/server.py`
  - FastAPI service exposing `/verify/endpoint` and `/verify/render`.
- **Infrastructure**: `jetski.Dockerfile`
  - Deployable container with Headless Chrome.

### 2. Governance Sidecar (The Brain)

- **SPM Engine**: `src/governance/voting/spm_engine.py`
  - Orchestrates the **4-Iteration Loop**: Research -> Suggest -> Vet -> Iterate.
  - Connects to **Jetski** sidecar for valid research.
  - Connects to **Vertex AI** for GCA intelligence.
- **Memory Bank**: `src/governance/memory/memory_bank.py`
  - Persists learned rules to **Firestore**, preventing regression.
- **MCP Server**: `src/governance/mcp_server.py`
  - Exposes `execute_omega_loop` tool.

### 3. Cloud Run Infrastructure

- **Deployment**: `scripts/deploy_omega_cloudrun.py`
  - Python script for source-based deployment (No Dockerfile needed for Governance service).
- **Configuration**: `cloudrun.yaml`
  - Enforces **300s timeout** (Replacing Rkill) and **512Mi limit**.

## Operational Status

- **Loop**: Built-in (Cor.Self Prompting).
- **Control**: Judge #6 Active.
- **Reality**: Jetski Online.
