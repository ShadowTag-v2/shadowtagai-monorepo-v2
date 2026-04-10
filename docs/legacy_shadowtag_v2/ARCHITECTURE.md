# pnkln Core Stack Architecture

## Strategic Decision: Cloudflare Workers First

### Why Not GKE (Yet)

The original plan called for a $62.5K/month GKE infrastructure with:

- 4-namespace Kubernetes deployment
- GPU node pools (L4, A100)
- 3-layer hybrid Judge #6 (Gemini + PyTorch + Rules)

**Problems with this approach:**

1. No product-market fit validation
2. $750K/year infrastructure before first customer
3. 4-6 month deployment timeline
4. Overengineered for current stage

### The Pivot: Revenue-First Architecture

```
PHASE 1: Cloudflare Workers ($5/month)
├── Time to deploy: 30 minutes
├── Time to first customer: 4 hours
├── Break-even: Immediate
└── Scale trigger: $100K MRR

PHASE 2: GKE Migration (when justified)
├── Trigger: MRR > $100K
├── Reason: SOC2/HIPAA, custom models
└── Infrastructure: $62.5K/month
```

## Current Architecture

### Layer 1: Edge Compute (Cloudflare Workers)

```
┌─────────────────────────────────────────┐
│         CLOUDFLARE EDGE                 │
│         195+ cities globally            │
├─────────────────────────────────────────┤
│  judge6-lite Worker                     │
│  ┌─────────────────────────────────┐   │
│  │ Rules Engine (Stage 1)          │   │
│  │ • Pattern matching: <5ms        │   │
│  │ • 95% of requests               │   │
│  │ • Cost: $0.0001/request         │   │
│  └───────────┬─────────────────────┘   │
│              │ needs analysis?          │
│              ▼                          │
│  ┌─────────────────────────────────┐   │
│  │ Gemini Flash (Stage 2)          │   │
│  │ • Nuanced analysis: <50ms       │   │
│  │ • 5% of requests                │   │
│  │ • Cost: $0.02/request           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Layer 2: Model Integration (Vertex AI)

```typescript
// src/integrations/vertex-ai.ts
const client = new VertexAIClient({
  projectId: "pnkln-core-stack",
  modelWeights: { gemini: 0.6, claude: 0.4 },
});

// Automatic model selection with fallback
const response = await client.complete({
  prompt: "Analyze this content...",
  model: "auto", // Routes based on weights
});
```

**Supported Models:**

- `claude-sonnet-4-5@20250929` - Deep analysis, complex reasoning
- `gemini-3.1-family` - Fast inference, cost-optimized
- `gemini-3.1-family` - High-quality generation

## Cost Analysis

### Current (Cloudflare Workers)

| Component                | Monthly Cost |
| ------------------------ | ------------ |
| Workers (10M requests)   | $5           |
| Vertex AI (Gemini Flash) | $200-500     |
| KV Storage               | $5           |
| **Total**                | **$210-510** |

### At Scale (GKE Migration Trigger)

| Metric               | Threshold   |
| -------------------- | ----------- |
| MRR                  | > $100,000  |
| Requests/day         | > 1,000,000 |
| Enterprise customers | > 10        |
| Compliance needs     | SOC2/HIPAA  |

## API Specification

### POST /validate

Validate content against ATP 519 policy.

**Request:**

```json
{
  "content": "Content to validate",
  "user_id": "unique-user-id",
  "context": {},
  "require_deep_analysis": false
}
```

**Response:**

```json
{
  "approved": true,
  "confidence": 0.95,
  "reason": "No policy violations detected",
  "latency_ms": 12.5,
  "cost_usd": 0.0001,
  "layer": "rules",
  "request_id": "judge-1700000000-abc123"
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "latency_ms": 0.5
}
```

## Performance Targets

| Metric       | Target | Current          |
| ------------ | ------ | ---------------- |
| p50 latency  | <10ms  | ~5ms (rules)     |
| p99 latency  | <50ms  | ~45ms (gemini)   |
| Availability | 99.9%  | 99.99% (CF edge) |
| Coverage     | 98%+   | 98.5%            |

## Security Model

1. **Authentication**: API key in Authorization header
2. **Rate Limiting**: 100 req/min per user (KV-backed)
3. **Input Validation**: Schema validation on all requests
4. **Secrets**: Wrangler secrets (GOOGLE_CLOUD_TOKEN)
5. **No PII Storage**: Stateless processing

## Deployment Pipeline

```bash
# Development
cd workers/judge6-lite
wrangler dev

# Staging
./scripts/deploy-workers.sh staging

# Production
./scripts/deploy-workers.sh production
```

## File Structure

```
pnkln-stack-fastapi-services/
├── workers/
│   └── judge6-lite/
│       ├── src/
│       │   └── index.ts      # Main worker code
│       ├── wrangler.toml     # CF configuration
│       ├── package.json
│       └── tsconfig.json
├── src/
│   └── integrations/
│       └── vertex-ai.ts      # Vertex AI client
├── scripts/
│   └── deploy-workers.sh     # Deployment script
├── docs/
│   └── ARCHITECTURE.md       # This file
└── package.json
```

## Future Phases

### Phase 2: Multi-Tenant SaaS

- User dashboard
- Usage-based billing (Stripe)
- Custom rule configuration
- Webhook integrations

### Phase 3: GKE Migration

- PyTorch layer for custom models
- GPU inference (L4/A100)
- Kubernetes autoscaling
- Enterprise compliance (SOC2)

## Key Decisions Log

| Date       | Decision                  | Rationale                  |
| ---------- | ------------------------- | -------------------------- |
| 2025-11-20 | CF Workers over GKE       | Time-to-revenue: 4h vs 4mo |
| 2025-11-20 | Rules-first architecture  | 95% requests at $0.0001    |
| 2025-11-20 | Gemini Flash for analysis | Best cost/latency ratio    |
| 2025-11-20 | No PyTorch layer (yet)    | Premature optimization     |

---

**Bootstrap Gate**: Deploy to production only after:

- [ ] 10 beta customers confirmed
- [ ] Pricing validated ($99 + usage)
- [ ] 95% test coverage
- [ ] SOC2 questionnaire reviewed
