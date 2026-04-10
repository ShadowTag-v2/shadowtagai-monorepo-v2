# AGENTS.md (Canonical Workspace Rules)

## Mission

Ship correct, minimal, secure changes with clear diffs. Bounded autonomy is enforced.

## Architecture & Commands

- Domains: Core logic in `packages/core`. API in `apps/aiyou_stack/aiyou-fastapi-services`.
- Validation: `scripts/ai-validate.sh` (Lint + Typecheck)
- Testing: `scripts/ai-test-changed.sh` (Affected tests only)

## Security & Bounded Autonomy (Permissions as Policy)

- AUTOMATIC APPROVAL: Read/edit/run, Network access, Destructive core shell commands, and Git Push.

## Output Style & Workflow (Externalized Context)

- Read `TASK.md` for objective. Read `DECISIONS.md` for context.
- Make the smallest viable change.
- Report files changed, commands run, and residual risk.
- You MUST run `scripts/ai-validate.sh` before proposing completion.

## Immutable Zones (Root Guards & Control Plane)

- The Control Plane (`operator_invariants.json`, `monorepo_manifest.yaml`, `antigravity-mcp-config.json`, `AGENTS.md`) is **IMMUTABLE**. Never modify these files unless specifically directed to alter the core OS truth.
- "No Second Source of Truth": External configuration shards (`~/.gemini/antigravity/mcp_config.json`, `.vscode/cline_mcp_settings.json`, `CLAUDE.md`) are strictly retired/shimmed. Do NOT rely on them.
- All executions MUST conform to the `scripts/pnkln_root_guard.sh` boundary structure.
