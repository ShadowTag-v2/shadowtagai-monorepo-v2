# Sentinel Ops & Sovereign Ingestion Execution Plan

## Goal

Transition the ShadowTag monorepo from primary scaffolding to **Sentinel Ops**. This involves enslaving the 10 Core MCP Servers to build the execution matrix for Semi-Formal Reasoning (SFR), implementing CodePMCS physical restraints, and integrating the massive Sovereign Knowledge artifacts into the memory matrix.

## Proposed Changes

### MCP Server Matrix Acquisition

- **Action:** Clone the official MCP servers bundle (`external_sdks/mcp_servers`) and the `googleworkspace/cli` bundle.
- **Purpose:** Serve as the "Nervous System" (Actuators) for the Semi-Formal Reasoning (SFR) Brain.
- **Specific Allocations:**
  - `memory`: Stateful persistence for hypothesis caching.
  - `sequential-thinking`: The overarching conductor for the SFR engine.
  - `github` / `linear` / `googleworkspace-cli`: The trigger and notification layer.

### Gate 0 CodePMCS Enforcements

- **Action:** Implement a physical constraint layer via `.git/hooks/pre-commit` called the "Gate 0 Linter".
- **Purpose:** Eliminate UI/UX semantic drift (e.g., hardcoded HEX values, manual pixel margins) before the code even triggers the agentic reasoning layer. If a commit violates the design system, the shock collar fires, rejecting the commit and forcing the agent back to fault localization.

### Sovereign Ingestion Integration

- **Action:** Clone the `ShadowTag-v2-fastapi-services` to `external_sdks/ShadowTag-v2-fastapi-services`.
- **Action:** Integrate the existing `artifacts/sovereign_knowledge_mass.jsonl` (4.5MB) into the L2 Memory Bridge.

## Verification Plan

- Manually stage a file with `#FF0000` to verify the pre-commit hook blocks the commit.
- Confirm clones have finished successfully.

### Addendum: Thread Transfer Phase 6 (Pnkln Autonomous Lab Scaffold)

- **Action**: Scaffolded the complete 250+ file directory tree for the serverless Cloud Run `pnkln` Autonomous Research Lab.
- **Action**: Populated the Python reference implementations for the AI Architect, Swarm execution runtimes, and the Autonomous AI Lab Control Kernel.
- **Action**: Bootstrapped the Antigravity Agent Configuration Control Plane (`.agent/`) specifying guardrails, concurrency, and recursive NAS pipelines.

### Addendum: Serverless Ascension (Cor.Omega/v2.0 & Cor.Uphillsnowball.5)

- **Architecture Shift**: Transitioned from stateful Cloud Workstations to Pure Serverless Cloud Run + GCS FUSE + Memorystore Redis.
- **Role Framework**: The system utilizes a 6-role agent paradigm operating in a Swarm over the VFS.
- **MCP Enforcement**: 10 MCP Servers (7 standard reference + Cloudflare Radar, Cloudflare API, Google Drive) function as the standardized tool substrate.
- **Security & Governance (Judge 6.1)**: Pre-VFS scanning enforcing the 17-layer DOW CRSMC Shield (zero-trust, secret veto bounds check). Addressed Webhook signature verification for inbound event safety (Slack/GitHub).
- **Core Replacements**: Implemented ShadowVFS (Virtual staging), ContextPruner (AST-Grep RAG), ServerlessSearchProvider (Ripgrep), and RelayServer (Redis Pub/Sub Sync to UI).
- **Cinematic Verification**: Added `src/telemetry/cinematic_studio.py` forcing automated multimodal proof (Video + Gemini 2.5 Pro visual critique) before allowing PRs.
