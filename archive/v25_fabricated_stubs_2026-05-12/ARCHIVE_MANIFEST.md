# V25 Fabricated Stubs — Archived 2026-05-12

These directories were created by the V25 "PINNACLE OMNI-BOOT" script.
They contain NO real source code — only empty `dist/` folders and MCP SDK stub imports.

## Reason for Archive
- Forensic MCP Fleet Audit (2026-05-12) confirmed these as fabricated infrastructure
- None of these correspond to real npm packages or functional MCP servers
- They were injected to make Cline show ✅ UP status for non-existent servers

## Archived Directories
- `packages/ast-grep-mcp/` — stub MCP wrapper (ast-grep CLI exists at /opt/homebrew/bin/sg)
- `packages/flpomp-team/` — "Pomelli swarm" — not a real npm package
- `packages/google-labs-code/` — fake stitch-sdk, jules-sdk, jules-skills stubs
- `tools/workspace-listener/` — empty dir (no source files)
- `tools/pomelli_swarm/` — empty dir (no source files)  
- `tools/workspace-api/` — empty dir (only node_modules)

## Safe to Delete
These archive contents have zero functional value. They exist only for audit trail.
