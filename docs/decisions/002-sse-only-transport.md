# ADR 002: SSE-Only Transport for AG-UI

**Status:** DECIDED  
**Date:** 2026-04-22  
**Deciders:** @pikeymickey, Antigravity Agent  

## Context

CounselConduit requires a real-time transport layer to stream agent reasoning, tool calls, and A2UI widget payloads from ADK 2.0 backends to CopilotKit frontends. The two candidates are Server-Sent Events (SSE) and WebSocket.

## Decision

**SSE is the EXCLUSIVE transport for AG-UI.** WebSocket is rejected.

## Rationale

| Factor | SSE | WebSocket |
|--------|-----|-----------|
| HTTP/2 multiplexing | ✅ Native | ❌ Separate TCP |
| Cloud Run scaling | ✅ Stateless | ⚠️ Sticky sessions required |
| Firewall traversal | ✅ Standard HTTP | ⚠️ Often blocked by corporate proxies |
| Complexity | ✅ Simple server-push | ❌ Full-duplex overhead for a unidirectional pattern |
| Agent streaming fit | ✅ Server → Client only | ❌ Over-engineered for our pattern |
| CDN/proxy compatibility | ✅ Works with standard reverse proxies | ⚠️ Requires WebSocket upgrade support |

Client-to-server communication uses standard `POST /agent/message` requests. The agent pattern is inherently server-push (agent reasons → client displays), making SSE the natural fit.

## Consequences

- All AG-UI endpoints MUST return `text/event-stream` content type
- Cloud Run services MUST set `--timeout=3600` for long-running streams
- Reverse proxies MUST disable buffering (`X-Accel-Buffering: no`)
- Heartbeat keepalive pings every 30s to maintain connections
- Clients MUST implement exponential backoff reconnection

## References

- AG-UI Protocol Specification
- W3C Server-Sent Events
- `skills/agui-sse-transport/SKILL.md`
