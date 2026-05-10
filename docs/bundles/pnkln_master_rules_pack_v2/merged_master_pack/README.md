# Merged master pack

This pack combines three layers:

- `governance/` — portable coding-agent rules, checklists, prompts, linting, pre-commit, CI.
- `operations/` — workspace truth, MCP truth, product/lab split, and operational helper scripts.
- `overlay_shadowtag/` — ShadowTag-specific constitution, live-engine workflow, and session bootstrap.

## Best entry points

- Root behavior contract: `AGENTS.md`
- Canonical sequencing: `INSTALL_ORDER.md`
- Portable rules: `governance/docs/vibe-coding-rules.md`
- Workspace truth: `operations/monorepo_manifest.yaml`
- ShadowTag constitution: `overlay_shadowtag/docs/Cor.Constitution.v3.md`

## One-line guidance

Use `governance` everywhere, `operations` when the repo needs a control plane, and `overlay_shadowtag` only when the work is truly ShadowTag-specific.
