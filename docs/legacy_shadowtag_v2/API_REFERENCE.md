# AI Agent Suite API Reference

> Complete API documentation for Wealth Acceleration and Gemini Ingestion Layer agents

**Version**: 2.0.0
**Base URL**: `http://localhost:8000`
**Protocol**: HTTP/REST
**Response Format**: Server-Sent Events (streaming)

---

## Quick Start

**Start the API server**:
```bash
cd src
uvicorn api.routes:app --reload --port 8000
```

**Test the API**:
```bash
curl http://localhost:8000/health
```

---

## Authentication

Currently no authentication required (development mode).

For production, implement API key authentication:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

---

## Common Endpoints

### `GET /`
Get API information and available endpoints

**Response**:
```json
{
  "name": "AI Agent Suite API - pnkln Core Stack™",
  "version": "2.0.0",
  "description": "Multi-agent AI system...",
  "agents": {
    "wealth_acceleration": { ... },
    "gemini_ingestion": { ... }
  }
}
```

### `GET /health`
Health check endpoint

**Response**:
```json
{
  "status": "healthy",
  "service": "ai-agent-suite-api",
  "agents": ["wealth_acceleration", "gemini_ingestion"],
  "version": "2.0.0"
}
```

---

## Wealth Acceleration Agent

> Revenue optimization and monetization strategy

### Base Path: `/wealth`

---

### `POST /wealth/analyze`
General analysis endpoint for custom queries

**Request Body**:
```json
{
  "business_context": {
    "niche": "SaaS founders",
    "current_monthly_revenue": 15000,
    "audience_size": 50000,
    "engagement_level": "high",
    "revenue_streams": ["consulting", "courses"],
    "platforms": ["Twitter", "LinkedIn"]
  },
  "prompt": "Analyze my complete monetization strategy"
}
```

**Response**: Streaming analysis

---

### `POST /wealth/analyze/monetization`
Complete monetization strategy analysis

**Request Body**:
```json
{
  "business_context": { ... },
  "focus_areas": ["pricing", "conversion", "LTV"]
}
```

**Includes**:
- Revenue leak identification
- Monetization architecture design
- Customer journey mapping
- 30-day implementation roadmap
- Immediate action challenges

---

### `POST /wealth/analyze/funnel`
Conversion funnel analysis

**Request Body**:
```json
{
  "business_context": { ... },
  "funnel_stages": [
    {"name": "Landing Page", "visitors": 10000, "conversions": 2000},
    {"name": "Lead Magnet", "visitors": 2000, "conversions": 800},
    {"name": "Sales Page", "visitors": 800, "conversions": 40, "revenue": 19800}
  ]
}
```

**Provides**:
- Biggest conversion leaks
- Tactical fixes per stage
- Expected revenue impact
- Immediate action items

---

### `POST /wealth/analyze/pricing`
Pricing strategy evaluation

**Request Body**:
```json
{
  "product_type": "course",
  "current_price": 497,
  "cost_to_deliver": 50,
  "monthly_customers": 30,
  "market_position": "mid-market"
}
```

**Market Positions**: `budget`, `mid-market`, `premium`, `luxury`

**Provides**:
- Market-aligned pricing recommendations
- Tiered pricing strategy
- Pricing experiments to run

---

### `POST /wealth/analyze/projections`
Revenue projections

**Request Body**:
```json
{
  "current_monthly_revenue": 10000,
  "current_audience_size": 50000,
  "monthly_audience_growth": 10,
  "current_conversion_rate": 2,
  "projection_months": 12
}
```

**Provides**:
- Baseline scenario (status quo)
- Optimized scenario (strategic improvements)
- Aggressive scenario (maximum execution)
- Strategic moves to bridge gaps

---

### `POST /wealth/analyze/ltv`
Customer lifetime value calculation

**Request Body**:
```json
{
  "average_order_value": 497,
  "purchase_frequency": 2.5,
  "customer_lifespan": 3,
  "gross_margin": 80
}
```

**Provides**:
- Current LTV analysis
- Optimization levers (AOV, frequency, lifespan)
- Specific tactics per lever
- Backend monetization opportunities

---

### `POST /wealth/analyze/opportunities`
Market opportunity assessment

**Request Body**:
```json
{
  "niche": "SaaS founders",
  "audience_size": 50000,
  "engagement": "high",
  "current_revenue": 15000,
  "potential_revenue_streams": [
    "courses", "coaching", "software", "membership"
  ]
}
```

**Engagement Levels**: `low`, `medium`, `high`

**Provides**:
- Ranked revenue stream opportunities
- Revenue potential estimates
- Prioritization by ease, speed, scale

---

## Gemini Ingestion Layer Agent

> Infrastructure analysis and compliance validation

### Base Path: `/gemini`

---

### `POST /gemini/analyze/full`
Comprehensive pre-production analysis

**Request Body**:
```json
{
  "system_context": {
    "architecture_docs": "# Architecture...",
    "k8s_manifests": "apiVersion: batch/v1...",
    "source_config": [...],
    "monthly_cost_budget": 77,
    "runtime_target_minutes": 45,
    "additional_context": "..."
  },
  "focus_sections": ["Performance", "Compliance", "Cost"],
  "target_confidence": 60
}
```

**Analyzes** (11 sections):
1. Architecture & Design
2. Performance & Scalability
3. Ethical Compliance Model
4. Quality Metrics & Gates
5. Multi-Source Coverage
6. Tier Classification Metrics
7. Cost Model & Optimization
8. Integration Points
9. AM Briefing Delivery Effectiveness
10. Failure Modes & Resilience
11. Recommendations (Critical → High → Medium → Low)

**Each section includes**:
- Confidence score (0-100%)
- Evidence citations
- Risk identification
- Actionable recommendations

---

### `POST /gemini/analyze/costs`
GKE cost projections and optimization

**Request Body**:
```json
{
  "daily_runtime_minutes": 45,
  "container_count": 4,
  "cpu_cores_per_container": 2,
  "memory_gb_per_container": 4,
  "storage_gb": 100,
  "monthly_egress_gb": 50,
  "use_preemptible": false
}
```

**Provides**:
- Monthly cost breakdown (compute, storage, egress)
- Comparison to $77 budget target
- Scaling scenarios (2x, 10x)
- Cost optimization recommendations
- Preemptible vs. standard analysis

---

### `POST /gemini/analyze/runtime`
Runtime efficiency and bottleneck analysis

**Request Body**:
```json
{
  "sources": [
    {"name": "YouTube", "estimated_minutes": 15, "can_parallelize": true},
    {"name": "Twitter", "estimated_minutes": 10, "can_parallelize": true},
    {"name": "Reddit", "estimated_minutes": 20, "can_parallelize": false}
  ],
  "container_count": 4,
  "target_minutes": 45
}
```

**Provides**:
- Projected total runtime
- Is 45-minute target achievable?
- Bottleneck identification
- Parallelization analysis
- Container count optimization

---

### `POST /gemini/analyze/compliance`
Ethical compliance and legal risk assessment

**Request Body**:
```json
{
  "sources": [
    {
      "name": "TechCrunch",
      "type": "web_scraping",
      "robots_txt_check": true,
      "rate_limit_implemented": true,
      "user_agent_transparent": true,
      "tos_reviewed": true
    },
    {
      "name": "Random Blog",
      "type": "web_scraping",
      "robots_txt_check": false,
      "rate_limit_implemented": false,
      "user_agent_transparent": false,
      "tos_reviewed": false
    }
  ]
}
```

**Source Types**: `web_scraping`, `api`, `rss`, `public_dataset`

**Provides**:
- Critical compliance issues (MUST fix)
- High-risk issues (legal exposure)
- Legal risk assessment (DMCA, ToS, IP bans)
- Specific fixes per source
- Overall status (PASS/FAIL/PARTIAL)

---

### `POST /gemini/analyze/coverage`
Multi-source coverage and diversity analysis

**Request Body**:
```json
{
  "sources": [
    {"name": "Tech YouTube", "platform": "youtube", "tier": 1, "estimated_items_per_day": 50},
    {"name": "Twitter Feeds", "platform": "twitter", "tier": 1, "estimated_items_per_day": 200},
    {"name": "News RSS", "platform": "news", "tier": 2, "estimated_items_per_day": 150}
  ],
  "target_daily_items": 1000
}
```

**Platforms**: `youtube`, `twitter`, `news`, `rss`, `api`, `other`

**Provides**:
- Platform diversity assessment
- Coverage gaps (missing platforms)
- Daily volume vs. target
- Underrepresented platforms
- Recommendations for new sources

---

### `POST /gemini/analyze/tiers`
Tier classification and quality distribution

**Request Body**:
```json
{
  "tier_metrics": {
    "tier1_count": 250,
    "tier2_count": 500,
    "tier3_count": 250,
    "tier1_avg_relevance": 85,
    "tier2_avg_relevance": 70,
    "tier3_avg_relevance": 45
  },
  "target_distribution": {
    "tier1_percent": 25,
    "tier2_percent": 50,
    "tier3_percent": 25
  }
}
```

**Provides**:
- Actual vs. target distribution
- Quality assessment per tier
- Tier imbalances
- Reclassification recommendations
- Quality improvement tactics

---

## Response Format

All endpoints return **streaming responses** (Server-Sent Events).

**Python Example**:
```python
import requests

response = requests.post(url, json=data, stream=True)
for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    print(chunk, end="", flush=True)
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/gemini/analyze/costs \
  -H "Content-Type: application/json" \
  -d '{
    "daily_runtime_minutes": 45,
    "container_count": 4,
    "cpu_cores_per_container": 2,
    "memory_gb_per_container": 4,
    "storage_gb": 100,
    "monthly_egress_gb": 50,
    "use_preemptible": false
  }'
```

---

## Error Handling

**HTTP Status Codes**:
- `200 OK`: Successful request
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Analysis failed

**Error Response Format**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Errors**:
- Missing required fields
- Invalid enum values
- Malformed JSON
- Claude API errors

---

## Rate Limiting

No rate limiting in development mode.

For production, implement rate limiting:
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/endpoint")
@app.limit("10/minute")
async def endpoint(...):
    ...
```

---

## Examples

See comprehensive examples:
- **TypeScript**: `docs/examples/typescript-example.ts`
- **Python (Wealth)**: `docs/examples/python-api-example.py`
- **Python (Gemini)**: `docs/examples/gemini-api-examples.py`

---

## Interactive API Docs

FastAPI provides auto-generated interactive documentation:

**Swagger UI**: http://localhost:8000/docs
**ReDoc**: http://localhost:8000/redoc

---

## Agent Comparison

| Feature | Wealth Acceleration | Gemini Ingestion |
|---------|---------------------|------------------|
| **Domain** | Revenue optimization | Infrastructure analysis |
| **Endpoints** | 7 endpoints | 6 endpoints |
| **Use Case** | Monetization strategy | Pre-prod evaluation |
| **Output** | Executive summary + challenge | Technical report + risks |
| **Confidence** | Action-oriented | Evidence-based (≥60%) |
| **Tools** | 5 monetization tools | 5 infrastructure tools |

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check examples in `/docs/examples`
- Review this API reference

---

**Last Updated**: 2025-11-08
**API Version**: 2.0.0 (Multi-Agent)
