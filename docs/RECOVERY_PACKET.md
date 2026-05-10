# Recovery Packet

If memory appears dropped:
- stop feature work
- run `scripts/root_guard.sh`
- run `python3 scripts/memory_lock_audit.py --repo-root . --write`
- run `python3 scripts/rebuild_context_packet.py --repo-root . --write`
- read `docs/SESSION_PACKET.md`
- continue only from canonical files and verified sources

## Canonical files
- AGENTS.md
- docs/MEMORY_LOCK.md
- docs/UPDATED_PNKLN_PACK.md
- monorepo_manifest.yaml
- antigravity-mcp-config.json
