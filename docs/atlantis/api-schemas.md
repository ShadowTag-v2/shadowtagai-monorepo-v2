# API Schemas & Integration Guide

## Overview

AiYou provides **five primary API surfaces** across the PNKLN Core Stack™:

1. **Inference API** — Route AI requests to edge GPUs

2. **ShadowTag API** — Verify and audit AI outputs

3. **PNT API** — Access anti-spoofing location/time services

4. **Ingestion API** — Submit intelligence items for collection (PNKLN: Preparation)

5. **Validation API** — Validate intelligence compliance (PNKLN: Logic & Validation / Judge 6)

**Base URL:** `https://api.aiyou.io/v1`
**Authentication:** Bearer token (OAuth 2.0 / API keys)
**Protocols:** REST (HTTP/JSON), gRPC (for low-latency), WebSocket (for streaming)

### PNKLN Core Stack™ API Flow

```

User/Service
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ P — Preparation (Ingestion API)                     │
│     POST /ingestion/submit                          │
│     GET  /ingestion/sources                         │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ N — Normalization (Internal ETL)                    │
│     [No public API - internal service]              │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ K — Knowledge Graph (Internal)                      │
│     [Entity extraction - internal service]          │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ L — Logic & Validation (Validation API / Judge 6)  │
│     POST /validation/validate                       │
│     GET  /validation/rules                          │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ N — Notarization (ShadowTag API)                    │
│     POST /shadowtag/verify                          │
│     GET  /shadowtag/proof/{id}                      │
└─────────────────────────────────────────────────────┘
    │
    ▼
Verified Intelligence Output

```

---

## 1. Inference API

### POST /inference

Route an AI inference request to the nearest edge GPU.

**Request:**

```json
{
  "model_id": "llama-3-70b-instruct",
  "prompt": "What is the capital of France?",
  "parameters": {
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9
  },
  "options": {
    "latency_priority": "ultra_low",  // "ultra_low" | "balanced" | "cost_optimized"
    "verification_level": "high",      // "none" | "basic" | "high" | "paranoid"
    "cache_enabled": true
  }
}

```

**Response (200 OK):**

```json
{
  "inference_id": "inf_a7b3c9d2e1f4",
  "result": {
    "text": "The capital of France is Paris.",
    "finish_reason": "stop",
    "tokens_used": 12
  },
  "performance": {
    "latency_ms": 18.3,
    "cache_hit": false,
    "pop_id": "sea-01",
    "gpu_id": "sea-01-pod-2-gpu-3"
  },
  "shadowtag": {
    "signature": "cose:a10126a1045249502b13...",
    "timestamp_utc": "2025-11-15T14:23:45.678901234Z",
    "verification_url": "https://shadowtag.aiyou.io/verify/inf_a7b3c9d2e1f4",
    "ledger_hash": "merkle:7a3f9b2c..."
  },
  "billing": {
    "cost_usd": 0.00144,
    "billing_id": "bill_x7y9z2"
  }
}

```

**Error (429 Too Many Requests):**

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Exceeded 1000 requests per minute limit",
    "retry_after_seconds": 30
  }
}

```

---

### GET /models

List available models.

**Response:**

```json
{
  "models": [
    {
      "id": "llama-3-70b-instruct",
      "name": "Llama 3 70B Instruct",
      "provider": "meta",
      "context_length": 8192,
      "cost_per_1k_tokens": 0.001,
      "availability": ["sea-01", "sfo-01", "fra-01"]
    },
    {
      "id": "gpt-4o",
      "name": "GPT-4o (via Azure)",
      "provider": "openai",
      "context_length": 128000,
      "cost_per_1k_tokens": 0.005,
      "availability": ["sea-01", "sfo-01"]
    }
  ]
}

```

---

## 2. ShadowTag API

### POST /shadowtag/verify

Verify a ShadowTag attestation.

**Request:**

```json
{
  "inference_id": "inf_a7b3c9d2e1f4",
  "signature": "cose:a10126a1045249502b13...",
  "payload_hash": "blake3:8af43c7b9d2e...",
  "requirements": {
    "min_pnt_confidence": 0.8,
    "clock_synced": true,
    "anchored": true,
    "allowed_jurisdictions": ["US", "EU"]
  }
}

```

**Response (200 OK - Verified):**

```json
{
  "status": "verified",
  "integrity": {
    "signature_valid": true,
    "hash_matches": true,
    "chain_intact": true
  },
  "attestation": {
    "timestamp_utc": "2025-11-15T14:23:45.678901234Z",
    "pop_id": "sea-01",
    "gpu_id": "sea-01-pod-2-gpu-3",
    "model_id": "llama-3-70b-instruct",
    "pnt_confidence": 0.93
  },
  "anchoring": {
    "anchored": true,
    "anchor_service": "opentimestamps",
    "anchor_timestamp": "2025-11-15T14:30:00Z",
    "tx_hash": "0x7f3b2a..."
  },
  "compliance": {
    "license_ok": true,
    "purpose": ["ai_inference"],
    "retention_ok": true,
    "jurisdiction_ok": true
  }
}

```

**Response (400 Bad Request - Verification Failed):**

```json
{
  "status": "failed",
  "integrity": {
    "signature_valid": false,
    "reason": "Signature does not match payload hash"
  },
  "warnings": [
    "PNT confidence below required threshold (0.72 < 0.8)",
    "Not yet anchored to public ledger"
  ]
}

```

---

### GET /shadowtag/events/{event_id}

Retrieve full event details from ledger.

**Response:**

```json
{
  "event_id": "evt_9c4a7f3b2e1d",
  "content_id": "blake3:8af43c7b9d2e...",
  "timestamp_utc": "2025-11-15T14:23:45.678901234Z",
  "manifest": {
    "eid": "evt_9c4a7f3b2e1d",
    "cid": "blake3:8af43c...",
    "ts": "2025-11-15T14:23:45.678901234Z",
    "prev": "blake3:7d2f9a...",
    "sig": "cose:a10126a1045..."
  },
  "l4_attestation": {
    "spacetime": {
      "lat": 47.6062,
      "lon": -122.3321,
      "pnt_conf": 0.93,
      "celestial": {"conf": 0.88}
    }
  },
  "merkle_proof": {
    "root": "sha256:3f8d2a...",
    "path": ["sha256:4a7b...", "sha256:9e3c..."]
  }
}

```

---

## 3. PNT API

### POST /pnt/solution

Get verified position/navigation/timing solution.

**Request:**

```json
{
  "sources": {
    "gnss": {
      "nmea": "$GPGGA,142345.00,4736.3720,N,12223.8932,W,1,12,0.7,12.3,M,,,*56"
    },
    "imu": {
      "accel_x_mps2": 0.12,
      "accel_y_mps2": -0.05,
      "accel_z_mps2": 9.81,
      "gyro_x_dps": 0.02,
      "gyro_y_dps": 0.01,
      "gyro_z_dps": -0.03
    },
    "network": {
      "cell_towers": [
        {"cid": 12345, "lac": 678, "rssi": -72},
        {"cid": 12346, "lac": 678, "rssi": -85}
      ]
    }
  },
  "options": {
    "confidence_threshold": 0.8,
    "include_celestial": false,
    "enable_spoofing_detection": true
  }
}

```

**Response:**

```json
{
  "solution_id": "pnt_f8e7d6c5b4a3",
  "timestamp_utc": "2025-11-15T14:23:45.678901234Z",
  "position": {
    "lat": 47.60604,
    "lon": -122.33196,
    "alt_m": 12.3,
    "confidence": 0.93,
    "hdop": 0.7,
    "source": "fusion"  // "gnss_only" | "fusion" | "imu_only" | "network_only"
  },
  "timing": {
    "utc": "2025-11-15T14:23:45.678901234Z",
    "gps_week": 2345,
    "gps_tow_s": 497025.678,
    "source": "gnss",  // "gnss" | "starlink" | "ntp" | "local_clock"
    "accuracy_ns": 50
  },
  "integrity": {
    "spoofing_detected": false,
    "anomaly_score": 0.02,  // 0-1 scale
    "sources_agree": true,
    "warnings": []
  },
  "shadowtag": {
    "signature": "cose:...",
    "ledger_hash": "merkle:..."
  }
}

```

**Response (Spoofing Detected):**

```json
{
  "solution_id": "pnt_f8e7d6c5b4a3",
  "position": {
    "lat": 47.60604,
    "lon": -122.33196,
    "confidence": 0.42,  // Low confidence
    "source": "imu_only"  // Fell back to inertial
  },
  "integrity": {
    "spoofing_detected": true,
    "anomaly_score": 0.94,
    "triggers": [
      "gnss_celestial_mismatch",
      "sudden_position_jump",
      "multi_source_disagreement"
    ],
    "warnings": [
      "GNSS shows impossible position change (200 km in 1 second)",
      "Celestial solution disagrees by 15 km",
      "Recommend switching to inertial + last-known-good"
    ]
  }
}

```

---

## 4. Admin & Management APIs

### GET /pops

List available PoPs (Points of Presence).

**Response:**

```json
{
  "pops": [
    {
      "id": "sea-01",
      "name": "Seattle",
      "location": {"lat": 47.6062, "lon": -122.3321},
      "status": "operational",
      "capacity": {
        "gpus_total": 32,
        "gpus_available": 18,
        "utilization_percent": 44
      },
      "latency_ms": {
        "p50": 12,
        "p95": 18,
        "p99": 25
      },
      "uptime_percent_30d": 99.97
    }
  ]
}

```

---

### POST /billing/usage

Query usage and billing.

**Request:**

```json
{
  "start_date": "2025-11-01",
  "end_date": "2025-11-30",
  "group_by": "day"  // "hour" | "day" | "month"
}

```

**Response:**

```json
{
  "period": {
    "start": "2025-11-01T00:00:00Z",
    "end": "2025-11-30T23:59:59Z"
  },
  "summary": {
    "total_requests": 108000000,
    "total_cost_usd": 155520.00,
    "avg_cost_per_request_usd": 0.00144
  },
  "breakdown": [
    {
      "date": "2025-11-15",
      "requests": 3600000,
      "cost_usd": 5184.00,
      "cache_hit_rate": 0.62
    }
  ]
}

```

---

## SDK Examples

### TypeScript / Node.js

**Installation:**

```bash
npm install @aiyou/sdk

```

**Usage:**

```typescript
import { AiYou } from '@aiyou/sdk';

const client = new AiYou({
  apiKey: process.env.AIYOU_API_KEY,
  environment: 'production'
});

// Inference
const result = await client.inference.create({
  modelId: 'llama-3-70b-instruct',
  prompt: 'Explain quantum computing in simple terms',
  options: {
    latencyPriority: 'ultra_low',
    verificationLevel: 'high'
  }
});

console.log(result.result.text);
console.log(`Latency: ${result.performance.latencyMs}ms`);
console.log(`ShadowTag: ${result.shadowtag.verificationUrl}`);

// Verify ShadowTag
const verification = await client.shadowtag.verify({
  inferenceId: result.inferenceId,
  signature: result.shadowtag.signature,
  payloadHash: result.shadowtag.ledgerHash
});

if (verification.status === 'verified') {
  console.log('✅ Output is cryptographically verified');
}

// PNT Solution
const pnt = await client.pnt.getSolution({
  sources: {
    gnss: { nmea: '$GPGGA,...' },
    imu: { accelX: 0.12, ... }
  },
  options: {
    enableSpoofingDetection: true
  }
});

if (pnt.integrity.spoofingDetected) {
  console.warn('⚠️ GPS spoofing detected!');
}

```

---

### Python

**Installation:**

```bash
pip install aiyou-sdk

```

**Usage:**

```python
from aiyou import AiYou

client = AiYou(api_key=os.environ['AIYOU_API_KEY'])

# Inference

result = client.inference.create(
    model_id='llama-3-70b-instruct',
    prompt='Explain quantum computing',
    options={
        'latency_priority': 'ultra_low',
        'verification_level': 'high'
    }
)

print(result.result.text)
print(f"Latency: {result.performance.latency_ms}ms")

# Verify

verification = client.shadowtag.verify(
    inference_id=result.inference_id,
    signature=result.shadowtag.signature
)

assert verification.status == 'verified'

```

---

### Rust (for embedded / high-performance)

**Cargo.toml:**

```toml
[dependencies]
aiyou-sdk = "0.1"
tokio = { version = "1", features = ["full"] }

```

**Usage:**

```rust
use aiyou_sdk::{AiYou, InferenceRequest};

#[tokio::main]

async fn main() {
    let client = AiYou::new(std::env::var("AIYOU_API_KEY").unwrap());

    let result = client
        .inference()
        .create(InferenceRequest {
            model_id: "llama-3-70b-instruct".to_string(),
            prompt: "Explain quantum computing".to_string(),
            ..Default::default()
        })
        .await
        .unwrap();

    println!("Result: {}", result.result.text);
    println!("Latency: {}ms", result.performance.latency_ms);
}

```

---

## 4. Ingestion API (PNKLN: Preparation)

The Ingestion API allows external services to submit intelligence items for collection, classification, and ingestion into the PNKLN pipeline.

### POST /ingestion/submit

Submit an intelligence item for ingestion.

**Request:**

```json
{
  "source": {
    "type": "news_api",
    "url": "https://example.com/article",
    "domain": "example.com"
  },
  "content": {
    "title": "Breaking: New Aviation Safety Regulation",
    "summary": "FAA announces DO-178D update...",
    "full_text": "[Full article text...]",
    "published_at": "2025-11-15T14:00:00Z"
  },
  "metadata": {
    "tags": ["aviation", "regulation"],
    "priority": "high"
  }
}

```

**Response (202 Accepted):**

```json
{
  "item_id": "ing_2025-11-15_x8y7z6",
  "status": "accepted",
  "message": "Item queued for classification",
  "estimated_processing_time_ms": 5000,
  "next_steps": [
    "tier_classification",
    "validation",
    "attestation"
  ]
}

```

### GET /ingestion/sources

List configured data sources and their health status.

**Response:**

```json
{
  "sources": [
    {
      "id": "youtube-api-v3",
      "type": "video",
      "status": "healthy",
      "daily_quota": 10000,
      "quota_used": 7234,
      "last_successful_fetch": "2025-11-15T14:20:00Z",
      "tier_1_yield": 0.18
    },
    {
      "id": "twitter-basic",
      "type": "social",
      "status": "rate_limited",
      "daily_quota": 15000,
      "quota_used": 15000,
      "last_successful_fetch": "2025-11-15T12:45:00Z",
      "tier_1_yield": 0.11
    }
  ],
  "summary": {
    "total_sources": 87,
    "healthy": 82,
    "degraded": 3,
    "failed": 2
  }
}

```

### GET /ingestion/items/{item_id}

Retrieve status and classification results for a submitted item.

**Response:**

```json
{
  "item_id": "ing_2025-11-15_x8y7z6",
  "status": "completed",
  "classification": {
    "tier": 1,
    "confidence": 0.92,
    "reasoning": "Primary source document with strategic implications",
    "tags": ["aviation", "regulation", "DO-178D"]
  },
  "validation_result": {
    "status": "passed",
    "compliance_framework_coverage": 0.984,
    "judge_id": "val_a1b2c3"
  },
  "shadowtag": {
    "attestation_level": "L4",
    "signature": "cose:a10126a1045249502b13...",
    "verification_url": "https://shadowtag.aiyou.io/verify/ing_2025-11-15_x8y7z6"
  },
  "processing_time_ms": 4723
}

```

---

## 5. Validation API (PNKLN: Judge 6)

The Validation API provides real-time Compliance Framework compliance validation and JR (Joint Requirements) checking for intelligence items.

### POST /validation/validate

Validate an intelligence item against Compliance Framework rules and JR compliance.

**Request:**

```json
{
  "item_id": "ing_2025-11-15_x8y7z6",
  "validation_profile": "defense_isr",  // "defense_isr" | "aviation" | "faang" | "general"
  "options": {
    "strict_mode": true,
    "require_human_review": false,
    "compliance_framework_coverage_threshold": 0.98
  }
}

```

**Response (200 OK - PASS):**

```json
{
  "validation_id": "val_a1b2c3d4e5",
  "result": "PASS",
  "compliance_framework_scores": {
    "source_reliability": "B (Usually Reliable)",
    "credibility": 2,
    "timeliness": "current (<24h)",
    "completeness": 0.95,
    "relevance": 3,
    "classification": "UNCLASSIFIED//FOUO"
  },
  "jr_compliance": {
    "itar_check": "passed",
    "ear_check": "passed",
    "nist_rmf_controls": "Level 5 - passed",
    "opsec_violations": []
  },
  "quality_metrics": {
    "coverage": 0.984,
    "false_positive_probability": 0.012,
    "confidence": 0.96
  },
  "next_action": "shadowtag_l4_attestation",
  "latency_ms": 67.3
}

```

**Response (200 OK - FAIL):**

```json
{
  "validation_id": "val_f6g7h8i9j0",
  "result": "FAIL",
  "failure_reasons": [
    {
      "rule": "ITAR Category VIII",
      "severity": "critical",
      "description": "Keyword 'avionics architecture' matches export-controlled technical data",
      "matched_text": "...new F-35 avionics architecture integrates..."
    }
  ],
  "compliance_framework_scores": {
    "source_reliability": "C (Fairly Reliable)",
    "credibility": 2,
    "timeliness": "current (<24h)",
    "completeness": 0.88,
    "relevance": 3,
    "classification": "SECRET//NOFORN"
  },
  "jr_compliance": {
    "itar_check": "FAILED - Category VIII violation",
    "ear_check": "flagged",
    "nist_rmf_controls": "pending manual review",
    "opsec_violations": ["potential_troop_movement_leak"]
  },
  "recommended_action": "block_and_notify_compliance_team",
  "latency_ms": 72.1
}

```

**Response (200 OK - FLAG):**

```json
{
  "validation_id": "val_k1l2m3n4o5",
  "result": "FLAG",
  "flag_reasons": [
    {
      "rule": "Borderline Credibility",
      "severity": "medium",
      "description": "Credibility score 3.5 falls in borderline range (3-4)",
      "recommendation": "human_review"
    }
  ],
  "compliance_framework_scores": {
    "source_reliability": "C (Fairly Reliable)",
    "credibility": 3.5,
    "timeliness": "current (<48h)",
    "completeness": 0.82,
    "relevance": 2,
    "classification": "UNCLASSIFIED"
  },
  "jr_compliance": {
    "itar_check": "passed",
    "ear_check": "passed",
    "nist_rmf_controls": "Level 3 - passed",
    "opsec_violations": []
  },
  "recommended_action": "shadowtag_l2_attestation_with_review_flag",
  "human_review_required": true,
  "latency_ms": 89.4
}

```

### GET /validation/rules

List all Compliance Framework rules and JR compliance checks.

**Response:**

```json
{
  "compliance_framework_rules": {
    "total_rules": 127,
    "categories": [
      {
        "category": "Source Reliability",
        "rule_count": 18,
        "description": "Evaluate trustworthiness of data sources (A-F scale)"
      },
      {
        "category": "Information Credibility",
        "rule_count": 22,
        "description": "Assess likelihood of content accuracy (1-6 scale)"
      },
      {
        "category": "Timeliness",
        "rule_count": 12,
        "description": "Check temporal relevance (tactical vs strategic)"
      },
      {
        "category": "Completeness",
        "rule_count": 31,
        "description": "Verify SALUTE format compliance"
      }
    ]
  },
  "jr_compliance_checks": {
    "total_checks": 45,
    "categories": [
      {
        "category": "ITAR",
        "check_count": 15,
        "description": "Export control for defense articles (Categories I-XXI)"
      },
      {
        "category": "EAR",
        "check_count": 8,
        "description": "Dual-use commercial items with military applications"
      },
      {
        "category": "NIST RMF",
        "check_count": 12,
        "description": "Cybersecurity controls (800-53 High Baseline)"
      }
    ]
  }
}

```

### POST /validation/batch

Validate multiple items in a single request (batch mode).

**Request:**

```json
{
  "items": [
    {"item_id": "ing_2025-11-15_a1"},
    {"item_id": "ing_2025-11-15_a2"},
    {"item_id": "ing_2025-11-15_a3"}
  ],
  "validation_profile": "general",
  "options": {
    "parallel_execution": true,
    "max_latency_ms": 200
  }
}

```

**Response:**

```json
{
  "batch_id": "batch_x7y8z9",
  "results": [
    {
      "item_id": "ing_2025-11-15_a1",
      "validation_id": "val_1",
      "result": "PASS",
      "latency_ms": 65.2
    },
    {
      "item_id": "ing_2025-11-15_a2",
      "validation_id": "val_2",
      "result": "FAIL",
      "latency_ms": 71.8
    },
    {
      "item_id": "ing_2025-11-15_a3",
      "validation_id": "val_3",
      "result": "FLAG",
      "latency_ms": 88.3
    }
  ],
  "summary": {
    "total_items": 3,
    "passed": 1,
    "failed": 1,
    "flagged": 1,
    "avg_latency_ms": 75.1,
    "p99_latency_ms": 88.3
  }
}

```

---

## Rate Limits

| Tier | Requests/Minute | Requests/Day | Burst |
|------|-----------------|--------------|-------|
| **Free** | 60 | 1,000 | 10 |
| **Starter** ($500/mo) | 1,000 | 100,000 | 100 |
| **Pro** ($3K/mo) | 10,000 | 1,000,000 | 1,000 |
| **Enterprise** | Custom | Custom | Custom |

**Rate limit headers:**

```

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1700000000

```

---

## Webhooks

Subscribe to events (e.g., inference completed, spoofing detected).

**Register webhook:**

```bash
curl -X POST https://api.aiyou.io/v1/webhooks \
  -H "Authorization: Bearer $AIYOU_API_KEY" \
  -d '{
    "url": "https://yourapp.com/webhooks/aiyou",
    "events": ["inference.completed", "pnt.spoofing_detected"]
  }'

```

**Webhook payload example:**

```json
{
  "event": "pnt.spoofing_detected",
  "timestamp": "2025-11-15T14:23:45.678901234Z",
  "data": {
    "solution_id": "pnt_f8e7d6c5b4a3",
    "anomaly_score": 0.94,
    "triggers": ["gnss_celestial_mismatch"]
  }
}

```

---

## Error Codes

| Code | HTTP Status | Meaning | Action |
|------|-------------|---------|--------|
| `invalid_api_key` | 401 | API key missing or invalid | Check authentication |
| `rate_limit_exceeded` | 429 | Too many requests | Retry after delay |
| `model_not_found` | 404 | Requested model doesn't exist | Check `/models` endpoint |
| `pop_unavailable` | 503 | Nearest PoP is down | Automatic failover in progress |
| `insufficient_credits` | 402 | Account balance too low | Add payment method |
| `verification_failed` | 400 | ShadowTag signature invalid | Check payload integrity |

---

## Support & Documentation


- **API Reference:** https://docs.aiyou.io/api

- **SDKs:** https://github.com/aiyou-platform/sdks

- **Status Page:** https://status.aiyou.io

- **Support:** support@aiyou.io

- **Discord:** https://discord.gg/aiyou
