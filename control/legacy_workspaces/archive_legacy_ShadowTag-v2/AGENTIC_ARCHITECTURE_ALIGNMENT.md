# Agentic Architecture Alignment (Google Cloud Standards)

**Date**: 2026-02-03
**Status**: DRAFT
**Reference**: [Google Cloud Agentic Architecture](https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system)

## 1. Design Pattern: Hierarchical Orchestrator with Governance

ShadowTag-v2 aligns with the **"Orchestrator-Workers"** pattern, enhanced with a unique **"Governance Sidecar"**.

| Component        | Google Cloud Standard         | ShadowTag Implementation                             | Status                           |
| :--------------- | :---------------------------- | :--------------------------------------------------- | :------------------------------- |
| **Orchestrator** | **Agent Runtime** (Cloud Run) | **Trinity** (`trinity_main.py` on Cloud Run)         | ✅ Aligned                       |
| **Workers**      | **Tools / MCP**               | **Gideon OS Engines** (`scholar`, `indexer` via MCP) | ⚠️ Partial (Migrate to Toolbox?) |
| **Governance**   | **Guardrails**                | **Judge6** (`judge6_enforcement.py`)                 | ✅ Exceeds Standard              |
| **Memory**       | **Vector Store / SQL**        | **Filesystem** (`task.md`, `json` manifests)         | ⚠️ Needs Upgrade (GenAI Toolbox) |

## 2. Integration Opportunities

### A. GenAI Toolbox + Firestore (Unified Memory)

- **Directive**: "Migrate both Workers and Memory to Toolbox."
- **Architecture**:
  - **Serving Layer**: **GenAI Toolbox** (MCP Server).
  - **Storage Layer**: **Firestore** (Native Mode with Pipeline Operations).
- **Benefit**:
  - **Governance**: Toolbox handles auth/observability (Datadog ADK).
  - **Power**: Firestore Pipelines handle complex vector/aggregation queries.
  - **Standardization**: Agents speak "MCP", Toolbox speaks "Firestore".
- **Action**: Deploy GenAI Toolbox configured with custom connectors for Firestore Pipelines.

### B. Dataform Strict Act-As Mode

- **Current**: `CrimeModule` (Judge6) runs raw BigQuery queries.
- **Target**: Wrap compliance queries in **Dataform** pipelines with **Strict Act-As Mode**.
- **Benefit**: Ensures audit logs show exactly _which_ service account (e.g., `judge6-auditor@`) accessed sensitive data, preventing "God Mode" leaks.
- **Action**: Create a `governance/dataform` directory for Judge6 queries.

### C. Pickle Rick (Persona Switching)

- **Concept**: Explicit modes for "Execute" vs "Plan".
- **Alignment**: We already use `task_boundary` (PLANNING vs EXECUTION).
- **Refinement**: Enforce stricter tool sets per mode.
  - _Planning_: Read-only tools + `notify_user`.
  - _Execution_: Write tools.
  - _Judge_: Verification tools only.

## 3. Immediate Action Plan

1.  **Adopt Pattern**: Formally define `Trinity` as the "ReAct Orchestrator".
2.  **Upgrade Memory**: Plan the `GenAI Toolbox` integration for the "Sovereign Library".

## 4. Edge Sovereignty (Distributed Cloud Edge)

- **Concept**: Run ShadowTag-v2 on **Google Distributed Cloud (GDC) Edge** for maximum sovereignty (Air-Gap capable).
- **Target**: Deploy `Trinity` and `Scholar` to GDC Edge clusters.
- **Benefit**:
  - **Data Residency**: Data never leaves the physical appliance.
  - **Low Latency**: Local manufacturing/defense AI inference.
  - **Compliance**: Meets stricter-than-cloud sovereignty requirements (Judge 6 "Wet Fleece" Protocol).
- **Action**: Designate `us-central1` workstation as the "Cloud Control Plane" and future GDC Edge nodes as "Sovereign Outposts".

## 5. Observability (Datadog ADK)

- **Concept**: Use **Datadog LLM Observability** to trace the "Thought Process" of the Trinity Agent.
- **Standard**: Adopt the **Agent Development Kit (ADK)** automatic instrumentation.
- **Benefit**:
  - **Traceability**: See every tool call, reasoning step, and failure in real-time.
  - **Cost/Latency**: Monitor token usage and latency per Agent Step.
  - **Safety**: "Judge6" evaluations can be logged as Datadog Quality Signals.
- **Action**: Instrument `trinity_main.py` with `ddtrace` and the ADK SDK.
