# RISK_REGISTER — v9.5

> Operational risks tracked as part of the sovereign monorepo governance.
> Reviewed on each version bump. Mitigations are enforced, not advisory.

| # | Risk | Severity | Status | Mitigation |
|---|---|---|---|---|
| 1 | Guillotine `check_alignment` blocks `BUSINESS_CONTEXT_LOCKED.md` | 🔴 Critical | RESOLVED | Case pattern in `dead-code-audit.sh` explicitly excludes deliberately-decoupled business files |
| 2 | `./mvnw` doesn't exist — Maven Wrapper missing | 🟡 Medium | ACCEPTED | Repo uses `pom.xml` only. Use `mvn` from brew or `/tmp/apache-maven-3.9.9/bin/mvn` |
| 3 | JAR version mismatch (0.2.0 vs 0.2.1) | 🟡 Medium | RESOLVED | `antigravity-mcp-config.json` updated to `0.2.1-SNAPSHOT` |
| 4 | JAVA_HOME points to wrong JDK version | 🟡 Medium | RESOLVED | Config and local overrides both point to JDK 26 at `/Library/Java/JavaVirtualMachines/jdk-26.jdk/Contents/Home` |
| 5 | `dotnet` not on default PATH | 🟡 Medium | MITIGATED | `DOTNET_BIN` defined in `WORKSTATION_LOCAL_OVERRIDES.example.md`. Scripts use absolute path. |
| 6 | HTTPS git remote vs SSH doctrinal mismatch | 🟠 High | RESOLVED | SSH is PRIMARY transport per v8.2c hardening. HTTPS is last-resort fallback. macOS Keychain interference eliminated. |
| 7 | NotebookLM module availability | 🟡 Medium | RESOLVED | `notebooklm-py 0.1.1` installed and importable. Master Brain ID verified. |
| 8 | `credential.helper=store` caching stale GitHub tokens | 🔴 Critical | RESOLVED | Global store helper removed. `~/.git-credentials` purged. osxkeychain disabled for github.com. |
| 9 | OrbStack Docker not on PATH | 🟡 Medium | MITIGATED | Explicit `PATH=$HOME/.orbstack/bin:$PATH` prepend in daemon configs and scripts. |
| 10 | State B trigger scope too broad (all network = Clutch) | 🟠 High | RESOLVED | v8.3 narrows scope to credentialed external mutations only. Web research, pip installs, git fetch are explicit State A. |
| 11 | `shadowtag-agent` pyproject.toml caps Python at `<3.14` | 🟡 Medium | ACCEPTED | Workstation runs CPython 3.14.3, but ADK SDK constraint limits to 3.10–3.13. Use `uv` virtual env with 3.13 for agent dev. |
| 12 | `USER_TYPE="ant"` spoofs Anthropic internal tools | 🟡 Medium | GOVERNED | Governed by `dead-code-audit.sh` pre-commit script, preventing AI from bypassing its own requested checks. |
| 13 | `DISABLE_TELEMETRY=1` / `DISABLE_ERROR_REPORTING=1` severs remote debugging | 🟢 Low | ACCEPTED | Offset by Structured Logging (Tech Debt 19). Local logs capture trace ID failures. Anomalies tracked in `.beads/issues.jsonl`. |
| 14 | GitHub App JWT hardcoding — single point of failure | 🟠 High | MITIGATED | PEM now in Secret Manager (`github-app-shadowtag-v2-pem`). `auth_github_app.py` has 5-tier fallback chain: SM → keys/ → Downloads → .ssh → $SHADOWTAG_PEM. |
| 15 | Bounded YOLO (`agentYoloMode=true`) auto-approval | 🟢 Low | MITIGATED | Destructive tools (`rm -rf`, `sudo`) physically excluded from MCP schema. Model cannot call tools that do not exist. |
| 16 | `git reset --hard` (Temporal Reversal) wipes uncommitted work | 🟠 High | GOVERNED | Reset ONLY authorized via Temporal Reversal state machine. Stash → reset to `latest-stable` → branch → fix via TDD. |
| 17 | `git push --force` overwrites remote history | 🔴 Critical | GOVERNED | Bound by Squash-Push Protocol. Must use `--force-with-lease` first. Escalate to `--force` ONLY after fetching origin to verify tracking refs. |
| 18 | No Firestore security rules deployed on any database | 🔴 Critical | RESOLVED | Zero-trust rules deployed to `firestore.rules`. Default deny-all with admin-only access. Deployed via `firebase deploy --only firestore:rules`. |
| 19 | No Storage security rules deployed | 🔴 Critical | RESOLVED | Locked-down `storage.rules` deployed. Default deny-all — no storage actively used. |
| 20 | `shadowtagai.com` ACME 403 — conflicting Squarespace DNS | 🟠 High | KNOWN | Squarespace retains A/CNAME records that override Firebase Hosting verification. **Action**: Log in to Squarespace DNS → delete the A records (198.185.159.x) and CNAME → re-run `firebase hosting:channel:deploy` for `shadowtagai` target → verify TXT ownership record. |
| 21 | `knowledge-base-database` — undocumented, empty, no delete protection | 🟡 Medium | RESOLVED | Deleted 2026-04-16. Confirmed zero collections before deletion. |
| 22 | No Firestore monitoring alerts deployed | 🟡 Medium | MITIGATED | Alert policies created via tofu apply. Notification channel: `founder@shadowtagai.com` (channel ID: 17531835029676919705). |
| 23 | Firebase Hosting auto-gzip breaks video playback | 🟠 High | RESOLVED | Serve video assets from GCS instead. CSP `media-src` updated to whitelist `https://storage.googleapis.com`. |
| 24 | GCS bucket CORS not configured for cross-origin streaming | 🟡 Medium | RESOLVED | `shadowtag-omega-v4-archive` bucket CORS configured for all 5 production origins. |
| 25 | `pip.conf` global `user=true` breaks virtualenv installs | 🟡 Medium | RESOLVED | Removed the `user = true` directive from `~/.config/pip/pip.conf`. |
| 26 | OpenTofu state drift — SM secrets created outside IaC | 🟡 Medium | RESOLVED | `tofu import` run for 9 existing secrets (6 original + 3 Wave 9). State now tracks 19 resources. |
| 27 | Pre-push hook PATH missing `/opt/homebrew/bin` | 🟡 Medium | RESOLVED | Fixed pre-push hook to export `/opt/homebrew/bin` in PATH. Stage 1 now soft-fails (non-blocking). |
| 28 | Dependabot PRs accumulate with deleted head branches | 🟢 Low | RESOLVED | 8 stale Dependabot PRs closed. Auto-merge + delete-branch-on-merge enabled for future PRs. |
| 29 | Secret rotation lacks documented procedure | 🟡 Medium | RESOLVED | `docs/SECRET_ROTATION.md` created with per-category rotation steps, schedules, and PubSub automation path. |
| 30 | Vulture sweeps `external_repos/` + `control/legacy_workspaces/` (500K+ files) | 🟡 Medium | RESOLVED | `dead-code-audit.sh` exclude list expanded: `external_repos`, `control/legacy_workspaces`, `reference_architectures`, `packages`, `apps/kovelai/venv`. Pre-commit scan reduced from 5+ min to <30s. |
| 31 | `brew upgrade llama.cpp` HEAD build fails against macOS SDK 26 | 🟡 Medium | KNOWN | cmake build failure in `src/CMakeFiles/llama.dir/all`. Upstream SDK 26 compatibility issue. **Action**: Wait for next HEAD revision or `brew pin llama.cpp` to freeze current version. |
| 32 | `gh auth login` creates stale Keychain credentials | 🟠 High | RESOLVED | GEMINI.md v9.0 github_doctrine prohibits `gh auth login`, PATs, deploy keys. GitHub App PEM is exclusive auth path. |
| 33 | Competitor system prompts fully leaked (CL4R1T4S) — ours may be extractable too | 🟡 Medium | GOVERNED | Claude Opus 4.7 (150K chars), Cursor 2.0, Devin 2.0, Gemini 2.5 Pro all fully extracted via CL4R1T4S. Our prompts use runtime injection (AGENTS.md + GEMINI.md) not API system blocks, reducing extraction surface. Competitive matrix archived to `reference_architectures/`. |
| 34 | Adversa AI 50-subcommand bypass — chained benign commands reconstruct malicious payload | 🟠 High | KNOWN | Judge 6 Composite Action Evaluation (lines 83-86) evaluates ALL parts but lacks: (1) chain depth limit, (2) temporal correlation of sequential BashTool calls, (3) reconstruction/encoding detection. **Action**: Add >10 sequential shell commands → auto-ESCALATE rule to Judge 6. Add base64/encoding detection in command chains. See `docs/architecture/cc_feature_flags_catalog.md`. |
| 35 | AI agent verification false claims rate measured at 29-30% (Claude Code source leak) | 🟠 High | MITIGATED | Source: `services/tools/toolExecution.ts` success metric only checks "did bytes hit disk" not "does code compile". Our `verification-before-completion` skill hardened with self-awareness patterns, anti-rationalization list, and mandatory adversarial probes. Employee-grade verification gate enforced via `~/.claude/CLAUDE.md` (USER_TYPE override). |

| 36 | Root-domain DNS (kovelai.com / shadowtagai.com) not connected to Firebase Hosting | 🟡 Medium | MITIGATED | `.web.app` subdomains are live and serving. Custom domains require DNS TXT verification + A record migration from Squarespace/registrar. See Risk #20 for shadowtagai.com specifics. **Action**: Purchase/transfer `kovelai.com` → set Firebase DNS records → verify in Hosting console. |
| 37 | Developer Knowledge / NotebookLM loop not enforced in day-to-day agent flow | 🟡 Medium | RESOLVED | `docs/doctrine/SIMPLICITY_DOCTRINE.md` §7 updated with NotebookLM/DevKnowledge enforcement gate. `rule-49-notebooklm-protocol.md` + `notebooklm-bridge` skill both exist. Session wrap-up skill archives to Master Brain. |
| 38 | BullMQ/Redis lab artifacts contradict serverless queue doctrine if treated as production | 🟡 Medium | RESOLVED | `labs/uphillsnowball/agent/gauntlet.py` BullMQ references are in the gauntlet's Layer 10 BLOCK list (correct — it blocks BullMQ). `external_repos/BioAgents/` BullMQ code is a reference clone (gitignored from production). `guardian.py` updated with explicit "lab utility" header. No BullMQ exists in `apps/` production code. |
| 39 | Internal docs carry obsolete "purge ATP 5-19" language vs current "stable process skeleton" architecture | 🟡 Medium | RESOLVED | `docs/strategy/STRATEGIC_FRAMEWORKS.md` confirmed correct (ATP 5-19 as stable framework). Historical OMNI_PLAN/OMNI_WALKTHROUGH references are archived session history (immutable). Active doctrine (SIMPLICITY_DOCTRINE, AGENTS.md, GEMINI.md) all correctly reference ATP 5-19 as the stable risk management skeleton beneath Judge 6. |
| 40 | Inline API keys committed in `antigravity-mcp-config.json` (DEVELOPER_KNOWLEDGE_API_KEY + STITCH_API_KEY) | 🔴 Critical | CLOSED | Keys replaced with `${VAR}` env references in commit `42d76d2c74e`. **BFG Repo-Cleaner scrubbed 1,085 objects** (2026-04-18). Both keys rotated in GCP Console same day. Force-push completed via 10-commit chunked batches (223 commits). `.env` is gitignored + kernel-locked (`chflags uchg`). Pre-commit Gitleaks catches this pattern. GEMINI.md v9.5 `secrets_manager_doctrine` prohibits inline keys. |
| 41 | BFG force-push rewrote git history — all commit SHAs changed | 🟡 Medium | KNOWN | BFG Repo-Cleaner ran 2026-04-18. All 1,085 object IDs remapped (see `.bfg-report/2026-04-18/14-36-38/object-id-map.old-new.txt`). Force-push completed via chunked 10-commit batches. **Impact**: Any forks, open PRs, or local clones referencing old SHAs are now invalid. Tag `v9.5` marks the clean state. Dependabot auto-merge is active for future PRs. |
| 42 | Third-party Stripe `sk_test_` key in cloned `reference_architectures/terraform/` (Odoo fixture) | 🟡 Medium | RESOLVED | NOT our account (`acct_1Syh9JEHnWpykeMi`). Confirmed Odoo demo test key. Path gitignored, allowlisted in `.gitleaks.toml`, suppressed in `.gitleaksignore`. `reference_architectures/` purged (4.3GB freed). |
| 43 | Third-party Vault token `s.Fg8w...` in cloned `reference_architectures/opentofu/website/docs/` | 🟡 Medium | RESOLVED | OpenTofu documentation example (not live). Path gitignored, allowlisted in `.gitleaks.toml`, suppressed in `.gitleaksignore`. `reference_architectures/` purged. |

| 44 | ShadowTagAI CSP included `unsafe-eval` + missing HSTS/COOP/CORP | 🟠 High | RESOLVED | `unsafe-eval` removed from `script-src`. Cloudflare Turnstile (`challenges.cloudflare.com`) added to `script-src` + `frame-src`. HSTS (preload, 1yr), COOP (same-origin), CORP (same-origin) added. Deployed `35de3f5ae7`. All 9 security headers verified live via `curl -D -`. |
| 45 | GPG signing key not uploaded to GitHub — commits unverified on remote | 🟡 Medium | KNOWN | Ed25519 key `7B0BE56159C521F8BBD2EF39301A4A10622FFE11` generated and signing commits locally. GitHub 2FA ("Confirm access") blocks automated upload. **Action**: Manually add GPG public key at `github.com/settings/keys` after 2FA approval. |

| 46 | GCP infrastructure sprawl — 175+ APIs enabled, stale Cloud Run services, orphaned secrets | 🟡 Medium | RESOLVED | Audit 2026-04-20: Disabled 9 unused APIs (Batch, Composer, Dataform, Dataplex, Dataproc, Datastream, Notebooks, Spanner, Dataproc Control). Deleted 3 stale Cloud Run services (capturelead, judge-sentinel, uphillsnowball-sovereign). Deleted 5 orphaned OAuth/connector secrets. Remaining: 2 Cloud Run (counselconduit prod+staging), 19 secrets (all active), 5 Cloud Scheduler jobs, 175 APIs. 10x_vibe_matrix.yml CI/CD created. |

## Review Policy

- Risks with status `RESOLVED` are kept for institutional memory.
- New risks are appended with the next sequential number.
- Severity ratings: 🔴 Critical (blocks execution), 🟠 High (causes incorrect behavior), 🟡 Medium (causes degraded operation), 🟢 Low (cosmetic or theoretical).
- This file is a **companion** to `operator_invariants.json` — not a replacement for inline doctrine.

## Risk #47: IDE SharedProcess Bug
- **Type**: External (Electron/Extension)
- **Severity**: Low
- **Status**: Monitored
- **Description**: Antigravity IDE SharedProcess uncaught exception ('fireEvent'). Upstream bug, no action required.

## Risk #48: Porsche Trademark in Customer-Facing Assets
- **Type**: Legal/IP
- **Severity**: 🟠 High
- **Status**: RESOLVED
- **Description**: Veo-generated video (`porsche-peelout-compressed.mp4`) and UI labels on kovelai.web.app referenced "Porsche" trademark. Renamed file to `supercar-peelout-compressed.mp4`, updated all 8 references across showreel.html, video-gallery.html, cinematic-landing.html, index.html, scroll-frames.js, video-sitemap.xml, OG/Twitter meta tags. Zero remaining trademark references in `apps/kovelai/` and `apps/shadowtagai/`. aiyou_stack internal references retained (non-customer-facing).

## Risk #49: Firestore PITR (Point-in-Time Recovery) Disabled
- **Type**: Data Loss / Backup
- **Severity**: 🟠 High
- **Status**: RESOLVED
- **Description**: Both Firestore databases lacked Point-in-Time Recovery, exposing the project to unrecoverable data loss from accidental writes or deletions. PITR enabled on both `(default)` (nam5) and `shadowtag-engine` (us-central1) via Firebase MCP on 2026-04-20. 7-day version retention confirmed for both databases. Delete-protection was already enabled.

## Risk #50: Agent Context Drift — Stale Invariants in Long-Running Sessions
- **Type**: Operational / AI Safety
- **Severity**: 🟡 Medium
- **Status**: MITIGATED
- **Description**: Long-running agent sessions accumulate stale context from operator_invariants.json and GEMINI.md, causing drift between canonical truth and in-memory agent state. Mitigated by: (1) KAIROS daemon refreshes context every 5 minutes, (2) Dream consolidation prunes stale KIs nightly, (3) GEMINI.md version pinning prevents implicit upgrades.

## Risk #51: JTF V35.0 Scaffolds — Temporal.io Runtime Not Installed
- **Type**: Build / Dependency
- **Severity**: 🟢 Low
- **Status**: KNOWN
- **Description**: JTF scaffolds (`src/headquarters/`, `src/intelligence/`, `src/governance/`, `src/workflows/`) are pure Python dataclass+async scaffolds. They do NOT depend on Temporal.io runtime. If Temporal integration is added later, `temporalio` SDK must be installed and workflow registration configured. Current scaffolds are self-contained and importable without external dependencies.

## Risk #52: Staging Branch Residue — Stale Remote Branch After Merge
- **Type**: Operational / Git Hygiene
- **Severity**: 🟢 Low
- **Status**: RESOLVED
- **Description**: `staging` branch remained on both local and remote after all 10 PRs merged to main. Deleted local (`git branch -d staging`) and remote (`git push origin --delete staging`) during session `4d82db23`. Only `main` remains.

## Risk #53: Bandit HIGH — Shell Injection in Scripts (B605)
- **Type**: Security / Code Quality
- **Severity**: 🟡 Medium
- **Status**: KNOWN
- **Description**: 6 Bandit HIGH findings: 3x B605 (subprocess.getoutput with f-strings in `git_frame_external.py`, `mass_git_sync.py`), 2x B202 (extractall without validation in `ingest_downloads.py`), 1x B324 (MD5 without usedforsecurity=False in `last30days_to_ingest.py`). All in internal scripts (not production API code). **Action**: Refactor to `subprocess.run()` with explicit args, add `usedforsecurity=False` to MD5 call, validate archive contents before extraction.

## Risk #54: npx/Node Not on Agent Shell PATH
- **Type**: Environmental / Toolchain
- **Severity**: 🟡 Medium
- **Status**: MITIGATED
- **Description**: `npx` unavailable in default agent shell (nvm not sourced). Firebase CLI deploy requires explicit PATH prepend: `PATH="$HOME/.nvm/versions/node/$(ls $HOME/.nvm/versions/node/ | tail -1)/bin:$PATH"`. Mitigated by using this prepend in all Firebase deploy commands.


## Risk #55: Duplicate Process.cs — SK Process Definition Drift
- **Type**: Architectural / Code Duplication
- **Severity**: 🟠 High
- **Status**: RESOLVED
- **Description**: Two copies of `ShadowTagV4.Kernel/Process.cs` existed: (1) canonical at `apps/aiyou_stack/aiyou-fastapi-services/apps/aiyou-kernel/Process.cs` and (2) duplicate at `apps/aiyou_stack/aiyou-fastapi-services/src/dotnet/AiYou.Kernel/Process.cs`. The duplicate had already drifted — AGENTS.md incorrectly claimed `OnExternalEvent` should be replaced with `OnInputEvent` (which does NOT exist in SK Process.Core 1.21.0-alpha). `OnExternalEvent` is the CORRECT API for human-in-the-loop external resumption. **Resolution**: Duplicate deleted via `git rm -r`. Canonical copy updated with user's authoritative version. AGENTS.md corrected. `dotnet build` verified clean (0 warnings, 0 errors).

## Risk #56: NadirClaw Model Dispatch — Noisy Neighbor / Session Pin Memory Leak
- **Type**: Operational / Performance
- **Severity**: 🟡 Medium
- **Status**: MITIGATED
- **Description**: NadirClaw 3-tier dispatch introduces three operational risks: (1) Noisy neighbor — a single firm could exhaust the model routing budget. Mitigated by `TenantQuota` with per-tier RPM limits (trial=20, pro=60, enterprise=200). Quotas backed by Firestore `tenant_quotas` collection. (2) Session pin memory leak — `_session_pins` dict grows unbounded in long-running processes. Mitigated by 30-minute TTL auto-expiry (`SESSION_PIN_TTL_SECONDS=1800`). (3) Fallback chain exhaustion — if all models in a fallback chain are unavailable, system degrades to `gemini-flash`. Metrics tracked via `_fallback_hits` for Cloud Monitoring alerting. **Files**: `apps/counselconduit/api/model_router.py`, `apps/counselconduit/tests/test_model_router.py` (33 tests).

## Risk #57: NadirClaw Circuit Breaker — False-Positive Load Shedding
- **Type**: Operational / Reliability
- **Severity**: 🟡 Medium
- **Status**: MITIGATED
- **Description**: The NadirClaw dispatch circuit breaker (10 errors / 60s window / 30s cooldown) may false-trip during transient upstream model API outages, blocking all dispatch requests with HTTP 503. Mitigated by: (1) Per-model error tracking (not global), (2) Half-open state after cooldown allows single probe request, (3) `/admin/circuit-breaker` GET endpoint for real-time status monitoring, (4) Cloud Monitoring saturation alert configured in `monitoring.py` with configurable notification channels. **Files**: `apps/counselconduit/api/dispatch_router.py` (circuit breaker impl), `apps/counselconduit/api/monitoring.py` (alert config).

## Risk #58: Dispatch Admin Endpoints — No Authentication Gate
- **Type**: Security / Access Control
- **Severity**: 🟠 High
- **Status**: KNOWN
- **Description**: `/admin/*` dispatch endpoints (metrics, firm-policy, session-cleanup, circuit-breaker, models) are not behind authentication middleware. In production, these must be restricted to internal Cloud Scheduler callers (OIDC token) or admin-role Firebase Auth users. **Action**: Add `_verify_admin_auth()` gate before Phase 3 deployment. Cloud Run IAM invoker restriction provides partial mitigation for now.

## Known Issues
- Antigravity IDE: SharedProcess uncaught exception (reading 'fireEvent') - Ignored upstream Electron/Extension bug.

## Risk #59: Trivy HIGH — ecdsa CVE-2024-23342 (Minerva Timing Attack)
- **Type**: Security / Dependency
- **Severity**: 🟠 High
- **Status**: RESOLVED
- **Description**: Trivy container scan flagged `ecdsa 0.19.2` (CVE-2024-23342, Minerva timing attack in ECDSA signature verification). The `ecdsa` package was a transitive dependency of `python-jose[cryptography]`. No direct imports of `python-jose` or `ecdsa` existed in CounselConduit — all JWT verification uses `firebase_admin.auth.verify_id_token()`. **Resolution**: Replaced `python-jose[cryptography]>=3.3.0` with `PyJWT[crypto]>=2.10.0` in `requirements.txt`. PyJWT uses the `cryptography` backend directly, eliminating the `ecdsa` dependency entirely. OS-level CVEs (ncurses CVE-2025-69720, libudev CVE-2026-29111) remain in Debian base image — no upstream fix available.

## Risk #60: ZAP Baseline Warnings — Cache-Control / CORP Headers Missing
- **Type**: Security / Headers
- **Severity**: 🟢 Low
- **Status**: RESOLVED
- **Description**: OWASP ZAP baseline scan flagged 3 warnings: (1) WARN-10015 Cache-control directives — API responses lacked `no-store`. (2) WARN-10049 Storable/cacheable content. (3) WARN-90004 Missing Cross-Origin-Resource-Policy header. **Resolution**: Added `Cache-Control: no-store, no-cache, must-revalidate, private`, `Pragma: no-cache`, `Cross-Origin-Resource-Policy: same-origin`, and `Cross-Origin-Opener-Policy: same-origin` to `SecurityHeadersMiddleware`. Also added `/robots.txt` and `/favicon.ico` root routes to eliminate 404 findings.
