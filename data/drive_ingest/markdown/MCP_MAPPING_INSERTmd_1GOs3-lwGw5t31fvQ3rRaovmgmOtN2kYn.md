# MCP MAPPING INSERT — PNKLN Namespace Analysis

Use for: Protocol analysis, SDK mapping, architecture integration

---

## MCP Component Inventory

### SDK Entrypoints

| Component | File/Module | PNKLN Namespace | Notes |
|-----------|-------------|-----------------|-------|
| Client sessions | | core-stack | |
| Tool calls | | judge-six | |
| Streaming/events | | ns-mesh | |
| Resources | | | |
| Prompts | | | |

### Server Patterns

| Server Type | Repo Path | Reusable? | Multi-tenant? |
|-------------|-----------|-----------|---------------|
| Filesystem | | | |
| Git | | | |
| Memory | | | |
| Database | | | |

---

## PNKLN Namespace Mapping

### core-stack
**Role**: Client orchestration, session management

**MCP Components to Map**:
- [ ] McpServer class
- [ ] Client connection handling
- [ ] Request routing

**Integration Points**:
```typescript
// Example mapping
```

---

### judge-six
**Role**: Gatekeeper for tool actions, Jura Protocol enforcement

**MCP Components to Map**:
- [ ] Tool call validation
- [ ] Permission checks
- [ ] Rate limiting

**Integration Points**:
```typescript
// Example mapping
```

---

### shadow-tag
**Role**: Request/response watermarking, audit trail

**MCP Components to Map**:
- [ ] Request envelope
- [ ] Response envelope
- [ ] Metadata injection

**Integration Points**:
```typescript
// Example mapping
```

---

### ns-mesh
**Role**: Real-time coordination, event streaming

**MCP Components to Map**:
- [ ] SSE transport
- [ ] Notifications
- [ ] Progress updates

**Integration Points**:
```typescript
// Example mapping
```

---

### audit-compress
**Role**: Telemetry, metrics, log compression

**MCP Components to Map**:
- [ ] Logging hooks
- [ ] Metrics collection
- [ ] Trace IDs

**Integration Points**:
```typescript
// Example mapping
```

---

## Analysis Checklist

### Phase 1: Discovery
- [ ] Clone repos via fork-repos.sh
- [ ] Run github_discovery_agent.py
- [ ] Safety scan results
- [ ] Index to corpus

### Phase 2: Architecture
- [ ] Identify SDK entrypoints
- [ ] Map to PNKLN namespaces
- [ ] Document integration points
- [ ] Note multi-tenant requirements

### Phase 3: Implementation
- [ ] Create wrapper modules
- [ ] Add ShadowTag hooks
- [ ] Implement Judge #6 gates
- [ ] Wire to Autoresearch

---

## Security Considerations

### Hard Isolation Required
- [ ] API keys per tenant
- [ ] Session separation
- [ ] Resource quotas

### ShadowTag Injection Points
- [ ] Request entry
- [ ] Tool invocation
- [ ] Response exit
- [ ] Error paths

---

## Output

### Architecture Document
```markdown
# PNKLN ← MCP Integration Architecture

## Overview
[Summary of how MCP components map to PNKLN namespaces]

## Component Diagram
[ASCII or Mermaid diagram]

## Implementation Notes
[Key decisions and rationale]
```

### Handoff JSON
```json
{
  "thread_id": "ATOMIC-XXX",
  "outcome": "MCP-to-PNKLN mapping complete",
  "files_changed": ["docs/architecture/mcp-pnkln-map.md"],
  "next_action": "Implement core-stack wrapper"
}
```