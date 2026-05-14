# 🛠️ Antigravity Self-Repair System

This workflow automates the detection of code issues via `current_issues` and provides a one-click mechanism to deploy an AI Agent to fix them autonomously.

## 📋 Prerequisites



* **Agent Permissions:**


    * **Terminal:** Set to "Turbo" (Always Allow).


    * **File Edits:** Set to "Always Proceed".


* **OS:** macOS (for Notifications/Automator steps).

## 1. The Daily Watchdog (Background)

**File:** `~/daily_fix_prep.sh`
**Purpose:** Runs every morning. If issues are found, it generates a log file, sends a desktop notification, and launches the Agent.

**Configuration:**
Ensure the `PROJECT_PATH` in `~/daily_fix_prep.sh` points to your project root.
Default: `/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/aiyou-fastapi-services/erik-hancock-llm-memory`

**Schedule (Cron):**
Run `crontab -e` and add:

```bash
0 8 * * * /Users/pikeymickey/daily_fix_prep.sh

```

## 2. The Manual Trigger (Terminal)

**Setup:**
Source the provided setup script in your `~/.zshrc` or `~/.bashrc`:

```bash
source /Users/pikeymickey/Documents/Claude\ Code/Code/Claude\ Demo/aiyou-fastapi-services/erik-hancock-llm-memory/scripts/fixloop_setup.sh

```

**Usage:**
Type `fixloop` in your terminal.


* **Success:** Prints green success message.


* **Failure:** Copies the error and the Agent Instructions to your clipboard automatically.

## 3. The Zero-Click "Ghost" Trigger

**File:** `~/trigger_agent.scpt`
**Purpose:** AppleScript that wakes the Antigravity app, opens the Agent panel, and types "FIX".
**Trigger:** Automatically called by `daily_fix_prep.sh` if errors are found.

## 4. The Agent Protocol

**File:** `.cursorrules`
**Purpose:** Tells the Agent exactly what to do when it sees the word "FIX".


* Reads `agent_todo.txt`.


* Fixes code.


* Verifies with `scripts/current_issues.sh`.


* Loops until success (Max 3 retries).

## 5. Maintenance

**Reset Logs:**
Run `~/reset_agent.sh` or alias `wipe` to clear old logs.

**Update Extensions:**
Run `python3 install_best_slant.py` to sync the "Golden Slant" of extensions.
