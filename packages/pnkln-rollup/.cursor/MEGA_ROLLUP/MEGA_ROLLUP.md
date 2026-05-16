## pnkln Cognitive Stack v5 — MEGA ROLL-UP (Cursor-Ready)

Purpose: pnklnJR. Reasons: Doctrine. Brakes: Army Risk Management. Operate in strict/Bourne posture with legal cognitive augmentation: SOPs, automation, static analysis, pair-programming, code review recipes, Pre-mortem, 5-Whys, and mandatory postmortems.

### Components
- **BDH (Behavior-Driven Heuristics)**: Decision scaffolding and guardrails; enforce pre-mortem and 5-Whys for major changes.
- **RoT (Reasoning-over-Thought)**: Persisted thought-graphs (optional pgvector) for traceability and reuse.
- **MoE-CL (Mixture-of-Experts, Continual Learning)**: Route ensembling per-token or per-span with confidence arbitration.
- **CoDA/DLM (Co-Deterministic Agents / Distributed Learning Module)**: Structured multi-agent collaboration with arbitration and rollbacks.
- **Qwen3-VL + Reranker**: Vision-language with reranking for retrieval and code search boosting.
- **Serverless Ops**: Optional Lambda/API Gateway microservice starter (Node), plus CI health checks.
- **Cursor Task Flow**: Task definitions wired via `.cursor/tasks/index.json`.

### Operating Posture
- **Strict mode** default; peg baseline at 160 IQ. Always voice objections; document risks (Army RM) and rollbacks.
- **Two green CI runs before merge**; target 98% coverage when test suites exist.
- **Healthcheck** ensures GitHub visibility. If not visible, fail loud and emit `healthcheck.json` with guidance.

### Task Wiring (Cursor)
- `agent:use:grok-fast`: Switch to Grok Fast route for speed-critical flows.
- `agent:bulk-sweep`: Batch-edit with retries and tests.
- `agent:validate`: Run linters/tests.
- `slurm_github:handshake`: Verify GitHub visibility; writes `healthcheck.json`.

### Ensembling (RoE toggle)
- See `src/inference/roe_toggle.ts` for a lightweight, type-safe pseudo-implementation of per-token route ensembling.

### Rollback & Controls (Army RM)
- Hazards identified per change; controls applied; instant rollback plan documented in PR body.

### Usage
1. Commit and push. Check Actions for `ci` and `bourne-healthcheck`.
2. In Cursor, open this file; execute tasks from `.cursor/tasks/index.json` as needed.
3. If healthcheck fails (GitHub not visible), fix PAT/SSO, re-run.

### Notes
- This roll-up is source-controlled. Prefer local facts and CI results over speculation.

