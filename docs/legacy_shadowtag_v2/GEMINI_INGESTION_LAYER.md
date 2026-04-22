# Gemini Ingestion Layer - Intelligence Collection Pipeline

**Architecture**: GKE CronJob Multi-Container
**Runtime Target**: ~45 minutes/night
**Operational Cost**: ~$77/month
**Role**: Pre-processing intelligence collection for pnkln Core Stack

---

## Overview

The Gemini Ingestion Layer is a nightly batch processing pipeline that collects, classifies, and delivers intelligence data from multiple sources. It runs as a Kubernetes CronJob with 8 specialized containers working in parallel to achieve comprehensive, ethical data collection.

### Position in pnkln Core Stack

```
┌─────────────────────────────────────────────────────────────┐
│                  pnkln CORE STACK™                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
    ┌───────────────────────────────────────────────────┐
    │   GEMINI INGESTION LAYER (Nightly 2 AM UTC)      │
    │   • YouTube, Twitter, News, Reddit, Web Crawl     │
    │   • Gemini 2.0 Classification & Tier Assignment   │
    │   • AM Briefing Generation                        │
    └───────────────────┬───────────────────────────────┘
                        ↓
    ┌───────────────────────────────────────────────────┐
    │   DATA DELIVERY (Called BY services)              │
    ├───────────────────┬───────────────────────────────┤
    │ pnkln-stackjr-governance│ Judge 6 Hybrid Enforcement   │
    │ autogen-orchestr. │ Multi-Agent Coordination      │
    │ cognitive-stack-v5│ LLM Routing Layer             │
    │ shadowtag-v2      │ Watermarking Security         │
    └───────────────────────────────────────────────────┘
```

### Design Philosophy

**Compared to Judge 6** (reactive validation):

- **Proactive vs Reactive**: Collects data upstream vs validates downstream
- **Batch vs Real-time**: Nightly cron (45 min) vs sub-90ms response
- **Caller vs Callee**: Called BY services vs calls services
- **Ethics-first**: Respects robots.txt, rate limits, transparency

---

## Architecture

### Multi-Container Pod Design

```
┌─────────────────────────────────────────────────────────────┐
│                    CronJob Pod (2 AM Daily)                 │
├─────────────────────────────────────────────────────────────┤
│ Init Container: Config Validator                            │
├───────────────────┬─────────────────────────────────────────┤
│ Container 1       │ YouTube Collector (API)                 │
│ Container 2       │ Twitter/X Collector (API)               │
│ Container 3       │ News Aggregator (API + Crawl)           │
│ Container 4       │ Reddit Collector (API)                  │
│ Container 5       │ Web Crawler (RSS + Generic)             │
│ Container 6       │ Gemini Classifier (Tier Assignment)     │
│ Container 7       │ Quality Gate Enforcer                   │
│ Container 8       │ AM Briefing Generator                   │
└───────────────────┴─────────────────────────────────────────┘
                            ↓
                   Shared Output Volume
                            ↓
                   Persistent Briefings PVC
```

### Data Flow

```
1. COLLECTION (Parallel)
   ├── YouTube API → raw_youtube.json
   ├── Twitter API → raw_twitter.json
   ├── News API + Crawl → raw_news.json
   ├── Reddit API → raw_reddit.json
   └── Web Crawler → raw_web.json

2. CLASSIFICATION (Sequential)
   └── Gemini 2.0 Flash → classified_items.json
       ├── Tier 1 (High-value, verified)
       ├── Tier 2 (Secondary sources)
       └── Tier 3 (Supplementary)

3. QUALITY GATES (Validation)
   └── Quality Gate Enforcer
       ├── Items/day ≥ 500 ✓
       ├── Source diversity ≥ 5 ✓
       ├── Cost/item ≤ $0.15 ✓
       └── Quality score ≥ 0.70 ✓

4. DELIVERY (Output)
   └── AM Briefing Generator
       ├── Markdown summary
       ├── Tier distribution charts
       └── POST to /v1/briefing endpoint
```

---

## Configuration

### Quality Gates

| Metric               | Threshold | Purpose                    |
| -------------------- | --------- | -------------------------- |
| **Items/Day**        | ≥500      | Ensure sufficient volume   |
| **Source Diversity** | ≥5        | Prevent single-source bias |
| **Cost/Item**        | ≤$0.15    | Budget control             |
| **Quality Score**    | ≥0.70     | Maintain relevance         |
| **Runtime**          | ≤45 min   | Efficiency target          |

### Ethical Compliance Model

```yaml
compliance:
  robots_txt:
    respect: true
    cache_ttl_hours: 24
    fallback: "allow" # If robots.txt unavailable

  rate_limiting:
    requests_per_minute: 60
    crawl_delay_seconds: 1
    max_concurrent: 10
    backoff_strategy: exponential

  transparency:
    user_agent: "pnkln-Ingestion-Bot/1.0 (+https://pnkln.ai/bot)"
    contact_email: "bot@pnkln.ai"
    respect_http_429: true
    respect_http_503: true
```

### Multi-Source Coverage

**Tier 1** (Primary, High-Value):

- YouTube API (quota: 10,000 units/day)
- News Aggregator (quota: 5,000 requests/day)

**Tier 2** (Secondary):

- Twitter/X API (quota: 3,000 tweets/day)
- Reddit API (quota: 2,000 posts/day)

**Tier 3** (Supplementary):

- RSS Feeds (quota: 1,000 feeds/day)
- Generic Web Crawler (quota: 500 pages/day)

### Tier Classification Criteria

```yaml
Tier 1 (Weight: 1.0):
  - Verified source: Yes
  - Recency: ≤24 hours
  - Engagement score: ≥8/10
  - Relevance score: ≥0.8

Tier 2 (Weight: 0.6):
  - Verified source: No
  - Recency: ≤48 hours
  - Engagement score: ≥5/10
  - Relevance score: ≥0.6

Tier 3 (Weight: 0.3):
  - Recency: ≤1 week
  - Engagement score: ≥2/10
  - Relevance score: ≥0.4
```

---

## Deployment

### Prerequisites

1. **API Keys Required**:

   ```bash
   kubectl create secret generic api-credentials \
     --from-literal=YOUTUBE_API_KEY='your-key' \
     --from-literal=TWITTER_BEARER_TOKEN='your-token' \
     --from-literal=REDDIT_CLIENT_ID='your-id' \
     --from-literal=REDDIT_CLIENT_SECRET='your-secret' \
     --from-literal=NEWS_API_KEY='your-key' \
     --from-literal=GEMINI_API_KEY='your-key' \
     -n gemini-ingestion
   ```

2. **Terraform Service Account**:

   ```bash
   cd terraform
   terraform apply  # Creates gemini-ingestion-workload-sa
   ```

3. **Deploy CronJob**:
   ```bash
   kubectl apply -f k8s/base/gemini-ingestion-layer.yaml
   ```

### Schedule Configuration

Default: 2 AM UTC daily (`0 2 * * *`)

To change timezone (e.g., 2 AM PST = 10 AM UTC):

```yaml
spec:
  schedule: "0 10 * * *" # 2 AM PST
```

### Manual Execution (Testing)

```bash
# Create a one-time job from the CronJob
kubectl create job --from=cronjob/gemini-ingestion-nightly \
  ingestion-test-$(date +%s) \
  -n gemini-ingestion

# Watch progress
kubectl logs -f job/ingestion-test-xxxxx -n gemini-ingestion --all-containers
```

---

## Monitoring & Observability

### Key Metrics

**Collection Metrics**:

- `ingestion_items_collected_total` - Total items ingested
- `ingestion_active_sources_count` - Number of active sources
- `ingestion_source_quota_remaining` - Remaining quota per source

**Quality Metrics**:

- `ingestion_item_quality_score` - Gemini-assigned quality scores
- `ingestion_tier_distribution` - Count per tier (1/2/3)
- `ingestion_relevance_score_avg` - Average relevance

**Cost Metrics**:

- `ingestion_cost_per_item_usd` - Cost efficiency
- `ingestion_api_calls_total` - API usage
- `ingestion_monthly_cost_estimate` - Projected monthly cost

**Performance Metrics**:

- `ingestion_runtime_minutes` - Total execution time
- `ingestion_container_duration_seconds` - Per-container timing
- `ingestion_parallelism_factor` - Effective parallelization

**Compliance Metrics**:

- `ingestion_robots_txt_violations_total` - Ethical violations
- `ingestion_rate_limit_hits_total` - 429 responses
- `ingestion_user_agent_blocks_total` - 403 responses

### Alerts

Configured in `PrometheusRule`:

| Alert                      | Condition     | Severity |
| -------------------------- | ------------- | -------- |
| LowDailyItemCount          | <500 items    | Warning  |
| LowSourceDiversity         | <5 sources    | Warning  |
| HighCostPerItem            | >$0.15        | Critical |
| LowQualityScore            | <0.70 avg     | Warning  |
| RuntimeExceeded            | >45 min       | Warning  |
| EthicalComplianceViolation | >0 violations | Critical |

### Dashboards

Access Grafana dashboard:

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Navigate to: Gemini Ingestion Layer - Nightly Intelligence
```

Key panels:

- Daily item count trend
- Source diversity pie chart
- Cost per item over time
- Quality score distribution
- Tier classification breakdown
- Runtime performance
- Ethical compliance scorecard

---

## Integration with Other Namespaces

### Called BY Services (Pull Model)

Services in the 4 namespaces can fetch ingested data:

**pnkln-stackjr-governance** (Judge 6):

```python
# Fetch daily intelligence for validation
import requests
response = requests.get(
    "http://ingestion-metrics.gemini-ingestion:9090/api/v1/query",
    params={"query": "ingestion_items_collected_total"}
)
```

**autogen-orchestration**:

```python
# Get tier 1 items for agent context
items = fetch_briefing(tier=1, max_items=50)
```

**cognitive-stack-v5** (LLM Routing):

```python
# Receive AM briefing delivery
@app.post("/v1/briefing")
def receive_briefing(briefing: BriefingPayload):
    # Process morning intelligence summary
    return {"status": "received"}
```

**shadowtag-v2**:

```python
# Access raw data for watermarking
raw_data = load_from_pvc("/briefings/2025-11-08/raw_items.json")
```

### RBAC Configuration

The `gemini-ingestion-sa` service account has:

- ✅ `get`, `list` on services across all namespaces
- ✅ `get`, `list` on pods (for health checks)
- ✅ `get`, `list` on configmaps (for dynamic config)

---

## Cost Analysis

### Monthly Breakdown (~$77)

| Component               | Cost | Notes                                |
| ----------------------- | ---- | ------------------------------------ |
| **GKE CronJob Runtime** | $15  | ~45 min/night × 30 days × $0.011/min |
| **YouTube API**         | $5   | Free tier (10K units/day)            |
| **Twitter API**         | $0   | Free tier (v2 API)                   |
| **Reddit API**          | $0   | Free tier                            |
| **News API**            | $0   | Free tier (500 req/day)              |
| **Gemini 2.0 Flash**    | $45  | ~500 items/day × $0.003/item         |
| **GCS Storage (PVC)**   | $2   | 50 GB × $0.04/GB                     |
| **Networking**          | $5   | Egress for API calls                 |
| **Monitoring**          | $5   | Prometheus metrics storage           |

**Total**: ~$77/month

### Cost Optimization Strategies

1. **Batch Gemini Calls**: Group items for classification (reduces API overhead)
2. **Smart Caching**: Cache robots.txt, RSS feeds (reduce redundant fetches)
3. **Quota Management**: Prioritize Tier 1 sources when near limits
4. **Compression**: Compress output JSON before storage
5. **Lifecycle Policies**: Delete briefings >90 days old

---

## Troubleshooting

### Common Issues

**1. CronJob Not Running**

```bash
# Check schedule
kubectl describe cronjob gemini-ingestion-nightly -n gemini-ingestion

# Check concurrency policy
kubectl get cronjob -n gemini-ingestion -o yaml | grep concurrencyPolicy

# Manually trigger
kubectl create job --from=cronjob/gemini-ingestion-nightly test-$(date +%s) -n gemini-ingestion
```

**2. Container Failures**

```bash
# Check pod status
kubectl get pods -n gemini-ingestion

# View logs for failed container
kubectl logs <pod-name> -n gemini-ingestion -c <container-name>

# Common issues:
# - Missing API keys → Check secret
# - Rate limit exceeded → Check quota config
# - robots.txt block → Review compliance settings
```

**3. Quality Gate Failures**

```bash
# View quality gate logs
kubectl logs -n gemini-ingestion -l app=gemini-ingestion -c quality-gate

# Check metrics
curl http://ingestion-metrics.gemini-ingestion:9090/metrics | grep quality_score

# Common causes:
# - Low item count → Check source quotas
# - Low quality score → Review classification criteria
# - High cost → Optimize Gemini usage
```

**4. Ethical Compliance Violations**

```bash
# Check robots.txt violations
kubectl logs -n gemini-ingestion -l app=gemini-ingestion | grep "robots.txt"

# Review cached directives
kubectl get cm robots-txt-config -n gemini-ingestion -o yaml

# Fix:
# - Update cache manually
# - Adjust crawl delay
# - Blacklist violating domains
```

---

## Performance Tuning

### Runtime Optimization

**Target**: ≤45 minutes

**Current Breakdown**:

- Collection (parallel): ~15 min
- Classification (sequential): ~20 min
- Quality gates: ~5 min
- Briefing generation: ~5 min

**Optimization Levers**:

1. **Increase Parallelism**:

   ```yaml
   resources:
     requests:
       cpu: "2" # Double CPU for faster processing
   ```

2. **Reduce Classification Latency**:

   ```yaml
   env:
     - name: GEMINI_BATCH_SIZE
       value: "50" # Classify 50 items per API call
   ```

3. **Smart Sampling**:

   ```yaml
   # Only classify Tier 1 candidates with Gemini
   # Use rule-based classification for Tier 2/3
   ```

4. **Caching**:
   ```yaml
   # Cache Gemini classifications for duplicate items
   # Cache-TTL: 7 days
   ```

### Source-Specific Tuning

**YouTube** (Slowest - 10 min):

- Use playlist API instead of individual videos
- Batch metadata requests
- Cache channel info

**Twitter/X** (Fast - 2 min):

- Use streaming API for real-time ingestion
- Combine with batch processing

**News** (Variable - 5-10 min):

- Parallelize across news sources
- Implement connection pooling
- Use async HTTP requests

---

## Security Considerations

### API Key Management

- ✅ Stored in Kubernetes Secrets (not ConfigMaps)
- ✅ Workload Identity for GCP services (no keys)
- ✅ Rotation policy: 90 days
- ✅ Least-privilege IAM roles

### Network Security

- ✅ Egress-only (no ingress to CronJob)
- ✅ Network policies restrict inter-namespace traffic
- ✅ TLS for all API calls
- ✅ User-Agent transparency

### Data Security

- ✅ PVC encrypted at rest (GKE default)
- ✅ Briefings contain no PII
- ✅ Raw data deleted after 7 days
- ✅ Audit logs for all API access

---

## Future Enhancements

### Short-term (Q1 2026)

1. **Real-time Augmentation**: Add streaming ingestion for breaking news
2. **Multi-language Support**: Translate non-English sources
3. **Deduplication**: Implement semantic dedup for similar items
4. **Source Scoring**: Dynamic prioritization based on historical quality

### Medium-term (Q2-Q3 2026)

5. **AutoML Tuning**: Fine-tune Gemini on domain-specific data
6. **Graph Analysis**: Build knowledge graphs from ingested data
7. **Anomaly Detection**: Flag unusual patterns in data streams
8. **Multi-region Ingestion**: Geo-distributed crawlers

### Long-term (Q4 2026+)

9. **Agentic Ingestion**: Use AutoGen to dynamically discover new sources
10. **Self-healing**: Auto-recovery from source failures
11. **Cost Prediction**: ML-based quota forecasting
12. **Federated Learning**: Privacy-preserving model training

---

## References

- **Architecture Analysis**: See `/GKE_ARCHITECTURE_ANALYSIS.md`
- **Deployment Guide**: See `/README.md`
- **Kubernetes Manifests**: See `/k8s/base/gemini-ingestion-layer.yaml`
- **Terraform Config**: See `/terraform/main.tf` (lines for service account)

---

**Status**: ✅ Production-ready
**Version**: 1.0.0
**Last Updated**: 2025-11-08
**Maintainer**: pnkln Core Stack Team
