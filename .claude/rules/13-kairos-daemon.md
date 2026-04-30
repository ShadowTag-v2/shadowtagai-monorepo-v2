# Rule 13: KAIROS — The Unreleased Autonomous Agent Mode

Throughout the codebase, there are references to a feature-gated mode called KAIROS. Based on the code paths in main.tsx, it's an unreleased autonomous agent mode that includes:

- A /dream skill for "nightly memory distillation" (Auto-Dream)
- Daily append-only logs
- GitHub webhook subscriptions
- Background daemon workers
- Cron-scheduled refresh every 5 minutes
- UDS (Unix Domain Socket) inbox for inter-agent communication

This is the biggest product roadmap reveal from the leak.

## Environment Variables (set in ~/.zshrc)
```bash
export CLAUDE_CODE_KAIROS="1"
export KAIROS="1"
export CLAUDE_AUTO_BACKGROUND_TASKS="1"
export KAIROS_GITHUB_WEBHOOKS="1"
export KAIROS_BRIEF_MODE="1"
```

These are all feature-gated server-side, so setting them doesn't guarantee activation — but it opts you in when the gates open.

## CronTask Scheduler (Source-Verified: cronTasks.ts — 459 lines)
Tasks come in two flavors:
- **One-shot** (recurring: false) — fire once, then auto-delete
- **Recurring** (recurring: true) — fire on schedule, reschedule from now,
  persist until deleted or auto-expire after `recurringMaxAgeMs`

### CronTask Shape (Source: cronTasks.ts:30-70)
```typescript
CronTask = {
  id: string,                // 8-hex-char UUID slice
  cron: string,              // 5-field cron (local time)
  prompt: string,            // Prompt to enqueue when fired
  createdAt: number,         // Epoch ms
  lastFiredAt?: number,      // Written back by scheduler
  recurring?: boolean,       // Reschedule vs one-shot
  permanent?: boolean,       // Exempt from auto-expiry (system tasks only)
  durable?: boolean,         // Runtime-only: false = session-scoped (never on disk)
  agentId?: string           // Runtime-only: routes to specific teammate queue
}
```

### Default Jitter Config (Source: cronTasks.ts:348-355)
```typescript
DEFAULT_CRON_JITTER_CONFIG = {
  recurringFrac: 0.1,         // Forward delay as fraction of interval
  recurringCapMs: 900_000,    // 15min upper bound on delay
  oneShotMaxMs: 90_000,       // 90s backward lead for one-shots
  oneShotFloorMs: 0,          // Minimum early-fire guarantee
  oneShotMinuteMod: 30,       // Jitter :00 and :30 marks
  recurringMaxAgeMs: 604_800_000  // 7-day auto-expiry
}
```

### Operational Details
- Tasks stored in `<project>/.claude/scheduled_tasks.json`
- `watchScheduledTasks()` acquires **PID-based per-directory lock** (no double-firing)
- Session-scoped tasks (`durable: false`) live in process memory only, die with process
- `permanent` tasks (dream, catch-up, morning-checkin) are exempt from auto-expiry
- Jitter prevents thundering-herd: hourly tasks spread across [:00, :06), per-minute ~seconds
- Missed tasks detected on startup via `findMissedTasks()` and surfaced to user

**Map to Antigravity:** Use Temporal.io workflows as orchestration layer, but inherit
CronJitterConfig tuning knobs. For macOS-local use, launchd WatchPaths provides
zero-overhead filesystem monitoring (see `.claude/launchd/` for installed plist).


## Multi-Agent Coordinator
coordinatorMode.ts manages worker agents through system prompt instructions, not code. Key directives:
- "Do not rubber-stamp weak work"
- "You must understand findings before directing follow-up work"
- "Never hand off understanding to another worker"

The orchestration algorithm is a prompt, not an algorithm. The coordinator evaluates worker output quality before accepting it.

## Environment Variables
```bash
export CLAUDE_CODE_COORDINATOR_MODE="1"
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS="1"
```

## The Buddy Easter Egg
buddy/companion.ts implements a Tamagotchi-style companion system. Every user gets a deterministic creature (18 species, rarity tiers from common to legendary, 1% shiny chance, RPG stats like DEBUGGING and SNARK) generated from user ID via Mulberry32 PRNG. Species names encoded with String.fromCharCode() to dodge grep.
