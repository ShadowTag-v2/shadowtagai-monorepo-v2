# PNKLN Ingestion Layer

## Overview

The PNKLN Ingestion Layer is a nightly intelligence collection pipeline that gathers legal document data from multiple sources with ethical compliance and tier-based classification.

**Architecture**: GKE CronJob Multi-Container
**Runtime**: ~45 minutes/night
**Budget**: ~$77/month
**Key Focus**: Ethical crawling, multi-source coverage, tier classification

## Architecture

### Multi-Container Design

The ingestion layer runs as a Kubernetes CronJob with 4 specialized containers:

1. **Ingestion Orchestrator** - Coordinates the pipeline
2. **Crawler** - Fetches data from web sources with ethical compliance
3. **Classifier** - Applies AI-based tier classification
4. **Metrics** - Collects and reports performance data

### Quality Gates

- **Items/Day**: Target based on source availability
- **Source Diversity**: YouTube, Twitter, News, RSS, Legal DBs, Gov sites
- **Cost/Item**: Monitored against $77/month budget
- **Tier Distribution**: Target 20%+ Tier 1 (high-value) items

## Features

### 1. Ethical Compliance

**robots.txt Respect**
```python
from app.ingestion import EthicalCrawler, CrawlerConfig

crawler = EthicalCrawler(CrawlerConfig(
    respect_robots_txt=True,  # Check robots.txt before fetching
    rate_limit_delay=1.0,     # 1 second between requests
    log_all_requests=True     # Full transparency logging
))
```

**Rate Limiting**: Automatic per-domain rate limiting to avoid overloading servers.

**Request Logging**: All requests logged for transparency and compliance auditing.

### 2. Multi-Source Coverage

**Supported Source Types**:
- **YouTube** - Official channels, transcripts
- **Twitter** - Legal experts, verified accounts
- **News** - Reuters, AP, legal news outlets
- **RSS** - Legal blog feeds
- **Legal DBs** - Court filings, case law
- **Government** - Official legal documents

**Source Tiers**:
- **Tier 1**: Authoritative (govt, courts, premium APIs)
- **Tier 2**: Semi-authoritative (major news, verified social)
- **Tier 3**: General web (blogs, forums)

Example:
```python
from app.ingestion import SourceManager, SourceType, SourceTier

manager = SourceManager()

# Get high-value sources
tier_1_sources = manager.get_sources_by_tier(SourceTier.TIER_1)

# Get all YouTube sources
youtube_sources = manager.get_sources_by_type(SourceType.YOUTUBE)

# Coverage stats
stats = manager.get_coverage_stats()
print(f"Active sources: {stats['enabled_sources']}")
print(f"Tier distribution: {stats['tier_distribution']}")
```

### 3. Tier Classification

AI-powered classification evaluates:
- **Relevance**: Legal relevance score (0-1)
- **Timeliness**: Time-sensitivity score (0-1)
- **Completeness**: Information completeness (0-1)

Example:
```python
from app.ingestion import classify_content

result = classify_content(
    content="Contract clause about payment terms...",
    source_name="Reuters Legal",
    source_type="news",
    source_tier=2
)

print(f"Tier: {result.tier.value}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning: {result.reasoning}")
```

### 4. Metrics Collection

**Core Metrics**:
- Items ingested per day
- Unique sources used
- Cost per item
- Tier distribution (% Tier 1/2/3)
- Quality scores (relevance, timeliness, completeness)
- Runtime efficiency

**Ethical Compliance Metrics**:
- robots.txt blocks
- Rate limit waits
- Total requests
- Compliance rate

Example:
```python
from app.ingestion import MetricsCollector

collector = MetricsCollector()

# Record an item
collector.record_item(
    source_id="reuters_legal",
    tier=1,
    cost=0.01,
    relevance=0.85,
    timeliness=0.92,
    completeness=0.78
)

# Get current metrics
metrics = collector.get_current_metrics()
print(metrics.to_dict())
```

### 5. AM Briefing Generation

Generates morning intelligence briefings from ingested data:

```python
from app.ingestion import AMBriefingGenerator

generator = AMBriefingGenerator()

briefing = generator.generate(
    metrics=metrics.to_dict(),
    tier_1_items=high_value_items,
    format="markdown"
)

# Save to file
generator.save_briefing(briefing, "/tmp/am_briefing.md")
```

## Deployment

### Local Development

```bash
# Run API server
python -m app.main

# Run ingestion manually
python scripts/run_ingestion.py

# Or with Docker Compose
docker-compose up api
docker-compose run --rm ingestion
```

### GKE Deployment

```bash
# Create namespace
kubectl create namespace pnkln-core

# Deploy configuration
kubectl apply -f k8s/cronjob.yaml

# Check job status
kubectl get cronjobs -n pnkln-core
kubectl get jobs -n pnkln-core

# View logs
kubectl logs -n pnkln-core -l app=pnkln,component=ingestion --tail=100
```

### Configuration

Edit `k8s/cronjob.yaml` ConfigMap:

```yaml
data:
  project_id: "your-gcp-project"
  region: "us-central1"
  bucket: "pnkln-your-project-us-central1"
```

## API Endpoints

### Crawling

**POST /api/v1/ingestion/crawl**
```json
{
  "url": "https://example.com",
  "respect_robots_txt": true,
  "rate_limit_delay": 1.0
}
```

### Classification

**POST /api/v1/ingestion/classify**
```json
{
  "content": "Legal document text...",
  "source_name": "Reuters",
  "source_type": "news",
  "source_tier": 2
}
```

Response:
```json
{
  "tier": 1,
  "confidence": 0.85,
  "reasoning": "High-value legal intelligence from authoritative source",
  "relevance_score": 0.9,
  "timeliness_score": 0.85,
  "completeness_score": 0.8
}
```

### Sources

**GET /api/v1/ingestion/sources**

Returns coverage statistics and source inventory.

**GET /api/v1/ingestion/sources/tier/{tier}**

Get sources by tier (1, 2, or 3).

### Metrics

**GET /api/v1/ingestion/metrics/current**

Current run metrics.

**GET /api/v1/ingestion/metrics/history?days=7**

Historical metrics (last N days).

**GET /api/v1/ingestion/metrics/summary**

Summary statistics and trends.

### Briefing

**POST /api/v1/ingestion/briefing/generate**
```json
{
  "metrics": {...},
  "tier_1_items": [...]
}
```

Returns formatted AM briefing.

## Performance Targets

| Metric | Target | Quality Gate |
|--------|--------|--------------|
| Runtime | ≤45 min | Hard limit |
| Monthly Cost | ~$77 | Budget cap |
| Tier 1 % | ≥20% | Quality threshold |
| Relevance Score | ≥0.6 | Minimum quality |
| Timeliness Score | ≥0.5 | Freshness check |
| Completeness | ≥0.6 | Information sufficiency |
| Ethics Compliance | ≥95% | robots.txt adherence |

## Integration with PNKLN Stack

The ingestion layer feeds into 4 namespaces:

1. **pnkln-rag** - RAG indexes for semantic search
2. **pnkln-analysis** - Legal document analysis
3. **pnkln-briefing** - AM briefing delivery
4. **pnkln-storage** - Long-term archival

Data flow:
```
Ingestion → Classification → Storage → [RAG, Analysis, Briefing]
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/api/v1/ingestion/health

# CronJob status
kubectl get cronjobs -n pnkln-core
kubectl describe cronjob pnkln-ingestion -n pnkln-core
```

### Logs

```bash
# Recent ingestion run
kubectl logs -n pnkln-core -l component=ingestion --tail=500

# Specific job
kubectl logs -n pnkln-core job/pnkln-ingestion-28391200
```

### Metrics Dashboard

View in Cloud Console or export to monitoring:
- Items/day trend
- Cost tracking
- Tier distribution
- Quality scores
- Compliance rate

## Troubleshooting

### Common Issues

**Timeout (>45 min)**:
- Check source count
- Review rate limiting delays
- Optimize classification batch size

**High Cost (>$77/month)**:
- Review API call patterns
- Check Gemini usage
- Audit per-item costs

**Low Tier 1 % (<20%)**:
- Review source quality
- Adjust classification prompts
- Add more Tier 1 sources

**robots.txt Blocks**:
- Review crawler configuration
- Check source robots.txt files
- Adjust crawl targets

## Best Practices

1. **Add Sources Gradually**: Start with a few high-quality sources, expand over time
2. **Monitor Costs**: Track per-item costs daily to stay within budget
3. **Review Classifications**: Audit tier classifications to ensure accuracy
4. **Respect Rate Limits**: Never disable ethical compliance features
5. **Archive Data**: Use GCS lifecycle policies for cost-effective storage
6. **Test Locally**: Run `scripts/run_ingestion.py` before deploying

## Future Enhancements

- [ ] Real-time ingestion (supplement nightly batch)
- [ ] Machine learning for classification (reduce Gemini costs)
- [ ] Source quality auto-tuning
- [ ] Alerting for quality gate failures
- [ ] Multi-region failover
- [ ] Custom source plugins
