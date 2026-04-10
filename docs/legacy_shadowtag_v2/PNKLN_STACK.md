# pnkln Core Stack™ Documentation

## Overview

The pnkln Core Stack™ is an AI-powered intelligence collection and delivery system built on FastAPI, featuring:

- **Gemini Ingestion Layer**: Multi-source data collection with ethical crawling
- **Judge #6 Validation**: Hybrid Gemini+PyTorch content validation system
- **Tier Classification**: Intelligent content prioritization (Tier 1/2/3)
- **AM Briefing Delivery**: Automated morning intelligence summaries

## Architecture

### 4-Namespace GKE Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                     pnkln Core Stack™                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Ingestion   │ -> │  Validation  │ -> │  Processing  │  │
│  │  Namespace   │    │  Namespace   │    │  Namespace   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │         │
│         └────────────────────┴────────────────────┘         │
│                              │                              │
│                      ┌──────────────┐                       │
│                      │   Delivery   │                       │
│                      │  Namespace   │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Integration Flow

```
External Sources (YouTube, Twitter, News, RSS)
    │
    ▼
┌─────────────────────┐
│ Gemini Ingestion    │  CronJob: Nightly ~45min runtime
│ - Multi-source      │  Cost: ~$77/month
│ - Ethical crawling  │  Confidence: ≥60%
│ - Rate limiting     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Judge #6 Validation │  Hybrid: Gemini + PyTorch
│ - Content filtering │  Target: p99 ≤90ms
│ - Quality gates     │  FP/FN: ≤2%
│ - Confidence scoring│
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Tier Classification │  Tier 1: High-value (≥80%)
│ - Relevance scoring │  Tier 2: Medium (≥50%)
│ - Cost optimization │  Tier 3: Low (<50%)
│ - Source diversity  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ AM Briefing         │  Delivery: 06:00 daily
│ - Markdown format   │  Format: Highlights + Metrics
│ - Top highlights    │  QA: Gate-checked
└─────────────────────┘
```

## Components

### 1. Gemini Ingestion Layer

**Purpose**: Collect intelligence from multiple sources with ethical compliance

**Features**:

- Multi-source ingestion (YouTube, Twitter, News, RSS)
- Ethical crawling (robots.txt, rate limiting)
- Real-time compliance tracking
- Cost-per-item optimization

**API Endpoints**:

- `POST /api/v1/ingestion/run` - Run ingestion pipeline
- `GET /api/v1/ingestion/metrics` - Get latest metrics
- `GET /api/v1/ingestion/compliance` - Compliance report
- `GET /api/v1/ingestion/sources` - List enabled sources
- `GET /api/v1/ingestion/quality-gates` - Quality gate config

**Key Metrics**:

- Runtime: Target ≤45 minutes/night
- Cost: Target ≤$77/month
- Daily items: ≥100
- Unique sources: ≥10
- Cost/item: ≤$0.05
- Relevance score: ≥0.70

**Configuration**:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.1-pro
INGESTION_RUNTIME_TARGET=45
INGESTION_MONTHLY_BUDGET=77.0
ENABLE_YOUTUBE_INGESTION=true
ENABLE_TWITTER_INGESTION=true
ENABLE_NEWS_INGESTION=true
ENABLE_RSS_INGESTION=true
RESPECT_ROBOTS_TXT=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### 2. Judge #6 Validation System

**Purpose**: Validate and filter ingested content using hybrid AI

**Features**:

- Hybrid Gemini+PyTorch validation
- Confidence-based filtering
- False positive/negative tracking
- Performance monitoring (latency, throughput)

**API Endpoints**:

- `POST /api/v1/validation/validate-item` - Validate single item
- `POST /api/v1/validation/validate-batch` - Validate batch
- `GET /api/v1/validation/metrics` - Performance metrics
- `GET /api/v1/validation/gates` - Performance gates
- `GET /api/v1/validation/status` - Service status

**Key Metrics**:

- Average latency: Target <50ms
- P99 latency: Target ≤90ms
- False positive rate: Target ≤2%
- False negative rate: Target ≤2%
- Confidence: Target ≥70% (prod), ≥60% (pre-prod)

**Configuration**:

```env
JUDGE_ENABLED=true
JUDGE_CONFIDENCE_THRESHOLD=0.70
JUDGE_FP_RATE_THRESHOLD=0.02
JUDGE_FN_RATE_THRESHOLD=0.02
```

### 3. Tier Classification

**Purpose**: Prioritize content by value/relevance

**Tiers**:

- **Tier 1** (High-value): Relevance ≥80% - Priority processing
- **Tier 2** (Medium-value): Relevance ≥50% - Standard processing
- **Tier 3** (Low-value): Relevance <50% - Optional/archive

**Distribution Targets**:

- Tier 1: 30% of items
- Tier 2: 50% of items
- Tier 3: 20% of items

**Configuration**:

```env
TIER_1_THRESHOLD=0.80
TIER_2_THRESHOLD=0.50
```

### 4. AM Briefing Delivery

**Purpose**: Generate and deliver morning intelligence summaries

**Features**:

- Automated 06:00 delivery
- Markdown formatting
- Tier 1 highlights
- Quality metrics overview
- Gate status reporting

**API Endpoints**:

- `GET /api/v1/pnkln/briefing/latest` - Get latest briefing

**Configuration**:

```env
BRIEFING_DELIVERY_TIME=06:00
BRIEFING_FORMAT=markdown
```

## Metrics & Monitoring

### Comprehensive Metrics

**API Endpoint**: `GET /api/v1/metrics/overview`

Returns:

- **Cost Metrics**: Daily/monthly costs, budget utilization
- **Performance Metrics**: Runtime, latency, throughput
- **Quality Metrics**: Tier distribution, relevance, approval rates
- **Compliance Metrics**: Violations, compliance score

### SLA Monitoring

**API Endpoint**: `GET /api/v1/metrics/sla-status`

Checks:

- Ingestion runtime ≤45 min
- Validation P99 latency ≤90ms
- Monthly cost ≤$77
- FP rate ≤2%
- FN rate ≤2%
- Compliance score ≥95%

### Stack Health

**API Endpoint**: `GET /api/v1/pnkln/status`

Returns health for all 4 namespaces:

- pnkln-ingestion
- pnkln-validation
- pnkln-processing
- pnkln-delivery

## Usage Examples

### Run Complete Pipeline

```python
import httpx

async with httpx.AsyncClient() as client:
    # Run ingestion
    response = await client.post(
        "http://localhost:8000/api/v1/ingestion/run",
        json={"sources": None}
    )
    metrics = response.json()

    # Check validation
    validation = await client.get(
        "http://localhost:8000/api/v1/validation/metrics"
    )

    # Get briefing
    briefing = await client.get(
        "http://localhost:8000/api/v1/pnkln/briefing/latest"
    )
```

### Run from Command Line

```bash
# Run complete pipeline demo
python examples/pnkln_complete_pipeline.py

# Simulate 4-namespace integration
python examples/gke_namespace_integration.py
```

### Check SLA Compliance

```bash
curl http://localhost:8000/api/v1/metrics/sla-status
```

## Ethical Compliance

### Robots.txt Adherence

The system respects `robots.txt` directives from all crawled sites:

```env
RESPECT_ROBOTS_TXT=true
```

### Rate Limiting

Requests are rate-limited to avoid overwhelming sources:

```env
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### Transparency

Clear user agent identification:

```env
USER_AGENT=pnkln-Ingestion-Bot/1.0 (+https://pnkln.ai/bot)
CRAWL_TRANSPARENCY_ENABLED=true
```

### Compliance Monitoring

Track violations in real-time:

```bash
curl http://localhost:8000/api/v1/ingestion/compliance
```

## Performance Optimization

### Runtime Optimization

**Target**: ≤45 minutes/night

Strategies:

- Parallel source processing
- Efficient API usage
- Caching frequently accessed data
- Connection pooling

### Cost Optimization

**Target**: ≤$77/month (~$2.57/day)

Strategies:

- Tier-based processing priorities
- Batch API calls
- Optimize token usage
- Cache validation results

### Quality Gates

**Purpose**: Ensure data meets minimum standards

Gates:

- ✓ Daily items ≥100
- ✓ Unique sources ≥10
- ✓ Cost/item ≤$0.05
- ✓ Relevance ≥0.70

Failed gates trigger alerts and prevent delivery.

## Deployment

### GKE Configuration

The stack deploys across 4 namespaces:

```yaml
# Ingestion Namespace
namespace: pnkln-ingestion
components:
  - gemini-ingestion-cronjob
  - source-crawlers

# Validation Namespace
namespace: pnkln-validation
components:
  - judge-six-service
  - validation-api

# Processing Namespace
namespace: pnkln-processing
components:
  - tier-classifier
  - analytics-service

# Delivery Namespace
namespace: pnkln-delivery
components:
  - briefing-generator
  - delivery-scheduler
```

### Environment Setup

1. Copy environment template:

```bash
cp .env.example .env
```

2. Configure API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
```

3. Adjust thresholds as needed:

```env
INGESTION_RUNTIME_TARGET=45
INGESTION_MONTHLY_BUDGET=77.0
JUDGE_CONFIDENCE_THRESHOLD=0.70
```

4. Deploy:

```bash
# Local
make run

# Docker
make docker-up

# Production
./scripts/deploy.sh v1.0.0
```

## Troubleshooting

### Common Issues

**Ingestion runtime exceeds target**:

- Check source availability
- Review rate limiting settings
- Consider parallel processing
- Optimize API calls

**High cost per item**:

- Review tier distribution
- Check for redundant processing
- Optimize Gemini API usage
- Review source selection

**Low validation approval rate**:

- Adjust Judge #6 thresholds
- Review source quality
- Check relevance scoring
- Validate tier thresholds

**Compliance violations**:

- Review robots.txt parsing
- Check rate limiting configuration
- Verify user agent string
- Monitor flagged domains

## References

- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Ethical Web Scraping](https://www.scrapehero.com/web-scraping-best-practices/)

---

**Version**: 0.1.0
**Last Updated**: 2025-11-15
**Confidence Threshold**: Pre-prod ≥60%, Prod ≥70%
