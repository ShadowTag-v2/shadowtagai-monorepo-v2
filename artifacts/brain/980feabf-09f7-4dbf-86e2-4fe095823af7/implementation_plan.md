# Implementation Plan: AG-UI & Legacy Integration

## Goal
Integrate "Agent-User Interaction" (AG-UI) protocol to enable "Agent-to-UI" (A2UI) generative interfaces, decoupling the backend agent from the frontend implementation using CopilotKit.

## User Review Required
> [!IMPORTANT]
> This requires `ag_ui_adk` and `copilotkit` packages. Ensure `uv` or `pip` can install them.

## Proposed Changes

### 1. Middleware (The Bridge)
#### [NEW] `middleware/ag_ui_adk_wrapper.py`
- Wraps the native ADK agent (`root_agent`) using `ag_ui_adk.ADKAgent`.
- Exposes a FastAPI endpoint compatible with AG-UI protocol.

### 2. Frontend (The Visualizer)
#### [NEW] `components/AgentDebugger.tsx`
- A React component using `useAgent` hook to visualize the raw AG-UI event stream (Blue=Text, Purple=Tools, Green=State).
#### [MODIFY] `app/api/copilotkit/route.ts`
- Needs to be created/configured to point to the Python backend.

### 3. External Intelligence
- Ingested 30+ Repos for "Vibe Coding" inspiration and tools (via `clone_universe.sh`).

## Verification Plan
1.  **Backend Start**: `uv run middleware/ag_ui_adk_wrapper.py`
2.  **Frontend Connect**: Verify `AgentDebugger` shows events when interacting with the agent.
