# pnkln Platform: Antigravity AI-Scientist Architecture

**Version:** 1.0 (Production Blueprint)
**Target Scale:** $100M+ ARR Scientific Infrastructure
**Paradigm:** Antigravity (VS Code) Multi-Agent Swarm
**Core Models:** `gemini-3.1-*` (Specifically `gemini-3.1-flash-lite-preview` for high-velocity cycles)

---

## 1. Executive Summary
The **pnkln** platform represents a paradigm shift from remote, stateless LLM calls to **stateful, localized, autonomous agent swarms** operating directly within the Antigravity IDE (VS Code).

By uniting the experimental rigor of Kosmos, the multi-agent topology of BioAgents, the execution environment of bio-edison, and the ecosystem of BIOS, **pnkln** establishes a completely autonomous AI-Scientist stack. It handles research, literature review, hypothesis generation, infrastructure hardening, and monetization natively within the user's IDE.

---

## 2. Antigravity Agent Topologies (30+ Swarm)

The platform utilizes Antigravity's concurrent agent manager to spawn 30+ specialized agents across 5 distinct Pods.

### 2.1 Research & Discovery Pod
1. **LiteratureAgent:** Continuously polls and ingests arXiv, PubMed, and Semantic Scholar into the RAG vector store.
2. **HypothesisAgent:** Synthesizes literature to generate falsifiable hypotheses.
3. **ExperimentDesignAgent:** Translates hypotheses into executable Python/JAX pipelines.
4. **DataAnalysisAgent:** Monitors running experiment streams in the background terminal processes.
5. **ValidationAgent:** Subjects experimental outputs to rigorous statistical checks (p-values, null models).
6. **ReportingAgent:** Compiles findings into LaTeX/Markdown research papers.

### 2.2 Infrastructure & Hardening Pod (The "Bourne" Operators)
7. **ThreadMinerAgent:** Recursively extracts un-actioned requirements from project threads.
8. **ArchitectureReconstructor:** Translates raw concepts into Bazel-compatible physical file structures.
9. **KovelEnclaveAgent:** Hardens FastAPI routes to physically prevent data retention (`Cache-Control: no-store`; zero-logging of PII).
10. **BazelBootstrapAgent:** Maintains `BUILD.bazel` target integrity strictly across the monorepo graph.
11. **TelemetryAgent:** Injects OpenTelemetry hooks into all newly generated execution paths.
12. **SecretsAuditorAgent:** Hooks into pre-commit and the Vercel/Cloud Run deployment layer to sniff out token leaks.

### 2.3 Economic Incentive & Monetization Pod
Billed as the $100M+ ARR scaling engine.
13. **CostCircuitAgent:** Hardcodes AI API cost limits dynamically intercepting requests before they hit the litellm proxy.
14. **YieldOptimizationAgent:** Determines if experimental metadata should be routed to a premium data-market API.
15. **ResourceAllocatorAgent:** Dynamically spins up/down GCP Cloud Run / Vertex endpoints based on active agent demand.
16. **BillingEventAgent:** Translates scientific workflow completions into Stripe webhook events.
17. **ArbitrageAgent:** Identifies optimal times to buy reserved GCP/CoreWeave compute based on upcoming hypothesis queue sizes.

### 2.4 Data Integrity & RAG Pod
18. **VectorSyncAgent:** Synchronizes ChromaDB state with the Antigravity filesystem `docs/` artifacts.
19. **GraphMemoryAgent:** Uses `@modelcontextprotocol/server-memory` to maintain L1 semantic graph persistence across IDE restarts.
20. **CitationVerificationAgent:** Halts the ReportingAgent if an ungrounded or hallucinated citation is detected.
21. **OCRDataIngestAgent:** Extracts text from image drops in the UI and feeds the active context window.

### 2.5 Policy & Governance Pod
22. **pnklnJR_PurposeAgent:** Enforces the "Purpose" directives of the system.
23. **DoctrineReasoningAgent:** Enforces structural methodologies.
24. **ArmyRiskManagementAgent:** Acts as the emergency "Brakes" - stopping runaway loops.
25. **BiomeShockCollarAgent:** Automatically rejects branches that fail rigid formatting and linting standards.
26. **CursorKillerAgent:** Performs visual verification of UI changes if applicable via multimodal video context.

*(Agents 27-35 represent auxiliary support units: CI/CD sync, GitOps operators, Slack notification dispatchers, etc.)*

---

## 3. RAG Architecture (Local-First Semantic Store)

**Primary Engine:** ChromaDB integrated directly into the workspace loop.
**Knowledge Graph:** MCP Memory Server (JSONL file path strictly committed).

### Ingestion Flow
1. Text/PDF/Source files dragged into the IDE trigger the **OCRDataIngestAgent**.
2. Files are chunked and summarized via `gemini-3.1-flash-lite-preview`.
3. Embeddings are pushed to the `libs/cortex` local Chroma store.
4. Triplet relationships (Subject -> Predicate -> Object) are written via MCP `create_relations`.

---

## 4. Experiment Execution & Fast Feedback Loop

Experiments are not isolated. They run directly inside Antigravity's integrated terminals using the `run_command` and `send_command_input` toolsets.

1. **Write:** Agent writes experiment scripts to `apps/shadowtag-core/experiments/`.
2. **Build:** Agent uses Bazel: `bazel build //apps/shadowtag-core:run_exp`.
3. **Execute:** Agent runs the background command.
4. **Monitor:** Agent continuously parses `stdout` via `command_status`.
5. **Auto-Heal:** If Python or JAX throws an error, the agent modifies the snippet and re-runs natively.

---

## 5. Deployment & Retention Doctrine

### 5.1 Model Normalization
All agents in the pnkln platform default to `gemini-3.1-flash-lite-preview` for blazing fast throughput (Outcome augmentation +35%). For deep reasoning (Treadstone augmentation), the system falls back to `gemini-3.1-family` or equivalent heavy models.

### 5.2 Zero-Retention (CounselConduit Kovel Enclave)
- Handled at the FastAPI middleware layer (`libs/integrations`).
- Forces `Cache-Control: no-store, no-cache, must-revalidate`.
- Intercepts default logging to strip payload contents.
- Ephemeral memory only. No DB persistence for sensitive legal discovery logic.

### 5.3 5-Step Repo Patch Queue Validation
- Legacy backups (`_PRE_OMEGA_BACKUP_*`) actively scrubbed via bash watchers.
- Rogue MCP generation files (`antigravity_block_3.sh`) zeroed to assert `pnklnJR` policy enforcement.

---
**Status:** Architecture Blueprint Finalized and Staged for Immediate Execution.
