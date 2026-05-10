# OBSERVABILITY_PROTOCOL.md

> **Status:** LOCKED — Monitoring, tracing, and audit trail specification.
>
> **Last updated:** 2026-04-27

---

## Purpose

Every agent action must produce a verifiable trace. No silent failures. No assumed success.
This document defines the observability stack that ensures complete visibility into agent
operations, daemon health, and system state.

---

## 1. Beads Audit Trail

### Directory Structure

```
.beads/
├── issues.jsonl              # Append-only structured issue log
├── kairos_heartbeat.json     # Daemon heartbeat state
├── session_pins/             # Active session state markers
└── gca_autolint_daemon.log   # Autolint daemon output
```

### Issue Log Format

Each line in `issues.jsonl` is a self-contained JSON object:

```json
{
  "ts": "2026-04-27T07:00:00Z",
  "type": "lint_fix|mcp_routing_violation|build_failure|deploy_success|auth_refresh|archive_action",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "file": "path/to/affected/file.py",
  "detail": "Human-readable description of what happened",
  "agent": "antigravity|claude|cline",
  "session": "526ea93d-922e-446b-b433-8a0e1428ef06"
}
```

### Rules

- **Append-only** — Never modify or delete existing entries
- **Structured** — Always valid JSON, one object per line
- **Timestamped** — ISO 8601 with timezone
- **Attributable** — Agent identity included

---

## 2. MCP Fleet Vanguard Status

### Pre-Flight Check

At conversation start, verify all 5 MCP servers:

| # | Server | Health Check Method | Expected |
|---|--------|-------------------|----------|
| 1 | StitchMCP | `list_projects` | Project list returned |
| 2 | chrome-devtools-mcp | `list_pages` | Page list returned |
| 3 | firebase-mcp-server | `firebase_get_environment` | Environment config returned |
| 4 | google-developer-knowledge | `search_documents` (test query) | Results returned |
| 5 | sequential-thinking | `sequentialthinking` (test thought) | Thought processed |

### Status Reporting

Report the fleet status table at:
- Conversation start
- After any server failure
- After any self-healing attempt

### Self-Healing Loop

```
IF server DOWN:
    1. Log to .beads/issues.jsonl (severity: HIGH)
    2. Attempt restart (kill + re-init)
    3. Re-check health
    4. IF still DOWN: report to user with exact error
    5. IF UP: report recovery, continue
```

---

## 3. Daemon Fleet Monitoring

### Active Daemons

| Daemon | Script | Schedule | Health Signal |
|--------|--------|----------|--------------|
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly | KI artifact timestamps |
| Loop Steward | `scripts/loop_steward.py` | 5-min cycles | Task file modification time |
| COR.KAIROS | `scripts/kairos_daemon.py` | Background | `.beads/kairos_heartbeat.json` |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Background | Evolution log entries |
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Daily 3-5AM | Last push timestamp |

### Heartbeat Format

```json
{
  "daemon": "kairos",
  "last_beat": "2026-04-27T07:00:00Z",
  "status": "running|idle|error",
  "cycle_count": 42,
  "last_error": null
}
```

### Stale Detection

A daemon is considered stale if:
- No heartbeat update in 2× its expected cycle time
- Last status is "error"
- Process is not found in `ps aux`

---

## 4. Git as Audit Log

### Commit as Trace Entry

Every git commit serves as an immutable audit entry. Format:

```
<type>(<scope>): <description>

Types: feat, fix, chore, docs, refactor, test, ci, perf
```

### Commit Metadata Requirements

| Field | Requirement |
|-------|------------|
| Author | Must be the authenticated user (not generic) |
| Timestamp | Must be accurate (no --date overrides) |
| Message | Must follow Conventional Commits |
| Scope | Must identify the affected package/module |
| Files | Must only include intentionally changed files |

### History Integrity

- **No force-pushes** without STATE B escalation
- **No history rewrites** without explicit human authorization
- **No squash of audit-relevant commits** (hygiene commits may be squashed)

---

## 5. Runtime Observability

### Cloud Run Monitoring

- **Logs:** Cloud Logging → structured JSON
- **Metrics:** Request count, latency, error rate
- **Alerts:** 8 GCP alert policies active
- **WAF:** Cloud Armor with 4 rules

### Firebase Hosting

- **Lighthouse CI:** Budget assertions in CI
- **GA4:** Measurement ID wired into `<Script>` tags
- **Core Web Vitals:** LCP, INP, CLS tracked

### Local Development

- **Console:** `chrome-devtools-mcp` → `list_console_messages`
- **Network:** `chrome-devtools-mcp` → `list_network_requests`
- **Performance:** `chrome-devtools-mcp` → `performance_start_trace`
- **Memory:** `chrome-devtools-mcp` → `take_memory_snapshot`

---

## 6. Nag Protocol as Observability

The nag protocol (5-22 actionable prompts per response) serves a dual purpose:

1. **User guidance** — Explicit next steps
2. **State visibility** — What the agent believes is true

### Forbidden Prompt Fillers

These indicate the agent is padding, not observing:

- `f1 gca` (operator alias, never a suggestion)
- `"Want me to show you?"` (rhetorical stalling)
- `"Should I proceed?"` (YOLO envelope = automatic approval)
- Restating what was just completed
- `"Let me know if you need anything else"` (not actionable)

---

## Cross-References

- [ANTIGRAVITY_CONTROL_PLANE.md](./ANTIGRAVITY_CONTROL_PLANE.md) — Parent control plane spec
- [AGENT_LOOP_HARDENING.md](./AGENT_LOOP_HARDENING.md) — Anti-theater protocol
- `.agents/skills/mcp-fleet-vanguard/SKILL.md` — MCP health enforcement
- `.agents/skills/tacsop5-linting-doctrine/SKILL.md` — Lint observability
- `scripts/gca_autolint_daemon.py` — Daemon reference implementation
