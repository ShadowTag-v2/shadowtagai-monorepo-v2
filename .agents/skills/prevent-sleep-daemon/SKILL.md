# Prevent Sleep Daemon

## Overview
This skill codifies the behavior of preventing the host machine or IDE from sleeping during long-running asynchronous tasks (e.g., mass refactoring, deployment, or mass ingestion). It was harvested from the `preventSleep.ts` architecture.

## Execution
- **macOS:** Wrap long-running shell commands with `caffeinate -i -s -u <command>`.
- **Linux:** Use `systemd-inhibit <command>`.
- **Node/Python:** If implementing a daemon, use native OS bindings or subprocess calls to acquire wake locks.

## Rules
1. Do NOT acquire wake locks for tasks expected to finish in under 60 seconds.
2. Always ensure the wake lock is released upon task completion, failure, or panic.
3. Log sleep prevention acquisition to `.beads/issues.jsonl` if the task is critical.
