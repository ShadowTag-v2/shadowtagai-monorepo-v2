# 🔍 Ingestion Layer Analyzer - PNKLN Core Stack™

**Monitors GKE CronJob-based intelligence gathering with ethical crawling, quality gates, and cost efficiency tracking.**

---

## ✨ Key Features

### 🚀 **Runtime Efficiency Monitoring**

- Track nightly batch job performance
- Target: ~45 minutes per night
- GKE CronJob multi-container architecture
- Identify slow jobs and suggest optimizations

### 📊 **Multi-Source Coverage Analysis**

- **YouTube** - Video content intelligence
- **Twitter** - Social media monitoring
- **News** - News article aggregation
- **RSS** - Feed monitoring
- **Web** - General web crawling
- **API** - Third-party API integrations
- **Podcast** - Audio content transcription
- **Research** - Academic paper tracking

Includes diversity scoring using Shannon entropy to prevent over-reliance on single sources.

### 🛡️ **Ethical Compliance Monitoring**

- **robots.txt** compliance checking
- **Rate limiting** enforcement
- **Transparent user agent** ("PNKLNBot/1.0")
- Violation tracking and reporting
- Compliance scoring (0-100)

### 📈 **Tier Classification**

- **Tier 1**: High-value, authoritative sources (target: ≥20%)
- **Tier 2**: Medium-value, verified sources (target: 30-50%)
- **Tier 3**: Low-value, general sources (target: ≤50%)

Ensures quality data distribution across intelligence pipeline.

### 💰 **Cost Tracking**

- Monthly operational budget: ~$77
- Cost breakdown: API, compute, storage, network
- Cost per item tracking
- Budget utilization monitoring
- End-of-month projections

### ✅ **Quality Gates**

Automated pass/fail checks:

- Daily items ≥ 1,000
- Source diversity ≥ 5 unique sources
- Cost per item ≤ $0.10
- Average quality score ≥ 70
- Tier 1 percentage ≥ 20%
- Ethical compliance ≥ 95%

### 📬 **AM Briefing Delivery**

- On-time delivery rate tracking
- Delivery delay monitoring
- Effectiveness scoring
- Recipient engagement metrics

---

## 🚀 Quick Start

### 1. Installation

```bash
# Already included in main installation
pip install -r requirements.txt
```

### 2. Start the API

```bash
./start.sh

# Or manually
uvicorn app.main:app --reload
```

### 3. Access Ingestion Endpoints

- **Summary**: <http://localhost:8000/ingestion/summary>
- **Full Report**: <http://localhost:8000/ingestion/report>
- **Docs**: <http://localhost:8000/docs>

---

## 📖 API Endpoints

### Core Endpoints

| Endpoint                        | Method | Description                        |
| ------------------------------- | ------ | ---------------------------------- |
| `/ingestion/summary`            | GET    | Quick overview of ingestion health |
| `/ingestion/report`             | GET    | Comprehensive ingestion report     |
| `/ingestion/runtime-efficiency` | GET    | Nightly batch job performance      |
| `/ingestion/quality-gates`      | GET    | Check if quality gates pass        |

### Source Coverage

| Endpoint                            | Method | Description                         |
| ----------------------------------- | ------ | ----------------------------------- |
| `/ingestion/source-coverage`        | GET    | Multi-source coverage analysis      |
| `/ingestion/source-coverage/gaps`   | GET    | Identify coverage gaps              |
| `/ingestion/source-coverage/{type}` | GET    | Quality metrics for specific source |
| `/ingestion/tier-distribution`      | GET    | Tier 1/2/3 distribution             |

### Ethical Compliance

| Endpoint                                   | Method | Description                  |
| ------------------------------------------ | ------ | ---------------------------- |
| `/ingestion/ethical-compliance`            | GET    | Full compliance report       |
| `/ingestion/ethical-compliance/score`      | GET    | Compliance score (0-100)     |
| `/ingestion/ethical-compliance/violations` | GET    | Recent violations            |
| `/ingestion/check-robots-txt`              | POST   | Check URL against robots.txt |
| `/ingestion/check-rate-limit`              | POST   | Verify rate limit compliance |

### Cost & Delivery

| Endpoint                       | Method | Description                  |
| ------------------------------ | ------ | ---------------------------- |
| `/ingestion/costs/monthly`     | GET    | Monthly cost tracking (~$77) |
| `/ingestion/briefing-delivery` | GET    | AM briefing effectiveness    |

---

## 🎯 Use Cases

### ✅ Runtime Efficiency

Monitor nightly batch jobs to ensure they complete within ~45 minutes:

```bash
curl http://localhost:8000/ingestion/runtime-efficiency?days=7
```

**Response:**

```json
{
  "target_runtime_minutes": 45,
  "actual_avg_runtime_minutes": 42.3,
  "meets_target": true,
  "jobs": [
    {
      "job_name": "youtube_ingestion",
      "avg_runtime_minutes": 15.2,
      "meets_target": true
    }
  ],
  "optimization_suggestions": []
}
```

### ✅ Quality Gates Monitoring

Check if all quality gates are passing:

```bash
curl http://localhost:8000/ingestion/quality-gates
```

**Response:**

```json
{
  "overall_status": "PASS",
  "gates": {
    "daily_items": {
      "value": 1250,
      "threshold": 1000,
      "passed": true,
      "status": "PASS"
    },
    "tier_1_percentage": {
      "value": 22.5,
      "threshold": 20.0,
      "passed": true,
      "status": "PASS"
    }
  },
  "passed_count": 6,
  "total_gates": 6
}
```

### ✅ Source Coverage Analysis

Ensure diverse intelligence sources:

```bash
curl http://localhost:8000/ingestion/source-coverage
```

**Response:**

```json
{
  "coverage": {
    "youtube": 150,
    "twitter": 320,
    "news": 450,
    "rss": 80,
    "total_sources": 8,
    "diversity_score": 78.5
  },
  "coverage_gaps": [
    {
      "source_type": "podcast",
      "current_count": 5,
      "target_count": 10,
      "priority": "medium",
      "recommendation": "Add 5 more podcast feeds to transcription pipeline"
    }
  ]
}
```

### ✅ Ethical Compliance

Monitor ethical crawling practices:

```bash
curl http://localhost:8000/ingestion/ethical-compliance
```

**Response:**

```json
{
  "compliance_score": {
    "overall_score": 96.8,
    "status": "excellent",
    "by_check_type": {
      "robots_txt": {
        "score": 98.5,
        "total_checks": 1200,
        "violations": 18
      },
      "rate_limit": {
        "score": 95.2,
        "violations": 45
      }
    }
  },
  "recent_violations": [
    {
      "source": "example.com/api",
      "check_type": "rate_limit",
      "details": "Rate limit violated: 0.45s < 1.00s"
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "issue": "45 rate limit violations in 24h",
      "recommendation": "Implement stricter rate limiting"
    }
  ]
}
```

### ✅ Cost Tracking

Monitor monthly operational costs:

```bash
curl http://localhost:8000/ingestion/costs/monthly
```

**Response:**

```json
{
  "month": "2025-11",
  "total_cost": 58.32,
  "budget": 77.0,
  "remaining_budget": 18.68,
  "budget_utilization": 75.7,
  "cost_breakdown": {
    "api_costs": 25.5,
    "compute_costs": 22.1,
    "storage_costs": 8.2,
    "network_costs": 2.52
  },
  "items_collected": 35420,
  "cost_per_item": 0.0016,
  "status": "healthy",
  "projection": {
    "projected_total": 72.45,
    "projected_overage": 0.0
  }
}
```

---

## 🏗️ Architecture Overview

### GKE CronJob Multi-Container

The ingestion layer runs as Kubernetes CronJobs in Google Kubernetes Engine:

```
┌─────────────────────────────────────────┐
│         GKE CronJob (Nightly)          │
├─────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐   │
│  │   YouTube    │  │   Twitter    │   │
│  │  Container   │  │  Container   │   │
│  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐   │
│  │    News      │  │     RSS      │   │
│  │  Container   │  │  Container   │   │
│  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────┘
           │
           ▼
   ┌───────────────────┐
   │ Ingestion Analyzer │ ← This API
   │   (Monitoring)     │
   └───────────────────┘
```

### Integration Points

Called by services in 4 namespaces:

- **Intelligence Pipeline**: Consumes ingested data
- **Analysis Engine**: Processes collected items
- **Briefing Service**: Uses data for AM briefings
- **Archive Service**: Long-term storage

---

## 🎓 Quality Gates Explained

The system enforces 6 quality gates:

### 1. Daily Items (≥1,000)

Ensures minimum data collection volume for meaningful intelligence.

### 2. Source Diversity (≥5)

Prevents over-reliance on single sources. Shannon entropy diversity score measures balance.

### 3. Cost Per Item (≤$0.10)

Keeps operational costs sustainable at ~$77/month budget.

### 4. Average Score (≥70)

Combines relevance, timeliness, and completeness scores.

- **Relevance**: Is data pertinent to intelligence goals?
- **Timeliness**: Is data recent and current?
- **Completeness**: Is data comprehensive?

### 5. Tier 1 Percentage (≥20%)

Ensures high-value authoritative sources make up significant portion.

### 6. Ethical Compliance (≥95%)

Maintains ethical crawling standards (robots.txt, rate limits, transparency).

**Example Gate Failure Response:**

```json
{
  "overall_status": "FAIL",
  "gates": {
    "tier_1_percentage": {
      "value": 15.3,
      "threshold": 20.0,
      "passed": false,
      "status": "FAIL"
    }
  },
  "recommendation": "Add more high-value Tier 1 sources"
}
```

---

## 🛡️ Ethical Compliance Model

### robots.txt Compliance

Checks disallow rules before crawling:

```bash
curl -X POST "http://localhost:8000/ingestion/check-robots-txt?url=https://example.com/page"
```

### Rate Limiting

Enforces per-source rate limits:

- YouTube: 2 seconds between requests
- Twitter: 1.5 seconds
- News: 0.5 seconds
- Default: 1 second

```bash
curl -X POST "http://localhost:8000/ingestion/check-rate-limit?source_type=youtube&source_identifier=channel123"
```

### Transparency

Uses clear user agent:

```
PNKLNBot/1.0 (+https://pnkln.ai/bot; Intelligence Collection)
```

---

## 📊 Metrics Comparison

### Traditional Metrics vs. Ingestion Metrics

| Judge #6 (Validation)    | Ingestion Layer                     |
| ------------------------ | ----------------------------------- |
| p99 ≤ 90ms (latency)     | ~45 min/night (batch runtime)       |
| FP/FN rates              | Relevance, timeliness, completeness |
| 98% coverage             | Quality gates (6 dimensions)        |
| API calls per validation | Monthly operational ~$77            |
| Calls 4 namespaces       | Called by 4 namespaces              |

---

## 🔧 Configuration

### Quality Gate Thresholds

Edit `app/models/ingestion.py`:

```python
class QualityGates(BaseModel):
    daily_items_threshold: int = 1000
    source_diversity_threshold: int = 5
    cost_per_item_threshold: float = 0.10
    average_score_threshold: float = 70.0
    tier_1_percentage_threshold: float = 20.0
    ethical_compliance_threshold: float = 95.0
    runtime_threshold_minutes: float = 45.0
```

### Rate Limits

Edit `app/services/ethical_compliance.py`:

```python
self.rate_limits = {
    'default': 1.0,
    'youtube': 2.0,
    'twitter': 1.5,
    'news': 0.5,
}
```

---

## 📈 Example Workflow

1. **Nightly CronJob Runs** (~45 minutes)
   - Collects data from YouTube, Twitter, News, etc.
   - Stores metrics in database

2. **Morning Analysis** (6 AM)

   ```bash
   curl http://localhost:8000/ingestion/summary
   ```

3. **Check Quality Gates**

   ```bash
   curl http://localhost:8000/ingestion/quality-gates
   ```

4. **Review Violations** (if compliance < 95%)

   ```bash
   curl http://localhost:8000/ingestion/ethical-compliance/violations
   ```

5. **Identify Coverage Gaps**

   ```bash
   curl http://localhost:8000/ingestion/source-coverage/gaps
   ```

6. **Monitor Costs**

   ```bash
   curl http://localhost:8000/ingestion/costs/monthly
   ```

---

## 🎯 Best Practices

### 1. Monitor Quality Gates Daily

Set up alerts when gates fail:

```bash
# Add to cron
0 6 * * * curl http://localhost:8000/ingestion/quality-gates | jq '.overall_status' | grep -q "FAIL" && notify-admin
```

### 2. Review Ethical Compliance Weekly

```bash
curl http://localhost:8000/ingestion/ethical-compliance
```

### 3. Track Budget Utilization

Set alerts at 80% budget:

```bash
curl http://localhost:8000/ingestion/costs/monthly | jq '.budget_utilization'
```

### 4. Balance Source Coverage

Aim for diversity score > 75:

```bash
curl http://localhost:8000/ingestion/source-coverage | jq '.coverage.diversity_score'
```

### 5. Optimize Runtime

Keep batch jobs under 45 minutes:

```bash
curl http://localhost:8000/ingestion/runtime-efficiency?days=7
```

---

## 🚨 Troubleshooting

### Quality Gates Failing

**Issue**: `daily_items` gate failing

```json
{
  "daily_items": {
    "value": 850,
    "threshold": 1000,
    "passed": false
  }
}
```

**Solution**: Add more sources or increase polling frequency

### Ethical Violations

**Issue**: Rate limit violations

```bash
curl http://localhost:8000/ingestion/ethical-compliance/violations
```

**Solution**: Adjust rate limits in `ethical_compliance.py`

### High Costs

**Issue**: Budget utilization > 90%

```json
{
  "budget_utilization": 95.2,
  "status": "critical"
}
```

**Solution**: Review cost breakdown, optimize expensive sources

### Low Tier 1 Percentage

**Issue**: < 20% Tier 1 sources

```json
{
  "tier_1_percentage": {
    "value": 15.3,
    "passed": false
  }
}
```

**Solution**: Add more authoritative sources, upgrade Tier 2 sources

---

## 📝 Data Models

### Source Tiers

**Tier 1** - Authoritative, high-value:

- Major news outlets (NYT, WSJ, BBC)
- Academic institutions
- Government sources
- Verified expert accounts

**Tier 2** - Verified, medium-value:

- Regional news
- Industry publications
- Verified professionals
- Established blogs

**Tier 3** - General, low-value:

- Social media aggregators
- User-generated content
- Unverified sources

---

## 🔗 Integration with PNKLN Stack

This ingestion layer feeds into:

1. **Intelligence Pipeline** - Processes collected items
2. **Analysis Engine** - Generates insights
3. **Briefing Service** - Creates AM briefings
4. **Archive Service** - Long-term storage

```
Ingestion Layer → Intelligence Pipeline → Analysis → Briefing
       ↓                                                ↓
   Archive ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

---

## 📞 Support

For issues:

- Check `/ingestion/summary` for quick diagnostics
- Review `/ingestion/quality-gates` for gate status
- Monitor `/ingestion/ethical-compliance` for violations

---

**Part of the PNKLN Core Stack™ - Ethical Intelligence Gathering** 🔍
