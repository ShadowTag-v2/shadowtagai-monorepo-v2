# AG-UI Protocol & Generative UI — Website Construction Reference

> **Canonical Rule for Agentic Web Frontends**
> Derived from: ag-ui-protocol/ag-ui, CopilotKit/CopilotKit, agno-agi/agent-ui, CopilotKit/generative-ui, Atmosphere/atmosphere

## AG-UI Protocol Event Taxonomy

The AG-UI protocol is the standard for agent↔frontend communication via event-based SSE.
All agentic UI features MUST use this event lifecycle:

```
RUN_STARTED → STEP_STARTED → (events) → STEP_FINISHED → RUN_FINISHED
```

### Event Types (from @ag-ui/core)

| Event Type | Direction | Purpose |
|-----------|-----------|---------|
| `TEXT_MESSAGE_START` | Agent→UI | Begin streaming text |
| `TEXT_MESSAGE_CONTENT` | Agent→UI | Delta text chunk |
| `TEXT_MESSAGE_END` | Agent→UI | End of text stream |
| `TEXT_MESSAGE_CHUNK` | Agent→UI | Combined start+content+end for simple messages |
| `THINKING_TEXT_MESSAGE_START` | Agent→UI | Begin thinking/reasoning display |
| `THINKING_TEXT_MESSAGE_CONTENT` | Agent→UI | Thinking delta |
| `THINKING_TEXT_MESSAGE_END` | Agent→UI | End thinking stream |
| `THINKING_START` | Agent→UI | General thinking indicator |
| `THINKING_END` | Agent→UI | Thinking complete |
| `TOOL_CALL_START` | Agent→UI | Tool invocation begins (name, id) |
| `TOOL_CALL_ARGS` | Agent→UI | Streamed tool arguments |
| `TOOL_CALL_END` | Agent→UI | Tool call complete |
| `TOOL_CALL_CHUNK` | Agent→UI | Combined tool call event |
| `TOOL_CALL_RESULT` | UI→Agent | Tool result returned |
| `STATE_SNAPSHOT` | Agent→UI | Full state replacement |
| `STATE_DELTA` | Agent→UI | Incremental state update (JSON Patch) |
| `MESSAGES_SNAPSHOT` | Agent→UI | Full message history |
| `ACTIVITY_SNAPSHOT` | Agent→UI | Agent activity indicator |

### Zod Schema Validation

All events are validated with Zod schemas. Use the schema types when building:

```typescript
import {
  TextMessageContentEventSchema,
  ToolCallStartEventSchema,
  StateSnapshotEventSchema
} from '@ag-ui/core';
```

## Three-Layer Architecture (CopilotKit)

```
Frontend (React/Angular/Vanilla) → Runtime (Express/Hono) → Agent (LangGraph/CrewAI/Custom)
```

### Request Lifecycle
1. Frontend creates `CopilotKitCore` → fetches agent info → creates `ProxiedAgent`
2. User sends message → `runAgent()` called
3. POST to runtime with `RunAgentInput` (messages, tools, context, threadId, state)
4. Runtime: middleware → agent resolution → `AgentRunner` execution
5. SSE stream: AG-UI events streamed back to frontend
6. Frontend tool execution: browser-local tool handlers
7. Core updates message store → React/Angular re-renders

### Key Frontend Hooks
```typescript
// Register frontend tools (run in browser)
useFrontendTool("tool-name", handler, { description });

// Provide context to agent
useAgentContext("description", data);

// Select agent
useAgent({ agentId: "my-agent" });
```

## Three Types of Generative UI

### 1. Controlled (AG-UI) — High control, low freedom
Agent sends structured events → frontend renders predefined components.
Best for: production apps with known UI patterns.

### 2. Declarative (A2UI + Open-JSON-UI) — Shared control
Agent sends UI specifications → frontend interprets and renders.
Best for: configurable dashboards, dynamic forms.

### 3. Open-ended (MCP Apps) — Low control, high freedom
Agent generates full UI code/markup → frontend renders arbitrary content.
Best for: creative tools, prototyping.

## Component Patterns (from agno-agi/agent-ui)

### Chat Architecture
```
Page → Sidebar + ChatArea
ChatArea → MessageArea + ChatInput
MessageArea → Messages → MessageItem
MessageItem → MarkdownRenderer / Images / Videos / Audios / AgentThinkingLoader
```

### Message Types
```typescript
interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  toolCalls: ToolCall[];     // Tool execution visualization
  steps: Step[];             // Multi-step progress
  isStreaming: boolean;      // Streaming indicator
  error?: string;            // Error state
  images?: string[];         // Multimodal
  videos?: string[];
  audio?: AudioContent[];
  response_audio?: AudioResponse;
}
```

### Essential UI Components
| Component | Purpose | Source |
|-----------|---------|-------|
| `MarkdownRenderer` | Render agent markdown with code highlighting | agno-agi |
| `AgentThinkingLoader` | Animated thinking indicator | agno-agi |
| `StreamingMessage` | Real-time text streaming display | Atmosphere |
| `StreamingProgress` | Multi-step progress bars | Atmosphere |
| `StreamingError` | Graceful error states | Atmosphere |
| `ChatLayout` | Responsive chat container | Atmosphere |
| `ChatInput` | Message composition with attachments | Atmosphere |

## Multi-Agent Frontend Pattern (Atmosphere)

```typescript
const AGENTS = {
  web_search:       { label: 'Research Agent',  icon: '🔍', color: '#f59e0b' },
  analyze_strategy: { label: 'Strategy Agent',  icon: '🎯', color: '#10b981' },
  financial_model:  { label: 'Finance Agent',   icon: '💰', color: '#8b5cf6' },
  write_report:     { label: 'Writer Agent',    icon: '✍️', color: '#ef4444' },
};
// Each agent has its own color, icon, and backend route
```

### Transport Negotiation (Atmosphere)
```typescript
const request = {
  url: '/atmosphere/agent/ceo',
  transport: 'webtransport',       // HTTP/3 (fastest)
  fallbackTransport: 'websocket',  // HTTP/1.1 fallback
  reconnect: true,
  maxReconnectOnClose: 10,
  reconnectInterval: 5000,
  trackMessageLength: true,
  contentType: 'application/json',
};
```

## Design System Standards (from agno-agi/agent-ui)

- **Font**: Geist (sans) + DM Mono (monospace)
- **Stack**: Next.js + Tailwind CSS + shadcn/ui + Framer Motion
- **State**: Zustand store + nuqs (URL query sync)
- **Toast**: Sonner
- **Rendering**: `antialiased` text, CSS variables for theming

## Integration Directives for Our Website

1. **Protocol**: Use AG-UI event types for any agent↔UI communication
2. **Streaming**: Implement SSE with reconnect and fallback transport
3. **Components**: Adopt ChatArea/MessageItem/MarkdownRenderer pattern
4. **Multi-agent**: Color-code agents, show activity indicators per agent
5. **Generative UI**: Start with Controlled (AG-UI), evolve to Declarative (A2UI)
6. **State**: Zustand for local state, AG-UI STATE_SNAPSHOT/STATE_DELTA for agent state
7. **Verification**: Display tool call results with PASS/FAIL indicators (Rule 44)
8. **Error handling**: StreamingError component with graceful degradation
