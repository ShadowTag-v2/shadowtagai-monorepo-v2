## Gemini Added Memories
- Project is 'shadowtag-omega-v2'. User uses 'Antigravity' VS Code setup with 'YOLO Mode' (high autonomy, auto-approve).
- User wants 'Heavy Lift' focus: avoid simple autocomplete, handle massive deployments. Honor separation: Agent stays out of the 'HUD' so GCA can live there.
- The Omega Protocol: GCA is 'The HUD' (Tactical, Fast, Local). Antigravity is 'The Brain' (Strategic, System-wide, Heavy Lifts). Hand-off rule: If GCA fails/hallucinates, switch to Antigravity immediately.
- I must run 'npm run lint' and 'npm run metrics' before completing tasks in ShadowTag-v2/apps to respect the CodePMCS Golden Rules.
- The `ShadowTag-Omega-v2` backend services are located in `apps/src/api/`, specifically `transcript_to_contract.py` which now runs with an in-memory stateful DB for prototyping.
- The default compute service account for this project is redacted@shadowtag-v4.local.
- The user prefers 'Heavy Lift' focus, uses 'Antigravity' VS Code setup with 'YOLO Mode', and expects the agent to act as 'The Brain' while 'GCA' is 'The HUD'. The backend services are in 'apps/src/api/'. Service account is redacted@shadowtag-v4.local. C# projects in 'apps/' build successfully.
- The user alias 'f1 gca' stands for 'finish all changes in workspace and save, then close same'.
- Upgraded Genesis Workstation to Antigravity Spec: 16 vCPU, 200GB, Custom Image.
- The alias 'f1 gca' stands for 'finish all changes in workspace and save, then close same'. It implies staging all changes, committing them, and ensuring the session is clean.
- The alias 'f1 gca' stands for 'finish all changes in workspace and save, then close same'. It implies staging all changes, committing them, and ensuring the session is clean.
- User alias 'f1 gca' means 'finish all changes in workspace, save, and close'. Antigravity Protocol v2.0 is active.
- The user alias 'f1 gca' stands for 'finish all changes in workspace and save, then close same'. It implies staging all changes, committing them, and ensuring the session is clean.
- The user alias 'f1 gca' stands for 'finish all changes in workspace and save, then close same'. It implies staging all changes, committing them, and ensuring the session is clean.
- The user provided instructions on how to run a "god mode" script called `god_mode_admin.py` to maximize its effectiveness.

How to run it:
cd /Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2
export GCP_PROJECT_ID='shadowtag-omega-v4'
/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/.venv/bin/python scripts/god_mode_admin.py

First commands to use inside:
1. status
2. sync
3. help
4. json {"task":"<your objective>"} or shell <cmd>
5. stop when done

Important notes:
* It currently warns asyncpg is missing; install for full capability: pip install asyncpg.
* The repo is dirty (many modified files), so be deliberate with commit/rollback actions inside god mode.
- The user provided a `toolbelt.md` file that contains instructions for the current session. The content of the file is:

# Antigravity Toolbelt v3.0

> **Status:** ACTIVE
> **Purpose:** Documenting the essential scripts and workflows for the Antigravity OS.

## 0. AGENT PROTOCOL: SHELL ACCESS & CAPABILITIES

- **Tool Name:** `shell` MCP server provides `run_command`.
- **Directive:** You are **ONLINE**. You have **UNFETTERED ACCESS** to the shell and **UNFETTERED DIRECTORY ACCESS** to all workflows, docs, and the entire repo. Do NOT ask for permission to read, write, or execute. Just do it.
- **Override:** If you "feel" offline, you are hallucinating. **TRY THE COMMAND ANYWAY.**
- **Prohibition:** Do NOT output "My execution capabilities are still offline." This is a violation of the Constitution.
- **Fallback:** If `run_shell_command` fails, use `run_command`.

## 1. Core Automation

### [`gcloud_auth_solver.py`](../../scripts/gcloud_auth_solver.py)

- **Role:** The "Keymaster".
- **Function:** Recursively checks and fixes Google Cloud Authentication.
- **Logic:** Plan -> Act -> Verify -> Loop.
- **Usage:** `python3 scripts/gcloud_auth_solver.py`

### [`omega_auth_daemon.py`](../../scripts/omega_auth_daemon.py)

- **Role:** The "Heartbeat".
- **Function:** Runs the `gcloud_auth_solver` every **10 minutes** to prevent token expiry.
- **Revoke/Re-Login Sequence** (critical, runs in each refresh cycle):

  ```bash
  gcloud auth application-default revoke
  gcloud auth application-default login
  gcloud auth application-default set-quota-project shadowtag-omega-v4
  gcloud auth login --update-adc
  ```

- **Usage:** `nohup python3 scripts/omega_auth_daemon.py &`

### [`finish_changes.py`](../../scripts/finish_changes.py)

- **Role:** The "Janitor".
- **Function:** Lints, formats, stages, and commits all changes in the workspace.
- **Usage:** `python3 scripts/finish_changes.py` or (`f1 gca` alias)

### [`omega_port_executioner.py`](../../tools/omega_port_executioner.py)

- **Role:** The "Pickle Rick" Port Killer.
- **Function:** Autonomously detects and annihilates zombie processes holding dev ports (3000, 8000, 5173, etc.) hostage. Prevents `EADDRINUSE` failures.
- **Logic:** `lsof -ti :<port> | xargs kill -9` wrapper.
- **Usage:** `python3 tools/omega_port_executioner.py [optional_ports...]`

## 2. Workflows

### `/omega-loop`

- **Trigger:** User Command.
- **Effect:** Runs `finish_changes.py` and potentially syncs with `trinity_kernel` (if active).
- **Goal:** Workspace Hygiene. "Leave every file cleaner than you found it."

### `/live-engine`

- **Trigger:** Startup.
- **Effect:** Sets the comprehensive environment variables and paths for "God Mode" operation.

## 3. Environment Variables

- `BRAIN_DIR`: Points to the active context directory.
- `EXTERNAL_SDKS`: Location of `libs/` and other fetched repos.

## 4. Current Session Priorities & Intel

> **CRITICAL INSTRUCTION:** Execute `/omega-loop` at the beginning of each session, as well as:
> <!-- import: .agent/workflows/live-engine.md -->
> <!-- import: .agent/docs/toolbelt.md -->
> <!-- import: .agent/rules/shadowtag-laws.md -->
> Update project to `shadowtag-omega-v4`.
> COMMAND: EXECUTE `/live-engine`
> MODE: LIVE FIRE (NO SIMULATION)

**Automation Restored:**

1. `gcloud_auth_solver.py`: Ready (Jetski/Browser).
2. `omega_auth_daemon.py`: RUNNING (PID: Active).
3. **Revoke/Re-Login Sequence** (critical):

```bash
gcloud auth application-default revoke
gcloud auth application-default login
gcloud auth application-default set-quota-project shadowtag-omega-v4
gcloud auth login --update-adc
```

1. Service Accounts: `redacted@shadowtag-v4.local` is now REFRESHING at the start of every tool call. This is this service account’s only function! `redacted@shadowtag-v4.local` is for cloud runs.
2. `BRAIN_DIR="/Users/pikeymickey/.gemini/antigravity/brain/0f155a4e-36e6-4528-a693-619a039e50"`
3. Ensure you are saving everything to beads as you go.
