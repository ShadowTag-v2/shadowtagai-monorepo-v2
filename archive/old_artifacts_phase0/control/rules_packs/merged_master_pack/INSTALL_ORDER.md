# Canonical install order

1. Read root `AGENTS.md`.
2. Read `governance/AGENTS.md` and adopt the portable engineering rules.
3. Install or copy governance assets as needed:
   - `.pre-commit-config.yaml`
   - `eslint.config.js`
   - `.github/workflows/ci.yml`
   - `.cursor/rules/vibe-coding.mdc`
4. Read `operations/AGENTS.md`.
5. Install workspace truth files if this repo needs operational structure:
   - `operations/monorepo_manifest.yaml`
   - `operations/workspace-mcp-config.json`
   - `operations/database_tools.yaml`
   - `operations/scripts/*`
6. If this is ShadowTag work, read `overlay_shadowtag/AGENTS.md`.
7. Apply the ShadowTag overlay in this order:
   - `overlay_shadowtag/docs/Cor.Constitution.v3.md`
   - `overlay_shadowtag/.cursor/rules/shadowtag-vibe-coding.mdc`
   - `overlay_shadowtag/.agent/workflows/live-engine.md`
   - `overlay_shadowtag/.agent/docs/toolbelt.md`
   - `overlay_shadowtag/.agent/rules/shadowtag-laws.md`
   - `overlay_shadowtag/configs/shadowtag-runtime.yaml`
   - `overlay_shadowtag/scripts/session_bootstrap.sh`
8. Use repo-local docs in `governance/docs/` and `operations/docs/` as working references.

## Recommended use
- Greenfield repo: install `governance/` first.
- Existing monorepo with MCP/workspace control: layer in `operations/` next.
- ShadowTag/Antigravity/monorepo-specific workflow: layer in `overlay_shadowtag/` last.
