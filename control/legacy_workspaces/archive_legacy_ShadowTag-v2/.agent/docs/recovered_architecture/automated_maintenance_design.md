# Design Specification: Automated System Maintenance (Janitor)

## 1. Overview

A "Janitor" system to automate the health and hygiene of the development environment. It leverages the existing `FlyingMonkeys` swarm capabilities (specifically `CODEPMCS` and `devops` specialists) to perform regular cleanup, updates, and memory consolidation.

## 2. Requirements

### 2.1 Core Components


1. **Monitor (`monitor.py`)**: A lightweight daemon or cron job that checks system health.

    * *Metrics*: CP usage, process uptime, git status, disk usage.

    * *Triggers*: "High CPU > 1h", "Uncommitted changes > 4h", "Daily Schedule".

2. **Janitor Agent (`janitor.py` or new `FlyingMonkey` skill)**:

    * *Safety*: Must verify "SafeToAutoRun" for all commands.

    * *Capabilities*:

        * Kill stuck processes (identifiable by regex/time).

        * Auto-squash git changes (with "WIP" prefix if unsure).

        * Run system update scripts.

        * Synthesize memory (LLM-based).

3. **Config (`janitor_config.yaml`)**:

    * Allowed processes to kill.

    * Excluded directories.

    * Update schedules.

### 2.2 Frequency Strategy

| Tier | Frequency | Actions |
| :--- | :--- | :--- |
| **Real-time** | Continuous | Monitor for "Runaway Processes" (e.g., recursive grep, stuck builds). Notify user if > 100% CPU for 10m. |
| **Hourly** | Every 60m | Check for uncommitted git changes. If > 1h idle, auto-commit as `backup: [timestamp]`. |
| **Daily** | 02:00 Local | Full System Sweep: Kill all dev servers, run `brew update`, synthesize daily `memory.md` summary. |
| **Weekly** | Sunday | Deep Clean: Delete temp files, prune docker images, full re-index of codebase. |

## 3. Integration with FlyingMonkeys

We will add a new **Troop** or **Specialization** to `agents/flying_monkeys.py`:

- **Role**: `JANITOR` (Sub-role of `devops` or `CODEPMCS`).

- **Traits**: "Obsessive Cleaner", "Zero Entropy".

- **Tool Access**: `bash`, `file_io`, `git`.

## 4. Implementation Steps


1. **Scaffold**: Create `src/ultrathink/agents/janitor.py`.

2. **Script**: Convert `update_system.sh` into a Python tool accessible by the agent.

3. **Schedule**: Generate a `launchd` plist for macOS automation.

## 5. Safety & Risk


- **Risk**: Killing a process the user is using.

- **Mitigation**: "Ask User" mode for uncertain processes, or only kill known-bad signatures (e.g., `gcloud` stuck).
