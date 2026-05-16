# Memory Lock

## Purpose
This file is the small, durable control-plane memory for the repo.
When live chat context gets thin, agents must recover from this file and the other canonical truth surfaces instead of guessing.

## Canonical truth order
1. `monorepo_manifest.yaml` = workspace truth
2. `antigravity-mcp-config.json` = MCP truth
3. `AGENTS.md` = agent behavior truth
4. `docs/UPDATED_pnkln_PACK.md` = survivorship truth
5. `docs/SESSION_PACKET.md` = current compact operating packet

## Product split
- `apps/counselconduit` = Google-native product path
- `labs/uphillsnowball` = local Apple Silicon lab path
- product truth must not be redefined by local-lab experiments

## Recovery rules
- never create a second source of truth
- never inline secrets into tracked config
- prefer latest-only artifacts over historical duplicates
- when uncertain, regenerate `docs/SESSION_PACKET.md` and `docs/RECOVERY_PACKET.md`
- when drift is detected, fix truth surfaces before feature work

## Required startup sequence
1. run `scripts/root_guard.sh`
2. run `scripts/memory_lock_audit.py --repo-root .`
3. run `scripts/rebuild_context_packet.py --repo-root . --write`
4. read `docs/SESSION_PACKET.md`
5. only then begin implementation

## Thin-context fallback
If context is weak or memory appears lost:
- stop drafting new architecture
- regenerate the packets
- compare canonical files against adapters and retired files
- continue only from evidence in repo files or verified external sources
