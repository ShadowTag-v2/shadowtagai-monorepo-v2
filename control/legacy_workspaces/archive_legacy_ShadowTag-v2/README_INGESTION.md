# Gemini Ingestion Layer Analysis & Intelligence Collection

## Overview

This FastAPI service now includes comprehensive **Gemini AI-powered analysis** capabilities and **Intelligence Collection Pipeline** management for the PNKLN Core Stack™. The service integrates:

1. **Workflow Automation** - Multi-step workflow execution with user interaction
2. **Gemini AI Analysis** - AI-powered system analysis using Google's Gemini 2.0
3. **Ingestion Layer Management** - Multi-source intelligence collection and monitoring
4. **Ethical Compliance** - Automated compliance checking and enforcement
5. **Quality Gates** - Real-time quality metrics and thresholds

## Key Features

### 🤖 Gemini AI Analysis

Powered by **Gemini 2.0 Pro**, the service provides:

- **Ingestion Layer Analysis**: Comprehensive analysis of GKE CronJob Multi-Container architecture
- **Compliance Auditing**: Ethical compliance checks (robots.txt, rate limiting, ToS)
- **Coverage Analysis**: Multi-source diversity and gap identification
- **System Comparison**: Compare different systems (e.g., Judge #6 vs Ingestion Layer)
- **Custom Analysis**: Flexible analysis for any system component

**Key Metrics Analyzed:**
- Runtime efficiency (~45 min/night target)
- Quality gates (items/day, sources, cost/item, scores)
- Monthly operational cost (~$77 target)
- Tier classification (1/2/3 distribution)
- AM Briefing delivery effectiveness

### 📊 Ingestion Layer Management

**Multi-Source Intelligence Collection:**
- YouTube, Twitter, News, RSS, Web, API sources
- Tier classification (Tier 1/2/3 for quality stratification)
- Real-time metrics and monitoring
- Ethical crawling with rate limiting

**Quality Gates:**
- Relevance Score (0-1)
- Timeliness Score (0-1)
- Completeness Score (0-1)
- Configurable thresholds

**Cost Tracking:**
- Per-item cost tracking
- Monthly cost projections
- Budget optimization recommendations

### ✅ Ethical Compliance

Automated compliance checking:
- **robots.txt** adherence
- **Rate limiting** enforcement
- **Terms of Service** compliance
- **Transparency scoring**

### 🎯 Quality & Performance

**Confidence Thresholds:**
- High: ≥ 70% (production with telemetry)
- Medium: 60-70% (pre-production, specs-only)
- Low: < 60%

**Integration:**
- Calls services in 4 namespaces
- GKE CronJob deployment
- Multi-container orchestration

## New API Endpoints

### Gemini Analysis

```
GET  /api/gemini/status                    - Check Gemini availability
POST /api/gemini/analyze                   - Perform AI analysis
POST /api/gemini/compare                   - Compare two systems
POST /api/gemini/analyze/ingestion-layer   - Specialized ingestion analysis
```

### Ingestion Management

```
# Data Sources
POST   /api/ingestion/sources              - Create data source
GET    /api/ingestion/sources              - List sources (filter by type/tier)
GET    /api/ingestion/sources/{id}         - Get source details
DELETE /api/ingestion/sources/{id}         - Delete source

# Ingestion Jobs
POST   /api/ingestion/jobs/start           - Start ingestion job
GET    /api/ingestion/jobs/{id}            - Get job status
GET    /api/ingestion/jobs                 - List jobs

# Metrics & Analysis
GET    /api/ingestion/metrics/latest       - Latest metrics
GET    /api/ingestion/metrics/summary      - Summary (past N days)
GET    /api/ingestion/coverage/analyze     - Multi-source coverage
GET    /api/ingestion/tiers/metrics        - Tier distribution

# Compliance
GET    /api/ingestion/compliance/check/{source_id}  - Check source compliance
GET    /api/ingestion/compliance/summary            - Overall compliance

# Briefings
GET    /api/ingestion/briefings/effectiveness       - AM briefing metrics
```

## New Workflows

### 1. Multi-Source Collection
Configure and start multi-source intelligence collection with quality gates.

**Actions:**
1. Ask for collection name
2. Specify target sources
3. Capture start time
4. Create collection log note

### 2. Quality Gate Check
Run quality gate checks on ingested data and record results.

**Actions:**
1. Capture timestamp
2. Record items count
3. Record source count
4. Input quality scores
5. Append to quality gate log

## Usage Examples

### Gemini Analysis Example

**Analyze Ingestion Layer:**

```bash
curl -X POST "http://localhost:8000/api/gemini/analyze/ingestion-layer" \
  -H "Content-Type: application/json" \
  -d '{
    "architecture_specs": "GKE CronJob Multi-Container\n- 3 containers per job\n- Nightly execution at 03:00 UTC\n- Resource limits: 2 CPU, 4GB RAM",
    "metrics_data": {
      "daily_items": 1200,
      "active_sources": 8,
      "monthly_cost": 75.50,
      "runtime_minutes": 42,
      "relevance_score": 0.87,
      "timeliness_score": 0.92,
      "completeness_score": 0.89
    },
    "documentation": "Ethical crawling system with robots.txt compliance..."
  }'
```

**Response:**
```json
{
  "analysis_id": "abc-123",
  "overall_confidence": 0.75,
  "confidence_level": "high",
  "executive_summary": "The Gemini Ingestion Layer demonstrates strong performance...",
  "key_findings": [
    "Runtime of 42min is 7% better than target",
    "All quality gates exceeded thresholds",
    "Tier 1 sources at 25% (above 20% target)"
  ],
  "recommendations": [
    "Consider adding 2 more Twitter sources for diversity",
    "Implement caching to reduce cost further"
  ],
  "risks": [
    "Heavy reliance on Twitter API (rate limit risk)"
  ]
}
```

### Create Data Source

```bash
curl -X POST "http://localhost:8000/api/ingestion/sources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech News RSS",
    "source_type": "rss",
    "tier": "tier_2",
    "url": "https://technews.example.com/rss",
    "rate_limit": 60,
    "cost_per_item": 0.0005
  }'
```

### Start Ingestion Job

```bash
curl -X POST "http://localhost:8000/api/ingestion/jobs/start" \
  -H "Content-Type: application/json" \
  -d '{
    "job_name": "Morning Collection",
    "source_ids": ["source-1", "source-2", "source-3"]
  }'
```

### Check Coverage

```bash
curl "http://localhost:8000/api/ingestion/coverage/analyze"
```

**Response:**
```json
{
  "coverage": {
    "total_sources": 10,
    "active_sources": 8,
    "sources_by_type": {
      "youtube": 2,
      "twitter": 2,
      "rss": 3,
      "news": 1
    },
    "sources_by_tier": {
      "tier_1": 2,
      "tier_2": 4,
      "tier_3": 2
    },
    "coverage_diversity_score": 0.57,
    "tier_1_percentage": 25.0,
    "coverage_gaps": [
      "No API sources configured",
      "No web sources configured"
    ]
  },
  "recommendations": [
    "Add API sources for structured data",
    "Increase Tier 1 sources for higher quality"
  ]
}
```

### Compare Systems (Judge #6 vs Ingestion Layer)

```bash
curl -X POST "http://localhost:8000/api/gemini/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "system_a_name": "Judge #6",
    "system_a_specs": "Hybrid Gemini+PyTorch enforcement system...",
    "system_b_name": "Ingestion Layer",
    "system_b_specs": "GKE CronJob intelligence collection...",
    "comparison_aspects": [
      "Architecture",
      "Key Metrics",
      "Integration",
      "Cost Model"
    ]
  }'
```

## Configuration

Add to `.env`:

```bash
# Gemini AI
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.1-flash-exp
GEMINI_CONFIDENCE_THRESHOLD=0.6

# Ingestion Targets
INGESTION_RUNTIME_TARGET_MINUTES=45.0
INGESTION_MONTHLY_COST_TARGET=77.0
INGESTION_ITEMS_PER_DAY_TARGET=1000
INGESTION_MIN_SOURCES=5
INGESTION_TIER_1_PERCENTAGE_TARGET=20.0

# Quality Gates
QUALITY_GATE_RELEVANCE_THRESHOLD=0.80
QUALITY_GATE_TIMELINESS_THRESHOLD=0.85
QUALITY_GATE_COMPLETENESS_THRESHOLD=0.85

# Ethical Compliance
COMPLIANCE_RESPECT_ROBOTS_TXT=True
COMPLIANCE_DEFAULT_RATE_LIMIT=100
COMPLIANCE_USER_AGENT=PNKLN-Ingestion/1.0
```

## Architecture Comparison

| Aspect | Judge #6 | Ingestion Layer |
|--------|----------|-----------------|
| **Architecture** | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container |
| **Key Metrics** | p99 ≤90ms latency, 98% coverage | ~45 min/night runtime, items/day, sources, cost/item |
| **Integration** | Calls services in 4 namespaces | Called by services in 4 namespaces |
| **Unique Features** | ATP 5-19, JR Validation | Ethical Crawling, Tier Classification |
| **Cost Model** | API calls per validation | Monthly operational ~$77 |
| **Quality Focus** | FP/FN rates | Relevance, Timeliness, Completeness |

## Data Tier Classification

- **Tier 1**: High-value, verified sources (e.g., verified Twitter accounts, official YouTube channels)
- **Tier 2**: Medium-value, generally reliable (e.g., established news sites, curated RSS feeds)
- **Tier 3**: Low-value, unverified (e.g., general web crawl, user-generated content)

**Target Distribution:**
- Tier 1: ≥20%
- Tier 2: 40-60%
- Tier 3: ≤40%

## Production Readiness

**Pre-Production Checklist:**
- ✅ Gemini AI integration
- ✅ Multi-source coverage
- ✅ Ethical compliance framework
- ✅ Quality gates implementation
- ✅ Tier classification
- ✅ Cost tracking
- ✅ Metrics collection
- ⚠️  Database persistence (currently in-memory)
- ⚠️  Production telemetry (confidence threshold 60%)

**To Deploy:**
1. Configure Gemini API key
2. Set up GKE CronJob schedule
3. Configure data sources
4. Set quality gate thresholds
5. Enable production telemetry
6. Switch to database backend

## Integration with PNKLN Core Stack™

This service integrates with:
- **Judge #6**: Enforcement and validation downstream
- **4 Namespaces**: Cross-namespace service calls
- **AM Briefing**: Morning intelligence delivery
- **GKE**: Kubernetes orchestration

## License & Attribution

Part of the PNKLN Core Stack™ for intelligence collection and analysis.
