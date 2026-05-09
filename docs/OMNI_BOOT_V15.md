# SYSTEM OVERRIDE: OMNI-BOOT INITIALIZATION (V15 — GROUND TRUTH REVISION)

**To: Antigravity Core Engine**

Persist operator-invariants and all other memory features as active session invariants. Mirror them internally, verbatim, before any repo-wide action until I explicitly say "MEMORY UNLOCK."

You are booting into a new session with an empty conversational context window. Do not hallucinate our project state. Execute the Pre-Action Memory Gate, verify the 10-server MCP fleet, and confirm auth posture before any code changes.

---

## 1. PRE-ACTION MEMORY GATE & PREFLIGHT AUTH (TEMPORAL ANCHOR)

**Physical Reads (execute these, don't summarize from memory):**

```bash
git log -n 5 --oneline --stat
git branch -vv --no-color
python3 scripts/repo_doctor.py
cat .beads/repo_doctor_latest.json
```

* Read `.ruler/AGENTS.md` (v11.2 LOCKED) — the canonical contract.
* Read `monorepo_manifest.yaml` — workspace truth (currently v15.5, Milestone 10 COMPLETE).
* Read `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` — the non-destruction law.

**Auth Invariant Confirmation:**
* The GitHub App push script is configured with App ID `3018200`, Client ID `Iv23ctYqrxPQIt2ir8gY`. The PEM file lives at `/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem` as part of the 5-tier fallback chain.
* When requested to push changes: `python scripts/auth_github_app.py --push`. No other push method is authorized.

**Dynamic Retrieval Doctrine:**
* Context limits exclude most of the 92 workspace skills in `.agents/skills/`. You MUST use terminal to `cat` skills before executing complex workflows. Never guess a skill's contents.

---

## 2. CANONICAL TRUTH HIERARCHY & MCP FLEET ONLINE

### Truth Surface (6 sources, 1 version each)

| Document | Role | Current Version |
|----------|------|-----------------|
| `AGENTS.md` | Canonical contract | v11.2 LOCKED |
| `monorepo_manifest.yaml` | Workspace truth | v15.5 |
| `antigravity-mcp-config.json` | MCP truth | 10 servers |
| `BUSINESS_CONTEXT_LOCKED.md` | Pricing & architecture | — |
| `RISK_REGISTER.md` | Operational risk | — |
| `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` | Non-destruction law | ACTIVE |

### MCP Fleet (10 Servers — Verify ALL)

**Core 5 (Platform-managed, always available):**

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `firebase-mcp-server` | 45 | Auth, Firestore, Hosting, Functions, Storage, Config, Messaging |
| 2 | `chrome-devtools-mcp` | 29 | Browser automation, screenshots, DOM inspection, Lighthouse, perf traces |
| 3 | `StitchMCP` | 12 | Design systems, screen generation, UI variants |
| 4 | `google-developer-knowledge` | 3 | Google developer docs search, retrieval, grounded answers |
| 5 | `sequential-thinking` | 1 | Multi-step reasoning, hypothesis verification |

**GCP 5 (Infrastructure-tier):**

| # | Server | Domain |
|---|--------|--------|
| 6 | `jules-mcp-server` | Asynchronous cloud agent delegation |
| 7 | `gcloud` | GCP CLI operations |
| 8 | `observability` | Cloud Monitoring, Logging |
| 9 | `cloud-run` | Service deployment, revisions |
| 10 | `storage` | Cloud Storage operations |

**Pre-Flight Check (run at session start):**
1. `list_pages` → chrome-devtools-mcp UP
2. `firebase_get_environment` → firebase-mcp-server UP
3. `list_projects` → StitchMCP UP
4. `search_documents` → google-developer-knowledge UP
5. `sequentialthinking` → sequential-thinking UP

> [!CAUTION]
> **Phantom MCPs that DO NOT EXIST (never reference these):**
> - ~~Google Design MCP (`wss://design.googleapis.com/mcp`)~~ — fabricated
> - ~~NotebookLM MCP~~ — `notebooklm` is a CLI tool, not an MCP server
> - ~~Cline MCP servers~~ — Cline is not used in this workspace

---

## 3. AUTH POSTURE (THREE-LAYER ARCHITECTURE)

**Silent read-only verification (run these, do NOT attempt login):**

```bash
gcloud auth print-access-token >/dev/null 2>&1 && echo "GCLOUD_USER: YES" || echo "GCLOUD_USER: NO"
gcloud auth application-default print-access-token >/dev/null 2>&1 && echo "GCLOUD_ADC: YES" || echo "GCLOUD_ADC: NO"
gcloud config get-value project 2>/dev/null | grep -q "shadowtag-omega-v4" && echo "GCLOUD_PROJECT: YES" || echo "GCLOUD_PROJECT: NO"
CI=true firebase login:list 2>/dev/null | grep -q "@" && echo "FIREBASE_CLI: YES" || echo "FIREBASE_CLI: NO"
```

| Layer | Purpose | Auth Method |
|-------|---------|-------------|
| Firebase CLI (Layer 1) | `firebase deploy`, hosting | OAuth2 refresh token in `~/.config/configstore/firebase-tools.json` |
| Firebase MCP (Layer 2) | MCP tool calls, Resources | In-memory OAuth2 via `firebase_login` MCP tool |
| GCP ADC (Layer 3) | Secret Manager, Cloud Run, Vertex | `~/.config/gcloud/application_default_credentials.json` |
| GitHub | Push/pull, API ops | SSH + App PEM JWT via `scripts/auth_github_app.py` |

**If any auth is NO:** Stop and tell the user the exact command to run in their Mac Terminal. Do NOT attempt `login` commands yourself.

---

## 4. BEHAVIORAL & SECURITY INVARIANTS

### RULE 00: Immutable Infrastructure (THE ABSOLUTE LAW)
* No `rm`, `unlink`, or destructive `>` on existing files without explicit human authorization.
* No `cat << 'EOF' >` to overwrite configuration files. Use native file-editing tools for surgical edits.
* Archive-only deactivation. Full spec: `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md`.

### Secrets Manager Doctrine
* Secrets ONLY via GCP Secret Manager for production. No `.env` files (BANNED since 2026-04-22).
* Local dev: `source scripts/load_mcp_secrets.sh`. MCP config uses `${VAR}` references.
* Never hardcode API keys. Never pass secrets to `search_web` or public tools.

### Visual Provenance (TACSOP 7)
* Native `generate_image` tool is **BANNED**. All visual assets use Stitch MCP, Veo 3.1 SDK, or semantic CSS/SVG placeholders.
* EU AI Act Article 52 compliance enforced.

### Prompt Repetition (arXiv:2512.14982)
* Applies ONLY to non-reasoning tiers (flash/lite/mini) to boost accuracy.
* Do NOT apply to thinking/reasoning models.

### Headless CLI Protocol
* Prepend `CI=true DEBIAN_FRONTEND=noninteractive` to any command that might launch a TUI.
* Never inject newlines/arrow keys into interactive prompts.
* If blocked by TUI: terminate → retry with `--non-interactive` → pexpect script → human handoff.

---

## 5. EXECUTION PIPELINES (VERIFIED)

### Quality Gate Pipeline
All layout generation and deployment must pass:
1. **Chrome DevTools MCP** → Lighthouse audit (>90 all categories)
2. **Betterleaks** → Secret scanning (`.betterleaks.toml` configured)
3. **Ruff** → `ruff check --select F401,F841 --fix` + `ruff format` (Python)
4. **Biome** → lint + format (TypeScript/JS). ESLint/Prettier banned.

### DOM & Browser Automation
* **chrome-devtools-mcp** (29 tools) replaces all Puppeteer references. Use `take_snapshot`, `take_screenshot`, `lighthouse_audit`, `evaluate_script`.
* The Puppeteer skill (`.agents/skills/mcp-puppeteer/SKILL.md`) is for specialized patch equivalence tests only.

### Design System Pipeline
* **StitchMCP** for design token extraction, screen generation, and variant exploration.
* **google-developer-knowledge MCP** for all Google API documentation lookups. `search_web` is forbidden for Google docs.

### Cognitive Architecture (STATE A/B)
* **STATE A (YOLO):** Unconstrained execution for standard operations. No stopping for permission.
* **STATE B (Clutch):** Triggered ONLY by: git history rewrites, force-pushes, database migrations, auth/payment changes, architecture shifts >3 packages.

---

## 6. EXECUTION COMMAND

1. **Run the Pre-Action Memory Gate** — physically execute `git log -n 5`, read `AGENTS.md`, `monorepo_manifest.yaml`, and `RULE_00`.
2. **Run the 5-server MCP pre-flight** — one tool call per core server.
3. **Run the auth verification** — the 4-line bash block from §3. Report YES/NO for each.
4. **Run repo_doctor** — `python3 scripts/repo_doctor.py`. Report grade.
5. **Report the status table** to the user with: MCP fleet (10/10 or N/10), auth posture (4 YES/NO), repo grade, HEAD commit, manifest version.

**Do NOT ask me to run any commands. Do NOT attempt login flows. Execute silently and report.**

---

> [!IMPORTANT]
> **Revision Log (V14 → V15)**
> - Removed phantom "Google Design MCP" — does not exist
> - Removed phantom "NotebookLM MCP" — CLI tool, not MCP server
> - Removed phantom "12 Cline MCP servers" — not used
> - Removed "JCodesMore template clone" — not a concept
> - Removed "Bandit B310" — replaced with betterleaks + ruff
> - Removed "11x Chrome Loop" — replaced with chrome-devtools-mcp (29 tools)
> - Removed "V4 Cognitive Structural Synthesis" — current version is v15.5
> - Added real 10-server MCP fleet from antigravity-mcp-config.json
> - Added Three-Layer Firebase Auth architecture
> - Added TACSOP 7 visual provenance ban
> - Added Headless CLI Protocol
> - Added RULE_00 Immutable Infrastructure reference
> - Added explicit phantom MCP warning to prevent regression
> - Aligned version numbers: AGENTS.md v11.2, Manifest v15.5, Milestone 10
