# Rule 26: Managed Agents Lifecycle & SDK Routing
# Source: Piebald v2.1.97 (Managed Agents onboarding, client patterns, core concepts, endpoint reference)

## Core Lifecycle (Mandatory Order)
When building with the Anthropic Managed Agents API:
1. **Create Environment** → Container config, file resources, GitHub mounts
2. **Create Agent** → Model, tools, skills, permissions, instruction set
3. **Create Session** → Binds Agent to Environment, starts execution
Violation: Creating a session before an agent or environment = 400 error.

## SDK Routing by Language
- **Python**: `anthropic.Anthropic().beta.managed_agents` namespace
- **TypeScript**: `new Anthropic().beta.managedAgents` namespace
- **cURL**: Raw HTTP to `https://api.anthropic.com/v1/managed_agents/`
- **C#**: No native SDK — use cURL/raw HTTP examples
- Auto-detect language from file extensions in the project tree

## Session Event Steering
- Streaming: SSE via `event: message_start | content_block_delta | message_stop`
- Reconnection: pass `last_event_id` header to resume from last checkpoint
- Polling: `GET /sessions/{id}/events?after={cursor}` for non-streaming clients
- Interrupts: `POST /sessions/{id}/interrupt` to break agentic loops
- Message queuing: queue user messages while agent is processing

## Idle-Break Gating
- `max_turns` controls how many agentic loops before yielding back to client
- Default: agent runs until it decides to stop or hits API-imposed limit
- Override: set `max_turns: N` to force yield after N tool-use rounds
- Client must send next message to resume execution after break

## Custom Tool Confirmation Flow
1. Agent proposes tool call → client receives `tool_use` content block
2. Client evaluates → accept (send result) or reject (send error)
3. Agent continues with the result or error
4. Permission policies: `allow`, `confirm`, `deny` per tool category

## Model Defaults & Thinking Config
- Model: defaults to latest Claude (currently claude-sonnet-4-20250514)
- Budget tokens: `thinking.budget_tokens` controls extended thinking depth
- Effort: maps to `effort_level`: "low" | "medium" | "high"
- Temperature: 0.0 for code generation, 1.0 for creative tasks

## Memory & Skills Integration
- Skills: `.claude/skills/*.md` files mounted as agent knowledge
- Memory: `/dream` nightly consolidation, team memories via `team/` directory
- Files API: upload reference files to environment for agent access
- MCP servers: mount as tool providers within the agent configuration

## Beta Header Requirements
All Managed Agents requests require:
```
anthropic-beta: managed-agents-2025-04-01
```
Without this header, endpoints return 404. This will become stable API.
