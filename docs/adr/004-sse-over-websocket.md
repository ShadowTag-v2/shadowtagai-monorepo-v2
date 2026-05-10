# ADR-004: SSE Over WebSocket for Agent Streaming

**Status:** Accepted
**Date:** 2026-04-24
**Source:** TACSOP 0 (Building Websites), AG-UI Protocol Specification

## Context

Agent-to-frontend streaming requires a transport protocol. Two candidates:

1. **Server-Sent Events (SSE)** — HTTP/2 multiplexed, unidirectional, native browser support
2. **WebSocket** — Full-duplex, binary-capable, requires connection management

## Decision

Adopt **SSE as the ONLY transport** for agent-to-frontend streaming. WebSocket is prohibited for new features.

### Rationale

- **Cloud Run compatibility**: SSE works over standard HTTP/2 with no special configuration. WebSocket requires Cloud Run's `--session-affinity` and has a 60-minute hard timeout.
- **AG-UI alignment**: The AG-UI protocol spec is SSE-native. WebSocket adapter exists but is secondary.
- **Simplicity**: SSE is unidirectional (server → client), which matches our use case (agent streams to UI). Client → server communication uses standard REST/fetch.
- **Retry semantics**: SSE has built-in `Last-Event-ID` reconnection. WebSocket requires custom reconnect logic.
- **CDN/proxy transparency**: SSE passes through Cloudflare, Cloud Armor, and Firebase Hosting rewrites without issue. WebSocket requires explicit `Upgrade` header handling.

### Implementation

```
Client (CopilotKit)  ←SSE←  Cloud Run (FastAPI)
Client (CopilotKit)  →REST→  Cloud Run (FastAPI)
```

- **Outbound (agent → UI)**: SSE via `text/event-stream` content type
- **Inbound (UI → agent)**: Standard `POST` requests with JSON body
- **Heartbeat**: Server sends `:ping` comment every 15s to keep connection alive

## Consequences

- No WebSocket dependencies in `package.json` or `requirements.txt`
- `fastapi[sse]` with `sse-starlette` is the canonical server library
- CopilotKit's `CopilotRuntime` configured with `httpTransport` (not `wsTransport`)
- Cloud Run services do NOT need `--session-affinity` flag

## Alternatives Rejected

- **WebSocket**: Connection management overhead, Cloud Run timeout issues, not AG-UI native
- **gRPC-Web**: Requires Envoy proxy sidecar, overkill for text streaming
- **Long polling**: Latency penalty, wasteful for streaming use cases
