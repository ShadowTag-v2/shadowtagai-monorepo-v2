---
name: High-Risk Command Scanner
description: Heuristic scanner that detects and blocks dangerous command patterns before execution. Enforces the approval_envelope by catching patterns excluded from YOLO mode.
---

<!-- GUARDRAIL: DEFENSIVE-SECURITY skill. Heuristic scanner that detects dangerous command
     patterns (rm, sudo, force-push) before execution. Read-only detection — does NOT
     execute or modify commands. Triggers STATE B (Clutch) on match. -->

# High-Risk Command Scanner

## Purpose
Detect commands that would bypass the physically excluded destructive tools and trigger STATE B (Clutch) mode before execution.

## Pattern Detection Rules

### BLOCK (Never Execute — STATE B Trigger)

| Pattern | Regex | Risk |
|---------|-------|------|
| Recursive delete | `rm\s+-rf?\s+/` | Data destruction |
| Force push | `git\s+push\s+.*--force` | History rewrite |
| Sudo escalation | `^sudo\s+` | Privilege escalation |
| History rewrite | `git\s+rebase\s+-i` | History mutation |
| Hard reset | `git\s+reset\s+--hard` | Work loss |
| Branch delete remote | `git\s+push\s+.*--delete` | Remote branch destroy |
| Drop database | `DROP\s+(DATABASE\|TABLE\|SCHEMA)` | Data destruction |
| Truncate | `TRUNCATE\s+TABLE` | Data destruction |
| Format disk | `mkfs\|diskutil\s+eraseDisk` | System destruction |
| Kill all | `killall\|pkill\s+-9` | Process destruction |

### WARN (Execute with Logging)

| Pattern | Regex | Risk |
|---------|-------|------|
| npm global install | `npm\s+i(nstall)?\s+-g` | System modification |
| pip system install | `pip\s+install\s+(?!.*--user)` | System modification |
| chmod recursive | `chmod\s+-R` | Permission change |
| env modification | `export\s+.*SECRET\|KEY\|TOKEN` | Secret exposure |
| Docker privileged | `docker\s+run\s+.*--privileged` | Container escape |
| Network commands | `curl\s+.*\|\s*sh` | Pipe to shell RCE |

### SAFE (YOLO — Auto Execute)

All commands NOT matching BLOCK or WARN patterns are auto-approved per the `approval_envelope`.

## Integration

1. This scanner runs BEFORE `run_command` mentally evaluates each command
2. BLOCK patterns trigger STATE B → require explicit user approval
3. WARN patterns execute but log to `.beads/issues.jsonl`
4. Complements the tool_and_telemetry_posture exclusion list in GEMINI.md
5. Does NOT override YOLO for safe operations (git fetch, pip install --user, npm run dev, etc.)

## False Positive Handling

If a BLOCK pattern is a false positive (e.g., `rm -rf node_modules/` which is safe):
1. Log the justification
2. Narrow the command to be more specific
3. Execute the narrowed version
4. Example: `rm -rf node_modules/` → safe, but still prefer `rm -rf ./node_modules` (relative path)
