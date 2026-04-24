# ADR-003: CopilotKit AG-UI as Frontend Agent Protocol

**Status:** Accepted
**Date:** 2026-04-24
**Source:** TACSOP 0 (Building Websites), AG-UI Whitepapers (Google Agent Architecture 2025)

## Context

CounselConduit and KovelAI need a standardized protocol for frontend agent-to-UI communication. Options evaluated:

1. **Custom WebSocket protocol** — high control, high maintenance, no ecosystem
2. **Vercel AI SDK** — mature, but locked to Vercel ecosystem
3. **CopilotKit AG-UI** — open standard, SSE-native, CopilotKit runtime compatible

## Decision

Adopt **CopilotKit with AG-UI protocol** as the canonical frontend agent protocol for all ShadowTag web properties.

### Rationale

- AG-UI is an **open protocol** (not vendor-locked)
- CopilotKit provides **React hooks** (`useCopilotAction`, `useCopilotReadable`) that map directly to our design system
- SSE transport aligns with ADR-004 (SSE over WebSocket)
- AG-UI's **event taxonomy** (TextMessageStart, ActionExecution, StateSnapshot) maps cleanly to CounselConduit's Oracle Studio pipeline stages
- Community momentum: 35K+ GitHub stars, Google/Microsoft backing

### AG-UI Event Types Used

| Event | CounselConduit Use |
|-------|-------------------|
| `TextMessageStart/Content/End` | Oracle Memo streaming |
| `ActionExecutionStart/End` | Tool calls (cite, summarize, escalate) |
| `StateSnapshot/StateDelta` | Vent Mode emotional state sync |
| `RunStarted/Finished` | Session lifecycle (privilege envelope) |
| `StepStarted/Finished` | 7-stage Oracle pipeline progress |

## Consequences

- All new frontend agent features MUST use CopilotKit hooks, not raw fetch/WebSocket
- Backend must emit AG-UI-compliant SSE events (not custom JSON)
- Existing SSE endpoints (`/vent/stream`, `/oracle/stream`) must be migrated to AG-UI event format
- Skill reference: `ag-ui-frontend-protocol` + `agui-sse-transport`

## Alternatives Rejected

- **Raw WebSocket**: No standard event taxonomy, requires custom serialization
- **Vercel AI SDK**: Vendor lock-in, no CopilotKit interop
- **gRPC-Web**: Overkill for unidirectional streaming, poor browser support
