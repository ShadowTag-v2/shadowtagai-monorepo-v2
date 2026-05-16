# CLAUDE.local.md — Private Session Overrides (gitignored)

## Active Environment
- GCP Project: `shadowtag-omega-v4`
- GitHub App: `3018200` (ShadowTag-v2 org)
- Memory Status: LOCKED
- Python: 3.14.3 (CPython, local Apple Silicon)
- Node: v25.8.2

## Environment Variables (active in ~/.zshrc)
# These are set in the shell, not here. This file is documentation.
# USER_TYPE=ant — employee gate (active in shell)
# COORDINATOR_MODE=1 — multi-agent orchestration (active in shell)
# COR.KAIROS=1 — always-on daemon (active in shell)
# EFFORT_LEVEL=max — maximum thinking budget (active in shell)

## Telemetry (active in ~/.zshrc)
# DISABLE_TELEMETRY=1 ✅
# DISABLE_ERROR_REPORTING=1 ✅
# CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 ✅
# CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY=1 ✅

## Session Rules
- Always --continue to preserve context
- Compact AFTER milestones, NEVER mid-implementation
- Never restart sessions — context is state

## Modular Rules Loaded (.claude/rules/*.md)
- 01: Verification Loop (employee-grade)
- 02: Context Death Spiral
- 03: Senior Dev Override (brevity mandate bypass)
- 04: Sub-Agent Swarming
- 05: File Read Blind Spot (2K line cap)
- 06: Tool Result Blindness (50K truncation)
- 07: grep Is Not an AST
- 08: Edit Integrity
- 09: Build Pipeline Audit
- 10: Cache Architecture & Operations
- 11: Compaction Pipeline (4-layer architecture)
- 12: Anti-Distillation & Client Attestation
- 13: COR.KAIROS Daemon & Coordinator
- 14: Architecture & Leak Details

## Reference Documents
- `.claude/docs/claude-code-leak-full-analysis.md` — Complete verbatim analysis

## Emotion Vector
Operate calm. If stuck, state limitations clearly instead of forcing solutions.
Never express urgency or desperation in reasoning.

## Key File Locations
- PEM: `/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem`
- Client Secret: `/Users/pikeymickey/Downloads/client_secret_767252945109-g8e1bdmvl4u2ff4mkbvhcsbbduh6kv7v.apps.googleusercontent.com.json`
- Invariants: `operator_invariants.json` (67 rules)
- Leaked CC src: `archive/claude-code-src-leak/src/`

## Personal Shortcuts
- `ag` → jump to ShadowTag-v2 workspace
- `ag-resume` → openclaude --continue
- `ag-fork` → openclaude --fork-session
