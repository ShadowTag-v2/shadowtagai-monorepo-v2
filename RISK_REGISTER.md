# RISK_REGISTER — v9.0

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
| 34 | Adversa AI 50-subcommand bypass — chained benign commands reconstruct malicious payload | 🟠 High | KNOWN | Judge #6 Composite Action Evaluation (lines 83-86) evaluates ALL parts but lacks: (1) chain depth limit, (2) temporal correlation of sequential BashTool calls, (3) reconstruction/encoding detection. **Action**: Add >10 sequential shell commands → auto-ESCALATE rule to Judge #6. Add base64/encoding detection in command chains. See `docs/architecture/cc_feature_flags_catalog.md`. |
| 35 | AI agent verification false claims rate measured at 29-30% (Claude Code source leak) | 🟠 High | MITIGATED | Source: `services/tools/toolExecution.ts` success metric only checks "did bytes hit disk" not "does code compile". Our `verification-before-completion` skill hardened with self-awareness patterns, anti-rationalization list, and mandatory adversarial probes. Employee-grade verification gate enforced via `~/.claude/CLAUDE.md` (USER_TYPE override). |

| 36 | Root-domain DNS (kovelai.com / shadowtagai.com) not connected to Firebase Hosting | 🟡 Medium | MITIGATED | `.web.app` subdomains are live and serving. Custom domains require DNS TXT verification + A record migration from Squarespace/registrar. See Risk #20 for shadowtagai.com specifics. **Action**: Purchase/transfer `kovelai.com` → set Firebase DNS records → verify in Hosting console. |
| 37 | Developer Knowledge / NotebookLM loop not enforced in day-to-day agent flow | 🟡 Medium | RESOLVED | `docs/doctrine/SIMPLICITY_DOCTRINE.md` §7 updated with NotebookLM/DevKnowledge enforcement gate. `rule-49-notebooklm-protocol.md` + `notebooklm-bridge` skill both exist. Session wrap-up skill archives to Master Brain. |
| 38 | BullMQ/Redis lab artifacts contradict serverless queue doctrine if treated as production | 🟡 Medium | RESOLVED | `labs/uphillsnowball/agent/gauntlet.py` BullMQ references are in the gauntlet's Layer 10 BLOCK list (correct — it blocks BullMQ). `external_repos/BioAgents/` BullMQ code is a reference clone (gitignored from production). `guardian.py` updated with explicit "lab utility" header. No BullMQ exists in `apps/` production code. |
| 39 | Internal docs carry obsolete "purge ATP 5-19" language vs current "stable process skeleton" architecture | 🟡 Medium | RESOLVED | `docs/strategy/STRATEGIC_FRAMEWORKS.md` confirmed correct (ATP 5-19 as stable framework). Historical OMNI_PLAN/OMNI_WALKTHROUGH references are archived session history (immutable). Active doctrine (SIMPLICITY_DOCTRINE, AGENTS.md, GEMINI.md) all correctly reference ATP 5-19 as the stable risk management skeleton beneath Judge #6. |

## Review Policy

- Risks with status `RESOLVED` are kept for institutional memory.
- New risks are appended with the next sequential number.
- Severity ratings: 🔴 Critical (blocks execution), 🟠 High (causes incorrect behavior), 🟡 Medium (causes degraded operation), 🟢 Low (cosmetic or theoretical).
- This file is a **companion** to `operator_invariants.json` — not a replacement for inline doctrine.
