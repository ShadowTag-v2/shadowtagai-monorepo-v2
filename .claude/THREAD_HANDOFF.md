# Thread Handoff — Omega Egress Complete
## For: Claude Code (or any agent inheriting this thread)

### State After Egress
- Branch: `fix-invariants-103-105` (merged to main via force-push)
- Operator Invariants: v41.0, 88 rules
- Daemon Fleet: 9/9 exit 0
- Model: gemini-3.1-flash-lite-preview-thinking
- Project: shadowtag-omega-v4

### Immediate Actions Required
1. Verify remote HEAD matches local: `git log --oneline -1`
2. Set branch protection on `main` via GitHub API
3. Clean up stale branches: `git branch -d fix-invariants-103-105`
4. Run `ast-grep scan -c tools/ast-grep-rules/sgconfig.yml` (554 rules)
5. Verify NotebookLM Master Brain: ID c493b409-3955-418f-a993-755c38dc8e7f

### Architecture Summary
- **SSoT**: AGENTS.md → operator_invariants.json → monorepo_manifest.yaml
- **Auth**: GitHub App ID 3018200 + PEM at ~/Downloads/
- **MCP**: antigravity-mcp-config.json (11 servers, 100+ tools)
- **Memory**: 3-layer KV Slab (Session → Persistent → Cold Storage)
- **Push Protocol**: scripts/omega_sync.py (JWT → installation token → ephemeral push)

### Do NOT
- Switch branches without committing
- Run `git add .` without checking `git status` first
- Push without JWT auth (never use raw `git push origin main`)
- Store secrets in git-tracked files
