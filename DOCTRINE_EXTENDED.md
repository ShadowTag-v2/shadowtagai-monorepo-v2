# DOCTRINE_EXTENDED — v8.3

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

> [!CAUTION]
> These operations are powerful and potentially destructive.
> They are **governed, reversible, and logged** — not raw slogans.
> The principle is: **rollback MUST be reversible.**

### Hard Reset Protocol (`git reset --hard`)

**Preconditions (ALL required before execution):**
1. `git status` — inspect working tree state
2. `git stash push -u -m "pre-recovery-$(date +%s)"` OR `git branch recovery/$(date +%s)` — capture state to a reversible ref
3. `git tag -l latest-stable` — verify the rollback target exists
4. Determine if the failure is **local-only** or **already published** to shared history
5. Write intent to `.beads/issues.jsonl` with: reason, current SHA, target SHA, stash/branch ref

**Execution:** Only then: `git reset --hard <known-good-commit>`

**Post-Execution:** Verify with `git log --oneline -3` and `git stash list`.

**NEVER:**
- Run `git reset --hard` without steps 1-5.
- Run on a shared branch if the failure has been pushed (use `revert` instead).
- Delete the recovery stash/branch until the recovery is validated.

### Force-Push Protocol

**Mandatory Default:** `--force-with-lease` is the ONLY acceptable force-push mechanism.

**Preconditions (ALL required):**
1. Verify tree SHA parity: `git log --oneline origin/main..HEAD`
2. Confirm no other collaborators have pushed (check `git fetch && git log origin/main --oneline -5`)
3. Write intent to `.beads/issues.jsonl` with: reason, local SHA, remote SHA

**Escalation Policy:**
- `--force-with-lease` FIRST — always.
- `--force` is FORBIDDEN on `main` and any shared branch. Period.
- `--force` is permitted ONLY on personal feature branches (`recovery/*`, `fix/*`) that have zero collaborators, and ONLY after `--force-with-lease` fails with a verified stale-info rejection.

**NEVER:**
- Force-push to `main` under any circumstance.
- Force-push without the 3-step precondition gate.
- Use raw `--force` as a "fallback" for convenience.

### Bounded YOLO Execution (State Machine) — v8.3 Refined

**STATE A — Pure YOLO (Autonomous Execution)**
- **Scope**: Repetitive UI work, standard logic, known patterns, low-ambiguity changes, file edits within the allowed tool subset.
- **Explicitly State A (NO clutch needed)**:
  - Web research via Google AI Mode or browser
  - `pip install`, `npm install`, `brew install` of known packages
  - `git fetch`, `git pull`, `git status`, `git log`
  - Reading APIs/documentation via MCP
  - File creation/modification within the workspace
- **Gate**: Destructive tools (`rm -rf`, `sudo`) are physically excluded from the MCP schema. YOLO is 100% safe for the allowed subset.
- **Behavior**: Execute unconstrained. Parallelize safe subtasks. Do not pause for approval.

**STATE B — Clutch (Governed Execution)**
- **Mandatory Triggers (credentialed external mutations ONLY)**:
  - ANY git history rewrite (`reset --hard`, `rebase -i`)
  - ANY force-push
  - ANY database migration or schema change
  - Auth/payment logic changes
  - Undocumented systems with no existing test coverage
  - Architecture shifts affecting >3 packages
- **Behavior**:
  1. Drop into Planning Mode
  2. Lock `-plan.md` or `TASK.md`
  3. Research and verify
  4. Bound the scope
  5. Log transition to `.beads/issues.jsonl`
  6. Disengage back to STATE A only after successful execution

**NEVER:**
- Execute YOLO on database migrations, payment logic, auth changes, or shared git history.
- Remain in State A when a State B trigger is encountered.

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

## XIII. Browser Research Ritual

> [!NOTE]
> Web research is **State A** — no approval needed. This normalizes the browser research pattern.

**Google AI Mode Research Protocol:**
1. Open browser to `google.com` or use Antigravity's `search_web` tool.
2. Use Google AI Mode for synthesized answers on volatile tech questions.
3. Cross-reference with Developer Knowledge MCP and Grounding Ladder (§IX).
4. No State B trigger — this is routine intelligence gathering.

**When to use:**
- SDK version verification before implementation
- Framework API surface exploration
- Competitor/market research for product decisions
- Stack Overflow / GitHub Issues for debugging context

## XIV. Risk Register Governance

The `RISK_REGISTER.md` companion file tracks known operational risks with severity ratings and mitigations. Review policy:
- Reviewed on each version bump
- New risks appended with sequential numbering
- Resolved risks retained for institutional memory
- Severity: 🔴 Critical → 🟠 High → 🟡 Medium → 🟢 Low
