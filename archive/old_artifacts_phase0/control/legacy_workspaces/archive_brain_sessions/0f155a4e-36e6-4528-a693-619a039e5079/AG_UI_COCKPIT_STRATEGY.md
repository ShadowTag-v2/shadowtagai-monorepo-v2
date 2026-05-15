# AG-UI STRATEGY: THE COCKPIT PROTOCOL

> **CLASSIFICATION**: TIER 20 // COCKPIT
> **STATUS**: ADOPTED (ShadowTag v5 ADDENDUM)

## 1. The Challenge
Our Agents ("The Brain") run on Cloud Run (`trinity_os`), but our User Interface ("The HUD") is a Next.js app (`Cockpit`).
Connecting them currently requires custom REST/SSE glue. This is brittle.

## 2. The Solution: AG-UI Protocol
We adopt **AG-UI** (Agent-User Interaction) as the standard protocol for the Cockpit.
*   **Backend**: `trinity_os` speaks AG-UI via `ag_ui_adk`.
*   **Frontend**: `Cockpit` listens via `CopilotKit`.

## 3. Architecture

```mermaid
graph LR
    A[Trinity OS (Python/ADK)] -- AG-UI Events (JSON) --> B[Next.js API Route]
    B -- CopilotKit Runtime --> C[React UI (The HUD)]
```

### Components
1.  **The Wrapper (`ag_ui_adk`)**: Intercepts ADK thoughts/tools and emits standard Events (`TEXT`, `TOOL_CALL`, `STATE`).
2.  **The Runtime (`@copilotkit/runtime`)**: Secure gateway in Next.js.
3.  **The Interface (`<CopilotKit>`)**: Provides "Chat Bubbles" and "Agent Debugger" out of the box.

## 4. Implementation Plan

### Backend (Python)
Wrap the ADK Agent in `trinity_main.py`:
```python
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from domain.trinity_os.kernel import trinity_brain

app = FastAPI()
# Magic Wrapper
wrapper = ADKAgent(adk_agent=trinity_brain)
add_adk_fastapi_endpoint(app, wrapper, path="/copilot")
```

### Frontend (Next.js)
1.  **Route handler**: `app/api/copilotkit/route.ts`
2.  **Provider**: `app/layout.tsx` -> `<CopilotKit runtimeUrl="/api/copilotkit">`

## 5. Benefits
*   **Zero-code Streaming**: Typing indicators and partial responses handling is automatic.
*   **Generative UI**: The Agent can "render" React components (Charts, Maps) via AG-UI payloads.
*   **Debugger**: We get a "Matrix View" of the agent's brain for free.
