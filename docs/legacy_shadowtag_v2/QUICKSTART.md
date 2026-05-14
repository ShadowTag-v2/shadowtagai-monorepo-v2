# pnkln Core Stack - Quick Start Guide

## Overview

The Gemini Ingestion Layer is pnkln's foundation for intelligence collection. It runs nightly to gather, classify, and deliver strategic information from multiple sources.

## Prerequisites

### Required
- Python 3.11+
- Docker (for containerization)
- Google Cloud SDK (for GKE deployment)
- API Keys:
  - Anthropic API key (Claude/Gemini)
  - YouTube Data API v3 key
  - Twitter/X API bearer token

### Optional
- Kubernetes cluster (GKE recommended)
- PostgreSQL database
- Redis cache

## Local Setup

### 1. Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd pnkln-stack-fastapi-services

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

Required configuration:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
YOUTUBE_API_KEY=your_youtube_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

### 3. Test Configuration

```bash
# Dry-run to validate credentials
python -m ingestion.main --dry-run
```

Expected output:
```json
{"event": "dry_run_success_all_keys_present", "timestamp": "..."}
```

### 4. Run Ingestion Pipeline

```bash
# Run with default settings (last 24 hours)
python -m ingestion.main

# Run with custom queries
python -m ingestion.main --queries "AI,machine learning,autonomous vehicles"

# Run with custom time range
python -m ingestion.main --since "2025-11-14T00:00:00Z"
```

### 5. Review Results

The pipeline will:
1. Fetch items from YouTube, Twitter, and News sources
2. Classify each item into Tier 1/2/3 using Gemini
3. Apply quality gates (relevance, timeliness, completeness)
4. Generate and display AM briefing
5. Output execution summary with metrics

Example output:
```json
{
  "status": "completed",
  "runtime_minutes": 12.3,
  "items_fetched": 1543,
  "items_accepted": 892,
  "pass_rate_pct": 57.8,
  "tier_distribution": {
    "tier_1": {"count": 178, "percentage": 20.0},
    "tier_2": {"count": 446, "percentage": 50.0},
    "tier_3": {"count": 268, "percentage": 30.0}
  },
  "costs": {
    "total_usd": 12.45,
    "budget_remaining_usd": 64.55
  }
}
```

## Docker Deployment

### Build Container

```bash
# Build Docker image
docker build -f infrastructure/docker/Dockerfile -t pnkln-ingestion .

# Test locally
docker run --rm \
  -e ANTHROPIC_API_KEY="your_key" \
  -e YOUTUBE_API_KEY="your_key" \
  -e TWITTER_BEARER_TOKEN="your_token" \
  pnkln-ingestion
```

## GKE Deployment

### Prerequisites

```bash
# Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create GKE cluster (if not exists)
gcloud container clusters create pnkln-cluster \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5
```

### Create Secrets

```bash
# Create Kubernetes secret with API keys
kubectl create secret generic pnkln-ingestion-secrets \
  --from-literal=ANTHROPIC_API_KEY="your_key" \
  --from-literal=YOUTUBE_API_KEY="your_key" \
  --from-literal=TWITTER_BEARER_TOKEN="your_token" \
  -n pnkln-core
```

### Deploy

```bash
# Build and deploy (automated)
./infrastructure/build.sh

# Or step-by-step:
# 1. Build image
./infrastructure/build.sh --build-only

# 2. Deploy to GKE
./infrastructure/build.sh --deploy-only
```

### Verify Deployment

```bash
# Check CronJob status
kubectl get cronjob -n pnkln-core

# View upcoming schedule
kubectl get cronjob pnkln-ingestion -n pnkln-core -o yaml | grep schedule

# Trigger manual run
kubectl create job --from=cronjob/pnkln-ingestion pnkln-ingestion-manual -n pnkln-core

# View logs
kubectl logs -l app=pnkln-ingestion -n pnkln-core --tail=100 -f
```

## Configuration Reference

### Ingestion Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `INGESTION_MAX_ITEMS_PER_RUN` | 10000 | Maximum items to fetch per run |
| `INGESTION_RUNTIME_LIMIT_MINUTES` | 45 | Max runtime before timeout |
| `INGESTION_COST_BUDGET_USD` | 77.0 | Monthly cost budget |

### Tier Classification Thresholds

| Variable | Default | Description |
|----------|---------|-------------|
| `TIER_1_SCORE_THRESHOLD` | 0.80 | Minimum score for Tier 1 |
| `TIER_2_SCORE_THRESHOLD` | 0.50 | Minimum score for Tier 2 |
| `RELEVANCE_MIN_SCORE` | 0.70 | Minimum relevance to pass quality gate |

### Ethical Crawling

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWLER_MAX_RATE_PER_DOMAIN` | 1.0 | Max requests/second per domain |
| `CRAWLER_RESPECT_ROBOTS_TXT` | true | Honor robots.txt directives |
| `CRAWLER_USER_AGENT` | pnkln-Ingestion/1.0 | User-Agent string |

## Monitoring

### Prometheus Metrics

The ingestion pipeline exposes metrics on port 9090:

- `ingestion_items_fetched_total{source}` - Total items fetched by source
- `ingestion_items_classified_total{tier}` - Total items by tier
- `ingestion_pipeline_duration_seconds` - Pipeline execution time
- `ingestion_pipeline_cost_usd` - Estimated cost of last run

### Viewing Metrics

```bash
# Port-forward to access Prometheus metrics
kubectl port-forward -n pnkln-core deployment/pnkln-ingestion 9090:9090

# View metrics
curl http://localhost:9090/metrics
```

### Logs

Structured JSON logs are written to stdout and captured by GKE Cloud Logging.

Example log query in Cloud Console:
```
resource.type="k8s_container"
resource.labels.namespace_name="pnkln-core"
resource.labels.container_name="ingestion"
```

## Troubleshooting

### Issue: "No items fetched"

**Cause**: API keys invalid or rate limits exceeded

**Solution**:
```bash
# Validate credentials
python -m ingestion.main --dry-run

# Check rate limits (YouTube quota, Twitter rate limits)
# Wait and retry
```

### Issue: "Cost budget exceeded"

**Cause**: Too many items fetched or classified

**Solution**:
```bash
# Reduce max items
export INGESTION_MAX_ITEMS_PER_RUN=5000

# Or disable expensive sources temporarily
export ENABLE_YOUTUBE_SOURCE=false
```

### Issue: "Runtime limit exceeded"

**Cause**: Pipeline running too slowly

**Solution**:
```bash
# Increase timeout
export INGESTION_RUNTIME_LIMIT_MINUTES=60

# Or reduce max items
export INGESTION_MAX_ITEMS_PER_RUN=7500
```

### Issue: "robots.txt blocking requests"

**Cause**: Crawler respecting site's robots.txt

**Solution**:
```bash
# This is expected behavior for ethical crawling
# Either:
# 1. Respect the block (recommended)
# 2. Temporarily disable (NOT recommended):
export CRAWLER_RESPECT_ROBOTS_TXT=false
```

## Next Steps

- [Architecture Documentation](../README.md)
- [API Reference](API.md)
- [Integration with Judge #6](INTEGRATION.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

## Support

- GitHub Issues: [Report bugs or request features]
- Documentation: `/docs`
- Runbooks: `/docs/runbooks`
