# RUNTIME_HEALTH — v8.3

## Active Daemons
| Daemon | Status | Purpose |
|---|---|---|
| `KAIROS_DAEMON` | PM2 `AG-KAIROS-DAEMON` | Offline AST-Watchdog bypassing NPM |
| `VDI_DAEMON` | `Xvfb :99`, `ffmpeg`, `novnc` port 8081 | Headless display and recording |
| `OMNI_WEBHOOKS` | Listening | `@antigravity` Slack/GitHub webhooks |
| `SINGULARITY_DAEMON` | `ws://127.0.0.1:9090` | Cost-Arbitrage Hypervisor & BCI Intent Predictor |
| `auto-dream` | 24h cycle | KAIROS consolidation (Orient→Gather→Consolidate→Prune) |
| `gitsync` | 5-min interval | `fetch`/`status` background sync |
| `aegaeon` | Idle mode | Cache warmer |
| `push` | Active | Git push daemon |
| `temporal-server` | PID active | Temporal.io worker queue |
| `claude-agents-sync` | Watch-based | `CLAUDE.md`→`AGENTS.md` sync |
| `antigravity.daemon` | 5-min interval | Health monitor |

## Watchdogs

### NotebookLM Health Monitor (Invariant #101)
- Status: **OPERATIONAL** — `notebooklm-py v0.1.1` installed.
- On session start: verify `python3 -c "import notebooklm"` succeeds.
- Before `/wrap-up`: probe Master Brain ID `c493b409-3955-418f-a993-755c38dc8e7f`.
- If probe fails → ALERT: `⚠️ NotebookLM is OFFLINE — re-auth: notebooklm auth login`.
- Log to `.beads/issues.jsonl` severity HIGH.

### OrbStack Health Monitor (Invariant #102)
- On session start: `pgrep -f OrbStack`.
- Before Docker tasks: `PATH=$HOME/.orbstack/bin:$PATH docker info`.
- If fails → ALERT: `⚠️ OrbStack is OFFLINE — restart: open -a OrbStack`.
- PATH fix: always prepend `$HOME/.orbstack/bin` explicitly.

## Companion Files Health
| File | Purpose | Required |
|---|---|---|
| `RISK_REGISTER.md` | Known operational risks | ✅ |
| `DOCTRINE_EXTENDED.md` | Full doctrinal reference | ✅ |
| `BOOT_SEQUENCE.md` | Startup choreography | ✅ |
| `WORKSTATION_LOCAL_OVERRIDES.example.md` | Machine-local paths template | ✅ |
| `BUSINESS_CONTEXT_LOCKED.md` | Pricing/architecture truth | ✅ |

## Launchd Fleet
All 9 daemons exit 0. Security fix applied: removed hardcoded `GEMINI_API_KEY` from `com.antigravity.daemon.plist`.

## Portable Hooks
- `scripts/ai-validate.sh` — mapped and executable.
- `scripts/ai-test-changed.sh` — mapped and executable.
- `scripts/dead-code-audit.sh` — 30-Point Tech Debt Guillotine (pre-commit).
