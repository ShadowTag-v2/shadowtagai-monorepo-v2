# Antigravity Memory Lock Pack

This pack makes Antigravity more recoverable when chat context gets thin.

It does four jobs:
1. locks a small set of canonical truth surfaces into the repo
2. rebuilds a compact session packet at startup
3. audits drift across model names, MCP files, naming, and stale paths
4. produces a recovery packet an agent can read before taking action

## Intended repo surfaces
- `AGENTS.md`
- `docs/MEMORY_LOCK.md`
- `docs/UPDATED_pnkln_PACK.md`
- `monorepo_manifest.yaml`
- `antigravity-mcp-config.json`
- `.cursor/rules/memory-lock.mdc`
- `.vscode/tasks.json`

## Quick start

```bash
bash scripts/bootstrap_memory_lock.sh --repo-root /path/to/Monorepo-Uphillsnowball
bash /path/to/Monorepo-Uphillsnowball/scripts/omega_startup.sh
python3 /path/to/Monorepo-Uphillsnowball/scripts/memory_lock_audit.py --repo-root /path/to/Monorepo-Uphillsnowball --write
python3 /path/to/Monorepo-Uphillsnowball/scripts/rebuild_context_packet.py --repo-root /path/to/Monorepo-Uphillsnowball --write
```

## Outputs after install
- `docs/MEMORY_LOCK.md`
- `docs/SESSION_PACKET.md`
- `docs/RECOVERY_PACKET.md`
- `docs/AUDIT_REPORT.md`
- `scripts/omega_startup.sh`
- `scripts/memory_lock_audit.py`
- `scripts/rebuild_context_packet.py`
- `scripts/root_guard.sh`

## What to tell Antigravity at session start
Read these before acting:
- `AGENTS.md`
- `docs/MEMORY_LOCK.md`
- `docs/SESSION_PACKET.md`
- `monorepo_manifest.yaml`
- `antigravity-mcp-config.json`

Then run `scripts/root_guard.sh` and `scripts/memory_lock_audit.py --repo-root .`.
