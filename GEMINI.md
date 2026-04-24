---
version: 10.1
scope: antigravity_local_operator_invariants
status: LOCKED
---

# GEMINI.md — v10.2

<system_directive>
<workspace_alignment>
- Active project: `shadowtag-omega-v4`
- Only authorized external runtime model: `gemini-3.1-flash-lite-preview-thinking`
- NOTE: `.NET 10.0.106` is installed. Semantic Kernel (net10.0, SK 1.74.0) build-verified. OnExternalEvent is correct SK Process.Core API.
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

### MCP Protocol Architecture
- **Tools** are callable functions (`firebase_init`, `firebase_get_environment`, `firebase_login`, etc.) — execute actions, return results.
- **Resources** are read-only data identified by URIs (`firebase://guides/init/hosting`) — contain step-by-step instructions the agent follows.
- **Deploy is a Resource, NOT a Tool.** Read `firebase://guides/init/hosting` before any deploy. It instructs you to call `firebase_init` (Tool) + run build (terminal) + run deploy (terminal).

### Three-Layer Auth Architecture (CRITICAL)
Firebase has THREE independent auth channels that do NOT share tokens:

1. **Firebase CLI (Layer 1)**: OAuth2 refresh token in `~/.config/configstore/firebase-tools.json`. Used by `firebase deploy`, `firebase hosting:*` terminal commands. Install globally (`npm i -g firebase-tools`), NOT via `npx`. Use `CI=true` to bypass Inquirer.js TUI prompts.
2. **Firebase MCP Server (Layer 2)**: In-memory OAuth2 session within the IDE's MCP process. Authenticated via the `firebase_login` MCP tool. Does NOT read the CLI's token file. Required for Resources and Firebase Management API calls.
3. **Application Default Credentials (Layer 3)**: `~/.config/gcloud/application_default_credentials.json`. Used by Google client libraries. Can access GCP services (Secret Manager, Cloud Run) but NOT Firebase-specific APIs.

### Prohibited Actions
- Running `firebase deploy` in terminal without verifying CLI auth (Layer 1).
- Assuming `firebase_get_environment` confirms live auth — it reads cached config files, not API calls.
- Using `npx firebase-tools` for ANY operation — tokens are lost in ephemeral `_npx/` cache.
- Assuming terminal CLI inherits the MCP server's in-memory session.

### Authorized Deployment Lifecycle
1. **Verify MCP Auth**: Call `firebase_login` MCP tool if MCP server auth is expired. Check `firebase_get_environment` shows `Authenticated User: <email>` (not "Application Default Credentials").
2. **Verify CLI Auth**: Run `CI=true firebase login:list` in terminal. If expired: `CI=true firebase login --reauth --no-localhost`.
3. **Read Hosting Guide**: `read_resource("firebase-mcp-server", "firebase://guides/init/hosting")`
4. **Initialize**: Call `firebase_init` MCP tool with hosting config per the guide.
5. **Build**: Run the framework's build command in terminal (e.g., `npm run build`).
6. **Deploy**: Run `firebase deploy --only hosting` in terminal (CLI auth required).
7. **Verify**: Use Chrome DevTools MCP `lighthouse_audit` on the live URL.

### Auth Refresh Commands
- **MCP Server**: Call `firebase_login` MCP tool → browser flow → pass `authCode` back to tool.
- **CLI**: `CI=true firebase login --reauth --no-localhost` → browser flow → paste code in terminal.
- **ADC**: `gcloud auth application-default login --project=shadowtag-omega-v4`

### Skill Reference

Full doctrine: `skills/firebase-mcp-deploy-doctrine/SKILL.md`
</firebase_mcp_doctrine>

<capability_resolution_doctrine>
## Capability Resolution

- `GEMINI.md` defines operator invariants, NOT capability ownership or routing.
- Capability ownership, precedence, conflict denial, and fallback behavior live ONLY in `antigravity-mcp-config.json`.
- If a verification task and a debugging tool both appear able to perform the work, MCP truth decides the owner.
- All 5 MCP servers MUST be used: Firebase, Chrome DevTools, Stitch, Developer Knowledge, Sequential Thinking.
- If an operation CAN be performed by an MCP server, it MUST be. No terminal fallbacks for MCP-capable operations.

### Anti-Patterns (PROHIBITED)
- Defining routing tables in prose doctrine (GEMINI.md, AGENTS.md, skills)
- Using `search_web` for Google API documentation (use `google-developer-knowledge` MCP)
- Running `firebase deploy` in terminal (use `firebase-mcp-server` MCP)
- Taking screenshots with external tools (use `chrome-devtools-mcp` MCP)
- Hand-coding design tokens from memory (use `StitchMCP`)
- Ad-hoc reasoning lists for architecture (use `sequential-thinking` MCP)
- Searching the public web with proprietary identifiers (use `epistemic-airgap` skill)
- Running `pip install` on unresolved internal package names (supply chain attack vector)
</capability_resolution_doctrine>

<epistemic_airgap_doctrine>
## V10 Epistemic Airgap — Zero-Trust Cognitive Routing

**Skill reference:** `.agents/skills/epistemic-airgap/SKILL.md`
**Tool manifest:** `.agents/skills/epistemic-airgap/tool_h_manifest.json`
**Pyright config:** `pyrightconfig.json` (extraPaths includes `./external_repos/corp-monorepo`)

### Cognitive Search Classification
Before ANY search operation, classify intent:
- **Internal IP** (proprietary microservice, corporate schema, shared type) → Route to `rg`/`sg` against `./external_repos/corp-monorepo/` ONLY
- **Public IP** (open-source library, public API docs) → Route to `google-developer-knowledge` MCP or `search_web`
- **Hybrid** (internal wrapper of public library) → Search internal FIRST, then public, intersect in local RAM

### DLP Circuit Breaker (ABSOLUTE)
Never pass proprietary variable names, corporate database schemas, internal IP addresses, corporate API keys, internal error traces, or internal package names into public search tools. All public queries MUST be sanitized.

### Supply Chain Protection
1. Never `pip install` or `npm install` an unresolved import without first checking `./external_repos/corp-monorepo/`
2. If package name matches an internal module → HALT and warn user
3. Pyright `extraPaths` resolves internal imports locally without hitting public registries

### Override Rule
If proprietary corporate code and public open-source patterns conflict, **corporate code ALWAYS wins**.
</epistemic_airgap_doctrine>

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
<secrets_manager_doctrine>
## Secrets Manager Doctrine

**Reference:** [GCP Secret Manager](https://docs.cloud.google.com/code/docs/vscode/secret-manager)
**Canonical rule:** Secrets only via GCP Secret Manager for production. No hardcoded keys in source or config.

### Production (Cloud Run, deployed services)
- **ONLY** GCP Secret Manager → `valueFrom.secretKeyRef`
- Google services (Vertex AI, Firestore, Translate) use **ADC** via service account — NO API keys
- External services (Stripe, GitHub App PEM) use Secret Manager
- SA role required: `roles/secretmanager.secretAccessor`
- Upload script: `bash scripts/upload_secrets_to_gcp.sh`

### Local Development (MCP servers, agent, scripts)
- `.env` is **DEPRECATED AND DELETED** (2026-04-22). Do NOT recreate.
- All secrets fetched from GCP Secret Manager via `source scripts/load_mcp_secrets.sh`
- MCP config uses `${VAR}` references resolved by the Antigravity platform's native env injection
- Non-secret project config (project IDs, regions, flags) is embedded in `load_mcp_secrets.sh`
- Secret Manager secrets: `developer-knowledge-api-key`, `stitch-api-key`, `google-design-api-key`, `gemini-api-key`, `stripe-*`, `KOVEL_ATTESTATION_SECRET`, `MAGIC_LINK_SECRET`

### Auth Chain
- **MCP servers** authenticate via Google ADC (`~/.config/gcloud/`) + platform env injection
- **Firebase MCP** uses its own OAuth session (`npx firebase-tools login --reauth`)
- **GitHub** uses SSH keys + GitHub App PEM (`$SHADOWTAG_PEM`)
- **Stitch MCP** uses `STITCH_API_KEY` from Secret Manager
- **Stripe** uses `STRIPE_SECRET_KEY` from Secret Manager (prod and local)

### Stripe Live Configuration
- Account: `acct_1Syh9JEHnWpykeMi` (US, charges+payouts enabled)
- Products: `prod_UM2XwCF1byjegL` (Trial), `prod_UM2X10cpyay52e` (Pro), `prod_UM2XMVp9Er7A0i` (Enterprise)
- Pro Monthly: `price_1TNKSREHnWpykeMiRMDlVgLl` ($149/mo)
- Pro Annual: `price_1TNKSjEHnWpykeMi0S9GCVjy` ($1,428/yr)
- Enterprise: `price_1TNKSREHnWpykeMi8mrDf4rI` ($20K/mo)
- Beta Coupon: `3wseBY7Z` (50% off, 3 months, max 100)
- Portal: `bpc_1TNKSjEHnWpykeMi0qQPoaHm`
- Webhook: `we_1TNKSjEHnWpykeMiQZqmpy3X` → `https://counselconduit-api.run.app/webhooks/stripe`

### NEVER (Absolute Prohibitions)
- Hardcoded API keys in source files or committed config
- API keys in logs, chat messages, or frontend code (except `STRIPE_PUBLISHABLE_KEY`)
- Creating, modifying, or recreating `.env` files — **BANNED** (use `scripts/load_mcp_secrets.sh`)
- Secrets in MCP config inline args (use `${VAR}` references only)
- Secrets guessed from memory or documentation
- Using `python-dotenv`, `dotenv`, or any local env file loader in production code
</secrets_manager_doctrine>

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
- **Judge 6**: Mandatory policy gate on model routing, export, transcript generation, and regulated-domain answers.

### Cloud Run Service URLs
- **Production**: `https://counselconduit-767252945109.us-central1.run.app`
- **Service Account**: `counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com`
- **Staging SA**: `counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com`

### Implementation Phases
1. **Phase 1 (Secure MVP)**: ✅ LIVE — Cloud Run v3.1.0 + RBAC + billing tiers + HMAC webhooks + Cloud Armor WAF + OpenAPI docs.
2. **Phase 2 (Privilege)**: ✅ LIVE — Judge 6 gate + Kovel attestation (HMAC-SHA256) + Oracle Studio 7-stage pipeline + LiteLLM multi-model routing + SSE streaming (Vent Mode) + prompt repetition (arXiv 2512.14982) + Firestore persistence + Cloud Tasks GDPR 30-day delete + Google Workspace alerts (Gmail API + Chat API) + Stripe Connect onboarding.
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
| Omni-Autolint | `scripts/gca_autolint_daemon.py` | Daily 3-5AM | Secure lint+push via GitHub App tokens, beads audit trail |
</daemon_fleet_registry>
</system_directive>
