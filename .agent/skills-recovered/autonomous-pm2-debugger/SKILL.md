---
name: autonomous-pm2-debugger
description: Empowers the agent to autonomously fetch backend logs and debug Node/Python services using PM2 without requiring user intervention.
---

# Autonomous PM2 Debugger

Use this skill when working with backend microservices, when a service crashes, or when the user mentions errors in a running daemon/server.

## Core Philosophy
Do NOT rely on the user to be a "human log-fetching service." If a backend service is failing, you have the autonomy and the tools to find out why yourself. 

## Execution Protocol

### 1. Investigate via PM2 Logs
If the user states a service is failing (or if you suspect a backend error), DO NOT ask them to paste the logs.
Instead, autonomously use the `run_command` tool to execute:
`pm2 logs <service_name> --lines 200`
Parse the output to identify the exact stack trace, database connection timeout, or runtime error.

### 2. Monitor CPU/Memory
If performance is degraded or a process loops, run:
`pm2 monit` or `pm2 list` to check the status, memory consumption, and restart counts of the services.

### 3. Autonomously Restart & Fix
Once the log is analyzed:
1. Identify the buggy file (e.g., `src/api/controller.ts`).
2. Fix the code using the appropriate code editing tools.
3. Automatically restart the service to apply the fix:
`pm2 restart <service_name>`
4. Verify the fix by checking the logs one final time before reporting back to the user.

## Configuration Awareness
If PM2 is not yet configured, proactively suggest creating an `ecosystem.config.js` file to manage the microservices so you can properly leverage this autonomous debugging workflow in the future.
