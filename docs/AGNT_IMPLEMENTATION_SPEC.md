# AGNT STATE B Implementation Spec
Version: 1.0.0
Status: LOCKED

## Objective
Formalize the 22-item STATE B plan into a locked architecture document for the Antigravity Monorepo-Uphillsnowball.

## Phase 1: Cognitive Compression & Context Budgeting
1. **Context Compaction Port**: `clear_tool_uses` + `clear_thinking` API stripping. Efficiency gain: ~30%.
2. **Context Budget Discipline**: Threshold-based token pruning to maintain tight reasoning windows.
3. **Loop Steward API**: Implement 5-min continuation intervals for autonomous background operation.
4. **Context Cache Tiering**: Differentiate between hot (active tools), warm (project context), and cold (historic memory).

## Phase 2: Autonomous Tools & Classifiers
5. **XML Classifier Side-Query**: Port Anthropic's XML classification logic to AGNT QueryEngine for semantic routing.
6. **Bash Classifier Telemetry Port**: Bring Claude Code's bash execution telemetry tracking over to AGNT.
7. **TungstenTool Forensics Implementation**: Replicate the `TungstenTool` behavior (`TungstenLiveMonitor` cross-ref in `REPL.tsx` / `AppStateStore.ts`) for long-running tmux tasks (`/hunter`).
8. **Web Extraction Sandbox**: Pure headless execution.

## Phase 3: Telemetry & Observability
9. **tengu_* Telemetry Catalog**: Port and catalog all telemetry events (e.g. `tengu_tool_used`, `tengu_ultraplan_launched`, `tengu_worktree_created`) for internal analytics.
10. **antModels.ts Codename Mapping**: Map Anthropic model codenames to known releases for accurate API routing and limits.
11. **Omni-Linter Telemetry Integration**: Track AST node mutations via unified linter pipeline.
12. **VCR Record/Replay**: Deterministic test reproduction subsystem for high-fidelity regression debugging.

## Phase 4: Security & Validation
13. **Rule 00 Immutable Infrastructure**: Formal checks against destructive commands.
14. **Gitleaks Guardian Protocol**: Zero-trust scan before commits.
15. **IPI Quarantine Pipeline**: Restrict all raw inputs through NotebookLM prior to context loading.
16. **TACSOP 5 Continuous Self-Healing**: Automated `ruff check --fix` post-edit loops.

## Phase 5: Architecture & Infrastructure (Cor.Cor.Kairos)
17. **Cor.30 Security Rules Enforcement**: Vibe-to-live serverless posture locks.
18. **Firebase MCP Deployment Engine**: Strict adherence to headless auth over interactive logins.
19. **GitHub App Short-Lived JWT Pipeline**: No more PATs.
20. **Sovereign Dual Stack Isolation**: Separate testing matrices from production deployment scripts.
21. **Dream Consolidation Engine**: Nightly KI extraction via `scripts/dream_consolidation.py`.
22. **Motor Cortex Skill Hunting**: Omni-Skill Hunter + Google Ingestor auto-acquisition.
