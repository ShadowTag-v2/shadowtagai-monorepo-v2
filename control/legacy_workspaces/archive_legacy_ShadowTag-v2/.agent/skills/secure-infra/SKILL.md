---
name: Secure Infrastructure Automation
description: Native Python scripts to automate GitHub and PostgreSQL operations without requiring active MCP server background processes.
---

# Secure Infrastructure Automation Skill

This skill provides native Python scripts that the agent can execute directly via the shell to interact with GitHub and PostgreSQL. By using these scripts, the agent avoids relying on external, constantly running Node.js MCP server background processes that might crash on window reloads or pose security daemon risks.

## Available Tools

### 1. PostgreSQL Automation (`my_postgres.py`)
Used to natively query databases, check schemas, and execute SQL statements via `psycopg2` or `asyncpg`.
**Usage:** `python3 .agent/skills/secure-infra/scripts/my_postgres.py "SELECT * FROM users LIMIT 5;"`

### 2. GitHub Automation (`my_github.py`)
Used to natively interact with the GitHub API (PRs, issues, repository metadata) via `requests` and a Personal Access Token (PAT).
**Usage:** `python3 .agent/skills/secure-infra/scripts/my_github.py --action list_issues --repo owner/repo`

### 3. Key-Value Memory Store (`my_memory.py`)

Acts as a high-concurrency robust local JSON memory vault (`.beads/agent_memory.json`). Replaces Redis/Memory MCP servers. Uses `fcntl` locks to prevent corruption under multi-agent pressure.
**Usage:** `python3 .agent/skills/secure-infra/scripts/my_memory.py --set "goal" "extracting 52 repos"`

### 4. Slack Automation (`my_slack.py`)

Posts messages natively to Slack channels via the Web API. Requires `SLACK_BOT_TOKEN` in `.env`.
**Usage:** `python3 .agent/skills/secure-infra/scripts/my_slack.py --send "#general" "Omni-Sweep is at 50%"`

### 5. Linear Automation (`my_linear.py`)

Queries and mutates issues on Linear via GraphQL. Requires `LINEAR_API_KEY` in `.env`.
**Usage:** `python3 .agent/skills/secure-infra/scripts/my_linear.py --action list_issues`

## Instructions for Agent
1. Whenever the user asks to query the database, do NOT ask for an MCP server. Simply formulate the SQL query and pass it to `my_postgres.py`.
2. Whenever the user asks to interact with GitHub issues or PRs remotely, pass the request to `my_github.py`.
3. Ensure the `.env` file contains `DATABASE_URL` and `GITHUB_PAT` before executing.
