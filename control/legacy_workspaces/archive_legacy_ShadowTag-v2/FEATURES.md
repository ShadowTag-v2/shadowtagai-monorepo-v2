# AI You Ingestion Service - Feature Overview

## Version 0.2.0 - Gemini Ingestion Layer

### Core Architecture

**Type**: GKE CronJob Multi-Container Intelligence Collection Pipeline
**Runtime**: ~45 minutes/night (automated ingestion)
**Monthly Cost**: ~$77 operational
**Deployment**: Cloud Run serverless with Cloud Scheduler automation

### Key Metrics & Quality Gates

#### Daily Performance Metrics
- **Items/Day**: Target 500+ across all sources
- **Source Diversity**: 9+ active sources
- **Cost/Item**: $0.005 - $0.01 per item ingested
- **Quality Scores**:
  - Relevance: ≥85% (AI/ML topic matching)
  - Timeliness: ≥70% (content <30 days old)
  - Completeness: ≥90% (all required fields populated)

#### Integration Model
- **Position**: Foundational layer (called BY services in 4 namespaces)
- **Consumers**: Search, Analysis, Briefing, Recommendation services
- **Data Flow**: Ingestion → BigQuery → Downstream Services

### Ethical Compliance Model

#### robots.txt Compliance
- **Implementation**: `app/utils/ethical_crawler.py`
- Respects all robots.txt directives
- Cached parsers (1-hour TTL)
- Fail-open policy (allows crawling if robots.txt unavailable)
- Full transparency logging

#### Rate Limiting
- **Per-Domain Delays**: Configured via robots.txt `Crawl-Delay`
- **Default Delay**: 1.0 seconds between requests
- **Exponential Backoff**: 2^n seconds on retries
- **Max Retries**: 3 attempts per URL

#### Transparency
- All crawl activity logged to structured JSON
- Audit trail includes:
  - URL, source type, robots.txt status
  - Success/failure, items extracted
  - Error details for failed requests
- User-Agent disclosure: `AIYouBot/1.0 (AI/MLOps Research; +URL)`

### Multi-Source Coverage Analysis

#### Tier 1 Sources (Premium - 100% Weight)
1. **arXiv Papers**
   - Categories: cs.AI, cs.LG, cs.CL, cs.CV, cs.NE, stat.ML
   - Target: 100+ papers/day
   - Full text extraction: Optional PDF parsing

2. **GitHub (Verified Orgs)**
   - Stars ≥10,000
   - Flattened code representation
   - Metadata: stars, forks, topics, language

#### Tier 2 Sources (Standard - 60% Weight)
3. **GitHub (General)**
   - Stars 1,000-10,000
   - Trending AI/ML repos
   - Code flattening with size limits

4. **HuggingFace Hub**
   - Models, datasets, spaces
   - Downloads ≥10,000 promoted to Tier 1
   - Model cards and documentation

5. **PyPI Packages**
   - Curated AI/ML packages
   - TensorFlow, PyTorch, scikit-learn, etc.
   - Version tracking

6. **Papers with Code**
   - SOTA benchmarks
   - Implementation links
   - Task-based organization

7. **Tech Blogs**
   - OpenAI, Anthropic, Google AI, Meta AI
   - DeepMind, Hugging Face, Cohere, Stability AI
   - Latest research announcements

#### Tier 3 Sources (Exploratory - 30% Weight)
8. **News RSS Feeds**
   - MIT Tech Review, VentureBeat, The Verge
   - TechCrunch, Ars Technica, IEEE Spectrum
   - Ethical crawling with robots.txt

9. **YouTube Videos**
   - Two Minute Papers, 3Blue1Brown, Lex Fridman
   - AI Coffee Break, Computerphile
   - Educational AI/ML content

10. **Twitter/X** (Optional)
    - AI researchers: @AndrewYNg, @ylecun, @karpathy
    - Organizations: @AnthropicAI, @OpenAI, @GoogleAI
    - Hashtags: #MachineLearning, #MLOps, #LLM

### Tier Classification Metrics

**Target Distribution**:
- Tier 1: ≥40% (high-value authoritative sources)
- Tier 2: ≥35% (quality community sources)
- Tier 3: ≤25% (exploratory/social sources)

**Dynamic Promotion**:
- GitHub repos with 10k+ stars → Tier 1
- HuggingFace models with 100k+ downloads → Tier 1
- Content quality signals can override base tier

### AM Briefing Delivery Effectiveness

#### Daily Intelligence Summary
- **Generation Time**: 6:00 AM daily
- **Delivery Format**: JSON API + formatted text
- **Content Sections**:
  1. Metrics summary (yesterday's stats)
  2. Top 5 research papers
  3. Top 5 trending repositories
  4. Top 5 models/tools
  5. Top 10 important news items

#### Quality Criteria
- **Freshness**: All content <24 hours old
- **Relevance**: AI/ML focused filtering
- **Actionability**: Direct links and summaries
- **Completeness**: All sections populated

#### Delivery Endpoints
- **GET /briefing?format=json**: Structured data
- **GET /briefing?format=text**: Human-readable format
- **Integration**: Callable by email/Slack delivery services

### Unique Features

#### Code Flattening (GitHub)
- Clones repositories (shallow, depth=1)
- Extracts all supported code files
- Creates searchable text representation:
  ```
  ================================================================================
  FILE: src/main.py
  ================================================================================
  [code content]
  ```
- Size limits: 500MB repo max, 10MB file max
- Truncation: 5MB max flattened output per repo

#### Ethical Crawling
- robots.txt compliance across all sources
- Rate limiting per domain
- Transparent user-agent
- Respect for Crawl-Delay directives
- Full audit logging

#### Tier Classification
- Three-tier quality system
- Dynamic promotion based on metrics
- Weighted scoring for ranking
- Distribution tracking and reporting

### Cost Model

**Monthly Operational**: ~$77

Breakdown:
- Cloud Run: ~$30 (compute + memory)
- BigQuery: ~$25 (storage + queries)
- Cloud Storage: ~$5 (artifacts)
- Cloud Scheduler: ~$2 (job triggers)
- Secret Manager: ~$5 (API key storage)
- Networking: ~$10 (egress)

**Cost per Item**: $0.005 - $0.01 (based on 500-1000 items/day)

**Scaling**:
- Linear up to 5,000 items/day (~$150/month)
- Batch optimization reduces per-item cost at scale

### Quality Focus

#### Relevance Scoring
- Topic matching against AI/ML keywords
- Tag/category verification
- Source reputation weighting
- Target: ≥85% relevance

#### Timeliness Scoring
- Publication date tracking
- Update frequency monitoring
- Freshness weighting (30-day window)
- Target: ≥70% recent content

#### Completeness Scoring
- Required field validation
- Content length checking
- Metadata completeness
- Target: ≥90% complete records

#### Overall Quality Score
- Composite of relevance, timeliness, completeness
- Weighted average with tier classification
- Minimum threshold: ≥75% for production
- Reported via /metrics endpoint

### API Endpoints

**Monitoring**:
- `GET /health` - Service health check
- `GET /metrics` - Comprehensive metrics dashboard
- `GET /briefing` - AM intelligence briefing

**Ingestion (Background Tasks)**:
- `POST /ingest/github` - GitHub repositories
- `POST /ingest/arxiv` - arXiv papers
- `POST /ingest/huggingface` - HuggingFace models
- `POST /ingest/paperswithcode` - SOTA papers
- `POST /ingest/pypi` - Python packages
- `POST /ingest/techblogs` - Tech blog posts
- `POST /ingest/news` - News RSS feeds
- `POST /ingest/youtube` - YouTube videos
- `POST /ingest/twitter` - Twitter/X posts
- `POST /ingest/full` - All sources (full sync)

### Data Schema

#### BigQuery Tables

**github_repos**:
- repo_id, full_name, url, description
- stars, forks, language, topics
- **flattened_code** (searchable text)
- file_count, total_size
- last_updated, ingested_at

**arxiv_papers**:
- arxiv_id, title, authors[], abstract
- categories[], published_date, updated_date
- pdf_url, full_text (optional)
- citations (future), ingested_at

**huggingface_models**:
- model_id, name, author, description
- downloads, likes, tags[]
- pipeline_tag, library_name
- model_card, ingested_at

**tech_sources** (unified):
- source_id, source_type, title, url
- content, metadata (JSON)
- ingested_at

### Deployment & Operations

#### Infrastructure as Code
- **deploy.sh**: Idempotent deployment script
- Versioned Docker images (git commit hash)
- Environment-based configuration
- Automatic rollback on failure

#### Scheduling
- **Daily 2 AM**: GitHub repos
- **Daily 3 AM**: arXiv papers
- **Daily 4 AM**: HuggingFace models
- **Daily 5 AM**: News, YouTube, Twitter
- **Daily 6 AM**: AM briefing generation
- **Weekly Sunday 1 AM**: Full sync

#### Monitoring & Logging
- Structured JSON logs (Google Cloud Logging)
- Metrics tracked: items/day, cost/item, quality scores
- Alerts: Ingestion failures, cost overruns, quality drops
- Dashboards: Cloud Monitoring integration

### Pre-Production Confidence

**Current Status**: ≥60% confidence (specs-only analysis)

**Path to Production** (Target: ≥85% confidence):
1. Deploy to dev environment
2. Run test ingestion across all sources
3. Validate data quality and completeness
4. Monitor costs and performance
5. Review ethical compliance logs
6. Tune rate limits and quotas
7. Load test with Cloud Run scaling
8. Gradual rollout: dev → staging → prod

### Next Steps

1. **Secret Configuration**:
   ```bash
   echo 'YOUR_TOKEN' | gcloud secrets versions add github-token --data-file=-
   echo 'YOUR_TOKEN' | gcloud secrets versions add huggingface-token --data-file=-
   echo 'YOUR_KEY' | gcloud secrets versions add youtube-api-key --data-file=-
   echo 'YOUR_TOKEN' | gcloud secrets versions add twitter-bearer-token --data-file=-
   ```

2. **Deploy to GCP**:
   ```bash
   export GCP_PROJECT_ID=your-project-id
   ./deploy.sh
   ```

3. **Trigger Test Run**:
   ```bash
   curl -X POST "$SERVICE_URL/ingest/full" \
     -H "Authorization: Bearer $(gcloud auth print-identity-token)"
   ```

4. **Monitor Results**:
   ```bash
   curl "$SERVICE_URL/metrics"
   curl "$SERVICE_URL/briefing"
   ```

### Success Criteria

- ✅ 9+ sources ingesting daily
- ✅ 500+ items/day total volume
- ✅ ≥85% relevance score
- ✅ ≥70% timeliness score
- ✅ ≥90% completeness score
- ✅ $77/month operational cost
- ✅ Zero robots.txt violations
- ✅ Successful AM briefing generation
- ✅ <1% error rate on ingestion
- ✅ Tier distribution: 40/35/25 (Tier 1/2/3)

---

**Document Version**: 0.2.0
**Last Updated**: 2025-11-15
**Status**: Ready for deployment
