---
id: "architecture-tool-gateway-v1"
created: "2026-04-27T17:52:00Z"
updated: "2026-04-27T17:52:00Z"
category: architecture
tags: [tool-gateway, contracts, preconditions, evidence]
references:
  - file:///tool_contracts/github_push.yaml
  - file:///tool_contracts/firebase_deploy.yaml
  - file:///tool_contracts/repo.secret_scan.yaml
  - file:///tool_contracts/index.query.yaml
  - file:///tool_contracts/large_file_scan.yaml
status: active
---

# ToolGateway Contract Architecture

## Purpose

Every agent action that modifies external state must pass through a
ToolGateway contract. Contracts define preconditions, required evidence,
blocking conditions, and reuse hints.

## Contract Registry

| Contract | Risk | Preconditions |
|----------|------|---------------|
| `github.push` | high | auth, branch, betterleaks, lint |
| `firebase.deploy` | high | auth, build, test, betterleaks |
| `repo.secret_scan` | high | scanner available |
| `index.query` | low | index freshness |
| `large_file_scan` | medium | file size limits |

## Evidence Chain

Every tool invocation produces evidence:
1. Contract checked → logged to `.beads/issues.jsonl`
2. Preconditions evaluated → pass/fail recorded
3. Tool executed → output evidence to `.agent/evidence/`
4. Result recorded → final status to issues.jsonl

## Reuse Hints

Contracts include reuse hints to prevent duplicate work:
- "Script already exists in scripts/"
- "Report already generated in .reports/"
- "Previous scan passed within 5 minutes"

## Blocking Rules

Hard blocks that cannot be overridden:
- Verified live secret in staged changes
- Private key in staged changes
- Service account JSON in staged changes
- File exceeding 95 MiB size limit
