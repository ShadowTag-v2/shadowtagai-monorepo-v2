## KUVASZ ASSESSMENT

┌─────────────────────────────────────────────────────────────────┐
│ KUVASZ [ˈkuvɒs] - Open-Source Uptime & SSL Monitoring          │
│ Tech: Kotlin | License: Apache 2.0 | 59 stars                  │
└─────────────────────────────────────────────────────────────────┘

### WHAT IT IS

Self-hosted uptime/SSL monitoring with:
- HTTP(S) monitoring (5-second intervals)
- SSL cert expiration alerts
- Status pages (public/private, brandable)
- Multi-channel notifications: Email, Discord, Slack, Telegram, PagerDuty
- Prometheus + OpenTelemetry export
- IAC via YAML config
- Full REST API
- PostgreSQL backend, single Docker image

### JR ENGINE SCAN

| Gate | Status | Notes |
|------|--------|-------|
| **Purpose** | ⚠️ INDIRECT | Doesn't advance Pnkln core stack directly |
| **Reasons** | ✅ VALID | Legitimate ops tooling for infrastructure monitoring |
| **Brakes** | ✅ PASS | Self-hosted, no vendor lock, Apache 2.0 |

### RELEVANCE TO PNKLN

```
DIRECT FIT: LOW
├── Not a revenue generator
├── Not part of Judge#6/JR Engine/Cor/ShadowTag
└── Commodity monitoring (many alternatives exist)

INDIRECT VALUE: MEDIUM
├── Could monitor AiU+ShadowTag-v2 endpoints post-launch
├── Prometheus integration → existing observability stack
└── Self-hosted → GCP cost control vs SaaS monitoring fees
```

### COMPETITIVE POSITION

vs **Uptime Kuma** (82K stars): Less adoption, more features (YAML IAC, OTLP)
vs **UptimeRobot**: Free self-hosted alternative, 5s vs 5min intervals
vs **Checkmate**: Similar positioning, Kuvasz more mature

### OPTIONS

| Option | Action | Risk |
|--------|--------|------|
| **BEST** | Defer. Not mission-critical pre-revenue | None |
| **FAST** | `docker run kuvaszmonitoring/kuvasz` when needed | Low |
| **CHEAP** | Use GCP Uptime Checks ($0.30/check/month) | Lock-in |

### VERDICT

```
┌─────────────────────────────────────────────────────────────────┐
│ RECOMMENDATION: NOT NOW                                        │
│                                                                 │
│ At $0K burn / zero revenue, monitoring tooling is premature.   │
│ Revisit when:                                                   │
│   1. Production endpoints exist to monitor                      │
│   2. SLA commitments require uptime proof                       │
│   3. Status pages needed for customer trust                     │
│                                                                 │
│ Bookmark for M3+ when GKE-native prod goes live.               │
└─────────────────────────────────────────────────────────────────┘
```
