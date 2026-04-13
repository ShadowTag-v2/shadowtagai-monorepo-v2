# DOCTRINE_EXTENDED — v8.2c

## I. Barney-Style UX
All ShadowTagAI products must be "Barney style" — a 5th grader can run them. Simple GUI for non-digital-native Boomer Fortune-500 CEOs and their spouses. Race-car complexity hidden entirely.

## II. Platform Separation Doctrine
- **Swiper**: EXCLUSIVELY the Craigslist Challenger.
- **Adaptive Shoppable Video**: Amazon Challenger.
- **Headfade**: Turing Test YouTube Challenger.
- STRICTLY FORBIDDEN from merging these discrete business logic pipelines.

## III. ROC Drill (Doctrinal Rehearsal)
"Amateurs discuss strategy. Professionals rehearse execution."
Back-brief → Rock Drill → PCC/PCI → Line of Departure.

## IV. MCTS Discovery Loops
For NP-Hard logic, generate 3–5 architectures. Simulate, prune dead ends, output optimal path. Q*/o1 Monte Carlo Tree Search.

## V. Anti-Vibe Code Doctrine (10 Prohibitions)
1. No hardcoded config — use env vars or `libs/core/config`.
2. No 500+ LOC monoliths — refactor to modular folder hierarchies.
3. No raw `fetch()` — use shared HTTP utility from `libs/core/http`.
4. No `console.log` in `apps/` — use structured logger.
5. No copy-pasted logic — extract to `libs/`.
6. No DB schema changes without migration files.
7. No undocumented dependencies.
8. No biz logic in route handlers — extract to service layer.
9. Deployment MUST have runbook.
10. Feature flags via config, not inline if-statements.

## VI. Shared Component Library Mandate
`libs/ui/` is the CANONICAL shared frontend library. 30+ button variants consolidated to 5 canonical: `primary`, `secondary`, `ghost`, `outline`, `icon`.

## VII. AG-UI Protocol Compliance
The Agent-User Interaction Protocol (AG-UI) is the canonical frontend-backend communication layer for KovelAI. Event types: Lifecycle, Text, ToolCall, State, Activity, Reasoning. Frontend uses CopilotKit + `useCoAgent` hook.

## VIII. Hooks Doctrine
Hooks are lifecycle interceptors configured in `.gemini/settings.json`. 11 events. Golden Rules: `stdout`=pure JSON only, `stderr`=debug, exit 0=allow, non-zero=deny. AfterTool hooks compress verbose JSON to flat CSV (70% context token savings).

## IX. Grounding Ladder
1. Developer Knowledge API
2. LanceDB (sovereign, $0.00)
3. Verified GitHub
4. Web Search
- Golden Rule: No decision without a verifiable known resource.
- Refresh volatile tech every 1 MONTH.

## X. Governed Recovery Defaults

> **CAUTION**: These operations are powerful and potentially destructive. They are governed, not raw slogans.

### `git reset --hard latest-stable`
- **When**: ONLY after an execution path fails entirely AND TDD branch-reality fix fails.
- **Gate**: Require `git stash` of any uncommitted work BEFORE reset.
- **Log**: Write reset event to `.beads/issues.jsonl` with reason and SHA.
- **Never**: Run without verifying `latest-stable` tag exists via `git tag -l`.

### Force-Push Recovery
- **When**: ONLY via the Squash-Push Protocol (Invariant #103) for massive repo egress.
- **Gate**: Must use `--force-with-lease` FIRST. Only fall back to `--force` on "stale info" rejection.
- **Log**: Write push event to `.beads/issues.jsonl`.
- **Never**: Force-push to `main` without tree SHA parity verification.

### Broad YOLO Execution
- **When**: STATE A (Pure YOLO) — repetitive UI, standard logic, known patterns.
- **Gate**: Destructive tools (`rm -rf`, `sudo`) are physically excluded from the MCP schema. YOLO is 100% safe for the allowed subset.
- **Escalation**: STATE B (Clutch) MUST trigger for: undocumented systems, complex flows, schema work, auth/payment, architecture shifts.
- **Never**: Execute YOLO on database migrations, payment logic, or auth changes.

## XI. Claude Code Source Leak Intelligence
- **AutoDream Pattern**: Background memory consolidation fires as forked subagent. Gate order: Time → Sessions → Lock.
- **Memory Type Taxonomy**: 4 types — user, feedback, project, reference. Code patterns and git history are DERIVABLE and must NOT be saved as memories.
- **Compact Service Architecture**: Multi-tier compaction — apiMicrocompact, microCompact, autoCompact, sessionMemoryCompact.
- **Forked Subagent Pattern**: `runForkedAgent()` creates cache-safe params.
- **Coordinator Mode**: Multi-agent orchestration. Workers isolated with tool subsets.

## XII. Model Cost Tiers (Intelligence Routing)
| Model | Input | Output | Use |
|---|---|---|---|
| Haiku 4.5 | $1/Mtok | $5/Mtok | Consolidation/Dream |
| gemini-3.1-flash-lite-preview-thinking | — | — | External runtime (CANONICAL) |
| Sonnet | $3/Mtok | $15/Mtok | Standard reasoning |
| Opus 4.6 | $30/Mtok | $150/Mtok | Q* MCTS heavy lifting |
