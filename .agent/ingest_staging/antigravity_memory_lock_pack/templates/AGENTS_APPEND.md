## Memory lock
Before repo-wide work, read:
- `docs/MEMORY_LOCK.md`
- `docs/SESSION_PACKET.md`
- `docs/UPDATED_PNKLN_PACK.md`
- `monorepo_manifest.yaml`
- `antigravity-mcp-config.json`

If context is thin, run:
- `scripts/root_guard.sh`
- `python3 scripts/memory_lock_audit.py --repo-root . --write`
- `python3 scripts/rebuild_context_packet.py --repo-root . --write`

Do not create new control-plane files when these already exist.
