# Gemini Ingestion Layer - Technical Specifications

## Executive Summary

The Gemini Ingestion Layer is the upstream, preventive component of the PNKLN Core Stack™, responsible for ethical, multi-source intelligence collection. Operating as a GKE CronJob with nightly batch processing, it focuses on volume, diversity, and cost efficiency while maintaining high ethical standards for web crawling and data collection.

**Status**: Pre-production analysis phase
**Architecture**: GKE CronJob with multi-container deployment
**Runtime**: ~45 minutes per nightly execution
**Monthly Cost**: ~$77 (operational)
**Analysis Tool**: Gemini 2.0 Pro

---

## System Architecture

### Deployment Model

```
┌─────────────────────────────────────────────────────┐
│           GKE CronJob - Nightly Execution           │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Collector   │  │  Classifier  │  │  Export   │ │
│  │  Container   │─>│  Container   │─>│ Container │ │
│  │              │  │              │  │           │ │
│  │ • API calls  │  │ • Tier       │  │ • Format  │ │
│  │ • Crawling   │  │   analysis   │  │ • Push to │ │
│  │ • ETL        │  │ • Scoring    │  │   services│ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│                                                      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  Services in 4 Namespaces    │
         │  (downstream consumers)      │
         └──────────────────────────────┘
```

### Container Breakdown

#### 1. Collector Container

**Responsibilities**:

- Execute API calls to data sources
- Perform ethical web crawling
- Extract and normalize raw data
- Apply rate limiting per source

**Technologies**:

- Python 3.11+ with aiohttp for async operations
- BeautifulSoup4 for HTML parsing
- Source-specific API clients (YouTube Data API, Twitter API v2, News API)

**Configuration**:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### 2. Classifier Container

**Responsibilities**:

- Analyze collected items for relevance
- Assign tier classification (Tier 1/2/3)
- Calculate quality scores
- Tag and categorize content

**Technologies**:

- Gemini 2.0 Pro API for content analysis
- Custom scoring algorithms
- Metadata enrichment

**Configuration**:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

#### 3. Export Container

**Responsibilities**:

- Format classified data for downstream services
- Push to service endpoints across namespaces
- Generate ingestion reports
- Update metrics

**Technologies**:

- FastAPI for internal APIs
- gRPC for service communication
- JSON/Protobuf serialization

**Configuration**:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

---

## Data Sources & Coverage

### Multi-Source Collection Strategy

| Source               | Purpose                             | API/Method                 | Daily Target  | Cost/1K Items |
| -------------------- | ----------------------------------- | -------------------------- | ------------- | ------------- |
| **YouTube**          | Video intelligence, trending topics | YouTube Data API v3        | 200-300 items | $0.05         |
| **Twitter**          | Real-time discussions, sentiment    | Twitter API v2 (Essential) | 300-500 items | $0.10         |
| **News Feeds**       | Authoritative reporting             | News API + RSS             | 400-600 items | $0.02         |
| **Web Crawling**     | Long-form content, analysis         | Custom crawler (ethical)   | 100-200 items | $0.01         |
| **Reddit** (planned) | Community discussions               | Reddit API                 | 200-300 items | $0.03         |

**Total Daily Target**: 1,000-1,600 items
**Source Diversity Index**: 4 active sources (target: ≥5 with Reddit)

### Source Configuration

Each source has dedicated configuration:

```python
# Example: YouTube source config
YOUTUBE_CONFIG = {
    "api_key": "{{GCP_SECRET}}",
    "quota_limit": 10000,  # Daily quota units
    "rate_limit": {
        "requests_per_second": 5,
        "burst": 10
    },
    "search_queries": [
        "cybersecurity threats",
        "geopolitical analysis",
        "technology trends",
        # ... customizable query set
    ],
    "max_results_per_query": 50,
    "filters": {
        "duration": "long",  # >20 minutes
        "upload_date": "today",
        "video_definition": "high"
    }
}
```

---

## Ethical Crawling Model

### Core Principles

1. **robots.txt Compliance**
   - Parse and respect robots.txt for all crawled domains
   - Honor Crawl-delay directives
   - Respect Disallow rules for specific paths

2. **Rate Limiting**
   - Maximum 1 request per second per domain (default)
   - Configurable per-domain limits
   - Exponential backoff on 429/503 responses
   - Respect Retry-After headers

3. **Transparency**
   - Custom User-Agent identifying the crawler
   - Contact email in User-Agent for site owners
   - Publicly documented crawling policies
   - Opt-out mechanism for site owners

4. **Attribution & Licensing**
   - Preserve source attribution metadata
   - Respect copyright notices
   - Track license requirements (CC, proprietary, etc.)
   - Only crawl publicly accessible content

### Implementation

```python
# Example: Ethical crawler implementation
class EthicalCrawler:
    USER_AGENT = "PNKLN-Bot/1.0 (+https://example.com/bot; contact@example.com)"

    async def crawl_url(self, url: str) -> Optional[dict]:
        # 1. Check robots.txt
        if not await self.is_allowed_by_robots(url):
            logger.info(f"Skipping {url} - disallowed by robots.txt")
            return None

        # 2. Apply rate limiting
        await self.rate_limiter.wait_if_needed(domain=get_domain(url))

        # 3. Make request with transparent User-Agent
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"User-Agent": self.USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                # 4. Handle rate limit responses
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    await asyncio.sleep(retry_after)
                    return await self.crawl_url(url)  # Retry

                # 5. Extract content with attribution
                content = await response.text()
                return {
                    "content": content,
                    "source_url": url,
                    "attribution": self.extract_attribution(content),
                    "license": self.detect_license(content),
                    "crawled_at": datetime.utcnow().isoformat()
                }
```

### Compliance Monitoring

- **robots.txt Cache**: 24-hour TTL, auto-refresh
- **Rate Limit Violations**: Logged and alerted (target: 0 violations)
- **Opt-Out Requests**: Processed within 24 hours
- **Attribution Failures**: Flagged for manual review

---

## Tier Classification System

### Three-Tier Model

Intelligence items are classified into three tiers based on relevance, authority, timeliness, and completeness:

#### Tier 1: High-Value Intelligence

**Criteria**:

- Highly relevant to configured intelligence priorities
- From authoritative sources (verified accounts, reputable outlets)
- Timely (published within last 24 hours)
- Complete (sufficient context, no truncation)
- Original content (not aggregated/reposted)

**Target Distribution**: 20-30% of daily items
**Scoring Threshold**: ≥80/100

**Examples**:

- Breaking news from AP, Reuters on priority topics
- Expert analysis from verified domain experts
- Primary source documents
- High-engagement original research

#### Tier 2: Moderate-Value Intelligence

**Criteria**:

- Moderately relevant or tangential to priorities
- From semi-authoritative sources (established but not premium)
- Timely (within last 48 hours)
- Mostly complete with minor gaps
- May include some aggregated content

**Target Distribution**: 40-50% of daily items
**Scoring Threshold**: 50-79/100

**Examples**:

- Regional news coverage of priority topics
- Community discussions with substantive analysis
- Secondary source reporting with good sourcing
- Trend identification content

#### Tier 3: Low-Value Intelligence

**Criteria**:

- Tangentially relevant or background noise
- From non-authoritative sources (unverified, low credibility)
- Older content (>48 hours)
- Incomplete or poorly contextualized
- Aggregated or duplicate content

**Target Distribution**: 20-30% of daily items
**Scoring Threshold**: <50/100

**Examples**:

- Opinion pieces without expert backing
- Duplicate stories from multiple aggregators
- Low-engagement social media posts
- Outdated information

### Scoring Algorithm

```python
def calculate_tier_score(item: IntelligenceItem) -> int:
    """
    Calculate tier score (0-100) based on multiple factors.

    Returns:
        int: Score from 0-100, where higher = more valuable
    """
    score = 0

    # Relevance (0-30 points)
    score += calculate_relevance_score(
        item.content,
        item.keywords,
        PRIORITY_TOPICS
    )

    # Authority (0-25 points)
    score += calculate_authority_score(
        item.source,
        item.author,
        AUTHORITATIVE_SOURCES
    )

    # Timeliness (0-20 points)
    hours_old = (datetime.utcnow() - item.published_at).total_seconds() / 3600
    if hours_old < 24:
        score += 20
    elif hours_old < 48:
        score += 10
    elif hours_old < 72:
        score += 5

    # Completeness (0-15 points)
    score += calculate_completeness_score(
        item.content,
        item.metadata
    )

    # Originality (0-10 points)
    if not item.is_duplicate:
        score += 10

    return min(score, 100)

def assign_tier(score: int) -> str:
    """Assign tier based on score."""
    if score >= 80:
        return "TIER_1"
    elif score >= 50:
        return "TIER_2"
    else:
        return "TIER_3"
```

### Tier Distribution Monitoring

```
Target Distribution:
┌────────────────────────────────┐
│ Tier 1: 20-30% (200-480 items) │ ███████████
├────────────────────────────────┤
│ Tier 2: 40-50% (400-800 items) │ ██████████████████████
├────────────────────────────────┤
│ Tier 3: 20-30% (200-480 items) │ ███████████
└────────────────────────────────┘

Daily Quality Gate:
- Tier 1 must be ≥20% of total
- Tier 2 must be ≥40% of total
- Alert if Tier 3 exceeds 35%
```

---

## Key Performance Metrics

### Runtime Efficiency

**Target**: ~45 minutes per nightly execution
**Breakdown**:

- Collection phase: 20-25 minutes
- Classification phase: 15-18 minutes
- Export phase: 5-7 minutes

**Monitoring**:

```
Runtime Threshold Alerts:
- Warning: >50 minutes
- Critical: >60 minutes
- Auto-scaling trigger: >55 minutes (add resources)
```

**Optimization Strategies**:

- Parallel API calls with connection pooling
- Async I/O throughout pipeline
- Caching for repeated entities
- Incremental processing for large batches

### Daily Items Ingested

**Target**: 1,000-1,600 items/day
**Quality Gates**:

- Minimum: ≥800 items (system health check)
- Optimal: 1,000-1,600 items
- Maximum: ≤2,000 items (cost control)

**Breakdown by Source**:

```
Expected Daily Distribution:
YouTube:     200-300 items (15-20%)
Twitter:     300-500 items (25-35%)
News:        400-600 items (30-40%)
Web Crawl:   100-200 items (10-15%)
```

### Source Diversity

**Metric**: Number of unique sources contributing ≥1 item
**Target**: ≥5 distinct sources daily
**Current**: 4 sources (YouTube, Twitter, News, Web Crawl)
**Planned**: +1 (Reddit integration)

**Diversity Index Formula**:

```python
def calculate_diversity_index(items: List[IntelligenceItem]) -> float:
    """
    Calculate source diversity using Shannon entropy.
    Higher = more diverse distribution.
    """
    source_counts = Counter(item.source for item in items)
    total = len(items)

    entropy = 0
    for count in source_counts.values():
        p = count / total
        entropy -= p * math.log2(p)

    # Normalize to 0-10 scale
    max_entropy = math.log2(len(source_counts))
    return (entropy / max_entropy) * 10 if max_entropy > 0 else 0

# Target: Diversity Index ≥ 7.0
```

### Cost Efficiency

**Monthly Operational Cost**: ~$77
**Breakdown**:

- GKE compute: $45/month
- API costs (YouTube, Twitter, News): $25/month
- Network egress: $5/month
- Storage (temp): $2/month

**Cost per Item**:

- Target: ≤$0.05/item
- Current projection: $0.048/item (1,600 items/day \* 30 days = 48,000 items)

**Cost Monitoring**:

```python
# Daily cost tracking
daily_cost = (
    compute_cost_per_day +
    sum(api_costs_per_source.values()) +
    network_egress_cost +
    storage_cost
)

cost_per_item = daily_cost / items_ingested_today

if cost_per_item > 0.05:
    alert("Cost per item exceeded threshold", severity="WARNING")
```

### Quality Scores

**Metrics**:

1. **Relevance Score**: Average relevance across all items
   - Target: ≥70/100
   - Measured via keyword matching + Gemini analysis

2. **Timeliness Score**: Percentage of items <24 hours old
   - Target: ≥60%
   - Measured via publication timestamp

3. **Completeness Score**: Percentage of items with full metadata
   - Target: ≥85%
   - Measured via field presence checks

4. **Overall Quality Gate**: Combined score
   - Formula: `(Relevance * 0.4) + (Timeliness * 0.3) + (Completeness * 0.3)`
   - Target: ≥70/100

---

## Integration with PNKLN Stack

### Upstream Triggers

The Ingestion Layer is triggered by:

1. **CronJob Schedule**: Primary trigger at 02:00 UTC daily
2. **Manual Trigger**: Via kubectl command for ad-hoc runs
3. **Service Requests**: Services in 4 namespaces can request on-demand collection

### Downstream Handoffs

Classified data is pushed to services in the following namespaces:

```
┌──────────────────────────────────────────────┐
│  Gemini Ingestion Layer Output               │
└──────────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ NS 1   │  │ NS 2   │  │ NS 3   │  │ NS 4   │
│ Ingest │  │ Valid. │  │ Intel. │  │ Deliv. │
│ -Proc. │  │ -Enfor.│  │ -Analy.│  │ -Orch. │
└────────┘  └────────┘  └────────┘  └────────┘
```

**Data Format**: JSON over gRPC
**Schema**:

```protobuf
message IntelligenceItem {
  string id = 1;
  string source = 2;
  string tier = 3;  // TIER_1, TIER_2, TIER_3
  int32 score = 4;  // 0-100
  string content = 5;
  map<string, string> metadata = 6;
  google.protobuf.Timestamp collected_at = 7;
  google.protobuf.Timestamp published_at = 8;
}

message IngestionBatch {
  repeated IntelligenceItem items = 1;
  BatchMetadata metadata = 2;
}

message BatchMetadata {
  string batch_id = 1;
  int32 total_items = 2;
  map<string, int32> items_per_tier = 3;
  map<string, int32> items_per_source = 4;
  float diversity_index = 5;
  float average_score = 6;
}
```

### Service Interactions

**Called By**:

- `ingestion-processing` namespace: Requests specific source refreshes
- `intelligence-analysis` namespace: Triggers targeted collection for trending topics
- Manual operators: Ad-hoc collection via kubectl

**Calls**:

- `ingestion-processing` namespace: Pushes raw batches
- `validation-enforcement` namespace: Sends items for Judge 6 validation
- Monitoring services: Sends metrics and health checks

---

## Monitoring & Alerting

### Key Dashboards

1. **Ingestion Health Dashboard**
   - Runtime per execution (trend chart)
   - Items ingested per day (bar chart)
   - Cost per item (line chart)
   - Tier distribution (pie chart)

2. **Source Coverage Dashboard**
   - Items per source (stacked bar)
   - Source diversity index (gauge)
   - API quota usage (progress bars)
   - Crawler success rate (percentage)

3. **Quality Metrics Dashboard**
   - Relevance score distribution (histogram)
   - Timeliness heatmap (by hour)
   - Completeness score (line chart)
   - Tier score trends (multi-line)

### Alert Rules

| Condition            | Severity | Action                             |
| -------------------- | -------- | ---------------------------------- |
| Runtime >60 min      | Critical | Page on-call, auto-scale resources |
| Items <800/day       | Warning  | Notify team, check source health   |
| Cost/item >$0.07     | Warning  | Review cost optimization           |
| Tier 1 <15%          | Warning  | Tune classification thresholds     |
| Diversity <5 sources | Info     | Plan source expansion              |
| robots.txt violation | Critical | Halt crawler, manual review        |
| API quota >80%       | Warning  | Throttle requests, plan upgrade    |

### Health Checks

```python
async def health_check() -> HealthStatus:
    """Comprehensive health check for Ingestion Layer."""
    checks = {
        "cron_schedule": check_cron_active(),
        "api_connectivity": await check_all_api_sources(),
        "gke_resources": check_resource_availability(),
        "downstream_services": await check_service_endpoints(),
        "last_run_success": check_last_execution_status(),
    }

    all_healthy = all(checks.values())
    return HealthStatus(
        status="healthy" if all_healthy else "degraded",
        details=checks,
        timestamp=datetime.utcnow()
    )
```

---

## Pre-Production Analysis

### Analysis Approach

Using **Gemini 2.0 Pro** with a specialized analysis prompt to evaluate the Ingestion Layer based on:

- Architecture specifications (this document)
- GKE deployment manifests
- Source integration diagrams
- Cost model projections

**Confidence Target**: ≥60% (pre-production, no real telemetry)

### Analysis Dimensions

1. **Architecture & Design**
   - Multi-container orchestration
   - CronJob scheduling strategy
   - Resource allocation
   - Scalability considerations

2. **Ethical Compliance**
   - robots.txt adherence
   - Rate limiting implementation
   - Transparency mechanisms
   - Attribution tracking

3. **Multi-Source Coverage**
   - Source diversity
   - API integration quality
   - Crawler coverage
   - Expansion roadmap

4. **Tier Classification**
   - Scoring algorithm robustness
   - Distribution balance
   - Threshold calibration
   - Gemini integration

5. **Runtime Efficiency**
   - 45-minute target feasibility
   - Bottleneck identification
   - Optimization opportunities
   - Resource utilization

6. **Cost Model**
   - $77/month sustainability
   - Cost per item projections
   - Scaling cost implications
   - Optimization strategies

7. **Quality Gates**
   - Metric appropriateness
   - Threshold setting
   - Alert coverage
   - Integration with downstream

8. **AM Briefing Delivery**
   - Data format suitability
   - Handoff efficiency
   - Timeliness guarantees
   - User experience

### Expected Analysis Outputs

The Gemini analysis prompt will produce:

- **Strengths**: Well-designed components and patterns
- **Weaknesses**: Potential issues or gaps
- **Risks**: Pre-production concerns to monitor
- **Recommendations**: Optimizations and improvements
- **Confidence Score**: 0-100% for each dimension + overall

---

## Comparison with Judge 6

| Aspect                  | Gemini Ingestion Layer                | Judge 6                        |
| ----------------------- | ------------------------------------- | ------------------------------- |
| **Role**                | Proactive collector                   | Reactive validator              |
| **Position**            | Upstream/preventive                   | Downstream/reactive             |
| **Architecture**        | GKE CronJob, multi-container          | Hybrid Gemini+PyTorch           |
| **Execution**           | Batch (nightly ~45 min)               | Real-time (p99 ≤90ms)           |
| **Key Metrics**         | Items/day, sources, cost/item, scores | Latency, throughput, block rate |
| **Integration**         | Called by services in 4 namespaces    | Calls services in 4 namespaces  |
| **Unique Features**     | Ethical crawling, tier classification | Compliance Framework, JR validation         |
| **Cost Model**          | Monthly operational (~$77)            | API calls per validation        |
| **Quality Focus**       | Relevance, timeliness, completeness   | FP/FN rates, coverage           |
| **Coverage Target**     | Source diversity, volume              | 98% test coverage               |
| **Analysis Confidence** | ≥60% (specs-only, pre-prod)           | ≥70% (with prod data)           |

**Complementary Design**: Ingestion focuses on broad, ethical collection; Judge 6 ensures what's collected meets strict validation rules. Together they form a robust intelligence pipeline.

---

## Future Roadmap

### Phase 2 (Q2 2026)

- [ ] Reddit integration for community intelligence
- [ ] Real-time ingestion mode for breaking events
- [ ] Advanced ML tier classification (beyond Gemini)
- [ ] Multi-language support (Spanish, French, Chinese)

### Phase 3 (Q3 2026)

- [ ] Sentiment analysis integration
- [ ] Entity extraction and linking
- [ ] Auto-tuning for tier thresholds
- [ ] Expanded crawler targets (LinkedIn, specialized forums)

### Phase 4 (Q4 2026)

- [ ] Multi-region deployment for global coverage
- [ ] Predictive collection (anticipate intelligence needs)
- [ ] Advanced deduplication algorithms
- [ ] Integration with external threat intelligence feeds

---

## References & Resources

### Internal Documentation

- [PNKLN Core Stack Architecture](./PNKLN_CORE_STACK.md)
- [Judge 6 Specifications](./Claude_Code_6.md)
- [Gemini Ingestion Layer Analysis Prompt](../prompts/gemini_ingestion_analysis.md)
- [Cost Model Details](./COST_MODEL.md)
- [Deployment Manifests](../deployment/gke/)

### External Resources

- [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [News API Documentation](https://newsapi.org/docs)
- [robots.txt Specification (RFC 9309)](https://www.rfc-editor.org/rfc/rfc9309.html)
- [GKE CronJob Best Practices](https://cloud.google.com/kubernetes-engine/docs/how-to/cronjobs)
- [Gemini 2.0 Pro API Reference](https://ai.google.dev/gemini-api/docs)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Status**: Pre-production specification
**Maintained By**: PNKLN Ingestion Team
**Review Cycle**: Bi-weekly until production deployment
