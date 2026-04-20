# Cor.workspace Boot Plan — Antigravity Execution Package
# Generated: 2026-04-18 | Operator: shadowtag-omega-v4 | PNKLN_GHOST: ON

---

## PRE-EXECUTION: Retrieve Missing Lists (TASK 3/4/6 placeholders)

The 9 playground repo names, 5 ZIP bundle specs, and 34 ehanc69 repo names exist **only** in
the original Cor.workspace message (compacted out of Claude context). Retrieve before starting:

```bash
# Option A: Query Master Brain (preferred if already seeded)
BRAIN_ID=$(cat ~/.notebooklm/master-brain-id 2>/dev/null)
nlm notebook query "$BRAIN_ID" "Cor.workspace Cor.Playground Transfer Package playground repos"
nlm notebook query "$BRAIN_ID" "antigravity ZIP bundle fold-in matrix ehanc69 repos"

# Option B: Read raw JSONL transcript directly (guaranteed source)
python3 - <<'EOF'
import json, pathlib, sys
transcript = pathlib.Path(
    "/Users/pikeymickey/.claude/projects/-Users-pikeymickey/a55a251e-6cbe-45ed-891b-81ded3342b17.jsonl"
)
for line in transcript.read_text().splitlines():
    try:
        obj = json.loads(line)
        # Search for Cor.workspace message containing the lists
        text = json.dumps(obj)
        if "Cor.Playground" in text or "ehanc69" in text or "fold-in matrix" in text:
            print(json.dumps(obj, indent=2)[:3000])
            print("---")
    except Exception:
        pass
EOF
```

Once retrieved, fill placeholders in TASK 3 (`ehanc69/REPO_1` ... `REPO_9`) and
TASK 6 (the 34-repo loop). TASK 7 targets are already filled — see 7a–7d below.

---

## SESSION INIT (Run first, every session)

```bash
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

# Live Engine exports
export GCP_PROJECT_ID="shadowtag-omega-v4"
export AGENT_TOOLBELT="$(pwd)/.agent/docs/toolbelt.md"
export AGENT_LAWS="$(pwd)/.agent/rules/shadowtag-laws.md"
export AGENT_LIVE_ENGINE="$(pwd)/.agent/workflows/live-engine.md"
export VITE_API_URL="http://localhost:8000"
export BRAIN_DIR="$HOME/.gemini/antigravity/brain/$(date +%s)"

# GitHub App auth (NEVER use personal PAT)
source <(python3 scripts/auth_github_app.py --export)

# Auth check
nlm login --check || nlm login
notebooklm auth check --test || notebooklm login

# Start daemons (non-blocking)
nohup python3 scripts/omega_auth_daemon.py > logs/omega_daemon.log 2>&1 &
nohup python3 tools/scripts/god_mode_admin.py > logs/godmode.log 2>&1 &

# Sovereign memory sync (non-blocking)
.venv/bin/python reference/public-demos/shadowtag-omega-v4/bin/ingest_memory_snapshots.py &

# Beads — fetch ready work
python tools/beads_core.py

# GitNexus — refresh index (background, ~5 min)
npx gitnexus analyze &
```

---

## TASK 0 — Fix `notebooklm` binary (PREREQUISITE)

> Plan detail: `~/.claude/plans/adaptive-kindling-harbor.md` (Steps 1–6)

```bash
# Step 1: Force-reinstall via Python 3.14
/opt/homebrew/bin/pip3 install --force-reinstall notebooklm-py

# Step 2: Verify shebang is Python 3.14
head -1 /opt/homebrew/bin/notebooklm
# Expected: #!/opt/homebrew/opt/python@3.14/bin/python3.14

# Step 3: Fix PATH — ensure Homebrew wins over Xcode Python 3.9
# Check ~/.zshrc; if /opt/homebrew/bin is not FIRST, prepend:
grep -n 'Library/Python/3.9' ~/.zshrc
# If found, ensure this line precedes it:
# export PATH="/opt/homebrew/bin:$PATH"

source ~/.zshrc
which notebooklm  # must return /opt/homebrew/bin/notebooklm

# Step 4: Install skills
notebooklm skill install
ls ~/.agents/skills/notebooklm/SKILL.md  # must exist
nlm skill install claude-code
nlm skill install agents
nlm skill list  # claude-code and agents must show ✓

# Step 5: Smoke test
nlm notebook list
notebooklm list
```

---

## TASK 1 — Write `Monorepo-Uphillsnowball.code-workspace`

Target: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/Monorepo-Uphillsnowball.code-workspace`

Overwrite with the full settings JSON (provided in Cor.workspace message). Key additions vs. current state:

- `geminicodeassist.agentYoloMode: true` — MISSING, must add
- `python.defaultInterpreterPath` — change relative to absolute `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/python`
- All `files.exclude`, `search.exclude`, `watcherExclude` entries for `archive/`, `legacy/`, `third_party/` paths
- Cline / Roo-Cline `autoApproval` flags
- `gcp.projectId: "shadowtag-omega-v4"`

```bash
# After write:
open Monorepo-Uphillsnowball.code-workspace
# Verify VS Code / Cursor re-opens with updated settings
```

---

## TASK 2 — GitNexus index refresh

> Already launched as background in SESSION INIT. Confirm completion:

```bash
# Poll (non-blocking check; do not wait synchronously)
npx gitnexus status
# When done: node count must be ≥455,599 (CLAUDE.md claim vs current 311,360)
```

---

## TASK 3 — Clone 9 Playground Repos to `third_party/`

> Repo list: see Cor.Playground Transfer Package (provided in original Cor.workspace message).
> Template for each:

```bash
mkdir -p third_party
TOKEN=$(python3 scripts/auth_github_app.py)

# For each of the 9 repos (replace ORG/REPO with actual names from package):
git clone "https://x-access-token:${TOKEN}@github.com/ORG/REPO.git" "third_party/REPO"
```

**Repos to clone** (fill from Cor.Playground Transfer Package):
1. `ehanc69/REPO_1`
2. `ehanc69/REPO_2`
3. `ehanc69/REPO_3`
4. `ehanc69/REPO_4`
5. `ehanc69/REPO_5`
6. `ehanc69/REPO_6`
7. `ehanc69/REPO_7`
8. `ehanc69/REPO_8`
9. `ehanc69/REPO_9`

```bash
# After clone, exclude from search (already in workspace JSON, but verify):
# third_party/ should appear in search.exclude and watcherExclude
```

---

## TASK 4 — Apply ZIP Bundles (Strict Order)

> `four_file_repo_audit_bundle.zip` is MISSING from `~/Downloads` — **SKIP IT**.

```bash
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball

BUNDLES=(
  "antigravity_rebuilt_bundle_2026_03_18.zip"
  "antigravity_gca_repo_bundle.zip"
  "antigravity_strict_final_foldin_apply.zip"
  "antigravity_manifest_bundle_v3.zip"
  "antigravity_memory_lock_pack_v1.zip"
)

for bundle in "${BUNDLES[@]}"; do
  echo "=== Applying: $bundle ==="
  unzip -o "$HOME/Downloads/$bundle" -d .
  echo "=== Done: $bundle ==="
done

# Post-apply: run typecheck to catch any breakage
npx tsc --noEmit 2>&1 | head -50

# Auto-repair if errors:
# python scripts/auto_error_repair.py
```

---

## TASK 5 — Fix 3 Transfer.Script Gaps

### Gap 1: CI/CD hardcoded paths

Targets:
- `scripts/audit_github_governance.sh`
- `scripts/check_mcp_stack.sh`

Find and replace hardcoded `/Users/` paths → use `$HOME` or `$(git rev-parse --show-toplevel)`:

```bash
grep -rn '/Users/pikeymickey' scripts/ --include='*.sh'
# For each match, replace hardcoded path with $HOME or $REPO_ROOT equivalent
# Edit files with sed or direct edit — do NOT use find+replace blindly (see grep note)
```

### Gap 2: NPM workspace linking in `external_sdks/npm/`

```bash
ls external_sdks/npm/
# For each package that references ../../apps/aiyou_stack:
grep -rn 'aiyou_stack' external_sdks/npm/ --include='package.json'
# Fix workspace: protocol references to use correct relative paths
# Then:
npm install --workspaces
```

### Gap 3: Ghost module imports (fractured `../../apps/aiyou_stack` paths)

```bash
# Ruff scan (Python)
.venv/bin/ruff check . --select F401,F811 --output-format=full 2>&1 | head -100

# Biome scan (TS/JS)
npx @biomejs/biome check . --diagnostic-level=error 2>&1 | grep 'Cannot find module' | head -50

# Fix each ghost import — update to correct monorepo-relative path or add to workspace excludes
```

---

## TASK 6 — ehanc69 Fold-In Batch (Cloud-Only, No Local Mac Download)

> Runs entirely on a GitHub Actions runner via `.github/workflows/ehanc69-foldin.yml`.
> No local `git clone` required. Auth uses two GitHub Apps.

### Step 1 — One-time secret setup (run ONCE on Mac, then never again)

```bash
# Store PEM keys as GitHub Actions secrets
gh secret set SHADOWTAG_APP_PRIVATE_KEY \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  < ~/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem

gh secret set EHANC69_APP_PRIVATE_KEY \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  < ~/Downloads/antigravity-manager.2026-03-13.private-key.pem

# Store App IDs as GitHub Actions variables (not secret — these are public)
gh variable set SHADOWTAG_APP_ID --body "3018200" \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball

gh variable set EHANC69_APP_ID --body "3018080" \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball
```

### Step 2 — Dry run (verify list before committing)

```bash
gh workflow run ehanc69-foldin.yml \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  -f dry_run=true

# Watch output:
gh run list --workflow=ehanc69-foldin.yml --repo ShadowTag-v2/Monorepo-Uphillsnowball
gh run watch --repo ShadowTag-v2/Monorepo-Uphillsnowball
```

### Step 3 — Live run (writes to monorepo, pushes to main)

```bash
gh workflow run ehanc69-foldin.yml \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  -f dry_run=false
```

Result: all ehanc69 repos folded into `third_party/ehanc69/[repo]/`
via copy + squash commit (snapshot only, no source history imported).

### What the workflow does
1. Generates installation tokens for both GitHub Apps (no secrets on disk)
2. Clones monorepo on ephemeral ubuntu runner (cloud, not Mac)
3. Self-discovers all non-archived ehanc69 repos via API (currently 56)
4. Shallow clones each source repo (~1Gbps between GitHub servers)
5. `scripts/mass_subtree_merge.py` copies each into `third_party/ehanc69/[repo]/`
6. Each repo gets a single squash commit (no history carried)
7. Pushes merged result to `main`

### Note
The Google OAuth client secret file (`client_secret_...apps.googleusercontent.com.json`)
is for NotebookLM/Google Workspace auth, NOT GitHub. Do NOT add it as a GH Actions secret.

---

## TASK 7 — ShadowTag-v2 Merge Threads

Four merge operations. All source paths under `third_party/` after Task 6 clones:

### 7a: molten-universe `.vscode/` → monorepo `.vscode/`
```bash
cp -r third_party/ehanc69-fold-staging/molten-universe/.vscode/* .vscode/
```

### 7b: deep-aurora `.vscode/` → monorepo `.vscode/`
```bash
cp -r third_party/ehanc69-fold-staging/deep-aurora/.vscode/* .vscode/
# Resolve conflicts: prefer monorepo-side on extensions.json, prefer source-side on settings.json
```

### 7c: ShadowTag-v2 `docs/` → monorepo `docs/`
```bash
# Identify source:
# archive_legacy_ShadowTag-v2/ OR third_party/ehanc69-fold-staging/ShadowTag-v2/docs/
rsync -av --ignore-existing \
  archive_legacy_ShadowTag-v2/docs/ \
  docs/
```

### 7d: `drive_knowledge/documents/` merge
```bash
rsync -av --ignore-existing \
  archive_legacy_ShadowTag-v2/drive_knowledge/documents/ \
  data/drive_ingest/markdown/
```

---

## TASK 8 — Post-Boot Validation

```bash
# 1. TypeScript clean
npx tsc --noEmit

# 2. ESLint clean
npx eslint . --quiet

# 3. GitNexus confirm
npx gitnexus status  # expect ≥455,599 nodes

# 4. Workspace file correct
cat Monorepo-Uphillsnowball.code-workspace | jq '.settings["geminicodeassist.agentYoloMode"]'
# must return: true

# 5. Auth check
nlm login --check && notebooklm auth check --test

# 6. RAG alive
curl -s -X POST "$VITE_API_URL/api/v1/shadowtag-omega-v4/agent/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "shadowtag-omega-v4 mission"}' | jq .status

# 7. Beads — close boot task
python tools/beads_core.py  # update status=closed on Cor.workspace task
```

---

## Operating Guide During Execution

This boot sequence runs under **Cor.Constitution v3** invariants:

- **Board Posture**: 160IQ lock. Verified facts only — no speculation.
- **Beads**: Log every completed task to beads immediately. If a bug is found mid-task, CREATE a beads issue — do NOT fix it inline.
- **PNKLN_GHOST**: No AI attribution in commits. No model codenames. Terse developer persona.
- **Auto-repair**: On any lint/type error → `python scripts/auto_error_repair.py` (Gemini primary). No approval needed.
- **GitHub Auth**: NEVER use personal PAT. Always `python3 scripts/auth_github_app.py`.
- **Source maps**: Verify `sourceMap: false` in any tsconfig touched during ZIP apply.
- **Hardcoded secrets**: If found during any task → immediately rewrite to `os.getenv()`.

---

## Known Blockers / Skips

| Item | Status | Action |
|------|--------|--------|
| `four_file_repo_audit_bundle.zip` | MISSING from ~/Downloads | SKIP — re-upload when available |
| 34 ehanc69 repo names | Need fill from original fold-in matrix | Clone list in TASK 6 template |
| 9 playground repo names | Need fill from Cor.Playground package | Clone list in TASK 3 template |
| `.ssh/`, `.nvm/`, `.orbstack/` | Not confirmed transferred | Separate Cor.Transfer thread |
| 72 `.claude/todos/` | Missing from current user | Separate recovery task |
| `gemini-key.json` at deleted user root | Still at `/Users/Deleted Users/pikeymickey/` | Migrate securely — separate task |

---

## Execution Order Summary

```
SESSION INIT
  ↓
TASK 0: notebooklm binary fix
  ↓
TASK 1: workspace JSON write + open
  ↓ (TASK 2 runs in background throughout)
TASK 3: clone 9 playground repos
  ↓
TASK 4: apply 5 ZIP bundles (in order, skip missing)
  ↓
TASK 5: fix 3 Transfer.Script gaps
  ↓
TASK 6: clone 34 ehanc69 repos → fold-in batch
  ↓
TASK 7: ShadowTag-v2 merge threads (4 ops)
  ↓
TASK 8: post-boot validation
  ↓
Beads: close all tasks, /wrap-up to Master Brain
```
