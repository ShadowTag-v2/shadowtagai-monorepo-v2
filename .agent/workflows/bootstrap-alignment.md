# Bootstrap Alignment

Align agent state to the canonical monorepo truth surfaces at session start.

## Contract
- Tool contract: `tool_contracts/bootstrap.alignment.yaml`
- Enforcement: mandatory

## Steps

// turbo
1. **Temporal Anchor** — Run `git log -n 3 --oneline` to establish HEAD.

// turbo
2. **Truth Surface Scan** — Read `truth_surfaces.yaml` and `monorepo_manifest.yaml`.

// turbo
3. **Doctrine Load** — Read `AGENTS.md` and verify hardened state version.

// turbo
4. **MCP Preflight** — Run the 5-server pre-flight check (list_pages, firebase_get_environment, list_projects, search_documents, sequentialthinking).

// turbo
5. **Beads Health** — Run `bash scripts/beads-health.sh` to validate work truth.

// turbo
6. **Contract Drift** — Run `bash scripts/contract-drift-check.sh` to detect misalignment.

7. **Report** — Summarize alignment state. If any drift detected, log to `.beads/issues.jsonl` and escalate.

## Completion Criteria
- All truth surfaces version-aligned with manifest
- MCP fleet reports 5/5 online
- No contract drift detected (or drift logged and escalated)
