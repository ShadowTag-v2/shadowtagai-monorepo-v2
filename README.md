# Gemini Ingestion Layer - PNKLN Core Stack™

Intelligent data collection and classification pipeline for the PNKLN Core Stack™. This service operates as a GKE CronJob that gathers intelligence from multiple sources nightly, classifies items by tier, and makes data available for downstream processing.

## Overview

The Gemini Ingestion Layer is a foundational component that:
- Collects data from 6+ sources (YouTube, Twitter, News, RSS, Web, APIs)
- Classifies items into 3 tiers based on authority, relevance, and timeliness
- Ensures ethical crawling compliance (robots.txt, rate limiting)
- Delivers processed intelligence to Judge #6 and AM Briefing services
- Operates within a ~$77/month budget at ~45 minutes runtime per night

**Documentation**: [Ingestion Layer Architecture](./docs/architecture/gemini-ingestion-layer.md)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Gemini Ingestion Layer (GKE)                   │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌─────────────┐          │
│  │  YouTube   │  │  Twitter   │  │    News     │          │
│  │ Collector  │  │ Collector  │  │  Collector  │          │
│  └─────┬──────┘  └─────┬──────┘  └──────┬──────┘          │
│        │                │                 │                 │
│  ┌─────┴───────┬────────┴────────┬────────┴──────┐         │
│  │    RSS      │  Web Scraper    │ API Integrator│         │
│  │  Collector  │                 │               │         │
│  └─────┬───────┴────────┬────────┴────────┬──────┘         │
│        │                │                 │                 │
│        └────────────────┼─────────────────┘                 │
│                         │                                   │
│              ┌──────────▼──────────┐                        │
│              │ Tier Classification │                        │
│              │   (Tier 1/2/3)      │                        │
│              └──────────┬──────────┘                        │
│                         │                                   │
│              ┌──────────▼──────────┐                        │
│              │ Ethical Compliance  │                        │
│              │    Validation       │                        │
│              └──────────┬──────────┘                        │
│                         │                                   │
│              ┌──────────▼──────────┐                        │
│              │  Quality Scoring    │                        │
│              └──────────┬──────────┘                        │
│                         │                                   │
│              ┌──────────▼──────────┐                        │
│              │  Storage (GCS/DB)   │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-Source Collection**: YouTube, Twitter, News, RSS, Web scraping, API integrations
- **Intelligent Tier Classification**: ML-based classification (Tier 1/2/3)
- **Ethical Crawling**: 100% robots.txt compliance, adaptive rate limiting
- **Cost Efficient**: ~$77/month operational cost (~$0.012 per item)
- **FastAPI Integration**: REST API for triggering, querying, and monitoring
- **GKE Native**: Kubernetes CronJob with multi-container orchestration
- **Quality Gated**: Relevance, completeness, and timeliness checks

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Platform account
- GKE cluster
- PostgreSQL database
- Redis instance

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ehanc69/aiyou-fastapi-services.git
   cd aiyou-fastapi-services
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Deploy to GKE**:
   ```bash
   kubectl apply -f k8s/ingestion-cronjob.yaml
   ```

### Running Locally

**Start the FastAPI server**:
```bash
uvicorn src.api.ingestion:app --reload --host 0.0.0.0 --port 8000
```

**Access the API**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ingestion/trigger` | Manually trigger ingestion job |
| `GET` | `/ingestion/status` | Get job status (current or by ID) |
| `GET` | `/ingestion/items` | Query ingested items (with filters) |
| `GET` | `/ingestion/metrics` | Performance metrics |
| `GET` | `/ingestion/sources` | Get source configuration |
| `POST` | `/ingestion/sources` | Update source configuration |

### Example Usage

**Trigger manual ingestion**:
```bash
curl -X POST http://localhost:8000/ingestion/trigger \
  -H "Content-Type: application/json" \
  -d '{"reason": "Breaking news event", "override_schedule": true}'
```

**Query Tier 1 items**:
```bash
curl "http://localhost:8000/ingestion/items?tier=tier_1&limit=10"
```

**Get metrics**:
```bash
curl "http://localhost:8000/ingestion/metrics?days=7"
```

## Configuration

### Source Configuration

Edit `config/sources.yaml` to add/modify data sources:

```yaml
sources:
  - type: youtube
    enabled: true
    channels:
      - UCxxxxxxxx
    max_videos_per_channel: 50

  - type: twitter
    enabled: true
    keywords:
      - "AI"
      - "machine learning"
```

### Tier Classification

Edit `config/tier-classification.yaml` to adjust tier rules:

```yaml
tier_1:
  min_authority: 90
  max_age_hours: 6
  min_relevance: 80
  min_engagement: 1000
```

### Ethical Crawling

Edit `config/ethical-crawling.yaml` to configure compliance:

```yaml
rate_limiting:
  default_delay_seconds: 2
  adaptive: true

robots_txt:
  enabled: true
  respect_crawl_delay: true
```

## Performance Metrics

### Target SLAs

| Metric | Target |
|--------|--------|
| Runtime | ≤45 minutes |
| Daily Items | 1000-5000 |
| Active Sources | ≥6 |
| Cost/Item | ≤$0.015 |
| Relevance (Avg) | ≥60/100 |
| Tier 1 % | 10-20% |
| Uptime | ≥99% |

### Current Performance

See the [Gemini Ingestion Layer Analysis](docs/prompts/gemini-ingestion-layer-analysis.md) for detailed performance analysis.

## Tier Definitions

### Tier 1 (Priority Intelligence)
- High-authority sources (verified news, official channels)
- Time-critical (≤6 hours old)
- High relevance (≥80/100)
- Strong engagement (≥1000 signals)
- **Target**: 10-20% of total items

### Tier 2 (Standard Intelligence)
- Moderate-authority sources
- Standard timeliness (≤72 hours)
- Moderate relevance (≥50/100)
- Moderate engagement (100-1000)
- **Target**: 30-40% of total items

### Tier 3 (Background Intelligence)
- Lower-authority sources
- Older content (>72 hours)
- Tangential relevance (<50/100)
- Low engagement (<100)
- **Target**: 40-60% of total items

## Ethical Guidelines

We adhere to strict ethical standards:

- ✅ **100% robots.txt compliance**: Never violate crawler policies
- ✅ **Adaptive rate limiting**: Prevent server overload
- ✅ **Transparent identification**: Clear User-Agent with contact info
- ✅ **No paywall circumvention**: Respect premium content
- ✅ **PII scrubbing**: Remove personal information
- ✅ **GDPR compliant**: Right to erasure, data retention limits

See [Ethical Crawling Guidelines](docs/architecture/ethical-crawling.md) for details.

## Development

### Project Structure

```
aiyou-fastapi-services/
├── docs/
│   ├── architecture/          # Architecture documentation
│   │   ├── gemini-ingestion-layer.md
│   │   ├── ethical-crawling.md
│   │   └── tier-classification.md
│   └── prompts/               # Analysis prompts
│       └── gemini-ingestion-layer-analysis.md
├── src/
│   ├── api/                   # FastAPI endpoints
│   │   └── ingestion.py
│   ├── collectors/            # Source-specific collectors
│   ├── processors/            # Tier classification, quality scoring
│   └── utils/                 # Shared utilities
├── config/                    # Configuration files
│   ├── ethical-crawling.yaml
│   ├── tier-classification.yaml
│   ├── sources.yaml
│   └── quality-gates.yaml
├── k8s/                       # Kubernetes manifests
│   └── ingestion-cronjob.yaml
├── models/                    # ML models
├── data/                      # Data files
├── schemas/                   # JSON schemas
├── requirements.txt           # Python dependencies
├── package.json               # Node.js dependencies
└── README.md
```

### Running Tests

```bash
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint
flake8 src/
mypy src/
```

## Deployment

### GKE Deployment

1. **Create namespace**:
   ```bash
   kubectl create namespace pnkln-ingestion
   ```

2. **Configure secrets**:
   ```bash
   kubectl create secret generic ingestion-secrets \
     --from-literal=youtube_api_key=YOUR_KEY \
     --from-literal=twitter_bearer_token=YOUR_TOKEN \
     --namespace pnkln-ingestion
   ```

3. **Deploy CronJob**:
   ```bash
   kubectl apply -f k8s/ingestion-cronjob.yaml
   ```

4. **Monitor**:
   ```bash
   kubectl get cronjobs -n pnkln-ingestion
   kubectl logs -f job/gemini-ingestion-layer-XXXXX -n pnkln-ingestion
   ```

## Monitoring & Alerting

### Prometheus Metrics

- `ingestion_items_total{tier}`: Total items by tier
- `ingestion_runtime_seconds`: Job runtime
- `ingestion_cost_usd`: Operational cost
- `ingestion_relevance_score`: Average relevance
- `ingestion_errors_total{source}`: Errors by source

### Grafana Dashboards

Import dashboards from `dashboards/` directory:
- Tier Distribution Over Time
- Source Performance
- Cost Tracking
- Quality Metrics

## Migration from Claude Code SDK

This project has been migrated from `@anthropic-ai/claude-code` to `@anthropic-ai/claude-agent-sdk`. See [MIGRATION.md](MIGRATION.md) for details.

## Documentation

- [Architecture Overview](docs/architecture/gemini-ingestion-layer.md)
- [Ethical Crawling Guidelines](docs/architecture/ethical-crawling.md)
- [Tier Classification Model](docs/architecture/tier-classification.md)
- [Analysis Prompt](docs/prompts/gemini-ingestion-layer-analysis.md)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: https://github.com/ehanc69/aiyou-fastapi-services/issues
- **Email**: contact@pnkln.ai
- **Docs**: https://pnkln.ai/docs

## Acknowledgments

- Part of the PNKLN Core Stack™
- Powered by Gemini 2.0 Pro
- Built with FastAPI, GKE, and Claude Agent SDK

---

**Status**: ✅ Production Ready (v1.0.0)
**Last Updated**: 2025-11-07
||||||| empty tree
