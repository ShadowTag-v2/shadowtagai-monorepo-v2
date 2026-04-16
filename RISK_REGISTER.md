# RISK_REGISTER — v8.4

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
| 14 | GitHub App JWT hardcoding — single point of failure | 🟠 High | GOVERNED | App ID scoped to `contents:write` + `pull-requests:write` on single repo only. `gh auth login` retained as manual repair fallback. |
| 15 | Bounded YOLO (`agentYoloMode=true`) auto-approval | 🟢 Low | MITIGATED | Destructive tools (`rm -rf`, `sudo`) physically excluded from MCP schema. Model cannot call tools that do not exist. |
| 16 | `git reset --hard` (Temporal Reversal) wipes uncommitted work | 🟠 High | GOVERNED | Reset ONLY authorized via Temporal Reversal state machine. Stash → reset to `latest-stable` → branch → fix via TDD. |
| 17 | `git push --force` overwrites remote history | 🔴 Critical | GOVERNED | Bound by Squash-Push Protocol. Must use `--force-with-lease` first. Escalate to `--force` ONLY after fetching origin to verify tracking refs. |
| 18 | No Firestore security rules deployed on any database | 🔴 Critical | RESOLVED | Zero-trust rules deployed to `firestore.rules`. Default deny-all with admin-only access. Deployed via `firebase deploy --only firestore:rules`. |
| 19 | No Storage security rules deployed | 🔴 Critical | RESOLVED | Locked-down `storage.rules` deployed. Default deny-all — no storage actively used. |
| 20 | `shadowtagai.com` ACME 403 — conflicting Squarespace DNS | 🟠 High | KNOWN | Squarespace retains A/CNAME records that override Firebase Hosting verification. **Action**: Log in to Squarespace DNS → delete the A records (198.185.159.x) and CNAME → re-run `firebase hosting:channel:deploy` for `shadowtagai` target → verify TXT ownership record. |
| 21 | `knowledge-base-database` — undocumented, empty, no delete protection | 🟡 Medium | RESOLVED | Deleted 2026-04-16. Confirmed zero collections before deletion. `previousId: knowledge-base-database`, `uid: d1a319bc-f657-42ff-a608-105bf9968e5f`. |
| 22 | No Firestore monitoring alerts deployed | 🟡 Medium | MITIGATED | Alerting requires: (1) `metric.type="firestore.googleapis.com/document/read_count"` threshold alert at 10K/5min, (2) `metric.type="firestore.googleapis.com/document/write_count"` threshold at 5K/5min, (3) `metric.type="firestore.googleapis.com/api/request_count"` with `response_code!=200` for error rates. Configure via Cloud Console → Monitoring → Alerting → Create Policy. Notification channel: `founder@shadowtagai.com`. |
| 23 | Firebase Hosting auto-gzip breaks video playback | 🟠 High | RESOLVED | Firebase Hosting applies `Content-Encoding: gzip/br` to MP4 files, causing `ERR_CONTENT_DECODING_FAILED` in Chrome's video decoder. **Fix:** Serve video assets from GCS (`gs://shadowtag-omega-v4-archive/hero-videos/`) instead. CSP `media-src` updated to whitelist `https://storage.googleapis.com`. |
| 24 | GCS bucket CORS not configured for cross-origin streaming | 🟡 Medium | RESOLVED | `shadowtag-omega-v4-archive` bucket had no CORS policy. Configured `GET`/`HEAD` from all 5 production origins with `Content-Range`/`Accept-Ranges` response headers. Max-age 86400s. |

## Review Policy

- Risks with status `RESOLVED` are kept for institutional memory.
- New risks are appended with the next sequential number.
- Severity ratings: 🔴 Critical (blocks execution), 🟠 High (causes incorrect behavior), 🟡 Medium (causes degraded operation), 🟢 Low (cosmetic or theoretical).
- This file is a **companion** to `operator_invariants.json` — not a replacement for inline doctrine.
