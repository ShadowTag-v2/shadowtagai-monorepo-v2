# HeadFade V2 API Technical Specification

**Version**: 1.0  
**Date**: May 6, 2026  
**Status**: Draft for Engineering Review

---

## 1. Overview

The HeadFade V2 API is the enterprise-grade, multi-protocol interface for the HeadFade Truth Oracle. It replaces the V1 MCP-only interface with a full-featured platform supporting GraphQL (primary), REST (compatibility), and MCP (agent-native).

**Base URL**: `https://api.headfade.ai/v2`

**Authentication**: 
- Workload Identity Federation (preferred for agents)
- Signed JWT + Ed25519 request signing (required for all production calls)
- API Key (legacy / low-volume)

---

## 2. Core Endpoints

### 2.1 Analyze Video (Primary)

**GraphQL**:
```graphql
mutation AnalyzeVideo($input: AnalyzeInput!) {
  analyzeVideo(input: $input) {
    id
    hdiScore
    modelsUsed
    remixTree {
      id
      depth
      transformations
    }
    provenance {
      source
      timestamp
      signature
    }
  }
}
```

**REST**:
```http
POST /v2/analyze
Content-Type: application/json
Authorization: Bearer <token>
X-Signature: <ed25519-signature>

{
  "videoUrl": "https://...",
  "options": {
    "includeRemixTree": true,
    "depth": 5,
    "models": ["all"]
  }
}
```

**Response** (200):
```json
{
  "id": "vid_9f3k2m1p",
  "hdiScore": 87.4,
  "isSynthetic": true,
  "modelsUsed": ["Sora", "Runway Gen-4", "Kling 2.0"],
  "remixTree": { ... },
  "processingTimeMs": 1240
}
```

---

### 2.2 Purchase Workflow License

**GraphQL**:
```graphql
mutation PurchaseLicense($input: LicensePurchaseInput!) {
  purchaseWorkflowLicense(input: $input) {
    licenseId
    status
    downloadUrl
    expiresAt
  }
}
```

**REST**:
```http
POST /v2/license/purchase
{
  "workflowId": "wf_cyberpunk_neon",
  "buyerAgentId": "agnt_7x9k2p",
  "paymentMethod": "stripe"
}
```

---

### 2.3 Query Remix Lineage

**GraphQL**:
```graphql
query GetRemixLineage($videoId: ID!, $depth: Int) {
  remixLineage(videoId: $videoId, depth: $depth) {
    edges {
      from { id }
      to { id }
      transformation
      model
      timestamp
      signature
    }
  }
}
```

---

## 3. MCP Tools (Agent-Native)

```json
{
  "verify_synthetic_video_v2": {
    "description": "Returns full provenance + HDI + Remix Tree v2",
    "input": { "videoId": "string", "options": "object" }
  },
  "purchase_workflow_license_v2": {
    "description": "Agent-to-Agent micro-license purchase with smart contract",
    "input": { "workflowId": "string", "buyerAgentId": "string" }
  },
  "query_remix_lineage_v2": {
    "description": "Returns cryptographically signed remix history",
    "input": { "videoId": "string", "depth": "int" }
  },
  "register_new_model": {
    "description": "Register new foundation model for provenance tracking",
    "input": { "modelName": "string", "provider": "string", "fingerprintMethod": "string" }
  }
}
```

---

## 4. Error Codes & Handling

| Code | Meaning | Retry Strategy |
|------|---------|----------------|
| 4001 | Invalid video URL | Do not retry |
| 4002 | Unsupported model | Fallback to visual-only analysis |
| 429 | Rate limit exceeded | Exponential backoff (max 5 retries) |
| 5001 | HDI model inference failure | Retry with different model subset |

---

## 5. Rate Limits

| Tier | Requests/min | Burst |
|------|--------------|-------|
| Public | 100 | 200 |
| B2B Tier 1 | 10,000 | 20,000 |
| B2B Tier 2 | 1,000 | 2,000 |
| Agent (MCP) | 500 | 1,000 |

---

## 6. Versioning & Deprecation

- Semantic Versioning (MAJOR.MINOR.PATCH)
- V1 will be deprecated 18 months after V2 GA
- Breaking changes announced 90 days in advance

---

## 7. OpenAPI + GraphQL Schema

Full specs available at:
- `https://api.headfade.ai/v2/openapi.json`
- `https://api.headfade.ai/v2/graphql`

---

**End of Technical Spec**  
**Next**: Full implementation begins May 12, 2026 (post-public launch)