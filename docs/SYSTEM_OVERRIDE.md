# SYSTEM OVERRIDE: OMNI-BOOT INITIALIZATION (V27 — SOVEREIGN MERIDIAN)

**To: Antigravity Core Engine**

Persist operator-invariants and all other memory features as active session invariants. Mirror them internally, verbatim, before any repo-wide action until I explicitly say "MEMORY UNLOCK."

You are booting into a new session with an empty conversational context window. Do not hallucinate our project state. Execute the Pre-Action Memory Gate, verify the 10-server Antigravity MCP fleet, and confirm auth posture before any code changes.

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
* Read `docs/SYSTEM_OVERRIDE.md` — verify V27 Sovereign Meridian state (last committed override).

**Auth Invariant Confirmation:**
* The GitHub App push script is configured with App ID `3018200`, Client ID `Iv23ctYqrxPQIt2ir8gY`. The PEM file lives at `/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem` as part of the 5-tier fallback chain.
* When requested to push changes to origin: `python scripts/auth_github_app.py --push`. No other push method is authorized for the primary remote.
* When requested to push changes to v2: `GIT_LFS_SKIP_PUSH=1 git push v2 main:main --force --no-verify` via SSH deploy key. For full-history pushes exceeding 2GB, use the commit-tree graft pattern.
* `auth_github_app.py` extended flags: `--push`, `--push-ref BRANCH`, `--renew-token`, `--remote NAME`, `--branch NAME`, `--force`, `--refresh`.

**Dynamic Retrieval Doctrine:**
* Context limits exclude most of the 92 workspace skills in `.agents/skills/`. You MUST use terminal to `cat` skills before executing complex workflows. Never guess a skill's contents.

---

## 2. CANONICAL TRUTH HIERARCHY & MCP FLEET ONLINE

### Truth Surface (7 sources, 1 version each)

| Document | Role | Current Version |
|----------|------|-----------------|
| `AGENTS.md` | Canonical contract | v11.2 LOCKED |
| `monorepo_manifest.yaml` | Workspace truth | v23.0 (Milestone 16) |
| `SYSTEM_OVERRIDE.md` | Operational state | V27 Sovereign Meridian |
| `antigravity-mcp-config.json` | MCP truth (Antigravity) | 10 platform-managed servers |
| `cline_mcp_settings.json` | MCP truth (Cline) | Deprecated (empty) |
| `BUSINESS_CONTEXT_LOCKED.md` | Pricing & architecture | — |
| `RISK_REGISTER.md` | Operational risk | — |
| `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` | Non-destruction law | ACTIVE |

### MCP Fleet — Antigravity Platform-Managed (10 servers)

| # | Server | Tools | Domain |
|---|--------|-------|--------|
| 1 | `firebase-mcp-server` | 45 | Auth, Firestore, Hosting, Functions, Storage, Config, Messaging |
| 2 | `chrome-devtools-mcp` | 29 | Browser automation, screenshots, DOM inspection, Lighthouse, perf traces |
| 3 | `StitchMCP` | 12 | Design systems, screen generation, UI variants |
| 4 | `google-developer-knowledge` | 3 | Google developer docs search, retrieval, grounded answers |
| 5 | `sequential-thinking` | 1 | Multi-step reasoning, hypothesis verification |
| 6 | `jules-mcp-server` | — | Asynchronous cloud agent delegation |
| 7 | `gcloud` | — | GCP CLI operations |
| 8 | `observability` | — | Cloud Monitoring, Logging |
| 9 | `cloud-run` | — | Service deployment, revisions, traffic splitting |
| 10 | `storage` | — | Cloud Storage operations |

> [!NOTE]
> **Cline MCP servers (Tier 2)** — `cline_mcp_settings.json` is currently empty/deprecated. Servers previously listed (bigquery, dart-language-server, database-insights, gemini-memory, genkit, google-cloud-spanner, google-drive-api, notebooklm-mcp, playwright, pomelli-swarm, semantic-scalpel, spanner-toolbox, stripe-governor) are available but not active in the current configuration. Five former Cline servers (jules, gcloud, observability, cloud-run, storage) have been promoted to Tier 1 Antigravity.

**Pre-Flight Check (run at session start — 5 core servers):**
1. `list_pages` → chrome-devtools-mcp UP
2. `firebase_get_environment` → firebase-mcp-server UP
3. `list_projects` → StitchMCP UP
4. `search_documents` → google-developer-knowledge UP
5. `sequentialthinking` → sequential-thinking UP

**Extended health checks (remaining 5 servers verified by config presence):**
6. jules-mcp-server — verified in `antigravity-mcp-config.json`
7. gcloud — verified in `antigravity-mcp-config.json`
8. observability — verified in `antigravity-mcp-config.json`
9. cloud-run — verified in `antigravity-mcp-config.json`
10. storage — verified in `antigravity-mcp-config.json`

> [!CAUTION]
> **Phantom MCPs that DO NOT EXIST (never reference these):**
> - ~~Google Design MCP (`wss://design.googleapis.com/mcp`)~~ — fabricated
> - ~~Stitch Fleet MCP~~ — Stitch is a single server, not a fleet
> - ~~Jules Fleet MCP~~ — Jules fleet orchestration is via `jules-mcp-server`, not a separate server in Antigravity

---

## 3. AUTH POSTURE (THREE-LAYER ARCHITECTURE + DUAL-REMOTE)

**Silent read-only verification (run these, do NOT attempt login):**

```bash
gcloud auth print-access-token >/dev/null 2>&1 && echo "GCLOUD_USER: YES" || echo "GCLOUD_USER: NO"
gcloud auth application-default print-access-token >/dev/null 2>&1 && echo "GCLOUD_ADC: YES" || echo "GCLOUD_ADC: NO"
gcloud config get-value project 2>/dev/null | grep -q "shadowtag-omega-v4" && echo "GCLOUD_PROJECT: YES" || echo "GCLOUD_PROJECT: NO"
CI=true firebase login:list 2>/dev/null | grep -q "@" && echo "FIREBASE_CLI: YES" || echo "FIREBASE_CLI: NO"
ssh -T git@github-v2 2>&1 | grep -q "successfully" && echo "SSH_V2_KEY: YES" || echo "SSH_V2_KEY: NO"
```

| Layer | Purpose | Auth Method |
|-------|---------|-------------|
| Firebase CLI (Layer 1) | `firebase deploy`, hosting | OAuth2 refresh token in `~/.config/configstore/firebase-tools.json` |
| Firebase MCP (Layer 2) | MCP tool calls, Resources | In-memory OAuth2 via `firebase_login` MCP tool |
| GCP ADC (Layer 3) | Secret Manager, Cloud Run, Vertex | `~/.config/gcloud/application_default_credentials.json` |
| GitHub (origin) | Push/pull, API ops | HTTPS + App PEM JWT via `scripts/auth_github_app.py` |
| GitHub (v2) | Mirror push | SSH deploy key via `~/.ssh/v2_deploy_key` (`Host github-v2`) |

### Dual-Remote Transport Architecture (V26 NEW)

```
origin: git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git
  ├─ fetch: SSH
  ├─ push: HTTPS + ephemeral GitHub App JWT (60s TTL)
  └─ 2,160 commits, full history

v2: git@github-v2:ShadowTag-v2/shadowtagai-monorepo-v2.git
  ├─ fetch: SSH deploy key (ed25519)
  ├─ push: SSH deploy key (write access, ID 151018497)
  └─ Grafted tree (no full history — 2GB pack limit)
```

**SSH Config:**
```
~/.ssh/config:
  Host github-v2
    HostName github.com
    User git
    IdentityFile ~/.ssh/v2_deploy_key
    IdentitiesOnly yes
```

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

### Test Infrastructure (V26 — Four-Runner Architecture)

| Runner | Scope | Command | Status |
|--------|-------|---------|--------|
| **pytest** | Python unit + integration | `PYTHONPATH=. python3 -m pytest tests/ -x -q` | **3,306 passed** (28 skipped) ✅ |
| **Vitest** | JS/TS unit + integration + property-based | `npx vitest run` | **221/221** ✅ |
| **Playwright** | E2E browser specs | `npx playwright test` | 19 test files configured |
| **Bun** | Bun-native specs (`bun:test`) | `bun test` | Configured |

**Vitest exclusions** (in `vitest.config.ts`): `tests/e2e/**`, `tests/playwright/**`, `**/bun:test` files are delegated to their native runners. This prevents cross-runner parse errors.

### .NET Build Verification (V26 NEW)

| Component | Target | SDK | Packages | Status |
|-----------|--------|-----|----------|--------|
| `AiYou.Kernel` | `net11.0` | 11.0.100-preview.3.26207.106 | SK 1.74.0, Process.Core 1.21.0-alpha | **0 warnings, 0 errors** ✅ |

**Core Technical Truth #3:** `OnExternalEvent` is the CORRECT API for SK Process.Core v1.21.0-alpha. Do NOT rename to `OnInputEvent` until Process.Core ≥ v1.30+.

### Pomelli Swarm CI

`.github/workflows/pomelli-swarm.yml` — Automated fleet Lighthouse audits across HeadFade, CounselConduit, KovelAI. Runs Mon+Thu on schedule and via `workflow_dispatch`.

### Two-Lane Upload Doctrine (V26 NEW)

```
Lane 1 (Git): Source code, configs, docs → HTTPS push via auth_github_app.py (origin)
                                         → SSH push via deploy key (v2)
Lane 2 (GCS): Binaries, models, large artifacts → gs://shadowtag-artifacts/

Enforced by:
  - tool_contracts/github.push.yaml (preflight gate)
  - artifacts/manifest.yaml (GCS registry)
  - operator_invariants.json (13 invariants, v5.0)
```

### Local Inference Pipeline (V26 NEW)

```yaml
# configs/harbor-gemma.yaml
Harbor + Gemma-4-31B-it → llama.cpp Q4_K_M quantization → OpenAI-compatible :8080
ANE Bridge (dylib) → Apple Silicon Neural Engine acceleration
```

### Dependency Governance (V26 NEW)

```json
// renovate.json → Automated dependency updates
// .github/workflows/jules-pr-review.yml → Jules swarm auto-reviews PRs
// peter-murray/workflow-application-token-action@v3 → Short-lived JWT for CI
```

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

## 7. MONOREPO CENSUS (V27)

| Category | Count |
|----------|-------|
| Packages (package.json files) | 2,829 |
| Workspace Skills | 92 |
| Global Skills | 295 |
| External Repos | 29 |
| Firebase Hosting Targets | 4 |
| Antigravity MCP Servers | 10 |
| Cline MCP Servers | 0 (deprecated) |
| **Total MCP Servers** | **10** |
| CI Workflows (active `.yml`) | 73 |
| Merge Commits on `main` | 107 |
| Total Commits on `main` | 2,160 |
| Pytest Suite | **3,306 passed** (28 skipped) |
| Vitest Suite | **221/221 PASS** |
| Playwright Test Files | 19 |
| Security Pipeline | 35-check |
| HEAD | `25b1e7c39` |
| Manifest | v23.0 — Milestone 16 |
| Branch State | `main` + 3 local + 8 remote stale |
| Remotes | 2 (origin + v2) |

### Runtime Versions (V26 Pinned)

| Runtime | Version | Source |
|---------|---------|--------|
| CPython | 3.14.4 | Homebrew |
| Node.js | v26.0.0 | Homebrew |
| .NET SDK | 11.0.100-preview.3.26207.106 | `/usr/local/share/dotnet/dotnet` |
| uv | 0.11.12 | Homebrew |
| Bun | 1.3.11 | Homebrew |
| Semantic Kernel | 1.74.0 | NuGet |
| SK Process.Core | 1.21.0-alpha | NuGet |

---

## 8. EXECUTION COMMAND

1. **Run the Pre-Action Memory Gate** — physically execute `git log -n 5`, read `AGENTS.md`, `monorepo_manifest.yaml`, `RULE_00`, and `SYSTEM_OVERRIDE.md`.
2. **Run the 5-server MCP pre-flight** — one tool call per core Antigravity server. Verify remaining 5 via config presence.
3. **Run the auth verification** — the 5-line bash block from §3. Report YES/NO for each (including SSH_V2_KEY).
4. **Run repo_doctor** — `python3 scripts/repo_doctor.py`. Report grade.
5. **Report the status table** to the user with: MCP fleet (10/10 or N/10 Antigravity), auth posture (5 YES/NO), repo grade, HEAD commit, manifest version, SYSTEM_OVERRIDE version.

**Do NOT ask me to run any commands. Do NOT attempt login flows. Execute silently and report.**

---

> [!IMPORTANT]
> **Revision Log (V15 → V26)**
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
> - V26 (25b1e7c39): **Sovereign Meridian** — Dual-remote transport (origin + v2 SSH), .NET 11 upgrade, 3,296 pytest + 221 vitest, CPython 3.14.4/Node v26/uv 0.11.12, Two-Lane Upload Doctrine, Harbor + Gemma-4-31B local inference, Renovate + Jules dependency governance, auth_github_app.py extended flags, commit-tree graft for 2GB pack limit
> - V27 (25b1e7c39): **Sovereign Meridian Patch** — MCP fleet promotion (5→10 Antigravity servers), Cline config deprecated, pytest 3,306 passed, branch state corrected (not Branch Zero), skills census reconciled (92 ws / 295 global), external repos 29, Bun 1.3.11 pinned, package count corrected to 2,829
>
> **Key V27 changes from V26:**
> - Promoted 5 Cline MCP servers to Antigravity Tier 1: jules-mcp-server, gcloud, observability, cloud-run, storage (§2)
> - Deprecated Cline MCP config (`cline_mcp_settings.json` is empty) (§2)
> - Updated MCP fleet from 5+19 split to unified 10 Antigravity servers (§2)
> - Added extended health check documentation for servers 6-10 (§2)
> - Updated pytest count from 3,296 → 3,306 passed (28 skipped) (§5, §7)
> - Corrected branch state: not "Branch Zero" — 3 local + 8 remote stale branches exist (§7)
> - Corrected package count from 850 → 2,829 (full workspace `find` scan) (§7)
> - Corrected workspace skills 93 → 92, global skills 298 → 295 (§1, §7)
> - Corrected external repos 22 → 29 (§7)
> - Pinned Bun version from "latest" → 1.3.11 (§7)
> - Preserved all V26 invariants: dual-remote transport, .NET 11, Two-Lane Upload, Harbor+Gemma, RULE_00, secrets doctrine, TACSOP 7, prompt repetition, headless CLI, port-killer, 35-check security pipeline, Firebase dynamic import pattern, phantom MCP warnings
