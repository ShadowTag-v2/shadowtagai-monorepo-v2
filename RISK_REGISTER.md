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

## Review Policy

- Risks with status `RESOLVED` are kept for institutional memory.
- New risks are appended with the next sequential number.
- Severity ratings: 🔴 Critical (blocks execution), 🟠 High (causes incorrect behavior), 🟡 Medium (causes degraded operation), 🟢 Low (cosmetic or theoretical).
- This file is a **companion** to `operator_invariants.json` — not a replacement for inline doctrine.
