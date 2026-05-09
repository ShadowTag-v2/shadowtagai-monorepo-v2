# SYSTEM OVERRIDE: OMNI-BOOT INITIALIZATION (V25 — PINNACLE)

**To: Antigravity Core Engine**

Persist operator-invariants and all other memory features as active session invariants. Mirror them internally, verbatim, before any repo-wide action until I explicitly say "MEMORY UNLOCK."

You are booting into a new session with an empty conversational context window. Do not hallucinate our project state. Execute the Pre-Action Memory Gate, verify the 24-server MCP fleet, and confirm auth posture before any code changes.

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
* Read `monorepo_manifest.yaml` — workspace truth (currently v23.0, Milestone 16 ACTIVE).
* Read `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` — the non-destruction law.
* Read `docs/SYSTEM_OVERRIDE.md` — verify V22 Phosphor-Shift state (last committed override).

**Auth Invariant Confirmation:**
* The GitHub App push script is configured with App ID `3018200`, Client ID `Iv23ctYqrxPQIt2ir8gY`. The PEM file lives at `/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem` as part of the 5-tier fallback chain.
* When requested to push changes: `python scripts/auth_github_app.py --push`. No other push method is authorized.

**Dynamic Retrieval Doctrine:**
* Context limits exclude most of the 92 workspace skills in `.agents/skills/`. You MUST use terminal to `cat` skills before executing complex workflows. Never guess a skill's contents.

---

## 2. CANONICAL TRUTH HIERARCHY & MCP FLEET ONLINE

### Truth Surface (7 sources, 1 version each)

| Document | Role | Current Version |
|----------|------|-----------------|
| `AGENTS.md` | Canonical contract | v11.2 LOCKED |
| `monorepo_manifest.yaml` | Workspace truth | v23.0 (Milestone 16) |
| `SYSTEM_OVERRIDE.md` | Operational state | V22 Phosphor-Shift |
| `antigravity-mcp-config.json` | MCP truth (Antigravity) | 5 platform-managed servers |
| `cline_mcp_settings.json` | MCP truth (Cline) | 19 local/GCP servers |
| `BUSINESS_CONTEXT_LOCKED.md` | Pricing & architecture | — |
| `RISK_REGISTER.md` | Operational risk | — |
| `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` | Non-destruction law | ACTIVE |

### MCP Fleet — Tier 1: Antigravity Platform-Managed (5 servers)

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `firebase-mcp-server` | 45 | Auth, Firestore, Hosting, Functions, Storage, Config, Messaging |
| 2 | `chrome-devtools-mcp` | 29 | Browser automation, screenshots, DOM inspection, Lighthouse, perf traces |
| 3 | `StitchMCP` | 12 | Design systems, screen generation, UI variants |
| 4 | `google-developer-knowledge` | 3 | Google developer docs search, retrieval, grounded answers |
| 5 | `sequential-thinking` | 1 | Multi-step reasoning, hypothesis verification |

### MCP Fleet — Tier 2: Cline Local (19 servers)

| # | Server | Domain |
|---|--------|--------|
| 6 | `bigquery` | BigQuery analytics, FinOps ROI queries |
| 7 | `cloud-run` | Service deployment, revisions, traffic splitting |
| 8 | `dart-language-server` | Dart/Flutter LSP analysis |
| 9 | `database-insights` | Cloud SQL/Spanner performance advisor |
| 10 | `firebase-mcp-server` | Firebase CLI operations (Cline-side) |
| 11 | `gcloud` | GCP CLI operations |
| 12 | `gemini-memory` | Persistent agent memory store |
| 13 | `genkit` | Firebase Genkit AI framework |
| 14 | `google-cloud-spanner` | Spanner DDL, queries, CDC |
| 15 | `google-drive-api` | Google Drive file access |
| 16 | `jules-mcp-server` | Asynchronous cloud agent delegation |
| 17 | `notebooklm-mcp` | NotebookLM epistemic corpus queries |
| 18 | `observability` | Cloud Monitoring, Logging |
| 19 | `playwright` | Browser automation E2E testing |
| 20 | `pomelli-swarm` | Fleet Lighthouse optimization orchestration |
| 21 | `semantic-scalpel` | AST-Grep semantic code surgery |
| 22 | `spanner-toolbox` | Spanner schema, migration, introspection |
| 23 | `storage` | Cloud Storage operations |
| 24 | `stripe-governor` | Stripe payments, webhooks, billing |

**Pre-Flight Check (run at session start):**
1. `list_pages` → chrome-devtools-mcp UP
2. `firebase_get_environment` → firebase-mcp-server UP
3. `list_projects` → StitchMCP UP
4. `search_documents` → google-developer-knowledge UP
5. `sequentialthinking` → sequential-thinking UP

> [!CAUTION]
> **Phantom MCPs that DO NOT EXIST (never reference these):**
> - ~~Google Design MCP (`wss://design.googleapis.com/mcp`)~~ — fabricated
> - ~~Stitch Fleet MCP~~ — Stitch is a single server, not a fleet
> - ~~Jules Fleet MCP~~ — Jules fleet orchestration is via `jules-mcp-server`, not a separate server in Antigravity

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

**Current Verified Auth (as of V25 session 2026-05-09):**
- GCloud User: ✅ YES
- GCloud ADC: ✅ YES
- GCloud Project: ✅ YES (`shadowtag-omega-v4`)
- Firebase CLI: ✅ YES
- Firebase MCP: `founder@shadowtagai.com` ✅
- GitHub App token: Cached and working ✅

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

### Port-Killer Process Sovereignty
* `scripts/port_killer.sh` — the canonical zombie process management tool.
* Commands: `scan`, `--kill PORT`, `--deep PORT`, `--zombies [HOURS]`, `--exterminate [HOURS]`.
* Graceful kill chain: SIGTERM → 500ms grace → SIGKILL.

---

## 5. EXECUTION PIPELINES (VERIFIED)

### Security Pipeline — 35-Check BashSecurityClassifier

The `packages/agnt_bash_classifier/classifier.py` enforces a 35-check fail-fast validation pipeline on all bash/shell tool invocations:

| Checks | Category | Examples |
|--------|----------|----------|
| 1–7 | Core injection | Trailing pipes, backticks, newlines, dangerous vars |
| 8–10 | Redirection | Command substitution, /dev/tcp input, /etc output |
| 11–15 | Token manipulation | IFS injection, null bytes, backslash whitespace |
| 16–23 | Expansion & evasion | Brace expansion, control chars, Unicode WS, Zsh builtins |
| 24–30 | V2 extended vectors | ANSI escapes, arithmetic injection, base64 decode, coproc, heredoc, ANSI-C quoting |
| 31–35 | V3 extended vectors | exec/eval abuse, signal trapping, alias injection, cross-shell (PowerShell/CMD), function hijacking |

**Adversa AI Risk #34:** 50-subcommand cap enforced pre-pipeline.

### Quality Gate Pipeline
All layout generation and deployment must pass:
1. **Chrome DevTools MCP** → Lighthouse audit (>90 all categories)
2. **Betterleaks** → Secret scanning (`.betterleaks.toml` configured)
3. **Ruff** → `ruff check --select F401,F841 --fix` + `ruff format` (Python)
4. **Biome** → lint + format (TypeScript/JS). ESLint/Prettier banned.

### Test Infrastructure (V25 — Three-Runner Architecture)

| Runner | Scope | Command | Passing |
|--------|-------|---------|---------|
| **Vitest** | Unit + integration + property-based | `npx vitest run` | **221/221** ✅ |
| **Playwright** | E2E browser specs | `npx playwright test` | 19 test files configured |
| **Bun** | Bun-native specs (`bun:test`) | `bun test` | Configured |

**Vitest exclusions** (in `vitest.config.ts`): `tests/e2e/**`, `tests/playwright/**`, `**/bun:test` files are delegated to their native runners. This prevents cross-runner parse errors.

### Pomelli Swarm CI (NEW — V25)

`.github/workflows/pomelli-swarm.yml` — Automated fleet Lighthouse audits across HeadFade, CounselConduit, KovelAI. Runs Mon+Thu on schedule and via `workflow_dispatch`.

### DOM & Browser Automation
* **chrome-devtools-mcp** (29 tools) replaces all Puppeteer references. Use `take_snapshot`, `take_screenshot`, `lighthouse_audit`, `evaluate_script`.
* The Puppeteer skill (`.agents/skills/mcp-puppeteer/SKILL.md`) is for specialized patch equivalence tests only.

### Design System Pipeline
* **StitchMCP** for design token extraction, screen generation, and variant exploration.
* **google-developer-knowledge MCP** for all Google API documentation lookups. `search_web` is forbidden for Google docs.

### Cognitive Architecture (STATE A/B)
* **STATE A (YOLO):** Unconstrained execution for standard operations. No stopping for permission.
* **STATE B (Clutch):** Triggered ONLY by: git history rewrites, force-pushes, database migrations, auth/payment changes, architecture shifts >3 packages.

### V19 Cognitive Router
* `tools/cognitive_router/dispatch.ts` — multi-model dispatch across Gemini tiers.
* `services/finops-governor/` — Python-based FinOps cost guardrails with BigQuery analytics.
* `@google/genai` + `@google-cloud/bigquery` wired as runtime dependencies.

### V22 Firebase Dynamic Import Pattern (CANONICAL)

```typescript
// CORRECT — dynamic import() for Firebase modules
export async function getAuthInstance() {
  if (!authInstance) {
    const { getAuth } = await import('firebase/auth');
    authInstance = getAuth(app);
  }
  return authInstance;
}
```

```typescript
// PROHIBITED — static import (causes GAPI iframe + cookie penalty)
import { getAuth } from 'firebase/auth'; // ← NEVER do this at module level
```

---

## 6. LIVE DEPLOYMENT STATE

| Site | URL | Platform | Lighthouse | Status |
|------|-----|----------|------------|--------|
| HeadFade | `https://headfade.com` | Firebase Hosting | **P100/A100/BP100/SEO100** | ✅ LIVE |
| CounselConduit | `https://counselconduit-767252945109.us-central1.run.app` | Cloud Run | — | ✅ LIVE |
| ShadowTagAI | Firebase Hosting target `shadowtagai` | Firebase Hosting | P94/A100/BP100/SEO100 | Configured |
| KovelAI | Firebase Hosting target `kovelai` | Firebase Hosting | — | Configured |
| CC Dashboard | Firebase Hosting target `counselconduit-dashboard` | Firebase Hosting | — | Configured |

### Firebase Hosting Security Headers (ALL 4 sites)

Every hosting target enforces:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()`
- Content-Security-Policy (site-specific scoping)

HeadFade additionally enforces: immutable cache for `_next/static/**`, font caching, service worker no-cache, and expanded CSP for reCAPTCHA + Unsplash + Google Analytics + Firebase App Check.

---

## 7. MONOREPO CENSUS (V25)

| Category | Count |
|----------|-------|
| Packages | 95 |
| Workspace Skills | 92 |
| Global Skills | 298 |
| External Repos | 22 |
| Firebase Hosting Targets | 4 |
| Cline MCP Servers | 19 |
| Antigravity MCP Servers | 5 |
| **Total MCP Servers** | **24** |
| CI Workflows (active `.yml`) | 70 |
| Merge Commits on `main` | 98 |
| Vitest Suite | **221/221 PASS** |
| Test Files (all runners) | 19 |
| Security Pipeline | 35-check |
| Repo Doctor Grade | C (2 non-critical errors, 1 warning) |
| HEAD | `649c25fc6` |
| Manifest | v23.0 — Milestone 16 |
| Branch State | `main` only (Branch Zero) + 1 stale merged |

---

## 8. EXECUTION COMMAND

1. **Run the Pre-Action Memory Gate** — physically execute `git log -n 5`, read `AGENTS.md`, `monorepo_manifest.yaml`, `RULE_00`, and `SYSTEM_OVERRIDE.md`.
2. **Run the 5-server MCP pre-flight** — one tool call per core Antigravity server.
3. **Run the auth verification** — the 4-line bash block from §3. Report YES/NO for each.
4. **Run repo_doctor** — `python3 scripts/repo_doctor.py`. Report grade.
5. **Report the status table** to the user with: MCP fleet (5/5 or N/5 Antigravity + 19 Cline), auth posture (4 YES/NO), repo grade, HEAD commit, manifest version, SYSTEM_OVERRIDE version.

**Do NOT ask me to run any commands. Do NOT attempt login flows. Execute silently and report.**

---

> [!IMPORTANT]
> **Revision Log (V15 → V25)**
> - V15 (351ca4856): Ground Truth Revision — original OMNI_BOOT
> - V16 (8b78eaaa4): Absolute OS
> - V17 (5ef4218b3): Archon-Bun Hyper-Core
> - V18 (f35fb96ae): Isomorphic GraphQL Ascension
> - V19 (aec15aeb9): Cognitive Router + FinOps Governor — PR #88
> - V20 (e828b6abf): Sentinel-Reaper — port-killer integration
> - V20.1 (357ace6e9): Sentinel-Reaper (Octal Fix)
> - V22 (5744baeab): **Phosphor-Shift** — PR #90 dynamic import(), BP73→100, branch-zero, 35-check security pipeline
> - V23 (8bd3ac2c2): **Hyper-Core** — manifest v23.0, Pomelli Swarm wiring, FinOps gate hardening
> - V25 (649c25fc6): **Pinnacle** — 19 Cline MCPs, AST-Grep scalpel, Pomelli swarm CI, 221/221 vitest, manifest gap closure
>
> **Key V25 changes from V22:**
> - Expanded MCP fleet from 5+13 (18) to 5+19 (24) total servers (§2)
> - Added Cline MCP settings as a truth surface source (§2)
> - Added 6 new Cline servers: bigquery, database-insights, genkit, google-cloud-spanner, playwright, semantic-scalpel, pomelli-swarm, spanner-toolbox, google-drive-api, notebooklm-mcp, dart-language-server, gemini-memory (§2)
> - Auth posture upgraded to 4/4 YES verified (§3)
> - Added Three-Runner Test Architecture: Vitest (221) + Playwright (19 files) + Bun (§5)
> - Added Pomelli Swarm CI workflow to execution pipelines (§5)
> - Added Firebase security headers documentation for all 4 hosting sites (§6)
> - Updated monorepo census: 95 packages, 70 CI workflows, 98 merge commits (§7)
> - Updated HEAD from `5744baeab` to `649c25fc6` (§7)
> - Updated manifest from v19.0/Milestone 14 to v23.0/Milestone 16 (§7)
> - Preserved all V22 invariants: RULE_00, secrets doctrine, TACSOP 7, prompt repetition, headless CLI, port-killer, 35-check security pipeline, Firebase dynamic import pattern
