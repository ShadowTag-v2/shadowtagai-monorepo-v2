---
name: setup-workspace
description: >
  Automated workspace initialization and bootstrap protocol for the UphillSnowball
  monorepo. Ensures all cognitive layers (Brainstem MCP servers, Hippocampus memory,
  Motor Cortex skill acquisition) are properly initialized on fresh clones,
  new environments, or after context loss. This is the operational counterpart
  to the kairos-zero-day-matrix session checklist.
---

# Setup Workspace — Bootstrap Protocol

**Source:** TACSOP 4 Kairos (Motor Cortex reflex)
**Trigger:** Fresh clone, new environment, `npx skills add` workspace init, or manual invocation

---

## Pre-Conditions

Before running this protocol, ensure:
1. Git SSH transport is configured (`git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git`)
2. Node.js v25+ is available (`node --version`)
3. Python 3.14+ is available (`/opt/homebrew/bin/python3.14 --version`)
4. .NET 11.0 Preview is available (`dotnet --version`)

---

## Phase 1: Repository Health

```bash
# Verify clean clone state
git remote -v
git status --short
git log -n 1 --oneline

# Verify canonical truth files exist
test -f AGENTS.md && echo "✅ AGENTS.md" || echo "❌ AGENTS.md MISSING"
test -f GEMINI.md && echo "✅ GEMINI.md" || echo "❌ GEMINI.md MISSING"
test -f monorepo_manifest.yaml && echo "✅ manifest" || echo "❌ manifest MISSING"
test -f antigravity-mcp-config.json && echo "✅ MCP config" || echo "❌ MCP config MISSING"
test -f BUSINESS_CONTEXT_LOCKED.md && echo "✅ business context" || echo "❌ business context MISSING"
test -f RISK_REGISTER.md && echo "✅ risk register" || echo "❌ risk register MISSING"
```

---

## Phase 2: Layer 1 — Brainstem (MCP Server Verification)

The 5 mandatory MCP servers must be reachable. Use the Fleet Vanguard pre-flight:

| Server | Verification Command |
|--------|---------------------|
| `firebase-mcp-server` | Call `firebase_get_environment` MCP tool |
| `chrome-devtools-mcp` | Call `list_pages` MCP tool |
| `StitchMCP` | Call `list_projects` MCP tool |
| `google-developer-knowledge` | Call `search_documents` with test query |
| `sequential-thinking` | Call `sequentialthinking` with trivial thought |

If any server fails, consult `.agents/skills/mcp-fleet-vanguard/SKILL.md` for the Self-Healing Loop.

---

## Phase 3: Layer 2 — Hippocampus (Memory Infrastructure)

### Obsidian Vault
```bash
# Verify vault scaffolding
test -d ~/Antigravity-Vault && echo "✅ Vault exists" || mkdir -p ~/Antigravity-Vault/{Zettelkasten,Auto-Dream,Logs,Templates}

# Verify vault directories
ls ~/Antigravity-Vault/
```

### NotebookLM
- Verify `notebooklm-orchestrator` skill is present in `.agents/skills/`
- Verify `notebooklm-bridge` skill is present in `.agents/skills/`
- Verify `notebooklm-oracle` skill is present in `.agents/skills/`

### Session Memory
- Verify `session-wrap-up` skill is present in `.agents/skills/`
- Verify `obsidian-formatter` skill is present in `.agents/skills/`
- Verify `expert-agent-builder` skill is present in `.agents/skills/`

---

## Phase 4: Layer 3 — Motor Cortex (Skill Acquisition)

### External Repositories
```bash
# Verify critical external repos
test -d external_repos/google-skills && echo "✅ google-skills" || echo "❌ google-skills MISSING"
test -d external_repos/vercel-skills && echo "✅ vercel-skills" || echo "❌ vercel-skills MISSING"
```

### npx Skills CLI
```bash
# Verify CLI is operational
CI=true npx -y skills --version
```

### Skill Fleet Census
```bash
# Count workspace skills
echo "Workspace skills: $(ls -d .agents/skills/*/ | wc -l)"
# Count global skills
echo "Global skills: $(ls -d ~/.gemini/antigravity/skills/*/ 2>/dev/null | wc -l)"
```

---

## Phase 5: Auth Infrastructure

### GitHub App
```bash
# Verify PEM is accessible (5-tier fallback)
python scripts/auth_github_app.py --export 2>&1 | head -5
```

### Firebase CLI
```bash
# Verify CLI auth (headless)
CI=true firebase login:list 2>&1 | head -5
```

### GCP ADC
```bash
# Verify Application Default Credentials
gcloud auth application-default print-access-token 2>&1 | head -1 | cut -c1-20
```

---

## Phase 6: Build Verification

### Python
```bash
/opt/homebrew/bin/python3.14 -m pytest --co -q 2>&1 | tail -3
```

### TypeScript (KovelAI)
```bash
cd apps/kovelai/site && npm run build 2>&1 | tail -5
```

### .NET (Semantic Kernel)
```bash
cd labs/uphillsnowball/apps/aiyou-kernel && dotnet build 2>&1 | tail -5
```

---

## Phase 7: Post-Bootstrap State Report

After all phases pass, output:
```
═══════════════════════════════════════════
  WORKSPACE BOOTSTRAP COMPLETE
═══════════════════════════════════════════
  Layer 1 (Brainstem):    [5/5 MCP servers]
  Layer 2 (Hippocampus):  [Vault + 6 memory skills]
  Layer 3 (Motor Cortex): [N workspace + M global skills]
  Auth:                   [GitHub App ✅ | Firebase ✅ | ADC ✅]
  Build:                  [Python ✅ | TypeScript ✅ | .NET ✅]
  State:                  STATE A (YOLO) — ready for work
═══════════════════════════════════════════
```

---

## Cross-References

- Kairos Zero-Day Matrix: `.agents/skills/kairos-zero-day-matrix/SKILL.md`
- MCP Fleet Vanguard: `.agents/skills/mcp-fleet-vanguard/SKILL.md`
- Hybrid Capability Cascade: `.agents/skills/hybrid-capability-cascade/SKILL.md`
- Dynamic Tool Acquisition: `.agents/skills/dynamic-tool-acquisition/SKILL.md`
- Firebase M2M Headless Auth: `.agents/skills/firebase-m2m-headless-auth/SKILL.md`
- GitHub App Push: `.agents/skills/github-app-push/SKILL.md`
