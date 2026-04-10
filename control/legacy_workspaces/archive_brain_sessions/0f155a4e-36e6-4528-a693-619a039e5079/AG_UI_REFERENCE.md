# AG-UI PROTOCOL REFERENCE

> **SOURCE**: User Input (Step 598) - "Cor. Integrating Google ADK agents with modern frontends using the AG-UI protocol"

## 1. Overview
AG-UI (Agent-User Interaction) is an open standard protocol designed to unify how AI agents communicate with user interfaces. It decouples the "Brain" (ADK/Agent) from the "UI" (CopilotKit/React), enabling rich, interactive, and streaming user experiences.

## 2. Architecture Components

### A. The Backend: Wrapped ADK Agent
- **Role**: The "Brain". Intelligence and logic.
- **Component**: `ag_ui_adk` (Protocol Adapter).
- **Function**: Intercepts native ADK behaviors (run start, token emit) and translates them into AG-UI events.
```python
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from data_science_agent.agent import root_agent

adk_agent_wrapper = ADKAgent(
    adk_agent=root_agent,
    user_id="demo_user",
    use_in_memory_services=True,
)
add_adk_fastapi_endpoint(app, adk_agent_wrapper, path="/")
```

### B. The Middleware: Copilot Runtime
- **Role**: Gateway and secure connection handler.
- **Component**: Next.js API Route (`src/app/api/copilotkit/route.ts`).
- **Function**: Connects Frontend to Backend.
```typescript
const runtime = new CopilotRuntime({
  agents: {
    "data_science_agent": new HttpAgent({ url: "http://localhost:8080/" }),
  }
});
```

### C. The Frontend: Global Context & UI
- **Role**: User Interface and Event Consumer.
- **Component**: `<CopilotKit>` provider and hooks like `useAgent`.
- **Function**: Renders chat, tools, and widgets based on the event stream.
```tsx
<CopilotKit runtimeUrl="/api/copilotkit" agent="data_science_agent">
  {children}
</CopilotKit>
```

## 3. Protocol Visualization (The "Matrix")

Access raw events using `useAgent` hook:
```tsx
const { agent } = useAgent({ agentId: "data_science_agent" });
agent.subscribe({
    onEvent: ({ event }) => { console.log(event); }
});
```

### Key Event Types (The "Core 17")
1.  **TEXT_MESSAGE_CONTENT**: Streaming text delta.
2.  **TOOL_CALL_ARGS**: Streaming tool usage.
3.  **RUN_STARTED**: Lifecycle event.
4.  **STATE_UPDATE**: Shared state changes.
(And more: Human-in-the-loop, Draft Proposals, Snapshots).

## 4. Key Takeaways
1.  **Decoupling**: Backend logic can swap (ADK <-> LangGraph) without breaking UI.
2.  **Streaming**: Immediate feedback via event stream (no waiting for full response).
3.  **Transparency**: "Glass Box" visibility into agent thought process.
