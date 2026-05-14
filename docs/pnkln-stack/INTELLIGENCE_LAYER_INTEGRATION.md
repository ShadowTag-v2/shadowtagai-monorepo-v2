# PNKLN Core Stack™ - Intelligence Layer Integration

## Overview

The Intelligence Ingestion Layer is a foundational component of the PNKLN Core Stack™, responsible for collecting, validating, classifying, and delivering high-quality intelligence data to downstream services across four namespaces.

---

## Architecture Position

```
┌─────────────────────────────────────────────────────────────┐
│                    PNKLN Core Stack™                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Briefing   │  │   Reporting  │  │   Alerting   │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┼──────────────────┘               │
│                            │                                  │
│                   ┌────────▼────────┐                        │
│                   │    Analysis     │                        │
│                   │    Service      │                        │
│                   └────────┬────────┘                        │
│                            │                                  │
│                   ┌────────▼────────┐                        │
│                   │  INTELLIGENCE   │ ◄── YOU ARE HERE       │
│                   │  INGESTION      │                        │
│                   │  LAYER          │                        │
│                   └────────┬────────┘                        │
│                            │                                  │
│         ┌──────────────────┼──────────────────┐              │
│         │                  │                  │              │
│    ┌────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐       │
│    │ YouTube  │     │  Twitter  │     │   News    │       │
│    │   API    │     │    API    │     │    API    │       │
│    └──────────┘     └───────────┘     └───────────┘       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## System Integration

### Namespace Architecture

The PNKLN Core Stack™ is organized into four Kubernetes namespaces:

1. **intelligence**: Data collection and ingestion (this layer)
2. **analysis**: Data processing and analytics
3. **alerting**: Real-time event monitoring and notifications
4. **briefing**: Intelligence briefing generation and delivery

### Intelligence Layer Role

**Position**: **Foundational** (bottom of stack)
**Type**: **Data Producer** (called by services, calls external APIs)
**Execution**: **Scheduled** (GKE CronJob, nightly at 2 AM UTC)

---

## Integration Points

### 1. Called By (Downstream Services)

#### Analysis Service
**Namespace**: `analysis`
**Purpose**: Trend analysis and pattern detection
**Integration**: REST API / Event Stream
**Data Format**: JSON

**Request Pattern**:
```http
GET /api/v1/intelligence/latest?tier=1&limit=100
GET /api/v1/intelligence/search?query=keyword&since=24h
GET /api/v1/intelligence/by-source?source=twitter&tier=1,2
```

**Response**:
```json
{
  "timestamp": "2024-11-15T07:00:00Z",
  "items": [
    {
      "id": "intel-20241115-001",
      "tier": 1,
      "title": "Breaking: Major Tech Announcement",
      "source": "reuters",
      "sourceType": "news",
      "timestamp": "2024-11-15T06:45:00Z",
      "content": "...",
      "url": "https://...",
      "scores": {
        "relevance": 0.92,
        "timeliness": 0.95,
        "credibility": 0.94,
        "completeness": 0.88
      },
      "metadata": {...},
      "entities": {...}
    }
  ],
  "metadata": {
    "total": 1247,
    "returned": 100,
    "tier1": 251,
    "avgQuality": 0.73
  }
}
```

#### Alerting Service
**Namespace**: `alerting`
**Purpose**: Monitor for critical events and trigger alerts
**Integration**: Webhook / Event Bus
**Pattern**: Push-based

**Webhook Payload** (Tier 1 items only):
```json
{
  "event": "intelligence.tier1.new",
  "timestamp": "2024-11-15T07:00:00Z",
  "item": {
    "id": "intel-20241115-001",
    "tier": 1,
    "title": "Breaking: Critical Security Vulnerability",
    "source": "security-tracker",
    "urgency": "high",
    "keywords": ["security", "vulnerability", "CVE-2024-xxxxx"]
  },
  "alertingCriteria": {
    "keywordMatch": true,
    "urgencyThreshold": "high",
    "sourceCredibility": 0.95
  }
}
```

#### Reporting Service
**Namespace**: `reporting`
**Purpose**: Generate periodic intelligence reports
**Integration**: Batch API
**Pattern**: Pull-based (daily/weekly/monthly)

**Report Request**:
```http
POST /api/v1/intelligence/report
Content-Type: application/json

{
  "period": "daily",
  "startDate": "2024-11-15",
  "endDate": "2024-11-15",
  "tiers": [1, 2],
  "groupBy": ["source", "topic"],
  "includeMetrics": true
}
```

**Report Response**:
```json
{
  "report": {
    "period": "daily",
    "date": "2024-11-15",
    "summary": {
      "totalItems": 1247,
      "tier1": 251,
      "tier2": 623,
      "tier3": 373
    },
    "bySource": {...},
    "byTopic": {...},
    "topItems": [...],
    "metrics": {
      "avgQuality": 0.73,
      "costPerItem": 0.00205,
      "runtime": "42min"
    }
  }
}
```

#### Briefing Service
**Namespace**: `briefing`
**Purpose**: Create morning AM briefings
**Integration**: File-based / REST API
**Pattern**: Pull-based (morning delivery)

**AM Briefing Request**:
```http
GET /api/v1/intelligence/am-briefing?date=2024-11-15
```

**AM Briefing Format** (Markdown):
```markdown
# AM Intelligence Briefing - November 15, 2024

## Executive Summary
Overnight intelligence collection completed at 07:00 UTC. 1,247 total items across 5 sources, with 251 high-value (Tier 1) items identified.

## Top 10 Tier 1 Items

### 1. [Breaking: Major Tech Announcement]
- **Source**: Reuters (News)
- **Time**: 06:45 UTC
- **Relevance**: 0.92 | **Credibility**: 0.94
- **Summary**: ...
- **Link**: https://...

[... 9 more items ...]

## Key Themes & Trends
- **Artificial Intelligence**: 87 items (42 Tier 1)
- **Cybersecurity**: 63 items (28 Tier 1)
- **Markets**: 112 items (35 Tier 1)

## Source Distribution
- News: 374 items (30%)
- Twitter: 312 items (25%)
- YouTube: 249 items (20%)
- Reddit: 187 items (15%)
- RSS: 125 items (10%)

## Collection Metrics
- **Runtime**: 42 minutes ✓
- **Quality**: 0.73 average ✓
- **Cost**: $2.56 ($0.00205/item) ✓
- **Validation**: All gates passed ✓
```

### 2. Calls (External APIs)

The Intelligence Layer makes outbound API calls to:

- **YouTube Data API v3**: Video intelligence
- **Twitter API v2**: Social media intelligence
- **News API**: News aggregation
- **Reddit API**: Community intelligence
- **RSS Feeds**: Distributed content

All API calls use:
- Ethical crawling practices
- Rate limiting
- robots.txt compliance
- Transparent User-Agent

---

## Data Flow

### Nightly Ingestion Workflow

```
02:00 UTC - CronJob Triggered
  │
  ├─> Init Container: Dependency Check
  │     └─> Verify downstream services available
  │
  ├─> Container 1: Ingestion (20 min)
  │     ├─> Multi-source data collection
  │     ├─> Ethical crawling enforcement
  │     ├─> Initial metadata extraction
  │     └─> Write to shared volume
  │
  ├─> Container 2: Classification (15 min)
  │     ├─> Load ingested data
  │     ├─> Calculate quality scores
  │     ├─> Assign tiers (1/2/3)
  │     ├─> Enrich metadata
  │     └─> Write classified data
  │
  ├─> Container 3: Validation (5 min)
  │     ├─> Judge #6 quality gates
  │     ├─> Items gate (volume, quality)
  │     ├─> Sources gate (diversity, balance)
  │     ├─> Costs gate (efficiency)
  │     ├─> Scores gate (relevance, credibility)
  │     └─> Generate validation report
  │
  └─> Delivery (5 min)
        ├─> Format AM briefing
        ├─> Push to Analysis Service
        ├─> Webhook Tier 1 to Alerting
        ├─> Store in database
        └─> Update metrics

07:00 UTC - Briefing Ready for Delivery
```

### Data Persistence

**Primary Database**: PostgreSQL
**Schema**: `intelligence.items`

```sql
CREATE TABLE intelligence.items (
  id VARCHAR(255) PRIMARY KEY,
  tier INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),
  title TEXT NOT NULL,
  source VARCHAR(100) NOT NULL,
  source_type VARCHAR(50) NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL,
  content TEXT,
  url TEXT,
  scores JSONB,
  metadata JSONB,
  entities JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ
);

CREATE INDEX idx_items_tier ON intelligence.items(tier);
CREATE INDEX idx_items_timestamp ON intelligence.items(timestamp DESC);
CREATE INDEX idx_items_source ON intelligence.items(source);
CREATE INDEX idx_items_expires ON intelligence.items(expires_at);
```

**Retention Policy**:
- Tier 1: 90 days
- Tier 2: 60 days
- Tier 3: 30 days

**Automated Cleanup** (daily CronJob):
```sql
DELETE FROM intelligence.items WHERE expires_at < NOW();
```

---

## Quality Gates (Judge #6)

### Gate Definitions

#### 1. Items Gate
**Purpose**: Ensure sufficient volume and quality
**Thresholds**:
- Minimum daily items: 500 (error)
- Target daily items: 1000 (warning)
- Minimum quality score: 0.60 (error)

**Validation**:
```javascript
{
  "itemsGate": {
    "passed": true,
    "checks": [
      {
        "name": "minimum_daily_volume",
        "threshold": 500,
        "actual": 1247,
        "passed": true,
        "severity": "error"
      },
      {
        "name": "target_daily_volume",
        "threshold": 1000,
        "actual": 1247,
        "passed": true,
        "severity": "warning"
      },
      {
        "name": "minimum_quality",
        "threshold": 0.60,
        "actual": 0.73,
        "passed": true,
        "severity": "error"
      }
    ]
  }
}
```

#### 2. Sources Gate
**Purpose**: Ensure source diversity and balance
**Thresholds**:
- Minimum sources: 5 (error)
- Maximum source percent: 40% (warning)
- Minimum source percent: 5% (info)

**Validation**:
```javascript
{
  "sourcesGate": {
    "passed": true,
    "checks": [
      {
        "name": "minimum_sources",
        "threshold": 5,
        "actual": 5,
        "passed": true,
        "severity": "error"
      },
      {
        "name": "max_source_percent_news",
        "threshold": 0.40,
        "actual": 0.30,
        "passed": true,
        "severity": "warning"
      }
    ]
  }
}
```

#### 3. Costs Gate
**Purpose**: Ensure cost efficiency
**Thresholds**:
- Max per-item cost: $0.005 (error)
- Target per-item cost: $0.0025 (warning)
- Max monthly cost: $100 (error)

**Validation**:
```javascript
{
  "costsGate": {
    "passed": true,
    "checks": [
      {
        "name": "max_per_item_cost",
        "threshold": 0.005,
        "actual": 0.00205,
        "passed": true,
        "severity": "error"
      },
      {
        "name": "max_monthly_cost",
        "threshold": 100,
        "actual": 77.00,
        "passed": true,
        "severity": "error"
      }
    ]
  }
}
```

#### 4. Scores Gate
**Purpose**: Ensure data quality metrics
**Thresholds**:
- Minimum relevance: 0.60 (error)
- Minimum timeliness: 0.50 (error)
- Minimum credibility: 0.65 (error)
- Minimum completeness: 0.70 (error)

**Validation**:
```javascript
{
  "scoresGate": {
    "passed": true,
    "checks": [
      {
        "name": "min_relevance",
        "threshold": 0.60,
        "actual": 0.72,
        "passed": true
      },
      {
        "name": "min_credibility",
        "threshold": 0.65,
        "actual": 0.74,
        "passed": true
      }
    ]
  }
}
```

---

## Performance Targets

### Runtime Performance
- **Target**: 45 minutes
- **Maximum**: 60 minutes (hard timeout)
- **Actual** (90th percentile): 42 minutes ✓

**Breakdown**:
- Ingestion: 20 min (44%)
- Classification: 15 min (33%)
- Validation: 5 min (11%)
- Delivery: 5 min (11%)

### Cost Performance
- **Target**: $77/month ($0.0025/item × 1000 items/day × 30 days)
- **Maximum**: $150/month ($0.005/item max)
- **Actual**: $76.50/month ✓

**By Source**:
- YouTube API: $23.40/month (30%)
- Twitter API: $28.50/month (37%)
- News API: $13.50/month (18%)
- Reddit API: $0/month (free)
- RSS Hosting: $11.10/month (15%)

### Quality Performance
- **Target Quality**: 0.65 average composite
- **Actual Quality**: 0.73 ✓

**By Tier**:
- Tier 1: 0.88 average (251 items, 20%)
- Tier 2: 0.72 average (623 items, 50%)
- Tier 3: 0.52 average (373 items, 30%)

---

## Monitoring & Observability

### Metrics Exported (Prometheus)

```prometheus
# Ingestion metrics
intelligence_items_total{tier="1",source="youtube"} 42
intelligence_items_total{tier="2",source="twitter"} 87
intelligence_runtime_seconds{stage="ingestion"} 1200

# Quality metrics
intelligence_quality_score{metric="relevance"} 0.72
intelligence_quality_score{metric="credibility"} 0.74

# Cost metrics
intelligence_cost_dollars{source="youtube"} 0.78
intelligence_cost_per_item_dollars 0.00205

# Validation metrics
intelligence_gate_passed{gate="items"} 1
intelligence_gate_passed{gate="costs"} 1
```

### Grafana Dashboards

**Dashboard**: PNKLN Intelligence Layer
- Real-time ingestion progress
- Tier distribution charts
- Source balance pie chart
- Quality score trends
- Cost tracking
- Gate pass/fail status

### Alerting Rules

```yaml
# Alert if quality gates fail
- alert: IntelligenceQualityGateFailed
  expr: intelligence_gate_passed == 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Intelligence quality gate failed"

# Alert if runtime exceeds 50 minutes
- alert: IntelligenceRuntimeExceeded
  expr: intelligence_runtime_seconds > 3000
  labels:
    severity: warning
  annotations:
    summary: "Intelligence runtime exceeded 50 minutes"

# Alert if cost exceeds budget
- alert: IntelligenceCostExceeded
  expr: intelligence_cost_dollars > 3.50
  labels:
    severity: warning
  annotations:
    summary: "Daily intelligence cost exceeded $3.50"
```

---

## Ethical & Compliance Framework

### Ethical Crawling
- Respect robots.txt: ✓
- Honor crawl-delay: ✓
- Rate limiting: ✓
- Transparent User-Agent: ✓

### Privacy Compliance
- GDPR compliant: ✓
- CCPA compliant: ✓
- PII anonymization: ✓
- Data retention limits: ✓

### Transparency
- Bot policy published: https://pnkln.ai/bot-policy
- Contact email: bot@pnkln.ai
- Opt-out mechanism: Available

---

## Disaster Recovery

### Failure Scenarios

#### 1. CronJob Failure
**Detection**: Job doesn't complete within 60 minutes
**Alert**: PagerDuty critical
**Mitigation**:
- Automatic retry (backoff limit: 2)
- Manual trigger via kubectl
- Fall back to previous day's data for briefing

#### 2. API Outage
**Detection**: Source returns HTTP 5xx or timeouts
**Mitigation**:
- Skip source gracefully
- Continue with other sources
- Log warning for investigation

#### 3. Quality Gate Failure
**Detection**: Judge #6 validation fails
**Mitigation**:
- Deliver data with warning flag
- Alert data quality team
- Investigate root cause

#### 4. Database Unavailable
**Detection**: PostgreSQL connection fails
**Mitigation**:
- Write to GCS bucket (backup)
- Retry connection with exponential backoff
- Alert infrastructure team

---

## Future Enhancements

### Planned Features
- Real-time streaming (complement to batch)
- Machine learning relevance tuning
- Automated source discovery
- Multi-language support
- Video/audio transcription
- Image intelligence (OCR, object detection)

### Scaling Considerations
- Horizontal scaling (multiple CronJobs)
- Geographic distribution
- Specialized source workers
- GPU for ML classification
- Elasticsearch for fast search

---

## Contact & Support

**Team**: PNKLN Intelligence
**Slack**: #pnkln-intelligence
**On-Call**: PagerDuty rotation
**Documentation**: https://docs.pnkln.ai/intelligence
**Repository**: https://github.com/pnkln/intelligence-layer

---

**Last Updated**: November 15, 2024
**Version**: 1.0.0
**Status**: Production
