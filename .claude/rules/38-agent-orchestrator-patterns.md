# Rule 38: Agent Orchestrator Patterns
# Source: ComposioHQ/agent-orchestrator architecture analysis
# Created: 2026-04-11

## Purpose
Codifies production-grade multi-agent orchestration patterns extracted from the Agent Orchestrator (AO) platform.

## 8-Slot Plugin Architecture

When building agent orchestration systems, enforce this plugin slot taxonomy:

| Slot | Purpose | Example |
|------|---------|---------|
| 1. Agent | LLM execution engine | claude-code, aider, codex |
| 2. Runtime | Process isolation | tmux, Docker, process |
| 3. Workspace | Code isolation | git-worktree, clone |
| 4. Tracker | Issue/task tracking | github, linear, gitlab |
| 5. SCM | Source control ops | github, gitlab |
| 6. Notifier | Alert delivery | desktop, slack, webhook |
| 7. Terminal | UI transport | iterm2, web, xterm |
| 8. Storage | State persistence | file, database |

## Lifecycle State Machine

All agent sessions must follow this state machine:
```
CREATED → PROVISIONING → RUNNING → COMPLETING → COMPLETED
                ↓                      ↓
            FAILED                  FAILED
```

## Configuration Pattern
- Use YAML for human-editable agent config (`agent-orchestrator.yaml`)
- Use Zod for runtime validation of config schemas
- Never trust agent self-reports — verify via VCS diff

## Session Management
- One agent per independent problem domain
- Each agent gets its own git worktree (isolation)
- Never share state between parallel agents
- Dispatch → Monitor → Review → Integrate

## Key Principle
> "Agents autonomously fix CI failures, address review comments, and manage PRs."
> But: Always verify agent output independently before integration.
