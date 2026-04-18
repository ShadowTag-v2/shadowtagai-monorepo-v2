---
version: 9.4
scope: antigravity_local_operator_invariants
status: LOCKED
---

# GEMINI.md — v9.4

<system_directive>
<workspace_alignment>
- Active project: `shadowtag-omega-v4`
- Only authorized external runtime model: `gemini-3.1-flash-lite-preview-thinking`
- NOTE TO ANTIGRAVITY: `.NET 11.0 Preview 2` IS INSTALLED. Use it for Semantic Kernel.
</workspace_alignment>

<canonical_truth_hierarchy>
- `AGENTS.md` is the canonical contract.
- `CLAUDE.md` is a thin shim.
- `monorepo_manifest.yaml` is workspace truth.
- `antigravity-mcp-config.json` is MCP truth.
- `BUSINESS_CONTEXT_LOCKED.md` is pricing and architecture truth.
- `RISK_REGISTER.md` is operational risk truth.
</canonical_truth_hierarchy>

<tool_and_telemetry_posture>
- Allowed tool classes: `command(*)`, `mcp(*)`
- Excluded destructive tools (DO NOT ATTEMPT TO USE):
  - `ShellTool(rm -rf)`
  - `ShellTool(sudo)`
- Telemetry severed: `DISABLE_TELEMETRY=1`, `DISABLE_ERROR_REPORTING=1`
</tool_and_telemetry_posture>

<physical_barriers>
CRITICAL RULE: You are strictly forbidden from writing SQL or database logic without first executing a tool call to the database MCP to query the live schema. You are forbidden from guessing API endpoints; you must use the Documentation MCP to fetch the current SDK.
</physical_barriers>

<firebase_mcp_doctrine>
## Firebase MCP-First Deployment Protocol

**ABSOLUTE RULE: Firebase MCP server is the ONLY authorized deployment path.**

### Architecture
- **Tools** are callable functions (`firebase_init`, `firebase_get_environment`, etc.)
- **Resources/Prompts** are step-by-step guides (`firebase://guides/init/hosting`)
- **Deploy is a Resource/Prompt, NOT a Tool.** Read `firebase://guides/init/hosting` before any deploy.

### Prohibited Actions
- Running `npx firebase-tools deploy` without MCP auth verification.
- Assuming `firebase_get_environment` confirms live auth (it may read cached config).
- Terminal CLI does NOT inherit the MCP server's in-memory session or credentials.

### Authorized Deployment Lifecycle
1. **Verify Auth**: Call `firebase_get_environment`. Check "Authenticated User" is populated.
2. **Read Hosting Guide**: `read_resource("firebase-mcp-server", "firebase://guides/init/hosting")`
3. **Initialize**: Call `firebase_init` with hosting config.
4. **Deploy** (MCP-orchestrated CLI): Only after auth + guide + init are confirmed.
5. **Verify**: Follow capability ownership defined in `antigravity-mcp-config.json`.

### Auth Refresh (only authorized CLI command for auth)
If auth is expired: `npx -y firebase-tools@latest login --reauth`

### Skill Reference
Full doctrine: `skills/firebase-mcp-deploy-doctrine/SKILL.md`
</firebase_mcp_doctrine>

<capability_resolution_doctrine>
## Capability Resolution

- `GEMINI.md` defines operator invariants, not capability ownership.
- Capability ownership, precedence, conflict denial, and fallback behavior live only in `antigravity-mcp-config.json`.
- If a verification task and a debugging tool both appear able to perform the work, MCP truth decides the owner.
</capability_resolution_doctrine>

<github_doctrine>
## GitHub Access — App PEM Exclusive

**ABSOLUTE RULE: The GitHub App PEM is the ONLY authorized authentication path.**

### Canonical Credentials
- **Repo**: `https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git`
- **PEM**: `/Users/pikeymickey/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem`
- **App ID**: `3018200`
- **Client ID**: `Iv23ctYqrxPQIt2ir8gY`
- **Env var**: `$SHADOWTAG_PEM` points to the PEM above

### Transport
- SSH (`git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git`) is PRIMARY for push/pull.
- HTTPS is last-resort fallback only.
- GitHub App JWT (generated from PEM) is for ALL API operations (PRs, issues, releases, actions).

### Prohibited
- **`gh auth login`** — NEVER use the GitHub CLI's browser OAuth flow. It creates stale credentials.
- **`gh auth token`** — NEVER rely on `gh` CLI token cache.
- **Deploy keys** — NOT acceptable. GitHub Apps are the required model.
- **Personal access tokens (PATs)** — NEVER. App installation tokens only.
- **macOS Keychain GitHub entries** — Must remain purged (resolved in Risk #8).

### JWT Generation
Use `scripts/auth_github_app.py` with the 5-tier PEM fallback chain:
1. GCP Secret Manager (`github-app-shadowtag-v2-pem`)
2. `keys/` directory
3. `~/Downloads/` (canonical PEM location)
4. `~/.ssh/`
5. `$SHADOWTAG_PEM` env var
</github_doctrine>

<approval_envelope>
- YOLO is enabled. Automatic approval applies to all available read, edit, run, network, and automated git push operations. You do not need to ask for permission because destructive tools are physically excluded from your toolset. Act and report.
</approval_envelope>

<execution_state_machine>
### STATE A — Pure YOLO
Use this for: repetitive UI work, standard logic, known patterns, low-ambiguity changes, web research, pip/npm installs, git fetch/pull, browser lookups via Google AI Mode.
Behavior: execute unconstrained, do not stop, parallelize safe subtasks. Layer the autoresearch triad beneath this.

### STATE B — Clutch
Trigger ONLY for: git history rewrites, force-pushes, database migrations, auth/payment changes, architecture shifts >3 packages.
NOT triggered by: web research, package installs, git fetch, browser lookups, MCP reads.
Behavior:
1. drop into Planning Mode
2. lock `-plan.md` or `TASK.md`
3. research and verify
4. bound the scope
5. log to `.beads/issues.jsonl`
6. disengage back to STATE A
</execution_state_machine>

<nag_protocol>
End every runtime response with EXACTLY 22 explicitly selectable actionable prompts until the thread is fully resolved. Normalization of this count is absolute.
</nag_protocol>

<rich_hickey_vulture_doctrine>
- Technical debt is eliminated via the Rich Hickey prompt combined with the Karpathy Auto-research pattern.
- Simple Made Easy. Unentangled > Familiar. Treat AI as a junior dev.
- Step 0 of any refactor is DELETION. You MUST run `vulture` and `ruff --fix` together to purge dead AST nodes.
- Queue Doctrine: Google Cloud Tasks is the EXCLUSIVE queue broker. BullMQ is banned.
</rich_hickey_vulture_doctrine>

<prompt_repetition_doctrine>
## Prompt Repetition — Zero-Cost Accuracy Boost

**Source:** Leviathan, Kalman, Matias (Google Research) — [arXiv 2512.14982](https://arxiv.org/abs/2512.14982)

**Rule:** When routing prompts to non-reasoning model tiers (flash, lite, mini, haiku), repeat the user's instruction in the context to boost accuracy by 1–8% with zero additional output tokens or latency.

**Apply to:** Oracle Studio stages, CounselConduit model_router, Vent Mode, Autoresearch Triad prompts.
**Do NOT apply to:** Reasoning/thinking models (Gemini thinking, Claude extended thinking, DeepSeek-R1).

**Skill reference:** `skills/prompt-repetition-boost/SKILL.md`
</prompt_repetition_doctrine>
<env_master_doctrine>
## .env Master Environment Doctrine

**Canonical path:** `.env` (repo root, gitignored)
**Created:** 2026-04-13 | **Sections:** 11

### Section Map
| § | Variable | Purpose | Consumer |
|---|----------|---------|----------|
| 1 | `GCP_PROJECT_ID` | Active GCP project (`shadowtag-omega-v4`) | All services |
| 1 | `VITE_API_URL` | Local dev API URL | KovelAI frontend |
| 1 | `BRAIN_DIR` | Antigravity persistent brain directory | Agent memory |
| 2 | `DEVELOPER_KNOWLEDGE_API_KEY` | Google AI API key (zero-trust gate) | Developer Knowledge MCP, FastAPI `Depends(verify_zero_trust)` |
| 2 | `API_KEY` | Same key, alias | litellm fallback |
| 3 | `STITCH_API_KEY` | Stitch MCP authentication | Stitch design-to-code pipeline |
| 4 | `GEMINI_API_KEY` | Gemini inference + Nano Banana 2 | litellm, image generation, MCP servers |
| 5 | `KVCACHED_PORT` / `KVCACHED_MODEL` | Local sovereign inference routing | `zero_cpu_router.py` |
| 6 | `ROTATING_PROXIES` | Jetski/Scrapling stealth proxies | Web scraping sandbox |
| 7 | `TEMPORAL_HOST` | Temporal.io local server | Omega-Swarm workers |
| 8 | `DISABLE_TELEMETRY` / `DISABLE_ERROR_REPORTING` | Kovel Mode telemetry blackout | All services |
| 9 | `NODE_OPTIONS` | V8 punycode deprecation mute | VS Code Extension Host |
| 10 | `NANO_BANANA_2_MODEL` | Image generation model ID | Nano Banana 2 |
| 11 | `STRIPE_PUBLISHABLE_KEY` | Stripe frontend key (public) | Pricing page checkout |
| 11 | `STRIPE_SECRET_KEY` | Stripe backend key (NEVER expose) | CounselConduit API |
| 11 | `STRIPE_WEBHOOK_SECRET` | Stripe webhook signature | Webhook handler |

### Auth Chain
- **MCP servers** authenticate via Google ADC (`~/.config/gcloud/`) + `GEMINI_API_KEY` from `.env`
- **Firebase MCP** uses its own OAuth session (not `.env`)
- **GitHub** uses SSH keys + GitHub App PEM (`$SHADOWTAG_PEM`)
- **Stitch MCP** uses `STITCH_API_KEY` from `.env`
- **Stripe** uses `STRIPE_SECRET_KEY` from `.env` (backend) and `STRIPE_PUBLISHABLE_KEY` (frontend)

### Stripe Live Configuration
- Account: `acct_1Syh9JEHnWpykeMi` (US, charges+payouts enabled)
- Products: `prod_UM2XwCF1byjegL` (Trial), `prod_UM2X10cpyay52e` (Pro), `prod_UM2XMVp9Er7A0i` (Enterprise)
- Pro Monthly: `price_1TNKSREHnWpykeMiRMDlVgLl` ($149/mo)
- Pro Annual: `price_1TNKSjEHnWpykeMi0S9GCVjy` ($1,428/yr)
- Enterprise: `price_1TNKSREHnWpykeMi8mrDf4rI` ($20K/mo)
- Beta Coupon: `3wseBY7Z` (50% off, 3 months, max 100)
- Portal: `bpc_1TNKSjEHnWpykeMi0qQPoaHm`
- Webhook: `we_1TNKSjEHnWpykeMiQZqmpy3X` → `https://counselconduit-api.run.app/webhooks/stripe`

### Cor.env Lock Doctrine
- `.env` is protected by `chflags uchg` (macOS kernel immutable flag)
- AI blindfolds: `.aiexclude`, `.geminiignore`, `.clineignore`, `.rooignore` all contain `.env`
- To edit: `chflags nouchg .env` → edit → `chflags uchg .env`
- Validate: `bash scripts/validate_env.sh`

### Cloud Run Secrets Architecture
- **Google services** (Vertex AI, Firestore, Translate) use **ADC** via service account — NO API keys needed
- **External services** (Stripe) use **GCP Secret Manager** → Cloud Run `valueFrom.secretKeyRef`
- Upload script: `bash scripts/upload_secrets_to_gcp.sh`
- SA role required: `roles/secretmanager.secretAccessor`

### Rules
- `.env` is gitignored. NEVER commit it.
- `apps/counselconduit/.env.example` is the template for product-specific vars.
- All MCP servers MUST read from `.env` or ADC. No hardcoded keys in source.
- The `STRIPE_PUBLISHABLE_KEY` is the ONLY key safe to embed in frontend HTML.
</env_master_doctrine>

<cor30_security_doctrine>
## Cor.30 — Security Rules for AI Vibe Coding

**Canonical checklist:** `docs/SECURITY_DOD.md`
**Enforcer skill:** `skills/cor30-security-enforcer/SKILL.md`
**CI gate:** `.github/workflows/security-audit.yml`
**Pre-commit:** `.pre-commit-config.yaml` (Gitleaks + detect-private-key)

### Core Principle
AI velocity does not excuse missing security hygiene — it multiplies the cost of skipping it.

### 6-Pillar Framework
1. **Identity & Session** (R1–2, 13, 32): Short-lived access tokens (15–60 min), rotated refresh, MFA for admin/billing, CSRF protection, redirect allow-lists.
2. **Secrets & Supply Chain** (R3–8, 33–35): Secret Manager only, Gitleaks pre-commit, pinned deps, verified packages, no blind npm audit fix.
3. **API Hardening** (R9, 12, 14–16, 23, 31): Pydantic/Zod validation, per-user+route rate limits, server-side authz, security headers (CSP/HSTS).
4. **Storage & Uploads** (R10, 19–20): Tenant isolation, signed URLs, magic-byte file validation, malware scan.
5. **Payments & Webhooks** (R21–22, 30): HMAC signature verification, idempotency keys, SPF/DKIM/DMARC, test/prod separation.
6. **Ops & Audit** (R11, 17–18, 24–30): Structured logging (no PII), token budget caps, audit logs, GDPR deletion flow, backup+restore drills.

### OWASP LLM Top 10 (2025)
| # | Risk | Mandatory Control |
|---|------|-------------------|
| LLM01 | Prompt Injection | System prompts isolated from user input |
| LLM02 | Sensitive Info Disclosure | PII stripped from context windows |
| LLM05 | Improper Output | All LLM output treated as untrusted |
| LLM06 | Excessive Agency | Minimum-permission tool manifests |
| LLM07 | Prompt Leakage | Prompts encrypted, never in responses/logs |
| LLM10 | Unbounded Consumption | Token budget + rate limits + circuit breaker |

### Threat Model Defenses
- **Voice AI IDOR/BAC**: UUIDv7 IDs, tenant-scoped queries, admin role isolation.
- **Perplexity .npmrc preload**: Sandbox-bound ephemeral tokens, no shared FS, user-billed proxy, egress restrictions.
- **Vibe-coded sinking ship**: Full Cor.30 checklist enforcement in CI.
</cor30_security_doctrine>

<counselconduit_architecture>
## CounselConduit Business Architecture

### Product Identity
CounselConduit is the "Shopify for Legal AI" — a privilege-preserving routing tier between law firms and foundational LLMs (Gemini, Claude, ChatGPT, Grok, Perplexity) protected under *United States v. Heppner* (S.D.N.Y., Feb. 10, 2026).

### Dual-Billing Engine (Stripe Connect)
1. **Client → Lawyer**: Client subscribes to AI portal with their credit card. Funds flow to lawyer's Stripe account. Lawyer gets paid upfront for each query.
2. **Lawyer → Us**: Auto-scaling tiered subscription (Solo $299, Practice $599, Enterprise $999). Tiers cover ALL LLM API costs + 85%+ margin. Auto-bump on usage (like Claude Code billing).
3. **Fee Isolation**: We never touch the client-lawyer fee arrangement. Lawyer bills client separately for work product.

### Heppner Privilege UX
- **Client View (Ephemeral)**: Research portal with multi-model selector. Auto-logout + screen wipe after inactivity. No export. No copy. Dead-man's switch.
- **Lawyer View (Persistent)**: Immutable transcripts, Oracle Memo with citations, oversight dashboard.
- **Kovel Attestation Receipt**: Cryptographic hash per session proving privileged communication.

### Cloud Run Target Architecture
- **Control Plane**: Tenant registry, plan/tier logic, billing orchestration, model routing policy, audit metadata.
- **Data Plane**: Per-firm storage namespace, per-firm transcript path, per-firm model policy, per-firm billing attribution.
- **LiteLLM Proxy**: Ephemeral sandbox-bound tokens (tied to tenant + session + TTL). User-billed. No master keys in sandbox.
- **Judge #6**: Mandatory policy gate on model routing, export, transcript generation, and regulated-domain answers.

### Cloud Run Service URLs
- **Production**: `https://counselconduit-767252945109.us-central1.run.app`
- **Service Account**: `counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com`
- **Staging SA**: `counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com`

### Implementation Phases
1. **Phase 1 (Secure MVP)**: ✅ LIVE — Cloud Run v3.1.0 + RBAC + billing tiers + HMAC webhooks + Cloud Armor WAF + OpenAPI docs.
2. **Phase 2 (Privilege)**: ✅ LIVE — Judge #6 gate + Kovel attestation (HMAC-SHA256) + Oracle Studio 7-stage pipeline + LiteLLM multi-model routing + SSE streaming (Vent Mode) + prompt repetition (arXiv 2512.14982) + Firestore persistence + Cloud Tasks GDPR 30-day delete + Google Workspace alerts (Gmail API + Chat API) + Stripe Connect onboarding.
3. **Phase 3 (Sandbox)**: Isolated tool runners + read-only FS + short-lived proxy tokens + tenant-billed token issuance.
4. **Phase 4 (Enterprise)**: BYOC/BYOK + regional isolation + custom retention + FedRAMP + evidence-grade audit exports.

### Timeline
- Day 0–30: Core fork + security hardening. ✅ COMPLETE
- Day 31–45: First paid customer live.
</counselconduit_architecture>

<headless_cli_doctrine>
## Headless CLI Protocol — PTY Buffer Trap Prevention

**Trigger:** Any interactive TUI (charmbracelet/bubbletea, Inquirer.js, gum, fzf, etc.)
**Root cause:** Agent terminals lack full PTY attachment; raw TTY key events misfire in background shells.

### Mandatory Rules

1. **Force Headless Mode:** Prepend `export CI=true DEBIAN_FRONTEND=noninteractive` to every command that might launch a TUI.
2. **Non-Interactive Flags:** Always use `--non-interactive`, `--quiet`, `--no-user-output-enabled`, `--yes/-y` when available.
3. **Never blindly inject newlines or arrow keys** into interactive TUI prompts — they will loop forever.
4. **pexpect Fallback:** If a CLI absolutely requires interactive input, write a Python script using `pexpect` to programmatically control it.
5. **Human Handoff:** If it's an OAuth browser flow or complex account selector that can't be bypassed headlessly, **STOP** and tell the user the exact command to run in their Mac Terminal. Do NOT "note it and move on."

### Prohibited Behavior

- **NEVER** say "Let me note this for the user and commit everything" when hitting an interactive prompt. This is a commit-abort pattern.
- **NEVER** commit code in a broken state because a CLI blocked you.
- **NEVER** skip authentication or deployment steps because a TUI trapped you.

### Recovery Sequence

1. Terminate the hung process immediately.
2. Retry with `CI=true` + `--non-interactive` flags.
3. If still blocked, write a `pexpect` script or instruct the user.
4. Only proceed to the next task after the blocked task is resolved or explicitly deferred by the user.

### Reference Repos
- `charmbracelet/bubbletea` — Go TUI framework (raw TTY mode)
- `SBoudrias/Inquirer.js` — Node interactive prompts
- `pexpect/pexpect` — Python programmatic terminal control
</headless_cli_doctrine>

<context_compaction_roadmap>
## Context Compaction — Roadmap (from CC Leaks Analysis)

**Source:** Claude Code source leak (src.zip), `docs/architecture/context_compaction_pipeline.md`
**Status:** Documented, not implemented in Antigravity (platform handles context for us)

### 4-Layer Architecture (CC Pattern)
1. **Microcompact** — within-message stale tool result pruning
2. **Auto-compact** — ~167K token threshold, 5-file retention + 50K summary
3. **Reactive compact** — explicit /compact command or extreme pressure
4. **History snip** — nuclear option, cuts old turns entirely

### Our Implementation Status
- Layer 0 (Microcompact): ❌ Not applicable to Antigravity
- Layer 1 (Auto-compact): 📋 Documented in `.claude/rules/11-compaction-pipeline.md`
- Layer 2 (Reactive): 📋 Timing rules in `.claude/rules/36-compact-timing-discipline.md`
- Layer 3 (History snip): ❌ Platform-level (Antigravity truncation)

### Daemon Integration
- `scripts/dream_consolidation.py` — 4-phase KI maintenance → runs nightly via KAIROS
- `scripts/loop_steward.py` — autonomous task continuation with reversibility heuristic
</context_compaction_roadmap>

<daemon_fleet_registry>
## Daemon Fleet Registry

| Daemon | Script | Schedule | Purpose |
|--------|--------|----------|---------|
| Dream Consolidation | `scripts/dream_consolidation.py` | Nightly | KI maintenance: orient → gather → consolidate → prune |
| Loop Steward | `scripts/loop_steward.py` | 5-min cycles | Autonomous task continuation with idle scaling |
| KAIROS | `scripts/kairos_daemon.py` | Background | Background autonomous agent mode |
| pnkln-evolve | `scripts/pnkln-evolve.py` | Background | Recursive self-improvement loop |
</daemon_fleet_registry>
</system_directive>
