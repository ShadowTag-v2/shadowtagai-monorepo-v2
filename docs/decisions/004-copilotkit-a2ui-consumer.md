# ADR 004: CopilotKit as Mandatory A2UI Consumer

**Status:** DECIDED
**Date:** 2026-04-22
**Deciders:** @pikeymickey, Antigravity Agent

## Context

A2UI (Agent-to-UI) is the presentation layer that converts declarative JSON widget blueprints from agents into rendered React components. The frontend needs a rendering engine that can:
1. Parse A2UI JSON payloads from AG-UI SSE streams
2. Render interactive widgets (CitationCard, DataTable, MetricChart)
3. Handle streaming state updates (STATE_DELTA)
4. Integrate with React Server Components architecture

## Decision

**CopilotKit is the MANDATORY frontend consumer for A2UI rendering.**

### Alternatives Evaluated

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| CopilotKit | Native AG-UI support, built-in A2UI renderer, maintained OSS | ~120KB bundle addition | ✅ SELECTED |
| Vercel AI SDK | Lightweight, good DX | No A2UI widget support, text-only streaming | ❌ REJECTED |
| Custom lightweight | Minimal bundle | Maintenance burden, no ecosystem | ❌ REJECTED |

### CopilotKit Integration Points

- `<CopilotSidebar>` for Oracle Studio chat
- `useCopilotAction()` for A2UI widget rendering
- `useCopilotReadable()` for state synchronization
- SSE transport adapter via `CopilotRuntime`

## Consequences

- KovelAI frontend MUST install `@copilotkit/react-core` and `@copilotkit/react-ui`
- All A2UI widgets rendered through CopilotKit's action system
- CopilotKit runtime proxy handles AG-UI SSE consumption
- Bundle size increases by ~120KB (gzipped), acceptable for a SaaS product

## References

- CopilotKit documentation
- AG-UI Protocol Specification
- `skills/a2ui-generative-blueprint/SKILL.md`
