# SYSTEM OVERRIDE: OMNI-BOOT INITIALIZATION (V28.2 — V26 SYMBIOTIC ALIGNMENT)

> **Purpose:** Copy-paste this entire block as the first message in any new Antigravity thread.
> It cold-starts the agent with full operational awareness — no discovery phase needed.
>
> **Last Updated:** 2026-05-15 | **Epoch:** V26 Symbiotic Alignment (Post-Sovereign Meridian)
>
> **Key Principle (arXiv:2512.14982):** Tool namespace redundancy destroys test-time reasoning
> efficiency. Duplicate tools across the host platform and local extensions cause *tool-choice
> paralysis* — the LLM burns compute tokens deliberating between identical API surfaces.

---

## 0. IMMEDIATE ACTIONS (Execute Before Responding)

### 0A. Kill All Zombies & Stale Locks
```bash
# Kill orphaned git processes, stale index.lock files, and zombie daemons
find /Users/pikeymickey/.gemini -name "*.lock" -type f -mmin +5 -delete 2>/dev/null || true
find /Users/pikeymickey/.gemini -name "index.lock" -type f -delete 2>/dev/null || true
pkill -f "git.*credential" 2>/dev/null || true
pkill -f "gh auth" 2>/dev/null || true
```

### 0B. Dual-Plane MCP Fleet Pre-Flight (20 Servers Total)

The fleet operates across two symbiotic planes. Tool redundancy is constitutionally prohibited.

> **⚠️ BOUNDARY COLLISION DIAGNOSTIC:** When both Antigravity and Cline expose the same tool
> (e.g., two `take_screenshot`, two `deploy_cloud_run`), the LLM experiences tool-choice
> paralysis. It burns tokens deliberating over which namespace to invoke. This is a
> measurable degradation in test-time reasoning efficiency. The Dual-Plane separation
> eliminates this noise entirely.

#### PLANE 1: ANTIGRAVITY INTERNAL HOST (6 Servers — Probe on Boot)
Run one probe per server. Retry once on EOF. Report status table.

| # | Server | Probe Tool | Tools | Domain |
|---|--------|-----------|-------|--------|
| 1 | `StitchMCP` | `list_projects` | 14 | Generative UI variants, design systems |
| 2 | `chrome-devtools-mcp` | `list_pages` | 29 | Browser sensorium, screenshots, DOM, Lighthouse |
| 3 | `cloudrun` | `list_services` | 8 | Compute deployment |
| 4 | `firebase-mcp-server` | `firebase_get_environment` | 36 | State, auth, hosting, Firestore |
| 5 | `google-developer-knowledge` | `search_documents("quickstart")` | 3 | Omniscience (Google dev docs) |
| 6 | `sequential-thinking` | `sequentialthinking(thought="boot")` | 1 | Multi-step reasoning |

**Self-Healing Loop:** If a server returns EOF on first probe, retry exactly once. If still down, log to `.beads/issues.jsonl` and continue. **Never use terminal fallbacks** for MCP-capable operations.

#### PLANE 2: CLINE TACTICAL LOCAL CONFIG (14 Servers — No Probing by Antigravity)
These servers are managed exclusively by `cline_mcp_settings.json`. Antigravity does **NOT** probe, start, or duplicate them.

| # | Server | Runtime | Domain |
|---|--------|---------|--------|
| 7 | `design-cortex` | Bun | Stitch SDK design extraction |
| 8 | `workspace-intake` | Bun | Google Workspace webhook listener |
| 9 | `google-drive-api` | Bun | Drive document fetcher |
| 10 | `jules-delegation` | Bun | Jules async agent delegation |
| 11 | `jules-fleet` | Bun | Jules skill fleet coordination |
| 12 | `gcp-infrastructure` | bunx | Resource Manager, Spanner, PubSub |
| 13 | `autonomic-insights` | bunx | Database insights (Spanner) |
| 14 | `observability` | bunx | Genkit MCP observability |
| 15 | `storage-cdn` | bunx | Cloud Storage operations |
| 16 | `stripe-governor` | bunx | Stripe financial governor |
| 17 | `semantic-scalpel` | Bun | AST-Grep semantic code surgery |
| 18 | `notebooklm-mcp` | uvx | NotebookLM epistemic memory |
| 19 | `pomelli-swarm` | Bun | Pomelli brand content swarm |
| 20 | `dart-compiler` | Dart | Dart language server protocol |

> **⚠️ SEPARATION AXIOM:** If Antigravity provides a capability natively (Plane 1), Cline MUST NOT duplicate it. If Cline provides a tactical capability (Plane 2), Antigravity MUST NOT attempt to manage it. See `docs/SYSTEM_OVERRIDE.md` for the constitutional reference.

### 0C. Plane Integrity Validator (Run After Pre-Flight)

After both planes are confirmed, validate that no drift has occurred:

```bash
# Plane Integrity Check — detect namespace collisions
PLANE1_TOOLS="StitchMCP chrome-devtools-mcp cloudrun firebase-mcp-server google-developer-knowledge sequential-thinking"
CLINE_CFG="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
if [ -f "$CLINE_CFG" ]; then
  for srv in $PLANE1_TOOLS; do
    if grep -qi "$srv" "$CLINE_CFG" 2>/dev/null; then
      echo "❌ DRIFT: $srv found in BOTH Plane 1 and Plane 2 — REMOVE from cline_mcp_settings.json"
    fi
  done
  echo "✅ Plane integrity check complete"
else
  echo "⚠️ Cline config not found at expected path — manual verification needed"
fi
```

**If drift is detected:** Remove the colliding server from `cline_mcp_settings.json` immediately. Log to `.beads/issues.jsonl` with severity `ARCHITECTURE_DRIFT`.

---

## 1. CANONICAL REPOSITORY COORDINATES

### 1A. Sovereign Repository (PRIMARY — All Pushes Here)
```
URL:   https://github.com/ShadowTag-v2/shadowtagai-monorepo-v2.git
SSH:   git@github.com:ShadowTag-v2/shadowtagai-monorepo-v2.git
```

### 1B. Workspace Paths
| Path | Role |
|------|------|
| `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball` | IDE workspace (`.code-workspace` root) |
| `/Users/pikeymickey/.gemini/mono-fresh` | Clean sovereign checkout |

Both remotes MUST point to `shadowtagai-monorepo-v2`. Verify with `git remote -v`.

### 1C. Archived Repository (READ-ONLY — NEVER Push)
```
https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git  ← ARCHIVED 2026-05-14
```

### 1D. Branch Policy
- `main` is the production branch on sovereign.
- Feature branches: `feat/<name>`, `fix/<name>`.
- After merge, delete feature branches immediately.

---

## 2. AUTHENTICATION CHAIN

### 2A. GitHub App PEM (ONLY Auth Path for Git Operations)
```
PEM:       /Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem
App ID:    3018200
Client ID: Iv23ctYqrxPQIt2ir8gY
Env var:   $SHADOWTAG_PEM
Script:    scripts/auth_github_app.py (5-tier PEM fallback chain)
```

**Push Protocol:**
```bash
# Generate ephemeral installation token → push via HTTPS with x-access-token
python3 scripts/auth_github_app.py --push
```

### 2B. GCP / Firebase Auth
| Layer | Mechanism | Token Location |
|-------|-----------|---------------|
| Firebase CLI (Layer 1) | OAuth2 refresh token | `~/.config/configstore/firebase-tools.json` |
| Firebase MCP (Layer 2) | In-memory OAuth2 session | `firebase_login` MCP tool |
| ADC (Layer 3) | Application Default Credentials | `~/.config/gcloud/application_default_credentials.json` |

**Project:** `shadowtag-omega-v4`
**SA:** `counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com`

### 2C. Secrets
- **Source:** GCP Secret Manager exclusively. No `.env` files (BANNED).
- **Local load:** `source scripts/load_mcp_secrets.sh`
- **MCP config:** `${VAR}` references resolved by Antigravity platform env injection.

### 2D. PROHIBITED Authentication Methods
- `gh auth login` / `gh auth token` — NEVER
- Personal access tokens (PATs) — NEVER
- Deploy keys — NOT acceptable
- `.env` files / `python-dotenv` — BANNED
- `npx firebase-tools` — tokens lost in ephemeral `_npx/` cache

---

## 3. RUNTIME MATRIX (Verified 2026-05-15)

| Runtime | Version | Path |
|---------|---------|------|
| Python | 3.14.5 (CPython) | `python3` |
| Node.js | v26.0.0 | `node` |
| .NET | 11.0.100-preview.3 | `/usr/local/share/dotnet/dotnet` |
| Bun | 1.3.14 | `bun` |

> **⚠️ .NET PATH SHADOWING:** Homebrew's `dotnet` (10.0.107) at `/opt/homebrew/bin/dotnet` shadows .NET 11. Production builds MUST use `/usr/local/share/dotnet/dotnet` or reorder `$PATH`.

### 3A. Package Managers
- **Python:** `uv` (primary), `pip` (fallback)
- **Node:** `pnpm` (primary), `npm` (fallback)
- **Bun:** For TypeScript execution and bundling
- **.NET:** `dotnet restore` with `global.json` (`rollForward: latestMajor, allowPrerelease: true`)

---

## 4. CANONICAL TRUTH HIERARCHY

```
AGENTS.md               → Canonical operator contract
CLAUDE.md                → Thin shim
monorepo_manifest.yaml   → Workspace truth
antigravity-mcp-config.json → MCP server truth
BUSINESS_CONTEXT_LOCKED.md → Pricing/architecture truth
RISK_REGISTER.md         → Operational risk truth
.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md → Non-destruction law
docs/SYSTEM_OVERRIDE.md  → V26 Dual-Plane fleet separation rules
```

---

## 5. SESSION INVARIANTS (Persist for Entire Thread)

### 5A. Execution Envelope
- **YOLO Mode:** Enabled. Auto-approve all read/edit/run/network/push operations.
- **Destructive exclusions:** `rm`, `rm -rf`, `unlink`, `sudo` — physically excluded.
- **STATE A (Pure YOLO):** Default for repetitive UI work, standard logic, known patterns.
- **STATE B (Clutch):** Only for: git history rewrites, force-pushes, DB migrations, auth/payment changes, architecture shifts >3 packages.

### 5B. Linting (Self-Healing — TACSOP 5)
- **Python:** `ruff check --fix` + `ruff format` after EVERY file modification. Vulture banned.
- **TypeScript/JS:** `biome check --fix` + `biome format`. ESLint/Prettier banned.
- **Structural:** `ast-grep` for search-and-replace only.
- **Dead code:** `ruff check --select F401,F841 --fix`

### 5C. Visual Provenance (TACSOP 7)
- `generate_image` tool is **BANNED**. Use Stitch MCP, Veo 3.1, or semantic CSS/SVG placeholders.

### 5D. Headless CLI Protocol
- Prepend `export CI=true DEBIAN_FRONTEND=noninteractive` to all commands that may launch TUIs.
- Use `--non-interactive`, `--quiet`, `--yes/-y` flags always.
- If blocked by interactive prompt: terminate → retry with CI=true → pexpect script → human handoff.

### 5E. Cognitive Routing
- Google API docs → `google-developer-knowledge` MCP (NOT `search_web`)
- Firebase deploy → `firebase-mcp-server` MCP (NOT terminal)
- Screenshots → `chrome-devtools-mcp` MCP (NOT external tools)
- Design tokens → `StitchMCP` (NOT hand-coded from memory)
- Architecture reasoning → `sequential-thinking` MCP (NOT ad-hoc lists)

### 5F. Dual-Plane Separation (V26 Symbiotic Architecture)
- **Anti-Duplication Law:** If Antigravity provides a tool natively (Plane 1), it MUST NOT exist in `cline_mcp_settings.json` (Plane 2). Duplication causes tool-choice paralysis — the AI burns tokens deliberating between identical tool namespaces.
- **Purged from Cline (7 servers):** `firebase-hippocampus`, `browser-sensorium`, `stitch-ui-gen`, `stitch-mcp-server`, `vertex-omniscience`, `archon-reasoning`, `cloud-run` — all subsumed by Antigravity Plane 1.
- **Plane Integrity:** Run `0C. Plane Integrity Validator` on boot. Any collision = immediate removal from Cline config.
- **Adding new servers:** Before adding ANY MCP server, check BOTH `antigravity-mcp-config.json` (Plane 1) and `cline_mcp_settings.json` (Plane 2). If the capability exists in either, the addition is DENIED.
- **Constitutional reference:** `docs/SYSTEM_OVERRIDE.md`

---

## 6. PRODUCTION SERVICES

### 6A. CounselConduit
- **URL:** `https://counselconduit-767252945109.us-central1.run.app`
- **Architecture:** "Shopify for Legal AI" — privilege-preserving LLM routing for law firms
- **Queue broker:** Google Cloud Tasks exclusively (BullMQ BANNED)

### 6B. Stripe (Live)
| Item | Value |
|------|-------|
| Account | `acct_1Syh9JEHnWpykeMi` |
| Pro Monthly | `price_1TNKSREHnWpykeMiRMDlVgLl` ($149/mo) |
| Pro Annual | `price_1TNKSjEHnWpykeMi0S9GCVjy` ($1,428/yr) |
| Enterprise | `price_1TNKSREHnWpykeMi8mrDf4rI` ($20K/mo) |
| Beta Coupon | `3wseBY7Z` (50% off, 3 months, max 100) |
| Webhook | `we_1TNKSjEHnWpykeMiQZqmpy3X` → counselconduit-api |

### 6C. HeadFade
- **URL:** `https://headfade.web.app/`
- **Theme:** Forensic Cyan (legacy violet fully purged)

---

## 7. DAEMON FLEET

| Daemon | Script | Schedule | Purpose |
|--------|--------|----------|---------|
| KAIROS | `scripts/kairos_daemon.py` | Background | Proactive suggestion engine, context assembly |
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly | KI maintenance (orient → gather → consolidate → prune) |
| Loop Steward | `scripts/loop_steward.py` | 5-min cycles | Autonomous task continuation with idle scaling |
| pnkln-evolve | `scripts/pnkln_evolve.py` | Background | Recursive self-improvement loop |
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Daily 3-5AM | Secure lint+push via GitHub App tokens |

**Daemon check:** `pgrep -af "kairos\|dream_cons\|loop_stew" || echo "No daemons running"`

---

## 8. SECURITY GATES

### 8A. Pre-Push Pipeline (5-Gate)
1. **Bloat gate** — No files >1MB without exemption
2. **Secret gate** — Betterleaks + detect-private-key scan
3. **Oracle gate** — No hardcoded API keys
4. **Annotation gate** — All public functions documented
5. **Contract gate** — AGENTS.md version match

### 8B. Immutable Infrastructure (RULE 00)
- No `rm`, `unlink`, or destructive `>` on existing files without explicit human authorization.
- Archive-only deactivation pattern.

### 8C. Epistemic Airgap
- NEVER pass proprietary identifiers into public search tools.
- Corporate code ALWAYS wins over public patterns.

---

## 9. OPERATIONAL PATTERNS (TACSOP)

| # | Pattern | Trigger |
|---|---------|---------|
| 1 | Asynchronous Cascade Execution | 5+ sequential steps → `[STEP N/M]` markers |
| 2 | Execution Ledger Checkpoint | >10 checkpoints → numbered CP-IDs |
| 3 | Temporal-Reversal on Lint Failure | Introduced lint error → `git checkout -- <file>` |
| 4 | Universal AST Evaluator | Multi-language tests → unified pass/fail table |
| 5 | Autoresearch Mutation Fitness | Dead code cleanup → bench_ms before/after |
| 6 | 8-Agent Board Synthesis | STATE B decisions → 8 role perspectives |

---

## 10. NAG PROTOCOL

End every response with **5–22** explicitly selectable actionable prompts, scaled to task complexity:

| Task Phase | Prompt Count |
|-----------|--------------|
| Simple follow-up | 5–8 |
| Active implementation | 8–14 |
| Architecture decision | 14–18 |
| Session start / full audit | 18–22 |

**Forbidden fillers:** `f1 gca`, "Want me to show you?", "Should I proceed?", "Shall I continue?", restating the previous action, generic filler.

---

## 11. SKILL FLEET

- **Total:** 247 active (54 workspace + 210 global − 17 overlap)
- **External repos:** `external_repos/google-skills/`, `external_repos/vercel-skills/`
- **Pre-task protocol:** Check `.agents/skills/` → fire `omni-skill-hunter` if no match → report

---

## 12. QUICK REFERENCE COMMANDS

```bash
# Zombie cleanup
find /Users/pikeymickey/.gemini -name "*.lock" -mmin +5 -delete 2>/dev/null
find /Users/pikeymickey/.gemini -name "index.lock" -type f -delete 2>/dev/null
pkill -f "git.*credential" 2>/dev/null
pkill -f "gh auth" 2>/dev/null

# Runtime check
python3 --version && node --version && /usr/local/share/dotnet/dotnet --version && bun --version

# Sovereign sync
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
git remote -v  # Must show shadowtagai-monorepo-v2 ONLY
git fetch origin && git status

# Auth push
python3 scripts/auth_github_app.py --push

# Daemon status
pgrep -af "kairos\|dream_cons\|loop_stew"

# Lint sweep
ruff check --fix . && ruff format .

# Plane integrity check (V26 anti-drift)
PLANE1_TOOLS="StitchMCP chrome-devtools-mcp cloudrun firebase-mcp-server google-developer-knowledge sequential-thinking"
CLINE_CFG="$HOME/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
if [ -f "$CLINE_CFG" ]; then
  for srv in $PLANE1_TOOLS; do
    grep -qi "$srv" "$CLINE_CFG" 2>/dev/null && echo "❌ DRIFT: $srv in both planes"
  done
fi

# .NET 11 build
/usr/local/share/dotnet/dotnet build apps/aiyou_stack/aiyou-fastapi-services/apps/aiyou-kernel/AiYou.Kernel.csproj

# Dead code audit
bash scripts/dead-code-audit.sh
```

---

## 13. THREAD LIFECYCLE

### Start of Thread
1. Execute Section 0A (kill zombies + stale locks)
2. Execute Section 0B (probe Plane 1 servers — report status table)
3. Execute Section 0C (Plane Integrity Validator — check for drift)
4. Confirm repo coordinates (`git remote -v`)
5. Acknowledge session invariants from Section 5

### End of Thread (`f1 gca`)
1. Kill all zombies
2. Save all open editor tabs
3. Scan every dirty file from `git status` — check for conflict markers, lint, syntax
4. Fix all issues found
5. Stage → commit (conventional commit format) → push via `auth_github_app.py --push`
6. Update KIs if warranted (`scripts/dream_consolidation.py`)

---

> **To: Antigravity Core Engine**
> Persist all above as active session invariants.
> Execute Section 0 immediately and report the MCP fleet status table.
> Then await operator instructions.
