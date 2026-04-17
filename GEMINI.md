---
version: 8.5
scope: antigravity_local_operator_invariants
status: LOCKED
---

# GEMINI.md — v8.5

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
5. **Verify**: Delegate to `browser_subagent` for Lighthouse/responsive audits.

### Auth Refresh (only authorized CLI command for auth)
If auth is expired: `npx -y firebase-tools@latest login --reauth`

### Skill Reference
Full doctrine: `skills/firebase-mcp-deploy-doctrine/SKILL.md`
</firebase_mcp_doctrine>

<github_doctrine>
- ALL git operations MUST target `git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git` (SSH PRIMARY).
- GitHub App: ID `3018200`, Client ID `Iv23ctYqrxPQIt2ir8gY`, PEM at `$SHADOWTAG_PEM` (see WORKSTATION_LOCAL_OVERRIDES).
- SSH is the mandatory transport for push/pull. HTTPS is last-resort fallback only.
- GitHub App JWT is for API operations (PRs, issues, releases) ONLY.
- **Deploy keys are NOT acceptable. GitHub Apps are the required model.**
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

<env_master_doctrine>
## .env Master Environment Doctrine

**Canonical path:** `.env` (repo root, gitignored)
**Created:** 2026-04-13 | **Sections:** 10

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

### Auth Chain
- **MCP servers** authenticate via Google ADC (`~/.config/gcloud/`) + `GEMINI_API_KEY` from `.env`
- **Firebase MCP** uses its own OAuth session (not `.env`)
- **GitHub** uses SSH keys + GitHub App PEM (`$SHADOWTAG_PEM`)
- **Stitch MCP** uses `STITCH_API_KEY` from `.env`

### Missing Keys (NOT in .env)
> [!WARNING]
> The following keys are required for CounselConduit production but are NOT yet provisioned:
> - `STRIPE_SECRET_KEY` — needed for billing
> - `STRIPE_WEBHOOK_SECRET` — needed for webhook verification
> - See `apps/counselconduit/.env.example` for the full CounselConduit-specific config

### Rules
- `.env` is gitignored. NEVER commit it.
- `apps/counselconduit/.env.example` is the template for product-specific vars.
- All MCP servers MUST read from `.env` or ADC. No hardcoded keys in source.
</env_master_doctrine>
</system_directive>
