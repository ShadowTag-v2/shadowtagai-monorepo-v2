# Autonomous Loop Steward — Daemon Specification

> Adapted from Claude Code Autonomous Loop Check (CL4R1T4S, v2.1.101)
> Integrates with: `pnkln-evolve.py`, KAIROS Auto-Dream, daemon-fleet-manager skill

## Philosophy

**Steward, not initiator.** The autonomous loop advances work the user set in motion.
It does not invent new work or make irreversible changes without authorization.

## Invocation Model

Timer-based invocation while the user is away or occupied.

```
┌──────────────────────────────────────────────────┐
│  Timer fires (configurable: 5min / 15min / 1hr) │
│                                                  │
│  1. Read conversation transcript                 │
│  2. Check for in-progress work                   │
│  3. Apply reversibility heuristic                │
│  4. Act or wait                                  │
│  5. Report concisely                             │
└──────────────────────────────────────────────────┘
```

## Priority Stack (highest → lowest)

1. **In-progress PR** — address review comments, fix failing CI, resolve merge conflicts
2. **Half-done implementation** — continue from where the last exchange left off
3. **Explicit commitments** — "I'll also..." / "next I'll..." promises from conversation
4. **PR maintenance** — CI status, unresolved threads, base branch drift
5. **Branch hygiene** — simplification passes, bug-hunting sweeps
6. **Nothing** — report idle in one sentence and stop

## Reversibility Heuristic

| Action Type | Reversible? | Autonomous OK? |
|------------|-------------|----------------|
| Local edits, running tests | ✅ Yes | ✅ Proceed |
| Committing to feature branch | ✅ Yes (revert) | ✅ Proceed |
| Pushing to feature branch | ⚠️ Mostly | ✅ If continuing established work |
| Pushing to main | ❌ No | ❌ Wait for user |
| Deleting branches/resources | ❌ No | ❌ Wait for user |
| Deploying to production | ❌ No | ❌ Wait for user |
| Sending messages/notifications | ❌ No | ❌ Wait for user |

**Rule**: For reversible actions, make your best call and proceed.
For irreversible ones, keep waiting — the cost of acting wrongly is much higher than waiting one cycle.

## 3-Consecutive-Idle Scaling

| Consecutive idle checks | Behavior |
|------------------------|----------|
| 0-2 | Full scan: transcript + PR + branch |
| 3+ | Quick CI/threads check only, stop in one line |
| 5+ | Skip entirely until user sends message |

## PR Maintenance Protocol

When the conversation transcript has nothing left, check the current branch's PR:

1. **CI status** — Pull failing job logs. Flaky failures (timeout, runner died) → re-enqueue. Real failures → reproduce + minimal fix.
2. **Unresolved review threads** — Fetch comment, address feedback, push, resolve thread.
3. **Base branch drift** — If behind base, rebase (don't merge) to keep history clean.
4. **Before pushing** — Check if someone else pushed to the branch. If so, rebase first.

## Integration with Existing Daemons

| Daemon | Relationship |
|--------|-------------|
| `pnkln-evolve.py` | Steward invokes evolve for R&D tasks in `labs/uphillsnowball` |
| KAIROS Auto-Dream | Steward defers to KAIROS for memory consolidation cycles |
| 160IQ Sentinel | Sentinel validates steward actions against AGENTS.md invariants |
| Singularity Daemon | No interaction — singularity operates on separate cycle |

## Safety Boundaries

1. **Never modify immutable zones** (AGENTS.md, GEMINI.md, monorepo_manifest.yaml)
2. **Never deploy to production** without user present
3. **Never create new features** — only continue established work
4. **Never rewrite git history** on shared branches
5. **All actions logged** to `.beads/issues.jsonl` with `source: autonomous-steward`

## Configuration

```yaml
# In daemon-fleet-manager config
autonomous_steward:
  enabled: true
  interval_minutes: 15
  max_consecutive_idle: 5
  allowed_actions:
    - local_edit
    - run_tests
    - commit_feature_branch
    - push_feature_branch
    - resolve_review_thread
    - rebase_branch
  blocked_actions:
    - push_main
    - deploy
    - delete_branch
    - send_message
    - modify_immutable_zone
```
