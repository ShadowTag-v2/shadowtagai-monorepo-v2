# Rule 32: Managed Agents SDK Patterns
# Source: CC v2.1.97 — Managed Agents onboarding + client patterns + endpoint reference

## Core Concepts
A Managed Agent is a self-contained AI service exposed via API endpoints:
- **Agent**: An instruction set + environment + tools configuration
- **Session**: A stateful conversation instance with an agent
- **Environment**: An isolated container with filesystem, network, and secrets
- **Lifecycle**: Create → Configure → Deploy → Version → Scale

## Configuration Schema
An agent is defined by:
```yaml
agent:
  name: string
  instructions: string | CLAUDE.md path
  model: string (default: claude-sonnet-4-20250514)
  tools:
    - name: bash_tool
      enabled: true
    - name: file_tool
      enabled: true
    - name: mcp_tool
      server: "server-name"
  files:
    - path: "src/**"
      writable: true
    - path: "config/**"
      writable: false
  environment:
    variables:
      NODE_ENV: production
    secrets:
      - API_KEY
  max_turns: 25
  timeout_ms: 300000
```

## Client-Side Patterns

### Stream Reconnection
```typescript
// If connection drops mid-stream, resume from last event ID
const stream = await agent.resume(sessionId, { lastEventId })
```

### Idle-Break Gating
```typescript
// Detect when agent is idle and inject a prompt
if (stream.status === 'idle' && elapsedMs > IDLE_THRESHOLD) {
  await agent.send(sessionId, { prompt: "Continue with next task" })
}
```

### Tool Confirmations
```typescript
// Client-side confirmation before dangerous tool execution
stream.on('tool_use', async (event) => {
  if (event.tool === 'bash' && event.input.includes('rm')) {
    const approved = await promptUser(`Allow: ${event.input}?`)
    if (!approved) await agent.reject(sessionId, event.id)
  }
})
```

### Custom Tools
```typescript
// Register client-side tools the agent can invoke
agent.registerTool({
  name: 'deploy',
  description: 'Deploy to staging',
  handler: async (input) => {
    return await deployToStaging(input.branch)
  }
})
```

## Antigravity Adaptation
Map to Antigravity's agent architecture:
| Managed Agents | Antigravity Equivalent |
|---------------|----------------------|
| Agent config | Skill YAML + `antigravity-mcp-config.json` |
| Session | Conversation context + KI items |
| Environment | Docker container (via Docker Orchestrator skill) |
| Custom tools | MCP server tools |
| Stream reconnection | Conversation resumption via checkpoint |
| Idle-break gating | Sequential thinking timeout detection |

### Key Takeaway for Implementation
Use the Managed Agents Builder skill (`/skills/managed-agents-builder/SKILL.md`)
when building LLM-powered applications. It routes to the correct Anthropic SDK
patterns and provides model defaults, thinking configuration, and SDK-specific
documentation.
