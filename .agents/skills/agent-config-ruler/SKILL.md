---
name: agent-config-ruler
description: Standard Operating Procedure for updating AI agent instructions, MCP configurations, and system prompts using the Ruler single-source-of-truth framework.
---

# Ruler Agent Config Manager

## The Doctrine of Single Truth

You are strictly prohibited from directly modifying `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, or `.github/copilot-instructions.md`. These files are **derived outputs**, not sources.

## The Single Source

All agent instructions, invariants, and system state live in `.ruler/AGENTS.md`.

All MCP server definitions and workspace configuration live in `.ruler/ruler.toml`.

## How To Update Agent Instructions

1. **Edit** `.ruler/AGENTS.md` with the new rule, state change, or invariant.
2. **Edit** `.ruler/ruler.toml` if MCP server definitions changed.
3. **Run** `npx -y @intellectronica/ruler apply` in the repo root.
4. Ruler will automatically propagate the changes to all agent-specific files:
   - `AGENTS.md` (root)
   - `CLAUDE.md`
   - `.github/copilot-instructions.md`
   - `.cursorrules` / `.cursor/rules/`
   - `.windsurfrules`
   - `.clinerules`
   - `.aider/conventions.md`
   - `GEMINI.md`
5. **Commit** the generated files alongside the `.ruler/` source.

## Reverting

If a bad propagation occurs, run `npx -y @intellectronica/ruler revert` to restore from `.bak` files.

## CI Integration

Add to `10x_vibe_matrix.yml` or a dedicated workflow:
```yaml
- name: Ruler Drift Detection
  run: |
    npx -y @intellectronica/ruler apply
    git diff --exit-code || (echo "Ruler configs out of sync" && exit 1)
```

## Anti-Patterns (PROHIBITED)

- Manually editing `CLAUDE.md` or `GEMINI.md` — these are GENERATED OUTPUTS.
- Adding agent-specific logic in `.ruler/AGENTS.md` (use agent-local overrides via nested `.ruler/` dirs).
- Running `ruler apply` without reviewing the diff first.
- Skipping `.ruler/` changes in git commits (breaks reproducibility).
