# ShadowTag Truth Map

Last verified: 2026-03-08

Purpose: separate repo reality from stale snippets, planning language, and prompt-theater.

How to read this:
- Rows are grouped by status.
- `Claim` is the assertion being checked.
- `Current reality` is the shortest defensible statement of fact.
- `File/source of truth` points to the local repo artifact used to verify it.

## Implemented

| Claim | Current reality | File/source of truth |
|---|---|---|
| `Tools Config Path` should be `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/database_tools.yaml`. | The file exists at that exact absolute path. | [`database_tools.yaml`](database_tools.yaml) |
| `python3 tools/gca_god_mode_bridge.py status` works. | Verified. The bridge starts `scripts/god_mode_admin.py`, sends `status`, then `stop`, and exits cleanly. | [`tools/gca_god_mode_bridge.py`](tools/gca_god_mode_bridge.py), [`scripts/god_mode_admin.py`](scripts/god_mode_admin.py) |
| `python3 tools/gca_god_mode_bridge.py json '{"task": "do something"}'` works. | Verified. The JSON task is received and acknowledged, and the engine shuts down cleanly. | [`tools/gca_god_mode_bridge.py`](tools/gca_god_mode_bridge.py), [`scripts/god_mode_admin.py`](scripts/god_mode_admin.py) |
| `scripts/gcloud_auth_solver.py` and `scripts/omega_auth_daemon.py` are the auth heartbeat pair. | Both files exist, and the daemon/check loop now uses `.pids/omega_daemon.pid`. | [`scripts/gcloud_auth_solver.py`](scripts/gcloud_auth_solver.py), [`scripts/omega_auth_daemon.py`](scripts/omega_auth_daemon.py), [`scripts/omega-loopin.py`](scripts/omega-loopin.py) |
| `scripts/finish_changes.py` is the janitor/egress script. | The file exists and is the current cleanup/stage/commit script. | [`scripts/finish_changes.py`](scripts/finish_changes.py) |
| The God Mode doctrine references `@.agent/workflows/live-engine.md`, `@.agent/docs/toolbelt.md`, and `@.agent/rules/shadowtag-laws.md`. | All three files exist and are the main repo-local doctrine sources for that flow. | [`.agent/workflows/live-engine.md`](.agent/workflows/live-engine.md), [`.agent/docs/toolbelt.md`](.agent/docs/toolbelt.md), [`.agent/rules/shadowtag-laws.md`](.agent/rules/shadowtag-laws.md) |
| `MODE: LIVE FIRE (NO SIMULATION)` is current doctrine. | That wording appears in the local live-engine workflow. | [`.agent/workflows/live-engine.md`](.agent/workflows/live-engine.md) |
| `agents/gemini_code_assist_proxy.py` supports direct-write preview bypass after Judge approval. | The current proxy directly writes approved code and returns `APPLIED_AUTOMATICALLY`; otherwise it returns a diff. | [`agents/gemini_code_assist_proxy.py`](agents/gemini_code_assist_proxy.py) |
| The project direction is `Cloud Run ONLY`. | This is explicitly documented as the target hosting model. | [`MIGRATION_PLAN_CLOUD_RUN.md`](MIGRATION_PLAN_CLOUD_RUN.md), [`deploy_cor58_uphillsnowball.sh`](deploy_cor58_uphillsnowball.sh) |
| A two-container Cloud Run service definition exists for brain + jetski. | A real `service.yaml` exists with a main container and a `jetski-sidecar` container. | [`service.yaml`](service.yaml) |
| `deploy_cor58_uphillsnowball.sh` deploys Judge, Jetski, and SeatJudge to Cloud Run. | The script exists and contains `gcloud run deploy` calls for those services. | [`deploy_cor58_uphillsnowball.sh`](deploy_cor58_uphillsnowball.sh) |
| `libs/steel/sentinel.py` is part of the system. | The file exists. | [`libs/steel/sentinel.py`](libs/steel/sentinel.py) |
| `apps/src/api/stripe_webhook.py` and `apps/src/api/copilot_proxy.py` are present. | Both files exist. | [`apps/src/api/stripe_webhook.py`](apps/src/api/stripe_webhook.py), [`apps/src/api/copilot_proxy.py`](apps/src/api/copilot_proxy.py) |
| `auto_finish.sh` now works because it separates logs from protocol JSON. | The script redirects logs to `stderr`, preserves original stdout on FD 3, and emits `{"decision":"allow"}` on the clean channel. | [`scripts/auto_finish.sh`](scripts/auto_finish.sh) |
| The `auto_finish.sh` explanation about `exec 1>&2`, `exec 3>&1`, and a clean JSON handshake is accurate. | That description matches the actual shell script. | [`scripts/auto_finish.sh`](scripts/auto_finish.sh) |
| A custom Python linter is linked into `.git/hooks`. | The current `.git/hooks/pre-commit` runs `python3 scripts/design_police_linter.py` against staged UI files. | [`.git/hooks/pre-commit`](.git/hooks/pre-commit), [`scripts/design_police_linter.py`](scripts/design_police_linter.py) |
| `cor-30-vibe-coding.md` exists. | The file exists and contains OWASP-flavored security guardrails for AI/vibe coding. | [`.agent/rules/cor-30-vibe-coding.md`](.agent/rules/cor-30-vibe-coding.md) |
| `/pnkln-sweep` exists as a mission directive. | A repo-local workflow file exists describing the pnkln engineering sweep mission. | [`.agent/workflows/pnkln-sweep.md`](.agent/workflows/pnkln-sweep.md) |

## Partial

| Claim | Current reality | File/source of truth |
|---|---|---|
| `scripts/god_mode_admin.py` is a simple loop that just initializes `VelocityEngine()` and sits in `while True: pass`. | It does initialize `VelocityEngine`, but the current file is an stdin command loop with `status`, `sync`, `shell`, `json`, and `stop`. | [`scripts/god_mode_admin.py`](scripts/god_mode_admin.py) |
| `scripts/god_mode_admin.py` is "active but unstable" because of `asyncpg` warnings. | `asyncpg` references exist under `libs/steel`, but that warning is not a proven direct property of the current `god_mode_admin.py` run path. | [`scripts/god_mode_admin.py`](scripts/god_mode_admin.py), [`libs/steel/retrieve_memory.py`](libs/steel/retrieve_memory.py), [`libs/steel/write_memory.py`](libs/steel/write_memory.py) |
| `COMMAND: EXECUTE /live-engine` is a canonical repo command. | It is canonical doctrine language, but not a verified executable shell command or IDE command implementation in this repo. | [`.agent/workflows/live-engine.md`](.agent/workflows/live-engine.md) |
| "Directory Access" and "Accept All Changes" are granted. | This is true as repo-local doctrine and `.agent` config, not as proof of OS-level or IDE-global privilege escalation. | [`.agent/workflows/live-engine.md`](.agent/workflows/live-engine.md), [`.agent/rules/shadowtag-laws.md`](.agent/rules/shadowtag-laws.md), [`.agent/config.json`](.agent/config.json) |
| The workflow iterates open tabs, fixes lint/import/formatting, rewrites secrets to `os.getenv()`, uses web/drive resources, and recurses. | That behavior is written as doctrine, but it was not verified here as an active IDE-native automation loop controlling editors on its own. | [`.agent/workflows/live-engine.md`](.agent/workflows/live-engine.md), [`.agent/rules/shadowtag-laws.md`](.agent/rules/shadowtag-laws.md) |
| `scripts/finish_changes.py` matches the pasted hardened janitor script exactly. | It plays that role, but the current implementation differs. It uses a PIIAA scan and a fixed commit message, not the pasted timestamped deploy message. | [`scripts/finish_changes.py`](scripts/finish_changes.py) |
| `scripts/god_mode_admin.py`, `scripts/finish_changes.py`, `scripts/ingest_drive_docs.py`, `tools/gca_god_mode_bridge.py`, and `scripts/omega_auth_daemon.py` are all "Active". | They exist, but they were not all running as live processes when checked. Existence is not runtime activity. | Repo process check on 2026-03-08 |
| Browser-DOM / reverse-engineered Jetski capabilities are already fully wired as runnable code. | The repo contains sidecar docs, reverse-engineering notes, and deployment scripts, but the exact implementation files described in the pasted sidecar plans are not all present. | [`ANTIGRAVITY_REVERSE_ENGINEERING.md`](ANTIGRAVITY_REVERSE_ENGINEERING.md), [`service.yaml`](service.yaml), [`deploy_cor58_uphillsnowball.sh`](deploy_cor58_uphillsnowball.sh) |
| The "Monkeys", "Judge 6", voting loop, and memory-layer architecture are current system reality. | These are clearly core doctrine and partially represented in code, but not as one single verified runtime loop at the exact pasted paths. | [`libs/steel/sentinel.py`](libs/steel/sentinel.py), [`.agent/rules/shadowtag-laws.md`](.agent/rules/shadowtag-laws.md), repo governance docs/code |
| `cor-30-vibe-coding.md` is fully enforced across the repo. | The file exists and the design linter cites `COR.30`, but the full rule set in that doc is broader than what the current hook automation enforces. | [`.agent/rules/cor-30-vibe-coding.md`](.agent/rules/cor-30-vibe-coding.md), [`.git/hooks/pre-commit`](.git/hooks/pre-commit), [`scripts/design_police_linter.py`](scripts/design_police_linter.py) |
| `/pnkln-sweep` is an active executed mission, not just a directive. | The workflow file exists, but this verification only confirms the directive document, not that the mission has been run to completion. | [`.agent/workflows/pnkln-sweep.md`](.agent/workflows/pnkln-sweep.md) |

## Proposed

| Claim | Current reality | File/source of truth |
|---|---|---|
| The repo currently has a live `src/governance/voting/spm_engine.py` implementing the full Self-Prompting Monkeys loop. | The architecture is discussed extensively, but the quoted SPM engine reads as design/planning language rather than a verified current implementation at that path. | Repo search on 2026-03-08 found doctrine and related code, but no exact current file at the quoted path |
| Gemini Code Assist memory integration, BigQuery-backed session memory, and multi-round rule learning are fully implemented now. | This reads as planning / strategy material. Memory-related code exists, but the pasted end-to-end architecture was not verified as current runtime. | Governance/memory docs and code found by repo search on 2026-03-08 |
| The "4-iteration Golden 4" self-prompting loop is a current enforced runtime rule. | This appears as architecture and business guidance, not as verified enforcement code. | Strategy text only; no exact enforcement file verified |
| Browser DOM should be used proactively and persistently for research/troubleshooting without user involvement. | This is a desired operating doctrine in prompt language and reverse-engineering notes, not a verified always-on repo automation switch. | Reverse-engineering and strategy docs; no single global enforcement file verified |
| GCA/local IDE can automatically "accept all" and continuously finish changed open editors via slash commands. | This appears in prompt/policy language, but no repo-wide implementation proving that behavior was verified here. | Prompt language only; no exact current implementation was confirmed |
| A two-sidecar Jetski implementation using the exact pasted `src/jetski/server.py`, `browser_engine.py`, and `deploy_jetski.sh` is already operational. | The repo contains adjacent strategy/deployment artifacts, but this exact implementation remains a plan more than a verified local runtime. | [`service.yaml`](service.yaml), [`deploy_cor58_uphillsnowball.sh`](deploy_cor58_uphillsnowball.sh) |
| The TAM, pricing, margin, ARR, and "$100M+ / $1T vertical" claims are measured business facts. | These are strategy/opinion statements, not repo-verifiable financial facts. | Narrative/business text only |

## Absent

| Claim | Current reality | File/source of truth |
|---|---|---|
| `scripts/omega_port_executioner.py` is active. | No file exists at that path. | Absence confirmed on 2026-03-08 by file check |
| `workbench.action.nextEditor` recursion is implemented in current repo automation. | No verified implementation was found in current repo code. | Repo search on 2026-03-08 found no executable implementation |
| `scripts/ingest_drive_docs.py` avoids cloud dependencies and talks to `http://127.0.0.1:8080`. | The current file uses `google.genai`, a Gemini model, and `GEMINI_API_KEY`; it does not implement the pasted localhost ANE bridge. | [`scripts/ingest_drive_docs.py`](scripts/ingest_drive_docs.py) |
| `biome.json` excludes `apps/external_sdks/**`, uses schema `2.4.5`, and uses tabs. | The current file uses schema `1.9.4`, spaces, and no `apps/external_sdks/**` ignore block. | [`biome.json`](biome.json) |
| `.vscode/settings.json` matches the large pasted ShadowTag Omega block. | The current file is much smaller and mainly covers Java runtimes, Bazel, and a direct `biome.lspBin`. | [`.vscode/settings.json`](.vscode/settings.json) |
| `microsoft-25.jdk` was fixed to `temurin-25.jdk` in the repo-local VS Code settings. | Neither string is the current repo-local truth; the file points at `/opt/homebrew/opt/openjdk@25`. | [`.vscode/settings.json`](.vscode/settings.json) |
| Branch `feat/financial-stripe-copilot` is the current branch. | It exists locally, but the verified current branch was `omnibus-agent-squash`. | Git branch state checked on 2026-03-08 |
| `src/jetski/server.py`, `src/jetski/browser_engine.py`, and `scripts/deploy_jetski.sh` exist at those exact paths. | Those exact files were not present when checked. | Absence confirmed on 2026-03-08 by file check |
| `third_party/servers` contains the 10 extracted standard-issue MCP servers. | `third_party/servers` does not exist in the current repo, so this extraction claim is not true as stated. | Absence confirmed on 2026-03-08 by file check |
| There is a verified "clone the user's gitignore repo" constraint wired into the current hooks/linter flow. | No evidence of that specific constraint was found in the current repo. The hook wiring that does exist is the local design linter. | [`.git/hooks/pre-commit`](.git/hooks/pre-commit), repo search on 2026-03-08 |
| NOPASSWD sudo and unrestricted direct system access are provable repo truths. | These are host/environment policy claims, not facts this repo can prove from code or files. | Outside repo scope |

## Checked In This Pass

| Claim | Current reality | File/source of truth |
|---|---|---|
| The latest request to check hook wiring, `/pnkln-sweep`, `third_party/servers`, and `cor-30-vibe-coding.md` is reflected in this truth map. | This pass added explicit rows for those claims and regrouped the map by status. | [`TRUTH_MAP.md`](TRUTH_MAP.md) |

