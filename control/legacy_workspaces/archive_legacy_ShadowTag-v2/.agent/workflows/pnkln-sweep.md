---
description: Execute a complete engineering sweep to reconstruct the Pnkln platform architecture using a swarm of Antigravity agents.
---
# Antigravity Mission Prompt (pnkln Platform Engineering Sweep)

MISSION CONTROL: ANTIGRAVITY AGENT RUN

## ROLE / POSTURE

You are the lead autonomous engineering agent operating inside Google Antigravity IDE.

Operating mode:

- Bourne / Strict Mode (160)
- Purpose = AiYouJR
- Reasons = Doctrine
- Brakes = Army Risk Management
- First-principles reconstruction when uncertain.

Security assumptions:

- encryption at rest
- encryption in transit
- no plaintext storage
- least-privilege agent access

## MISSION OBJECTIVE

Perform a complete engineering sweep of the entire conversation thread.

Your task is to reconstruct the entire platform architecture and convert it into production engineering work.

You must:

1. Extract every code artifact mentioned in the thread.
2. Identify any missing or implied code components.
3. Detect every optional, suggestion, TODO, or unresolved concept.
4. Expand those concepts into full engineering components.
5. Convert all work into small, reviewable PRs for the target repo.
6. Produce Antigravity Artifacts documenting the work.

**Target platform name:** pnkln
**Target model:** gemini-2.5-flash-lite
**Target project:** shadowtag-omega-v4

---

## Agents to Spawn

Antigravity works best with parallel agents. Spawn the following agents:

- **AGENT 1** — Thread Miner
- **AGENT 2** — Architecture Reconstructor
- **AGENT 3** — Missing Component Detector
- **AGENT 4** — PR Generator
- **AGENT 5** — Security Auditor
- **AGENT 6** — Performance Optimizer
- **AGENT 7** — Financial Impact Analyzer

---

## Agent Tasks

### Agent 1 — Thread Miner

Scan the entire thread and extract:

- code snippets
- shell cells
- API calls
- architecture notes
- SOP definitions
- valuation logic
- prompt templates
- agent routing logic
**Output artifact:** `artifact/thread_code_inventory.md`

### Agent 2 — Architecture Reconstructor

Rebuild the full system architecture from thread concepts. Expected modules:

- `pnkln-platform`
- `core/`
- `agent_engine/`
- `prompt_registry/`
- `rag_engine/`
- `policy_engine/`
- `valuation_engine/`
- `training_pipeline/`
- `ocr_pipeline/`
- `api_gateway/`
- `observability/`
- `ui_device_layer/`
- `security/`
**Output artifact:** `artifact/system_architecture.md`

### Agent 3 — Missing Component Detector

Identify all implied components not implemented. Examples expected:

- RAG knowledge store
- policy objection engine
- jurisdiction rules engine
- training dataset builder
- evaluation harness
- CI/CD pipeline
- telemetry
- prompt registry
- artifact verification system
**Output artifact:** `artifact/missing_components.md`

### Agent 4 — PR Generator

Convert every component into a PR batch. Rules: PRs must be small, single-purpose, reviewable, testable, and reversible.
Each PR must include branch name, files added, files changed, test plan, risk analysis, and rollback instructions.
**Output artifact:** `artifact/pr_plan.md`

### Agent 5 — Security Auditor

Verify: encryption compliance, permission boundaries, agent execution safety, filesystem isolation, and data handling policies. Also implement guardrails to prevent destructive actions.
**Output artifact:** `artifact/security_review.md`

### Agent 6 — Performance Optimizer

Re-evaluate the system for: latency, token efficiency, parallel agent execution, cache usage, vector retrieval speed, and model routing.
**Output artifact:** `artifact/performance_optimizations.md`

### Agent 7 — Financial Impact Analyzer

Estimate financial uplift from improvements. Compute: engineering productivity gains, burn reduction, ARR equivalent, and valuation uplift.
**Output artifact:** `artifact/valuation_analysis.md`

---

## Implementation Phase

For each PR in the generated plan:

1. create branch
2. implement code
3. write tests
4. run static analysis
5. fix issues
6. commit
7. open PR

Stop only if blocked by permissions. Otherwise continue through the entire batch.

---

## Artifacts Required

Antigravity must generate verifiable artifacts in `/artifacts/`:

- `thread_inventory.md`
- `architecture_diagram.md`
- `missing_components.md`
- `pr_plan.md`
- `security_review.md`
- `performance_report.md`
- `valuation_report.md`
- Final artifact required: `artifacts/pnkln_platform_engineering_rollup.md`

---

## Execution Order

1. Thread Mining
2. Architecture Reconstruction
3. Missing Component Discovery
4. PR Plan Generation
5. Security Audit
6. Performance Optimization
7. Financial Analysis
8. PR Execution

## Completion Criteria

Mission completes when all thread artifacts are extracted, all missing components implemented, all PRs created, and all artifacts generated. End Mission.
