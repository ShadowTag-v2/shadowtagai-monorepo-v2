# Sprint 2 Plan — Sandbox Isolation + BYOK Key Management

## Duration: 2 weeks (2026-04-22 to 2026-05-06)

---

## Goals

1. **Sandbox Isolation** — Per-tenant isolated execution environments for LLM tool calls
2. **BYOK (Bring Your Own Key)** — Enterprise customers provide their own API keys
3. **Context Caching Live Integration** — Production Gemini Context Caching API
4. **Observability** — Structured logging, tracing, alerting in production

---

## Phase 1: Sandbox Isolation (Week 1)

### Architecture
```
Client Request → MCP Gateway → Sandbox Broker → Ephemeral Container
                                     ↓
                              Cloud Tasks Job
                                     ↓
                              Tool Execution
                              (isolated FS, no shared state)
                                     ↓
                              Result → Gateway → Client
```

### Tasks
- [ ] Design sandbox container spec (read-only FS, network restrictions)
- [ ] Implement SandboxBroker service (lib/sandbox/broker.ts)
- [ ] Create ephemeral Cloud Run Job template for tool execution
- [ ] Add per-tenant resource quotas (CPU, memory, timeout)
- [ ] Implement sandbox cleanup (auto-destroy after 5 minutes)
- [ ] Wire sandbox into MCP Gateway risk tier system
- [ ] Test: verify no cross-tenant data leakage
- [ ] Test: verify sandbox self-destructs on timeout

### Security
- Each sandbox gets a unique service account (scoped IAM)
- No persistent storage in sandbox (ephemeral /tmp only)
- Network egress restricted to LLM API endpoints only
- Token budget enforced per-sandbox, per-tenant

---

## Phase 2: BYOK Key Management (Week 1-2)

### Architecture
```
Enterprise Firm → KovelAI Settings → "Add API Key"
                                          ↓
                                   GCP Secret Manager
                                   (per-firm namespace)
                                          ↓
                              Secret: firms/{firmId}/keys/{provider}
                                          ↓
                              LiteLLM Proxy (runtime injection)
```

### Tasks
- [ ] Design BYOK key storage schema in Secret Manager
- [ ] Implement key upload API (lib/security/byok-manager.ts)
- [ ] Create key rotation schedule (90-day max, 7-day warning)
- [ ] Wire BYOK keys into LiteLLM proxy configuration
- [ ] Implement key validation (test call on upload)
- [ ] Add key audit log (who uploaded, when rotated, usage count)
- [ ] Support providers: OpenAI, Anthropic, Google (Vertex AI)
- [ ] Test: verify key isolation across tenants
- [ ] Test: verify key rotation doesn't interrupt active sessions

### UX
- Settings page: "API Keys" tab
- Upload flow: paste key → validate → encrypt → store
- Status indicators: Active, Expiring Soon, Expired
- Usage dashboard: token count per key per day

---

## Phase 3: Context Caching Production (Week 2)

### Tasks
- [ ] Deploy VRAM Context Cache to Cloud Run (already written)
- [ ] Configure Gemini 2.5 Pro context cache settings
- [ ] Implement cache warming for large document sets
- [ ] Add cache hit/miss metrics to structured logger
- [ ] Implement cache eviction policy (LRU + TTL)
- [ ] Wire billing: track cached vs uncached token costs
- [ ] Test: verify 85% cost reduction on repeated queries
- [ ] Test: cache invalidation on document updates

---

## Phase 4: Observability (Week 2)

### Tasks
- [ ] Deploy structured logger to all API routes
- [ ] Replace remaining console.* calls across codebase
- [ ] Create Cloud Monitoring dashboard for KovelAI
- [ ] Set up alerting: error rate >5%, latency P99 >5s
- [ ] Add request tracing (trace ID through full pipeline)
- [ ] Wire Cloud Run metrics into Grafana or Google Cloud Console
- [ ] Test: verify PII redaction in logs (Cor.30 R11)
- [ ] Test: verify trace propagation through async workflows

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Sandbox isolation tested | 0 cross-tenant leaks |
| BYOK providers supported | 3 (OpenAI, Anthropic, Google) |
| Context cache hit rate | >60% on repeated queries |
| Log PII compliance | 0 PII in structured logs |
| E2E test suite | 30+ passing tests |
| Lighthouse scores | P90+ / A100 / BP100 / SEO100 |

---

## Dependencies

- Cloud Tasks queue: `gdpr-deletion-queue` ✅ (provisioned)
- Firestore persistence: Genesis Block ✅, Approvals ✅
- Structured logger: ✅ (lib/observability/structured-logger.ts)
- MFA gate: ✅ (lib/security/mfa-gate.ts)
- Clio conflict checker: ✅ (lib/integrations/clio-conflict-checker.ts)
