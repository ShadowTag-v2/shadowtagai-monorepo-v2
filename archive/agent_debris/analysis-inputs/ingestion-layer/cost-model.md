# Cost Model - Gemini Ingestion Layer

**Version**: 1.0-draft
**Status**: Pre-Production Estimates
**Last Updated**: 2025-11-15
**Monthly Budget Target**: $77

---

## Cost Breakdown (Monthly)

### 1. GKE Compute Costs

**Component**: Google Kubernetes Engine cluster

| Resource | Specification | Cost/Hour | Hours/Month | Monthly Cost |
|----------|---------------|-----------|-------------|--------------|
| **Control Plane** | GKE Autopilot | $0.10/hour | 730 | $73.00 |
| **Worker Nodes** | 2× e2-standard-4 (preemptible) | $0.067/node/hour | 22.5 hours/month<br/>(45 min/night × 30 nights) | $3.02 |
| **Persistent Volumes** | 5GB ephemeral (no cost) | $0 | - | $0 |
| **Load Balancer** | Not needed (batch job) | $0 | - | $0 |

**Subtotal GKE**: ~$76.02/month

**Cost Optimization**:

- Using **Autopilot** (pay-per-pod) instead of Standard saves ~40%
- **Preemptible nodes** save 80% vs on-demand ($0.067 vs $0.335/hour)
- **No persistent storage** (ephemeral volumes only)
- **No load balancer** (batch job, not web-facing)

**Risk**: Preemptible nodes can be interrupted mid-job (~5% failure rate)

---

### 2. API Costs

#### Gemini 2.0 Pro API (Tier Classification)

**Usage**: 1000-2000 items/night classified

| Tier | Price | Items/Night | API Calls | Monthly Cost |
|------|-------|-------------|-----------|--------------|
| **Gemini 2.0 Pro** | $0.001/1K chars input<br/>$0.003/1K chars output | 1500 avg | 150 calls<br/>(batch 10 items/call) | $18.00 |

**Assumptions**:

- Average item size: 500 characters (title + snippet)
- Batch size: 10 items per API call
- Input tokens: 500 chars × 10 items = 5K chars/call = $0.005/call
- Output tokens: ~200 chars/call (tier + score) = $0.0006/call
- Total per call: ~$0.006 × 150 calls/night × 30 nights = $27/month

**Actual estimate (with buffers)**: $18-20/month

**Cost Optimization**:

- **Batching**: 10 items/call vs 1 item/call saves 90% on API overhead
- **Caching**: Identical items (repost detection) skip classification
- **Fallback**: Rule-based classifier for obvious Tier 3 (spam) saves API calls

---

#### Source API Costs

| Source | API | Price | Usage | Monthly Cost |
|--------|-----|-------|-------|--------------|
| **YouTube** | Data API v3 | $0.001/quota unit | 10K units/night × 30 | $0.30 |
| **Twitter** | API v2 Elevated | $100/month base | Included in subscription | $3.33 (amortized) |
| **Reddit** | PRAW API | Free | N/A | $0 |
| **Hacker News** | Firebase | Free | N/A | $0 |
| **arXiv** | OAI-PMH | Free | N/A | $0 |
| **Others** | Various | Free/public | N/A | $0 |

**Subtotal APIs**: ~$21.63/month

---

### 3. Storage Costs

#### Cloud Storage (Raw Data)

**Usage**: Store raw crawl data for 30 days (audit/reprocessing)

| Storage Type | Data Volume | Price | Monthly Cost |
|--------------|-------------|-------|--------------|
| **Standard Storage** | 1500 items × 1KB avg × 30 nights = 45MB/month cumulative | $0.020/GB | $0.001 |
| **Operations** | 1500 writes/night × 30 = 45K ops | $0.005/10K ops | $0.02 |

**Subtotal Cloud Storage**: ~$0.02/month (negligible)

---

#### Cloud SQL (Metadata)

**Usage**: Store item metadata, source health metrics

| Resource | Specification | Price | Monthly Cost |
|----------|---------------|-------|--------------|
| **Instance** | db-f1-micro (shared, 0.6GB RAM) | $7.67/month | $7.67 |
| **Storage** | 10GB SSD | $0.17/GB/month | $1.70 |

**Subtotal Cloud SQL**: ~$9.37/month

**Alternative**: Use Cloud Firestore (serverless) for ~$1-2/month at current scale

---

### 4. Networking Costs

#### Egress (Crawling External Sources)

| Traffic Type | Volume | Price | Monthly Cost |
|--------------|--------|-------|--------------|
| **Egress to Internet** | 1500 items × 2KB avg × 30 nights = 90MB/month | $0.12/GB (first 1GB free) | $0 (under 1GB) |
| **Ingress** | Free | $0 | $0 |

**Subtotal Networking**: ~$0/month (under free tier)

---

### 5. Monitoring & Logging

#### Cloud Monitoring + Logging

| Service | Usage | Price | Monthly Cost |
|---------|-------|-------|--------------|
| **Metrics** | ~100 metrics × 30 days | $0.258/MB ingested | $0.50 |
| **Logs** | 1GB logs/month (job output) | $0.50/GB | $0.50 |

**Subtotal Monitoring**: ~$1.00/month

---

## Total Monthly Cost Summary

| Category | Cost | % of Total |
|----------|------|------------|
| **GKE Compute** | $76.02 | 62.5% |
| **APIs (Gemini + Sources)** | $21.63 | 17.8% |
| **Storage (Cloud SQL + GCS)** | $9.39 | 7.7% |
| **Networking** | $0.00 | 0% |
| **Monitoring** | $1.00 | 0.8% |
| **TOTAL** | **$108.04** | 100% |

**Note**: Exceeds target of $77/month by $31. Need optimization.

---

## Cost Optimization Strategies

### Option 1: Use Cloud Run Instead of GKE

**Savings**: ~$70/month (no Autopilot control plane cost)

| Resource | Cloud Run Cost | GKE Cost | Savings |
|----------|---------------|----------|---------|
| **Compute** | $0.00002/vCPU-sec × 4 vCPU × 2700 sec = $0.216/night | $3.02/month | Minimal |
| **Control Plane** | $0 (serverless) | $73/month | **$73/month** |

**Trade-off**: Cloud Run has 60-minute max runtime (vs GKE unlimited). For 45-minute target, acceptable.

**Recommended**: Migrate to Cloud Run to hit $77 budget.

---

### Option 2: Reduce Gemini API Usage

**Savings**: ~$10/month

- Pre-filter obvious Tier 3 (spam) with rule-based classifier (saves ~30% of API calls)
- Increase batch size from 10 to 20 items/call (saves ~10% on overhead)
- Cache classification for duplicate items (retweets, cross-posts)

**New API Cost**: $18 → $8/month

---

### Option 3: Use Smaller Cloud SQL Instance

**Savings**: ~$5/month

- Migrate from Cloud SQL ($9/month) to Firestore ($1-2/month)
- Store only metadata in Firestore, raw data in Cloud Storage

**New Storage Cost**: $9.37 → $2/month

---

### Option 4: Optimize Source Crawling

**Savings**: ~$5/month

- Remove or reduce frequency of low-yield sources (YouTube at 25% Tier 1)
- Focus on high-yield sources (Hacker News, News RSS, Government at 45-70% Tier 1)
- Reduces item count from 1500 → 1000/night, but maintains Tier 1 absolute count

**New Item Count**: 1500 → 1000/night
**Tier 1 Count**: 450 → 400/night (still meets targets)

---

## Revised Cost Model (With Optimizations)

| Category | Original | Optimized | Savings |
|----------|----------|-----------|---------|
| **Compute** | $76.02 (GKE) | $6.48 (Cloud Run) | **$69.54** |
| **APIs** | $21.63 | $11.63 | **$10.00** |
| **Storage** | $9.39 | $2.00 (Firestore) | **$7.39** |
| **Networking** | $0.00 | $0.00 | $0 |
| **Monitoring** | $1.00 | $1.00 | $0 |
| **TOTAL** | **$108.04** | **$21.11** | **$86.93** |

**New Monthly Cost**: ~$21/month (well under $77 budget)

**Margin**: $77 - $21 = **$56/month buffer** for growth

---

## Scaling Scenarios

### Scenario A: 2× Item Volume (3000 items/night)

| Category | Cost Impact | New Cost |
|----------|-------------|----------|
| Compute (Cloud Run) | 2× runtime (90 min/night) | $12.96 |
| APIs | 2× Gemini calls | $23.26 |
| Storage | 2× data | $3.00 |
| Other | Unchanged | $1.00 |
| **TOTAL** | | **$40.22/month** |

**Still under budget** ($77 target)

---

### Scenario B: 5× Item Volume (7500 items/night)

| Category | Cost Impact | New Cost |
|----------|-------------|----------|
| Compute | 5× runtime (225 min = 3.75 hours) | $32.40 |
| APIs | 5× Gemini calls | $58.15 |
| Storage | 5× data | $8.00 |
| Other | Unchanged | $1.00 |
| **TOTAL** | | **$99.55/month** |

**Exceeds budget** by $22.55 (need to increase budget or optimize further)

---

### Scenario C: 10× Item Volume (15,000 items/night)

| Category | Cost Impact | New Cost |
|----------|-------------|----------|
| Compute | 10× runtime (450 min = 7.5 hours) | $64.80 |
| APIs | 10× Gemini calls | $116.30 |
| Storage | 10× data | $15.00 |
| Other | Unchanged | $1.00 |
| **TOTAL** | | **$197.10/month** |

**Exceeds budget** by $120.10 (need to re-architect or significantly increase budget)

**Economies of Scale**: Cost/item decreases from $0.021 (1000 items) → $0.013 (15K items)

---

## Cost per Item Analysis

### Current (Optimized)

- **Total Cost**: $21.11/month
- **Items**: 1000 items/night × 30 nights = 30,000 items/month
- **Cost/Item**: $21.11 / 30,000 = **$0.0007/item** (well under $0.04 target)

### Original (Unoptimized)

- **Total Cost**: $108.04/month
- **Items**: 45,000 items/month
- **Cost/Item**: $108.04 / 45,000 = **$0.0024/item** (still under $0.04 target)

**Target**: $0.04/item (conservative)
**Actual**: $0.0007-0.0024/item (16-57× better than target)

**Implication**: Cost targets are very conservative, significant headroom for growth.

---

## Budget Alerts Configuration

### Alert Thresholds

- **70% of budget** ($53.90): Warning alert to Slack
- **90% of budget** ($69.30): Critical alert to on-call + email
- **100% of budget** ($77): Auto-shutdown + PagerDuty alert

### Alert Triggers

```yaml
# Cloud Monitoring alert policy
- name: ingestion-cost-warning
  condition: monthly_cost >= 53.90
  notification: slack-#pnkln-alerts

- name: ingestion-cost-critical
  condition: monthly_cost >= 69.30
  notification:
    - slack-#pnkln-alerts
    - email-oncall@pnkln.ai

- name: ingestion-cost-exceeded
  condition: monthly_cost >= 77.00
  notification: pagerduty-high
  action: disable-cronjob
```

---

## Open Questions (for Analysis)

1. **Should we migrate from GKE to Cloud Run** for $70/month savings?
2. **Is $21/month realistic**, or are we missing hidden costs (data transfer spikes, etc.)?
3. **What's the acceptable buffer** (50% under budget = $35-40/month target)?
4. **How do we handle unexpected API price increases** (e.g., Gemini pricing up 50%)?
5. **Should we set up billing export to BigQuery** for detailed cost attribution per source?
6. **What's the cost impact of adding 5 more sources** (Telegram, Discord, Medium)?

---

**Status**: Draft cost model for analysis review
**Recommendation**: Implement all 4 optimizations to achieve $21/month (vs $77 budget)
**Next Steps**: Gemini 2.0 Pro analysis of cost assumptions, scaling risks, optimization trade-offs
