# pnkln CORE STACK™ — DUAL-SYSTEM ARCHITECTURE

## Gemini Ingestion Layer + Judge 6 Integration (GKE-Native)

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Status:** Pre-Production Architecture
**Platform:** GKE (Google Kubernetes Engine) + Vertex AI

---

## EXECUTIVE SUMMARY

The pnkln Core Stack™ implements a **two-stage intelligence-to-governance pipeline**:

1. **Gemini Ingestion Layer** (Upstream): Proactive intelligence collection via ethical web crawling
2. **Judge 6** (Downstream): Real-time governance enforcement with <500μs p99 latency

This architecture separates **acquisition** (batch, nightly) from **enforcement** (real-time, continuous), optimizing each for its purpose while maintaining end-to-end data quality and compliance.

**Combined Economics:**

- Gemini Ingestion: ~$77/month operational cost
- Judge 6: $60-65K/month production deployment (includes full stack)
- **Total Core Stack ARR Target:** $1.5B (2030)

---

## SYSTEM 1: GEMINI INGESTION LAYER

### Purpose

Proactive intelligence collection pipeline that feeds high-quality, ethically-sourced data into the pnkln ecosystem.

### Architecture (GKE-Native)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gemini-ingestion
  namespace: gke-training-system
spec:
  schedule: "0 2 * * *" # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: crawler
              image: gcr.io/pnkln/gemini-crawler:latest
              resources:
                requests:
                  memory: "4Gi"
                  cpu: "2"
                limits:
                  memory: "8Gi"
                  cpu: "4"
              env:
                - name: TIER_1_SOURCES
                  valueFrom:
                    configMapKeyRef:
                      name: ingestion-config
                      key: tier1_sources

            - name: classifier
              image: gcr.io/pnkln/gemini-classifier:latest
              resources:
                requests:
                  nvidia.com/gpu: 1 # T4 sufficient for classification

            - name: quality-gate
              image: gcr.io/pnkln/quality-gate:latest
              resources:
                requests:
                  memory: "2Gi"
                  cpu: "1"

          restartPolicy: OnFailure
          nodeSelector:
            cloud.google.com/gke-preemptible: "true" # Cost optimization
```

### Key Metrics (vs Judge 6)

| Dimension             | Gemini Ingestion Layer                    | Judge 6                                    |
| --------------------- | ----------------------------------------- | ------------------------------------------- |
| **Architecture**      | GKE CronJob Multi-Container               | GKE StatefulSet + Redis                     |
| **Execution Model**   | Batch (nightly, ~45 min)                  | Real-time (<500μs p99)                      |
| **Primary Metrics**   | Items/day, Sources, Cost/item, Relevance  | Latency, Throughput, Block Rate, FP/FN      |
| **Integration Role**  | **Called by** services (upstream trigger) | **Calls** services (downstream enforcement) |
| **Key Features**      | Ethical crawling, Tier classification     | Compliance Framework CRM, JR validation, PRB gates      |
| **Cost Model**        | ~$77/month operational                    | Included in $60-65K stack                   |
| **Quality Focus**     | Relevance, Timeliness, Completeness       | False Positive/Negative rates               |
| **Confidence Target** | ≥60% (pre-prod, specs-only)               | ≥70% (prod, telemetry-backed)               |

### Performance Gates

**Daily Quality Thresholds:**

```yaml
quality_gates:
  items_per_day:
    minimum: 10000
    target: 50000
    alert_below: 8000

  source_diversity:
    tier_1_minimum: 5 # High-value sources (YouTube, major news)
    tier_2_minimum: 15 # Medium-value (Twitter, blogs)
    tier_3_maximum: 80% # Low-value shouldn't dominate

  cost_efficiency:
    max_cost_per_item: "$0.001"
    target_cost_per_item: "$0.0005"
    monthly_budget: "$77"

  relevance_scoring:
    minimum_average: 0.70
    tier_1_minimum: 0.85
    reject_below: 0.40

  runtime_efficiency:
    max_duration_minutes: 60
    target_duration_minutes: 45
    alert_above_minutes: 55
```

### Ethical Compliance Model

**Critical Pre-Production Requirements:**

```python
# robots.txt Compliance
class EthicalCrawler:
    def __init__(self):
        self.robots_parser = RobotFileParser()
        self.rate_limiter = RateLimiter(
            max_requests_per_second=2,  # Conservative default
            respect_crawl_delay=True
        )

    def can_fetch(self, url: str) -> bool:
        """Check robots.txt before every request"""
        return self.robots_parser.can_fetch("pnklnBot/1.0", url)

    def fetch_with_transparency(self, url: str) -> Response:
        """Transparent user-agent, contact info in headers"""
        headers = {
            'User-Agent': 'pnklnBot/1.0 (+https://pnkln.ai/bot)',
            'From': 'crawler@pnkln.ai'
        }
        return requests.get(url, headers=headers, timeout=30)
```

**Compliance Checklist:**

- ✅ robots.txt honored 100% (zero violations tolerated)
- ✅ Rate limiting: ≤2 req/sec default, respect site-specific crawl-delay
- ✅ Transparent user-agent with contact info
- ✅ Respect noindex, nofollow directives
- ✅ DMCA safe harbor compliance
- ✅ GDPR right-to-be-forgotten hooks

### Multi-Source Coverage Analysis

**Tier Classification (Strategic Prioritization):**

```yaml
tier_1_sources:  # High-value, authoritative
  - youtube_official_channels  # Political statements, hearings
  - major_news_apis:           # AP, Reuters, BBC
      cost_per_item: "$0.002"
      update_frequency: "hourly"
  - government_feeds:          # FDA, DOD, NASA
      cost_per_item: "$0.000"  # Public domain
  target_percentage: "20-30%"

tier_2_sources:  # Medium-value, diverse perspectives
  - twitter_verified_accounts
  - regional_news
  - industry_blogs
  - academic_preprints
  target_percentage: "40-50%"

tier_3_sources:  # Low-value, bulk context
  - general_twitter
  - reddit_submissions
  - user_forums
  target_percentage: "20-30%"
```

**Source Diversity Metrics:**

- **Platform Coverage:** YouTube, Twitter, RSS, APIs, scraped HTML
- **Geographic Diversity:** US (60%), EU (20%), APAC (15%), Other (5%)
- **Language Distribution:** English (80%), Spanish (10%), Other (10%)
- **Content Types:** Video transcripts (30%), Text (50%), Metadata (20%)

### AM Briefing Delivery Effectiveness

**Output Format (Downstream Handoff to Services):**

```json
{
  "briefing_date": "2025-11-15",
  "ingestion_window": "2025-11-14T02:00:00Z to 2025-11-15T02:45:00Z",
  "total_items": 47234,
  "tier_distribution": {
    "tier_1": 12456,
    "tier_2": 21089,
    "tier_3": 13689
  },
  "top_topics": [
    { "topic": "AI Regulation", "items": 8234, "avg_score": 0.87 },
    { "topic": "DoD Procurement", "items": 3421, "avg_score": 0.82 }
  ],
  "quality_metrics": {
    "avg_relevance": 0.76,
    "completeness": 0.94,
    "timeliness": 0.89
  },
  "cost_summary": {
    "total_cost_usd": 2.54,
    "cost_per_item": 0.000054
  },
  "delivery_status": "ready_for_judge_6"
}
```

**Delivery SLA:**

- **Target Completion:** 2:45 AM daily (before Judge 6 morning validation)
- **Format:** JSON to Cloud Storage, Pub/Sub event trigger
- **Latency to Services:** <5 minutes from ingestion completion to availability

---

## SYSTEM 2: JUDGE #6

### Purpose

Real-time governance enforcement ensuring all AI outputs comply with Compliance Framework CRM, JR doctrine, and PRB framework.

### Architecture (GKE-Native)

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: judge-6
  namespace: gke-inference-system
spec:
  serviceName: judge-6
  replicas: 3
  template:
    spec:
      containers:
        - name: judge-6
          image: gcr.io/pnkln/judge-6:latest
          resources:
            limits:
              nvidia.com/gpu: 1 # A100 for <500μs p99
              memory: "64Gi"
          env:
            - name: COVERAGE_GATE_MINIMUM
              value: "98"
            - name: ROLLBACK_THRESHOLD
              value: "95"
          ports:
            - containerPort: 8080
              name: grpc

        - name: redis-cache
          image: redis:7-alpine
          resources:
            limits:
              memory: "32Gi" # In-memory state for sub-ms latency
          volumeMounts:
            - name: redis-data
              mountPath: /data

        - name: metrics-exporter
          image: gcr.io/pnkln/metrics-exporter:latest
          resources:
            requests:
              memory: "1Gi"
              cpu: "0.5"
```

### Performance Gates

```yaml
performance_gates:
  latency:
    p50_max_ms: 30
    p90_max_ms: 60
    p99_max_ms: 500 # Hard requirement
    p99_9_max_ms: 800

  throughput:
    min_qps: 1000
    target_qps: 10000
    burst_qps: 50000

  coverage:
    minimum_percentage: 98.0
    rollback_threshold: 95.0
    alert_below: 97.0

  accuracy:
    max_false_positive_rate: 0.02
    max_false_negative_rate: 0.01
    min_f1_score: 0.97
```

### Integration with 4 GKE Namespaces

**Calls Services Across:**

1. `gke-inference-system/` - Validates model outputs before serving
2. `gke-training-system/` - Pre-commit hooks on training data
3. `gke-monitoring-system/` - Feeds audit logs, compliance reports
4. `gke-gateway-system/` - API-level enforcement (admission webhooks)

---

## INTEGRATION ARCHITECTURE: INGESTION → JUDGE #6 → SERVICES

### Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ GEMINI INGESTION LAYER (Nightly 2:00 AM - 2:45 AM)         │
│                                                             │
│  Tier 1 Sources ──┐                                         │
│  Tier 2 Sources ──┼─→ [Crawler] → [Classifier] → [QA Gate] │
│  Tier 3 Sources ──┘         │            │            │     │
│                             ↓            ↓            ↓     │
│                        Raw Items → Tagged Items → JSON      │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ↓ (Pub/Sub Event)
┌─────────────────────────────────────────────────────────────┐
│ CLOUD STORAGE (gs://pnkln-ingestion-daily/)                 │
│  └─ 2025-11-15-briefing.json (47,234 items)                 │
└─────────────────────────────────────────────────────────────┘
                                    │
                                    ↓ (Triggered on new file)
┌─────────────────────────────────────────────────────────────┐
│ JUDGE #6 (Continuous, <500μs p99)                           │
│                                                             │
│  [Redis Cache] ←→ [Judge 6 Core] ←→ [Compliance Framework Validator]  │
│        │                 │                      │           │
│        ↓                 ↓                      ↓           │
│  Sub-ms Lookup    PRB Enforcement    JR Doctrine Check     │
└─────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ↓               ↓               ↓
         ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
         │  Inference   │  │  Training    │  │  Gateway     │
         │  System      │  │  System      │  │  System      │
         │              │  │              │  │              │
         │ (Validates   │  │ (Pre-commit  │  │ (Admission   │
         │  outputs)    │  │  hooks)      │  │  webhooks)   │
         └──────────────┘  └──────────────┘  └──────────────┘
```

### Handoff Contract

**Gemini Ingestion → Cloud Storage:**

```python
@dataclass
class IngestionBriefing:
    """Output contract from Gemini Ingestion Layer"""
    briefing_date: str
    total_items: int
    tier_distribution: Dict[str, int]
    items: List[IngestedItem]
    quality_metrics: QualityMetrics

    def meets_quality_gates(self) -> bool:
        return (
            self.quality_metrics.avg_relevance >= 0.70 and
            self.quality_metrics.completeness >= 0.90 and
            self.total_items >= 10000
        )
```

**Cloud Storage → Judge 6:**

```python
@dataclass
class IngestedItem:
    """Individual item for Judge 6 validation"""
    item_id: str
    source: str
    tier: int  # 1, 2, or 3
    content: str
    metadata: Dict[str, Any]
    ingestion_score: float

    # Judge 6 adds these fields during validation
    judge_verdict: Optional[str] = None
    prb_compliance: Optional[bool] = None
    atp_519_risk: Optional[str] = None  # RA-1 through RA-4
```

**Judge 6 → Services:**

```python
class JudgeDecision:
    """Real-time validation response"""
    item_id: str
    allowed: bool
    latency_us: int  # Must be <500,000 for p99
    coverage: float  # Must be ≥0.98
    reasoning: Optional[str]
    fallback_triggered: bool
```

### Failure Modes and Resilience

**Scenario 1: Ingestion Layer Fails (Stale Data)**

- **Detection:** No Pub/Sub event by 3:00 AM
- **Fallback:** Judge 6 uses previous day's briefing (marked as stale)
- **Alert:** PagerDuty → On-call engineer
- **Impact:** Minimal (services still validated, data 24h old)

**Scenario 2: Judge 6 Coverage Drops <98%**

- **Detection:** Prometheus alert on coverage metric
- **Action:** Automatic rollback to last known good version (GKE rollout undo)
- **Fallback:** Reject all ambiguous requests (fail-closed)
- **Impact:** High (potential service degradation, manual review required)

**Scenario 3: Judge 6 Latency Exceeds 500μs p99**

- **Detection:** Cloud Monitoring latency alert
- **Action:** Scale StatefulSet replicas (3 → 6 → 9)
- **Fallback:** Redis cache warming, reduce coverage temporarily (98% → 95%)
- **Impact:** Medium (SLA breach, auto-scaling mitigates)

---

## COST MODEL (COMBINED)

### Gemini Ingestion Layer: ~$77/month

```yaml
breakdown:
  gke_compute:
    node_type: "e2-standard-4 preemptible"
    hours_per_month: 45 # 45 min/night × 30 days = 22.5 hours
    cost_per_hour: "$0.10"
    total: "$2.25"

  gpu_classification:
    accelerator: "nvidia-tesla-t4"
    hours_per_month: 15 # Parallel to crawler, less time
    cost_per_hour: "$0.35"
    total: "$5.25"

  api_costs:
    youtube_api: "$30"
    twitter_api: "$20"
    news_apis: "$15"
    total: "$65"

  storage:
    cloud_storage: "$2"
    pub_sub: "$1"
    total: "$3"

  networking: "$1.50"

  monthly_total: "$77"
  annual_total: "$924"
```

### Judge 6: Included in $60-65K/month Stack

Judge 6 cost is part of the full pnkln Core Stack™ deployment, which includes:

- 3× A100 GPUs for StatefulSet
- 32GB Redis instances × 3
- Monitoring, logging, networking
- Multi-region redundancy

**Note:** Ingestion layer is incremental (~$1K/year), negligible compared to core stack.

---

## QUALITY GATES COMPARISON

| Gate          | Gemini Ingestion    | Judge 6           |
| ------------- | ------------------- | ------------------ |
| **Primary**   | Relevance ≥0.70     | Coverage ≥98%      |
| **Secondary** | Items/day ≥10K      | Latency p99 ≤500μs |
| **Tertiary**  | Cost/item ≤$0.001   | FP rate ≤2%        |
| **Rollback**  | 3 consecutive fails | Coverage <95%      |
| **Alert**     | Relevance <0.65     | Latency p99 >500μs |

---

## ANALYSIS PROMPT CALIBRATION

Both systems use Gemini 2.0 Pro for pre-production analysis, with confidence targets adjusted for data availability:

**Judge 6 Analysis Prompt:**

- **Input:** Production telemetry (logs, metrics, traces)
- **Confidence Target:** ≥70%
- **Focus:** Performance optimization, error reduction

**Gemini Ingestion Analysis Prompt:**

- **Input:** Architecture specs, pipeline docs (pre-prod)
- **Confidence Target:** ≥60%
- **Focus:** Design validation, ethical compliance, scalability

### Suggested Iteration Steps

1. **Test Runs:** Execute both prompts on sample data, compare outputs
2. **Visualization:** Add requests for tier distribution charts, latency histograms
3. **Edge Cases:** Probe failure modes (source outages, cost spikes, latency degradation)
4. **Combined Analysis:** Single prompt analyzing Ingestion → Judge 6 handoff

---

## NEXT STEPS

### Pre-Production (Q4 2025)

- [ ] Deploy Gemini Ingestion to GKE staging cluster
- [ ] Validate ethical compliance (robots.txt, rate limits)
- [ ] Run 30-day pilot with tier classification
- [ ] Benchmark AM briefing delivery effectiveness
- [ ] Execute combined Gemini 2.0 Pro analysis (both prompts)

### Production Readiness (Q2 2026)

- [ ] Judge 6 <500μs p99 validated with ingested data
- [ ] Multi-source coverage: 5+ Tier 1, 15+ Tier 2 sources
- [ ] Cost efficiency: <$0.001/item sustained over 90 days
- [ ] End-to-end integration test (Ingestion → Judge → Services)
- [ ] Confidence targets met: Ingestion ≥60%, Judge 6 ≥70%

### Scale (2027-2030)

- [ ] 1B+ items/month ingestion capacity
- [ ] Judge 6: 10M+ queries/day, p99 <500μs
- [ ] Global multi-cluster deployment (Anthos)
- [ ] Full pnkln Core Stack™: $1.5B ARR

---

## DOCUMENT REFERENCES

- **Cor.26:** Cognitive Stack v5 technical architecture
- **Cor.53:** Source code definitions (JR, PRB, Compliance Framework)
- **Cor.55:** Pre-hoc compliance moat ($8.6B EV premium)
- **GKE Inference Ref:** https://github.com/GoogleCloudPlatform/accelerated-platforms/.../inference-ref-arch/

---

**Status:** Ready for GKE staging deployment and Gemini 2.0 Pro analysis execution.

**Approval Gate:** Erik sign-off on ethical compliance model + cost targets.
