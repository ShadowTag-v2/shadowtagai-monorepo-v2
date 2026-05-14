<<<<<<< HEAD

# Gemini Ingestion Layer Architecture

## Overview

The **Gemini Ingestion Layer** is a foundational component of the SHADOWTAGAI Core Stack™, responsible for collecting, processing, and classifying intelligence from multiple sources. It operates as a scheduled GKE CronJob that runs nightly, gathering data for downstream analysis and briefing generation.

## System Architecture

### High-Level Design

```

┌─────────────────────────────────────────────────────────────────┐
│                    SHADOWTAGAI Core Stack™                            │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │  Namespace 1 │    │  Namespace 2 │    │  Namespace 3 │    │
│  │   Services   │    │   Services   │    │   Services   │    │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│         │                   │                    │             │
│         └───────────────────┴────────────────────┘             │
│                             │                                  │
│                             ▼                                  │
│         ┌───────────────────────────────────────┐             │
│         │   Gemini Ingestion Layer (GKE)       │             │
│         │                                       │             │
│         │  ┌─────────────────────────────────┐ │             │
│         │  │   CronJob Scheduler             │ │             │
│         │  │   (Nightly: ~45 min runtime)    │ │             │
│         │  └────────────┬────────────────────┘ │             │
│         │               │                       │             │
│         │  ┌────────────▼───────────────────┐  │             │
│         │  │  Multi-Container Orchestration │  │             │
│         │  │                                 │  │             │
│         │  │  ┌──────────┐  ┌─────────────┐ │  │             │
│         │  │  │  YouTube │  │   Twitter   │ │  │             │
│         │  │  │ Collector│  │  Collector  │ │  │             │
│         │  │  └──────────┘  └─────────────┘ │  │             │
│         │  │  ┌──────────┐  ┌─────────────┐ │  │             │
│         │  │  │   News   │  │     RSS     │ │  │             │
│         │  │  │ Collector│  │  Collector  │ │  │             │
│         │  │  └──────────┘  └─────────────┘ │  │             │
│         │  │  ┌──────────┐  ┌─────────────┐ │  │             │
│         │  │  │   Web    │  │     API     │ │  │             │
│         │  │  │  Scraper │  │  Integrator │ │  │             │
│         │  │  └──────────┘  └─────────────┘ │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Tier Classification Engine    │  │             │
│         │  │   (Tier 1/2/3 Assignment)       │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Ethical Compliance Validator  │  │             │
│         │  │   (robots.txt, rate limits)     │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Data Quality & Scoring        │  │             │
│         │  │   (Relevance, Completeness)     │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Storage & Handoff             │  │             │
│         │  │   (GCS Bucket / Database)       │  │             │
│         │  └─────────────────────────────────┘  │             │
│         └───────────────────────────────────────┘             │
│                             │                                  │
│                             ▼                                  │
│         ┌───────────────────────────────────────┐             │
│         │      Judge #6 Validation Layer        │             │
│         │      AM Briefing Generator            │             │
│         │      Other SHADOWTAGAI Services             │             │
│         └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘

```

### Container Architecture

The ingestion layer uses a **multi-container pod** design in GKE for parallel processing:


1. **Coordinator Container**: Orchestrates the ingestion workflow

2. **Source-Specific Collectors**: Parallel containers for each data source

3. **Processing Containers**: Tier classification, quality scoring

4. **Compliance Container**: Ethical validation and rate limiting

5. **Storage Container**: Data persistence and handoff management

### Technology Stack


- **Orchestration**: Google Kubernetes Engine (GKE)

- **Scheduling**: Kubernetes CronJob

- **Language**: Python 3.11+

- **Framework**: FastAPI for API endpoints

- **AI/ML**: Gemini 2.0 Pro (analysis), PyTorch (classification)

- **Storage**: Google Cloud Storage (GCS), PostgreSQL

- **Monitoring**: Prometheus, Grafana

- **Logging**: Cloud Logging (Stackdriver)

## Key Components

### 1. CronJob Scheduler

**Schedule**: Nightly execution (configurable, default: 2:00 AM UTC)
**Target Runtime**: ≤45 minutes
**Retry Policy**: 3 attempts with exponential backoff

**Configuration**:

```yaml
schedule: "0 2 * * *"  # 2:00 AM daily
concurrencyPolicy: Forbid
successfulJobsHistoryLimit: 3
failedJobsHistoryLimit: 1

```

### 2. Multi-Source Collectors

#### YouTube Collector


- **API**: YouTube Data API v3

- **Targets**: Specified channels, playlists

- **Data**: Video metadata, transcripts, comments

- **Rate Limit**: 10,000 quota units/day

- **Cost**: Included in GCP quota

#### Twitter/X Collector


- **API**: Twitter API v2 (Essential tier)

- **Targets**: Keywords, hashtags, accounts

- **Data**: Tweets, threads, engagement metrics

- **Rate Limit**: 500K tweets/month

- **Cost**: $100/month (external to $77 budget)

#### News Collector


- **API**: NewsAPI, custom RSS feeds

- **Targets**: Configured news outlets

- **Data**: Headlines, articles, metadata

- **Rate Limit**: 1000 requests/day (NewsAPI)

- **Cost**: Free tier

#### RSS Collector


- **Protocol**: RSS/Atom feed parsing

- **Targets**: Custom feed list

- **Data**: Feed items, full content

- **Rate Limit**: Per-feed robots.txt

- **Cost**: Negligible (bandwidth only)

#### Web Scraper


- **Library**: BeautifulSoup4, Scrapy

- **Targets**: Whitelisted domains

- **Data**: Structured content extraction

- **Rate Limit**: Configurable per-domain

- **Cost**: Compute + egress

#### API Integrator


- **Purpose**: Custom API integrations

- **Targets**: Proprietary data sources

- **Data**: Structured JSON responses

- **Rate Limit**: Per-API contract

- **Cost**: Variable

### 3. Tier Classification Engine

Classifies ingested items into three tiers based on:

- **Source Authority**: Reputation and reliability scores

- **Content Relevance**: Keyword matching, topic modeling

- **Timeliness**: Recency and trend alignment

- **Engagement**: Social signals, virality metrics

**Classification Model**:

- **Algorithm**: Ensemble (rules + ML)

- **Training**: Historical performance data

- **Features**: 20+ signals

- **Accuracy Target**: ≥85%

**Tier Definitions**:

- **Tier 1** (Priority): High-authority, time-critical, high-relevance

- **Tier 2** (Standard): Moderate value, supplementary intelligence

- **Tier 3** (Background): Low-priority, contextual information

### 4. Ethical Compliance Validator

Ensures responsible data collection:

**robots.txt Compliance**:

- Fetches and caches robots.txt for all domains

- Validates crawl permissions before requests

- Respects `Crawl-delay` directives

**Rate Limiting**:

- Per-domain request throttling

- Exponential backoff on errors

- Distributed rate limiting across containers

**Transparency**:

- Custom User-Agent identification

- Contact information in headers

- Purpose declaration

**Example User-Agent**:

```

SHADOWTAGAI-Ingestion-Bot/1.0 (+https://shadowtagai.ai/bot; contact@shadowtagai.ai)

```

### 5. Data Quality & Scoring

Assesses ingested data quality:

**Relevance Scoring** (0-100):

- Keyword match strength

- Topic alignment with objectives

- Source reputation weight

**Completeness Checks**:

- Required fields present

- Content length thresholds

- Metadata availability

**Timeliness Scoring**:

- Publication date recency

- Trending topic alignment

- Event correlation

**Quality Gates**:

- Minimum relevance: 40/100

- Minimum completeness: 80%

- Maximum age: 7 days (Tier 1), 30 days (Tier 2/3)

### 6. Storage & Handoff

**Primary Storage**: Google Cloud Storage (GCS)

- **Bucket**: `shadowtagai-ingestion-data`

- **Structure**: `/YYYY/MM/DD/tier-{1|2|3}/`

- **Format**: JSONL (JSON Lines)

- **Retention**: 90 days (Tier 1), 30 days (Tier 2/3)

**Metadata Storage**: PostgreSQL

- **Table**: `ingested_items`

- **Indexes**: Source, tier, timestamp, relevance

- **Retention**: Permanent (metadata only)

**Handoff Mechanism**:

- GCS bucket notifications trigger downstream processing

- REST API endpoints for pull-based access

- Event bus (Pub/Sub) for real-time consumers

## Integration Patterns

### Upstream (Invocation)

The ingestion layer is invoked by:


1. **Namespace 1**: Briefing scheduler (triggers AM briefing ingestion)

2. **Namespace 2**: On-demand intelligence requests

3. **Namespace 3**: Event-driven collection (breaking news)

4. **Namespace 4**: Research batch jobs

**Invocation Methods**:

- CronJob schedule (default)

- REST API trigger endpoint

- Pub/Sub event subscription

- kubectl job trigger

### Downstream (Consumption)

Ingested data is consumed by:


1. **Judge #6**: Validation and quality filtering

2. **AM Briefing Generator**: Morning summary creation

3. **Analytics Services**: Trend analysis, insights

4. **Research Tools**: Ad-hoc query interfaces

**Consumption Methods**:

- GCS bucket access (batch)

- REST API queries (on-demand)

- Pub/Sub subscriptions (streaming)

- PostgreSQL queries (metadata search)

## Performance Metrics

### Target SLAs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Runtime | ≤45 minutes | CronJob duration |
| Daily Items | 1000-5000 | Count in GCS/DB |
| Active Sources | ≥6 | Successful collectors |
| Cost/Item | ≤$0.015 | Monthly cost / items |
| Relevance (Avg) | ≥60/100 | Quality scoring |
| Tier 1 % | 10-20% | Classification distribution |
| Uptime | ≥99% | Successful runs/total |
| Error Rate | ≤1% | Failed items/total |

### Monitoring

**Key Dashboards**:

- Runtime trends (45-min threshold)

- Items ingested by source

- Tier distribution over time

- Cost tracking ($77/month budget)

- Quality scores by tier

- Failure rates by collector

**Alerts**:

- Runtime exceeds 50 minutes

- Daily items below 500

- Cost exceeds $3/day ($90/month)

- Source failure (3+ consecutive runs)

- Ethical violation detected

- Quality score drops below 50

## Cost Model

**Monthly Budget: ~$77**

**Cost Breakdown**:

- **GKE Compute**: $40/month (1 preemptible node, ~45 min/day)

- **GCS Storage**: $5/month (50GB average)

- **API Calls**: $20/month (NewsAPI, misc)

- **Network Egress**: $7/month (data transfer)

- **PostgreSQL**: $5/month (Cloud SQL micro instance)

**Cost Optimization**:

- Use preemptible nodes for CronJob (60-90% savings)

- Aggressive data retention policies

- Batch API calls to minimize quota usage

- Regional egress to minimize transfer costs

**Sensitivity**:

- 2x items → +$20/month (storage, compute)

- New paid API → varies ($10-100/month)

- Increased runtime → +$10/month per 15 minutes

## Operational Resilience

### Failure Handling

**Source Outages**:

- Retry with exponential backoff (2s, 4s, 8s, 16s)

- Skip and alert if 4 retries fail

- Continue with other sources

- Daily summary includes missing sources

**Rate Limiting**:

- Detect 429 responses

- Adaptive throttling (reduce rate by 50%)

- Resume after Retry-After header delay

- Spread requests across CronJob window

**Data Quality Issues**:

- Flag low-quality items (don't block)

- Alert if >20% items below quality threshold

- Manual review queue for edge cases

**Infrastructure Failures**:

- GKE pod restart (automatic)

- CronJob retry (3 attempts)

- Circuit breaker for persistent failures

- Fallback to backup sources

### Disaster Recovery

**Backup Strategy**:

- GCS bucket versioning enabled

- Daily PostgreSQL backups (7-day retention)

- Configuration versioned in Git

- Secrets in Google Secret Manager

**Recovery Procedures**:

- RTO (Recovery Time Objective): 4 hours

- RPO (Recovery Point Objective): 24 hours

- Runbook: `/docs/runbooks/ingestion-recovery.md`

## Security & Compliance

### Data Privacy


- No PII collection from public sources

- GDPR-compliant data retention

- Right to erasure (manual process)

- Audit logs for all data access

### Authentication & Authorization


- GKE workload identity for GCP services

- API keys stored in Secret Manager

- RBAC for Kubernetes resources

- mTLS for inter-service communication

### Ethical Guidelines


- Respect robots.txt (100% compliance)

- Rate limiting (prevent server overload)

- Transparent identification (User-Agent)

- No circumventing paywalls/protections

- Compliance with terms of service

## Deployment

See [GKE CronJob Configuration](../../k8s/ingestion-cronjob.yaml) for deployment manifests.

**Deployment Steps**:

1. Configure secrets (API keys)

2. Deploy ConfigMaps (source configs)

3. Apply CronJob manifest

4. Verify first run

5. Enable monitoring/alerting

**Configuration Management**:

- Sources: `/config/sources.yaml`

- Tier rules: `/config/tier-classification.yaml`

- Ethical policies: `/config/ethical-crawling.yaml`

- Quality gates: `/config/quality-gates.yaml`

## API Endpoints

See [FastAPI Integration](../../src/api/ingestion.py) for REST API documentation.

**Key Endpoints**:

- `POST /ingestion/trigger` - Manual CronJob trigger

- `GET /ingestion/status` - Current/last run status

- `GET /ingestion/items` - Query ingested items

- `GET /ingestion/metrics` - Performance metrics

- `POST /ingestion/sources` - Update source configuration

## Future Enhancements


1. **Real-time Streaming**: Continuous ingestion (not just nightly)

2. **ML-Based Tier Classification**: Replace rules with deep learning

3. **Multi-Language Support**: Non-English sources

4. **Source Discovery**: Automatic identification of new sources

5. **Federated Learning**: Privacy-preserving model training

6. **Advanced Deduplication**: Cross-source content matching

7. **Sentiment Analysis**: Emotional tone scoring

8. **Entity Recognition**: Automated tagging of people, places, organizations

## References


- [SHADOWTAGAI Core Stack™ Overview](./shadowtagai-core-stack.md)

- [Ethical Crawling Guidelines](./ethical-crawling.md)

- [Tier Classification Model](./tier-classification.md)

- [Judge #6 Validation Layer](./judge-six.md)

- [GKE CronJob Manifests](../../k8s/ingestion-cronjob.yaml)

- [FastAPI Endpoints](../../src/api/ingestion.py)

## Version History


- **v1.0** (2025-11-07): Initial architecture documentation

- Target runtime: ~45 minutes

- Budget: ~$77/month

- Sources: YouTube, Twitter, News, RSS, Web, APIs
||||||| c348392b7
=======

# Gemini Ingestion Layer Architecture

## Overview

The **Gemini Ingestion Layer** is a foundational component of the PNKLN Core Stack™, responsible for collecting, processing, and classifying intelligence from multiple sources. It operates as a scheduled GKE CronJob that runs nightly, gathering data for downstream analysis and briefing generation.

## System Architecture

### High-Level Design

```

┌─────────────────────────────────────────────────────────────────┐
│                    PNKLN Core Stack™                            │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │  Namespace 1 │    │  Namespace 2 │    │  Namespace 3 │    │
│  │   Services   │    │   Services   │    │   Services   │    │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    │
│         │                   │                    │             │
│         └───────────────────┴────────────────────┘             │
│                             │                                  │
│                             ▼                                  │
│         ┌───────────────────────────────────────┐             │
│         │   Gemini Ingestion Layer (GKE)       │             │
│         │                                       │             │
│         │  ┌─────────────────────────────────┐ │             │
│         │  │   CronJob Scheduler             │ │             │
│         │  │   (Nightly: ~45 min runtime)    │ │             │
│         │  └────────────┬────────────────────┘ │             │
│         │               │                       │             │
│         │  ┌────────────▼───────────────────┐  │             │
│         │  │  Multi-Container Orchestration │  │             │
│         │  │                                 │  │             │
│         │  │  ┌──────────┐  ┌─────────────┐ │  │             │
│         │  │  │  YouTube │  │   Twitter   │ │  │             │
│         │  │  │ Collector│  │  Collector  │ │  │             │
│         │  │  └──────────┘  └─────────────┘ │  │             │
│         │  │  ┌──────────┐  ┌─────────────┐ │  │             │
│         │  │  │   News   │  │     RSS     │ │  │             │
│         │  │  │ Collector│  │  Collector  │ │  │             │
│         │  │  └──────────┘  └─────────────┘ │  │             │
│         │  │  ┌──────────┐  ┌─────────────┐ │  │             │
│         │  │  │   Web    │  │     API     │ │  │             │
│         │  │  │  Scraper │  │  Integrator │ │  │             │
│         │  │  └──────────┘  └─────────────┘ │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Tier Classification Engine    │  │             │
│         │  │   (Tier 1/2/3 Assignment)       │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Ethical Compliance Validator  │  │             │
│         │  │   (robots.txt, rate limits)     │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Data Quality & Scoring        │  │             │
│         │  │   (Relevance, Completeness)     │  │             │
│         │  └─────────────┬───────────────────┘  │             │
│         │                │                       │             │
│         │  ┌─────────────▼───────────────────┐  │             │
│         │  │   Storage & Handoff             │  │             │
│         │  │   (GCS Bucket / Database)       │  │             │
│         │  └─────────────────────────────────┘  │             │
│         └───────────────────────────────────────┘             │
│                             │                                  │
│                             ▼                                  │
│         ┌───────────────────────────────────────┐             │
│         │      Judge #6 Validation Layer        │             │
│         │      AM Briefing Generator            │             │
│         │      Other PNKLN Services             │             │
│         └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘

```

### Container Architecture

The ingestion layer uses a **multi-container pod** design in GKE for parallel processing:


1. **Coordinator Container**: Orchestrates the ingestion workflow

2. **Source-Specific Collectors**: Parallel containers for each data source

3. **Processing Containers**: Tier classification, quality scoring

4. **Compliance Container**: Ethical validation and rate limiting

5. **Storage Container**: Data persistence and handoff management

### Technology Stack


- **Orchestration**: Google Kubernetes Engine (GKE)

- **Scheduling**: Kubernetes CronJob

- **Language**: Python 3.11+

- **Framework**: FastAPI for API endpoints

- **AI/ML**: Gemini 2.0 Pro (analysis), PyTorch (classification)

- **Storage**: Google Cloud Storage (GCS), PostgreSQL

- **Monitoring**: Prometheus, Grafana

- **Logging**: Cloud Logging (Stackdriver)

## Key Components

### 1. CronJob Scheduler

**Schedule**: Nightly execution (configurable, default: 2:00 AM UTC)
**Target Runtime**: ≤45 minutes
**Retry Policy**: 3 attempts with exponential backoff

**Configuration**:

```yaml
schedule: "0 2 * * *"  # 2:00 AM daily
concurrencyPolicy: Forbid
successfulJobsHistoryLimit: 3
failedJobsHistoryLimit: 1

```

### 2. Multi-Source Collectors

#### YouTube Collector


- **API**: YouTube Data API v3

- **Targets**: Specified channels, playlists

- **Data**: Video metadata, transcripts, comments

- **Rate Limit**: 10,000 quota units/day

- **Cost**: Included in GCP quota

#### Twitter/X Collector


- **API**: Twitter API v2 (Essential tier)

- **Targets**: Keywords, hashtags, accounts

- **Data**: Tweets, threads, engagement metrics

- **Rate Limit**: 500K tweets/month

- **Cost**: $100/month (external to $77 budget)

#### News Collector


- **API**: NewsAPI, custom RSS feeds

- **Targets**: Configured news outlets

- **Data**: Headlines, articles, metadata

- **Rate Limit**: 1000 requests/day (NewsAPI)

- **Cost**: Free tier

#### RSS Collector


- **Protocol**: RSS/Atom feed parsing

- **Targets**: Custom feed list

- **Data**: Feed items, full content

- **Rate Limit**: Per-feed robots.txt

- **Cost**: Negligible (bandwidth only)

#### Web Scraper


- **Library**: BeautifulSoup4, Scrapy

- **Targets**: Whitelisted domains

- **Data**: Structured content extraction

- **Rate Limit**: Configurable per-domain

- **Cost**: Compute + egress

#### API Integrator


- **Purpose**: Custom API integrations

- **Targets**: Proprietary data sources

- **Data**: Structured JSON responses

- **Rate Limit**: Per-API contract

- **Cost**: Variable

### 3. Tier Classification Engine

Classifies ingested items into three tiers based on:

- **Source Authority**: Reputation and reliability scores

- **Content Relevance**: Keyword matching, topic modeling

- **Timeliness**: Recency and trend alignment

- **Engagement**: Social signals, virality metrics

**Classification Model**:

- **Algorithm**: Ensemble (rules + ML)

- **Training**: Historical performance data

- **Features**: 20+ signals

- **Accuracy Target**: ≥85%

**Tier Definitions**:

- **Tier 1** (Priority): High-authority, time-critical, high-relevance

- **Tier 2** (Standard): Moderate value, supplementary intelligence

- **Tier 3** (Background): Low-priority, contextual information

### 4. Ethical Compliance Validator

Ensures responsible data collection:

**robots.txt Compliance**:

- Fetches and caches robots.txt for all domains

- Validates crawl permissions before requests

- Respects `Crawl-delay` directives

**Rate Limiting**:

- Per-domain request throttling

- Exponential backoff on errors

- Distributed rate limiting across containers

**Transparency**:

- Custom User-Agent identification

- Contact information in headers

- Purpose declaration

**Example User-Agent**:

```

PNKLN-Ingestion-Bot/1.0 (+https://pnkln.ai/bot; contact@pnkln.ai)

```

### 5. Data Quality & Scoring

Assesses ingested data quality:

**Relevance Scoring** (0-100):

- Keyword match strength

- Topic alignment with objectives

- Source reputation weight

**Completeness Checks**:

- Required fields present

- Content length thresholds

- Metadata availability

**Timeliness Scoring**:

- Publication date recency

- Trending topic alignment

- Event correlation

**Quality Gates**:

- Minimum relevance: 40/100

- Minimum completeness: 80%

- Maximum age: 7 days (Tier 1), 30 days (Tier 2/3)

### 6. Storage & Handoff

**Primary Storage**: Google Cloud Storage (GCS)

- **Bucket**: `pnkln-ingestion-data`

- **Structure**: `/YYYY/MM/DD/tier-{1|2|3}/`

- **Format**: JSONL (JSON Lines)

- **Retention**: 90 days (Tier 1), 30 days (Tier 2/3)

**Metadata Storage**: PostgreSQL

- **Table**: `ingested_items`

- **Indexes**: Source, tier, timestamp, relevance

- **Retention**: Permanent (metadata only)

**Handoff Mechanism**:

- GCS bucket notifications trigger downstream processing

- REST API endpoints for pull-based access

- Event bus (Pub/Sub) for real-time consumers

## Integration Patterns

### Upstream (Invocation)

The ingestion layer is invoked by:


1. **Namespace 1**: Briefing scheduler (triggers AM briefing ingestion)

2. **Namespace 2**: On-demand intelligence requests

3. **Namespace 3**: Event-driven collection (breaking news)

4. **Namespace 4**: Research batch jobs

**Invocation Methods**:

- CronJob schedule (default)

- REST API trigger endpoint

- Pub/Sub event subscription

- kubectl job trigger

### Downstream (Consumption)

Ingested data is consumed by:


1. **Judge #6**: Validation and quality filtering

2. **AM Briefing Generator**: Morning summary creation

3. **Analytics Services**: Trend analysis, insights

4. **Research Tools**: Ad-hoc query interfaces

**Consumption Methods**:

- GCS bucket access (batch)

- REST API queries (on-demand)

- Pub/Sub subscriptions (streaming)

- PostgreSQL queries (metadata search)

## Performance Metrics

### Target SLAs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Runtime | ≤45 minutes | CronJob duration |
| Daily Items | 1000-5000 | Count in GCS/DB |
| Active Sources | ≥6 | Successful collectors |
| Cost/Item | ≤$0.015 | Monthly cost / items |
| Relevance (Avg) | ≥60/100 | Quality scoring |
| Tier 1 % | 10-20% | Classification distribution |
| Uptime | ≥99% | Successful runs/total |
| Error Rate | ≤1% | Failed items/total |

### Monitoring

**Key Dashboards**:

- Runtime trends (45-min threshold)

- Items ingested by source

- Tier distribution over time

- Cost tracking ($77/month budget)

- Quality scores by tier

- Failure rates by collector

**Alerts**:

- Runtime exceeds 50 minutes

- Daily items below 500

- Cost exceeds $3/day ($90/month)

- Source failure (3+ consecutive runs)

- Ethical violation detected

- Quality score drops below 50

## Cost Model

**Monthly Budget: ~$77**

**Cost Breakdown**:

- **GKE Compute**: $40/month (1 preemptible node, ~45 min/day)

- **GCS Storage**: $5/month (50GB average)

- **API Calls**: $20/month (NewsAPI, misc)

- **Network Egress**: $7/month (data transfer)

- **PostgreSQL**: $5/month (Cloud SQL micro instance)

**Cost Optimization**:

- Use preemptible nodes for CronJob (60-90% savings)

- Aggressive data retention policies

- Batch API calls to minimize quota usage

- Regional egress to minimize transfer costs

**Sensitivity**:

- 2x items → +$20/month (storage, compute)

- New paid API → varies ($10-100/month)

- Increased runtime → +$10/month per 15 minutes

## Operational Resilience

### Failure Handling

**Source Outages**:

- Retry with exponential backoff (2s, 4s, 8s, 16s)

- Skip and alert if 4 retries fail

- Continue with other sources

- Daily summary includes missing sources

**Rate Limiting**:

- Detect 429 responses

- Adaptive throttling (reduce rate by 50%)

- Resume after Retry-After header delay

- Spread requests across CronJob window

**Data Quality Issues**:

- Flag low-quality items (don't block)

- Alert if >20% items below quality threshold

- Manual review queue for edge cases

**Infrastructure Failures**:

- GKE pod restart (automatic)

- CronJob retry (3 attempts)

- Circuit breaker for persistent failures

- Fallback to backup sources

### Disaster Recovery

**Backup Strategy**:

- GCS bucket versioning enabled

- Daily PostgreSQL backups (7-day retention)

- Configuration versioned in Git

- Secrets in Google Secret Manager

**Recovery Procedures**:

- RTO (Recovery Time Objective): 4 hours

- RPO (Recovery Point Objective): 24 hours

- Runbook: `/docs/runbooks/ingestion-recovery.md`

## Security & Compliance

### Data Privacy


- No PII collection from public sources

- GDPR-compliant data retention

- Right to erasure (manual process)

- Audit logs for all data access

### Authentication & Authorization


- GKE workload identity for GCP services

- API keys stored in Secret Manager

- RBAC for Kubernetes resources

- mTLS for inter-service communication

### Ethical Guidelines


- Respect robots.txt (100% compliance)

- Rate limiting (prevent server overload)

- Transparent identification (User-Agent)

- No circumventing paywalls/protections

- Compliance with terms of service

## Deployment

See [GKE CronJob Configuration](../../k8s/ingestion-cronjob.yaml) for deployment manifests.

**Deployment Steps**:

1. Configure secrets (API keys)

2. Deploy ConfigMaps (source configs)

3. Apply CronJob manifest

4. Verify first run

5. Enable monitoring/alerting

**Configuration Management**:

- Sources: `/config/sources.yaml`

- Tier rules: `/config/tier-classification.yaml`

- Ethical policies: `/config/ethical-crawling.yaml`

- Quality gates: `/config/quality-gates.yaml`

## API Endpoints

See [FastAPI Integration](../../src/api/ingestion.py) for REST API documentation.

**Key Endpoints**:

- `POST /ingestion/trigger` - Manual CronJob trigger

- `GET /ingestion/status` - Current/last run status

- `GET /ingestion/items` - Query ingested items

- `GET /ingestion/metrics` - Performance metrics

- `POST /ingestion/sources` - Update source configuration

## Future Enhancements


1. **Real-time Streaming**: Continuous ingestion (not just nightly)

2. **ML-Based Tier Classification**: Replace rules with deep learning

3. **Multi-Language Support**: Non-English sources

4. **Source Discovery**: Automatic identification of new sources

5. **Federated Learning**: Privacy-preserving model training

6. **Advanced Deduplication**: Cross-source content matching

7. **Sentiment Analysis**: Emotional tone scoring

8. **Entity Recognition**: Automated tagging of people, places, organizations

## References


- [PNKLN Core Stack™ Overview](./pnkln-core-stack.md)

- [Ethical Crawling Guidelines](./ethical-crawling.md)

- [Tier Classification Model](./tier-classification.md)

- [Judge #6 Validation Layer](./judge-six.md)

- [GKE CronJob Manifests](../../k8s/ingestion-cronjob.yaml)

- [FastAPI Endpoints](../../src/api/ingestion.py)

## Version History


- **v1.0** (2025-11-07): Initial architecture documentation

- Target runtime: ~45 minutes

- Budget: ~$77/month

- Sources: YouTube, Twitter, News, RSS, Web, APIs
>>>>>>> origin/claude/encode-cor8-aiyou-global-edge-fabric-012j1em5ogeXnbbtG5DDZuZg
