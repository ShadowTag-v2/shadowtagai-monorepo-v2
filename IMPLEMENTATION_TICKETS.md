# PNKLN CORE STACK™ - IMPLEMENTATION TICKETS
**Created:** 2025-11-15
**Epic:** PNKLN Core Stack™ v1.0

---

## OVERVIEW

This document contains all implementation tickets for both components:
1. **Judge #6** (Enforcement Layer)
2. **Gemini Ingestion Layer** (Collection Layer)

**Total Tickets:** 32 (16 per component)
**Total Effort:** 60 person-weeks (36 + 24)
**Timeline:** 12 weeks (parallel development)

---

## JUDGE #6 IMPLEMENTATION TICKETS

### EPIC: Judge #6 - ATP 5-19 Enforcement Engine

---

### PHASE 1: FOUNDATION (Weeks 1-3)

#### Issue #1: [JUDGE-6] JR Engine Core Framework
**Labels:** `enhancement`, `judge-6`, `core`, `phase-1`
**Effort:** 3 weeks (1 engineer)

**Description:**
Implement the core Purpose/Reasons/Brakes (JR Engine) validation framework.

**Acceptance Criteria:**
- [ ] `Purpose` validator: Checks business objective alignment
- [ ] `Reasons` validator: Evidence-based decision validation
- [ ] `Brakes` validator: Security/compliance/performance risk detection
- [ ] Python classes: `JREngine`, `PurposeValidator`, `ReasonsValidator`, `BrakesValidator`
- [ ] Unit tests: ≥85% coverage for core logic
- [ ] Documentation: JR Engine philosophy guide

**Technical Specs:**
```python
class JREngine:
    def validate(self, action: Action) -> JRVerdict:
        purpose = self.validate_purpose(action)
        reasons = self.validate_reasons(action)
        brakes = self.validate_brakes(action)
        return JRVerdict(purpose, reasons, brakes)
```

**Files to Create:**
- `src/judge_six/jr_engine.py`
- `src/judge_six/validators/__init__.py`
- `src/judge_six/validators/purpose.py`
- `src/judge_six/validators/reasons.py`
- `src/judge_six/validators/brakes.py`
- `tests/test_jr_engine.py`

**Dependencies:** None

---

#### Issue #2: [JUDGE-6] ATP 5-19 Policy Schema
**Labels:** `enhancement`, `judge-6`, `atp-5-19`, `phase-1`
**Effort:** 1 week

**Description:**
Define ATP 5-19 policy schema (JSON format) covering 44 threat categories.

**Acceptance Criteria:**
- [ ] JSON schema for policies (OpenAPI-compatible)
- [ ] 44 threat categories defined (OWASP Top 10 + ATP 5-19)
- [ ] Policy validation logic
- [ ] Example policies (20+ rules)
- [ ] Schema documentation

**Schema Structure:**
```json
{
  "policy_id": "atp-5-19-001",
  "category": "injection",
  "severity": "high",
  "description": "Prevent SQL injection attacks",
  "detection_pattern": "SELECT.*FROM.*WHERE",
  "action": "block",
  "atp_5_19_mapping": "3.2.1.a"
}
```

**Files to Create:**
- `schemas/atp_5_19_policy_schema.json`
- `src/judge_six/policies/__init__.py`
- `src/judge_six/policies/loader.py`
- `policies/security/injection.json`
- `policies/security/xss.json`
- `policies/compliance/data_residency.json`
- `tests/test_policy_schema.py`

**Dependencies:** None

---

#### Issue #3: [JUDGE-6] Gemini API Integration
**Labels:** `enhancement`, `judge-6`, `gemini`, `phase-1`
**Effort:** 1 week

**Description:**
Integrate Gemini Flash 2.0 for AI-powered policy validation.

**Acceptance Criteria:**
- [ ] Gemini API client wrapper
- [ ] Prompt engineering for policy validation
- [ ] Caching layer (Redis) for repeated validations
- [ ] Rate limiting (respect Gemini quotas)
- [ ] Error handling & retries
- [ ] Cost tracking (tokens/validation)
- [ ] <200ms p99 latency

**Technical Specs:**
- Model: `gemini-2.0-flash-exp`
- Max tokens: 500/response
- Temperature: 0.1 (deterministic)
- Caching: 1-hour TTL for identical inputs

**Files to Create:**
- `src/judge_six/gemini_client.py`
- `src/judge_six/prompts/__init__.py`
- `src/judge_six/prompts/validation.py`
- `src/judge_six/cache.py`
- `tests/test_gemini_integration.py`

**Dependencies:**
- Gemini API credentials (env var: `GEMINI_API_KEY`)

---

#### Issue #4: [JUDGE-6] Validation API Endpoints
**Labels:** `enhancement`, `judge-6`, `api`, `phase-1`
**Effort:** 1 week

**Description:**
Build FastAPI REST endpoints for validation requests.

**Acceptance Criteria:**
- [ ] POST `/api/v1/validate` - Single validation
- [ ] POST `/api/v1/validate/batch` - Batch validation
- [ ] GET `/api/v1/policies` - List policies
- [ ] GET `/api/v1/health` - Health check
- [ ] OpenAPI documentation
- [ ] Rate limiting (100 req/min per client)
- [ ] Authentication (API keys)

**API Spec:**
```python
@app.post("/api/v1/validate")
async def validate(request: ValidationRequest) -> ValidationResponse:
    verdict = jr_engine.validate(request.action)
    return ValidationResponse(verdict=verdict, latency_ms=...)
```

**Files to Create:**
- `src/api/main.py`
- `src/api/routes/validation.py`
- `src/api/routes/policies.py`
- `src/api/models.py`
- `src/api/auth.py`
- `tests/test_api_endpoints.py`

**Dependencies:**
- Issue #1 (JR Engine)
- Issue #2 (Policy Schema)

---

### PHASE 2: ENHANCEMENT (Weeks 4-6)

#### Issue #5: [JUDGE-6] Hybrid Enforcement (Gemini + PyTorch)
**Labels:** `enhancement`, `judge-6`, `hybrid`, `phase-2`
**Effort:** 2 weeks

**Description:**
Add PyTorch local models as fallback for Gemini API failures or offline mode.

**Acceptance Criteria:**
- [ ] PyTorch model selection (BERT, RoBERTa, or custom)
- [ ] Model training on policy dataset (1000+ labeled examples)
- [ ] Hybrid routing logic (Gemini primary, PyTorch fallback)
- [ ] Accuracy ≥92% (compared to Gemini baseline)
- [ ] Latency: <300ms (offline mode acceptable)

**Files to Create:**
- `src/judge_six/pytorch_validator.py`
- `models/policy_classifier.pt`
- `scripts/train_pytorch_model.py`
- `tests/test_hybrid_enforcement.py`

**Dependencies:**
- Issue #3 (Gemini integration)
- Training dataset (create via Issue #2 policies)

---

#### Issue #6: [JUDGE-6] Performance Optimization
**Labels:** `enhancement`, `judge-six`, `performance`, `phase-2`
**Effort:** 1 week

**Description:**
Optimize for <200ms p99 latency and 150 validations/sec throughput.

**Acceptance Criteria:**
- [ ] Redis caching for policy rules
- [ ] Async batch processing
- [ ] Connection pooling (PostgreSQL, Redis)
- [ ] Lazy loading (policies loaded on-demand)
- [ ] Latency benchmarks: p50 <80ms, p95 <150ms, p99 <200ms
- [ ] Throughput: 150/sec sustained load

**Optimizations:**
- Policy compilation (regex → compiled patterns)
- Gemini response streaming
- Request coalescing (batch similar validations)

**Files to Create:**
- `src/judge_six/optimizations/__init__.py`
- `src/judge_six/optimizations/caching.py`
- `src/judge_six/optimizations/batching.py`
- `benchmarks/latency_test.py`
- `benchmarks/throughput_test.py`

**Dependencies:**
- Issue #3 (Gemini integration)
- Redis instance

---

#### Issue #7: [JUDGE-6] Extended Policy Categories (40+ Threats)
**Labels:** `enhancement`, `judge-six`, `policies`, `phase-2`
**Effort:** 1 week

**Description:**
Expand from 20 to 44 threat categories (OWASP + ATP 5-19 + custom).

**Acceptance Criteria:**
- [ ] 44 threat categories defined
- [ ] Policy coverage: ≥94%
- [ ] Each category: ≥3 example policies
- [ ] Documentation: Threat taxonomy
- [ ] Tests: Validate each category

**Threat Categories to Add:**
- Injection: SQL, NoSQL, LDAP, Command, XPath
- XSS: Stored, Reflected, DOM
- Authentication: Bypass, weak credentials
- Authorization: Privilege escalation, IDOR
- AI-specific: Prompt injection, model extraction, data poisoning
- Business logic: JR violations

**Files to Create:**
- `policies/security/auth_bypass.json`
- `policies/security/privilege_escalation.json`
- `policies/ai/prompt_injection.json`
- `policies/business_logic/jr_violations.json`
- `docs/threat_taxonomy.md`

**Dependencies:**
- Issue #2 (Policy Schema)

---

#### Issue #8: [JUDGE-6] Audit Logging System
**Labels:** `enhancement`, `judge-six`, `audit`, `phase-2`
**Effort:** 1 week

**Description:**
Implement tamper-proof audit logging for compliance.

**Acceptance Criteria:**
- [ ] All validations logged (action, verdict, timestamp, user)
- [ ] PostgreSQL append-only audit table
- [ ] Audit log immutability (hash chain or similar)
- [ ] Query API for audit retrieval
- [ ] Retention policy (90 days default)
- [ ] Export to SIEM (JSON format)

**Audit Log Schema:**
```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    action_id UUID NOT NULL,
    action_type VARCHAR(255),
    verdict VARCHAR(50),
    policy_id VARCHAR(255),
    user_id VARCHAR(255),
    metadata JSONB,
    hash VARCHAR(64) -- SHA-256 of prev_hash + current_row
);
```

**Files to Create:**
- `src/judge_six/audit/__init__.py`
- `src/judge_six/audit/logger.py`
- `src/judge_six/audit/retrieval.py`
- `migrations/001_create_audit_log.sql`
- `tests/test_audit_logging.py`

**Dependencies:**
- PostgreSQL database

---

### PHASE 3: ENTERPRISE (Weeks 7-9)

#### Issue #9: [JUDGE-6] Multi-Framework Compliance (SOC 2, HIPAA)
**Labels:** `enhancement`, `judge-six`, `compliance`, `phase-3`
**Effort:** 2 weeks

**Description:**
Extend beyond ATP 5-19 to support SOC 2, HIPAA, ISO 27001.

**Acceptance Criteria:**
- [ ] SOC 2 policy mappings (TSC controls)
- [ ] HIPAA policy mappings (Security Rule)
- [ ] ISO 27001 policy mappings (Annex A controls)
- [ ] Compliance reports (automated generation)
- [ ] Policy multi-tagging (one policy → multiple frameworks)

**Policy Example:**
```json
{
  "policy_id": "multi-001",
  "description": "Encrypt data at rest",
  "frameworks": {
    "atp_5_19": "3.2.1.b",
    "soc_2": "CC6.1",
    "hipaa": "164.312(a)(2)(iv)",
    "iso_27001": "A.10.1.1"
  }
}
```

**Files to Create:**
- `policies/compliance/soc2/`
- `policies/compliance/hipaa/`
- `policies/compliance/iso27001/`
- `src/judge_six/compliance/__init__.py`
- `src/judge_six/compliance/soc2.py`
- `src/judge_six/compliance/hipaa.py`
- `src/judge_six/compliance/report_generator.py`
- `tests/test_multi_framework.py`

**Dependencies:**
- Issue #7 (Extended policies)

---

#### Issue #10: [JUDGE-6] Custom Policy Authoring
**Labels:** `enhancement`, `judge-six`, `custom-policies`, `phase-3`
**Effort:** 1 week

**Description:**
Enable customers to create custom policies via UI/API.

**Acceptance Criteria:**
- [ ] POST `/api/v1/policies` - Create policy
- [ ] PUT `/api/v1/policies/{id}` - Update policy
- [ ] DELETE `/api/v1/policies/{id}` - Delete policy
- [ ] Policy validation (schema enforcement)
- [ ] Policy testing (dry-run mode)
- [ ] Version control (policy history)

**API Spec:**
```python
@app.post("/api/v1/policies")
async def create_policy(policy: PolicyCreate) -> Policy:
    # Validate schema
    # Test policy (dry-run on sample data)
    # Store in database
    # Invalidate cache
    return created_policy
```

**Files to Create:**
- `src/api/routes/policy_management.py`
- `src/judge_six/policy_tester.py`
- `src/judge_six/policy_versioning.py`
- `tests/test_custom_policies.py`

**Dependencies:**
- Issue #2 (Policy Schema)
- Issue #4 (API Endpoints)

---

#### Issue #11: [JUDGE-6] Real-Time Dashboard
**Labels:** `enhancement`, `judge-six`, `dashboard`, `phase-3`
**Effort:** 2 weeks

**Description:**
Build real-time monitoring dashboard for validation metrics.

**Acceptance Criteria:**
- [ ] Metrics: Latency, throughput, false positive/negative rates
- [ ] Real-time charts (validations/sec, policy coverage)
- [ ] Alert configuration (email, Slack)
- [ ] Historical trends (7 days, 30 days)
- [ ] Policy effectiveness ranking

**Tech Stack:**
- Frontend: React + Chart.js (or use existing PNKLN dashboard)
- Backend: WebSocket for real-time updates
- Metrics: Prometheus + Grafana (or custom)

**Files to Create:**
- `dashboard/frontend/src/components/Metrics.tsx`
- `dashboard/frontend/src/components/Alerts.tsx`
- `src/api/routes/metrics.py`
- `src/judge_six/metrics/__init__.py`
- `src/judge_six/metrics/collector.py`

**Dependencies:**
- Metrics storage (Prometheus or PostgreSQL)

---

#### Issue #12: [JUDGE-6] SLA Guarantees (99.2%)
**Labels:** `enhancement`, `judge-six`, `sla`, `phase-3`
**Effort:** 1 week

**Description:**
Implement SLA monitoring and guarantees for enterprise customers.

**Acceptance Criteria:**
- [ ] Uptime tracking (99.2% target)
- [ ] Latency SLA: p99 <200ms
- [ ] Throughput SLA: ≥150/sec
- [ ] SLA reporting (monthly)
- [ ] Automated alerts (SLA breach)
- [ ] Graceful degradation (PyTorch fallback counts toward SLA)

**SLA Tiers:**
- **Standard:** 99% uptime, <300ms p99
- **Enterprise:** 99.2% uptime, <200ms p99
- **Mission-Critical:** 99.5% uptime, <150ms p99

**Files to Create:**
- `src/judge_six/sla/__init__.py`
- `src/judge_six/sla/monitor.py`
- `src/judge_six/sla/reporter.py`
- `tests/test_sla_tracking.py`

**Dependencies:**
- Issue #11 (Metrics)

---

### PHASE 4: SCALE (Weeks 10-12)

#### Issue #13: [JUDGE-6] Horizontal Scaling Architecture
**Labels:** `enhancement`, `judge-six`, `scaling`, `phase-4`
**Effort:** 1 week

**Description:**
Enable horizontal scaling for >150 validations/sec.

**Acceptance Criteria:**
- [ ] Stateless design (no local state)
- [ ] Load balancer configuration (nginx or K8s ingress)
- [ ] Session affinity (if needed)
- [ ] Auto-scaling rules (CPU >70% → scale up)
- [ ] Distributed caching (Redis Cluster)
- [ ] Database connection pooling

**Architecture:**
```
                  Load Balancer
                       |
       ┌───────────────┼───────────────┐
       │               │               │
   Judge #6        Judge #6        Judge #6
   Instance 1      Instance 2      Instance 3
       │               │               │
       └───────────────┼───────────────┘
                       |
                 Redis Cluster
                       |
                  PostgreSQL
```

**Files to Create:**
- `kubernetes/judge_six_deployment.yaml`
- `kubernetes/judge_six_service.yaml`
- `kubernetes/judge_six_hpa.yaml` (HorizontalPodAutoscaler)
- `docs/scaling_guide.md`

**Dependencies:**
- Kubernetes cluster (or Docker Swarm)

---

#### Issue #14: [JUDGE-6] Advanced Analytics (Threat Trends)
**Labels:** `enhancement`, `judge-six`, `analytics`, `phase-4`
**Effort:** 1 week

**Description:**
Analyze validation patterns to detect emerging threats.

**Acceptance Criteria:**
- [ ] Threat trend detection (frequency analysis)
- [ ] Anomaly detection (unusual validation patterns)
- [ ] Top 10 blocked threats (daily, weekly, monthly)
- [ ] Policy effectiveness scoring
- [ ] Recommendations (suggest new policies)

**Analytics:**
- Time-series analysis (validations/hour per threat category)
- Clustering (group similar attack patterns)
- Forecasting (predict next week's threat landscape)

**Files to Create:**
- `src/judge_six/analytics/__init__.py`
- `src/judge_six/analytics/trend_detector.py`
- `src/judge_six/analytics/anomaly_detector.py`
- `src/judge_six/analytics/recommender.py`
- `tests/test_analytics.py`

**Dependencies:**
- Issue #8 (Audit logging for historical data)

---

#### Issue #15: [JUDGE-6] API Rate Limiting & Quotas
**Labels:** `enhancement`, `judge-six`, `rate-limiting`, `phase-4`
**Effort:** 1 week

**Description:**
Implement per-client rate limiting and quota management.

**Acceptance Criteria:**
- [ ] Rate limiting: 100 req/min (standard), 500 req/min (enterprise)
- [ ] Quota tracking: 10,000 validations/month (standard)
- [ ] Quota alerts (80%, 90%, 100%)
- [ ] Overage billing (if applicable)
- [ ] Rate limit headers (X-RateLimit-Remaining, etc.)

**Rate Limit Algorithm:**
- Token bucket (smooth rate limiting)
- Redis-based counter (distributed)

**Files to Create:**
- `src/api/middleware/rate_limiter.py`
- `src/judge_six/quota/__init__.py`
- `src/judge_six/quota/tracker.py`
- `tests/test_rate_limiting.py`

**Dependencies:**
- Redis

---

#### Issue #16: [JUDGE-6] Customer-Facing Compliance Reports
**Labels:** `enhancement`, `judge-six`, `reports`, `phase-4`
**Effort:** 1 week

**Description:**
Generate downloadable compliance reports for customers.

**Acceptance Criteria:**
- [ ] Report formats: PDF, CSV, JSON
- [ ] Report types: ATP 5-19, SOC 2, HIPAA, ISO 27001
- [ ] Time range selection (daily, weekly, monthly, custom)
- [ ] Branding customization (customer logo)
- [ ] Automated scheduling (email reports)

**Report Contents:**
- Validation summary (total, blocked, allowed)
- Policy coverage breakdown
- False positive/negative rates
- Compliance score (% of validations passed)
- Top threats blocked

**Files to Create:**
- `src/judge_six/reports/__init__.py`
- `src/judge_six/reports/pdf_generator.py`
- `src/judge_six/reports/csv_exporter.py`
- `src/api/routes/reports.py`
- `templates/compliance_report.html` (PDF template)
- `tests/test_report_generation.py`

**Dependencies:**
- Issue #9 (Multi-framework compliance)
- Issue #8 (Audit logging)

---

## GEMINI INGESTION LAYER IMPLEMENTATION TICKETS

### EPIC: Gemini Ingestion Layer - Intelligence Collection Pipeline

---

### PHASE 1: FOUNDATION (Weeks 1-3)

#### Issue #17: [INGESTION] GKE Cluster Setup
**Labels:** `enhancement`, `ingestion`, `gke`, `phase-1`
**Effort:** 0.5 weeks

**Description:**
Provision GKE cluster for nightly CronJob orchestration.

**Acceptance Criteria:**
- [ ] GKE cluster created (3 nodes, n1-standard-2)
- [ ] Namespace: `pnkln-ingestion`
- [ ] Service account with permissions
- [ ] Secrets management (API keys for YouTube, Twitter, News)
- [ ] Network policies (egress to source APIs)
- [ ] Cost monitoring enabled

**GKE Specs:**
- Cluster name: `pnkln-core-stack`
- Zone: `us-central1-a`
- Nodes: 3 × n1-standard-2 (2 vCPU, 7.5 GB RAM each)
- Auto-scaling: disabled (static for cost control)

**Files to Create:**
- `kubernetes/cluster_setup.sh`
- `kubernetes/namespace.yaml`
- `kubernetes/secrets.yaml` (template)
- `docs/gke_setup_guide.md`

**Dependencies:**
- GCP project with billing enabled

---

#### Issue #18: [INGESTION] Core CronJob Manifest
**Labels:** `enhancement`, `ingestion`, `gke`, `phase-1`
**Effort:** 1 week

**Description:**
Create Kubernetes CronJob manifest for nightly ingestion.

**Acceptance Criteria:**
- [ ] CronJob schedule: 3:00 AM daily
- [ ] Multi-container pod (YouTube, Twitter, News)
- [ ] Shared volume for inter-container data exchange
- [ ] Retry policy: 3 attempts
- [ ] Timeout: 90 minutes
- [ ] Success/failure notifications (Slack webhook)

**CronJob Spec:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: gemini-ingestion
  namespace: pnkln-ingestion
spec:
  schedule: "0 3 * * *"  # 3:00 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: youtube-collector
            image: gcr.io/pnkln/youtube-collector:latest
          - name: twitter-collector
            image: gcr.io/pnkln/twitter-collector:latest
          - name: news-collector
            image: gcr.io/pnkln/news-collector:latest
```

**Files to Create:**
- `kubernetes/cronjob.yaml`
- `kubernetes/configmap.yaml` (source configuration)
- `docs/cronjob_configuration.md`

**Dependencies:**
- Issue #17 (GKE cluster)

---

#### Issue #19: [INGESTION] YouTube Collector Container
**Labels:** `enhancement`, `ingestion`, `youtube`, `phase-1`
**Effort:** 1 week

**Description:**
Build Docker container for YouTube data collection.

**Acceptance Criteria:**
- [ ] YouTube Data API integration
- [ ] Channel subscriptions monitoring (6 channels)
- [ ] Metadata extraction (title, description, views, published_at)
- [ ] Ethical compliance (API quota: 10,000 units/day)
- [ ] Output: JSON array to shared volume
- [ ] Target: 145 items/day

**YouTube API:**
- Endpoint: `youtube.googleapis.com/youtube/v3/search`
- Quota cost: 100 units per request
- Daily limit: 10,000 units = 100 requests

**Files to Create:**
- `collectors/youtube/Dockerfile`
- `collectors/youtube/collector.py`
- `collectors/youtube/requirements.txt`
- `collectors/youtube/config.yaml` (channel IDs)
- `tests/test_youtube_collector.py`

**Dependencies:**
- YouTube Data API key (env var: `YOUTUBE_API_KEY`)

---

#### Issue #20: [INGESTION] Twitter Collector Container
**Labels:** `enhancement`, `ingestion`, `twitter`, `phase-1`
**Effort:** 1 week

**Description:**
Build Docker container for Twitter/X data collection.

**Acceptance Criteria:**
- [ ] Twitter API v2 integration
- [ ] List monitoring (3 Twitter lists)
- [ ] Metadata extraction (tweet text, author, timestamp, engagement)
- [ ] Rate limiting (450 requests/15 min)
- [ ] Output: JSON array to shared volume
- [ ] Target: 380 items/day

**Twitter API:**
- Endpoint: `api.twitter.com/2/lists/{id}/tweets`
- Rate limit: 450 requests per 15-minute window
- Authentication: OAuth 2.0 Bearer Token

**Files to Create:**
- `collectors/twitter/Dockerfile`
- `collectors/twitter/collector.py`
- `collectors/twitter/requirements.txt`
- `collectors/twitter/config.yaml` (list IDs)
- `tests/test_twitter_collector.py`

**Dependencies:**
- Twitter API Bearer Token (env var: `TWITTER_BEARER_TOKEN`)

---

#### Issue #21: [INGESTION] PostgreSQL Database Schema
**Labels:** `enhancement`, `ingestion`, `database`, `phase-1`
**Effort:** 0.5 weeks

**Description:**
Create PostgreSQL schema for storing ingested items.

**Acceptance Criteria:**
- [ ] Tables: `items`, `sources`, `scores`, `audit_log`
- [ ] Indexes: timestamp, source_id, tier
- [ ] Constraints: unique(source_id, external_id)
- [ ] Partitioning: by month (for performance)
- [ ] Retention policy: 90 days for raw items

**Schema:**
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL,
    source_id INTEGER REFERENCES sources(id),
    title TEXT,
    content TEXT,
    url TEXT,
    published_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT NOW(),
    tier INTEGER CHECK (tier IN (1, 2, 3)),
    relevance_score DECIMAL(3, 1),
    metadata JSONB
);

CREATE INDEX idx_items_timestamp ON items(ingested_at DESC);
CREATE INDEX idx_items_tier ON items(tier);
CREATE UNIQUE INDEX idx_items_unique ON items(source_id, external_id);
```

**Files to Create:**
- `migrations/001_create_schema.sql`
- `migrations/002_create_indexes.sql`
- `migrations/003_create_partitions.sql`
- `docs/database_schema.md`

**Dependencies:**
- PostgreSQL instance (GCP Cloud SQL or self-hosted)

---

#### Issue #22: [INGESTION] Basic Tier Classification (Rule-Based)
**Labels:** `enhancement`, `ingestion`, `classification`, `phase-1`
**Effort:** 1 week

**Description:**
Implement rule-based tier classification (before Gemini NLP).

**Acceptance Criteria:**
- [ ] Source reputation scoring (Reuters = +3, Reddit = +1)
- [ ] Keyword matching (hot topics list)
- [ ] Timeliness scoring (<6hr = +2, <24hr = +1)
- [ ] Tier assignment (≥8.0 = Tier 1, 5.0-7.9 = Tier 2, <5.0 = Tier 3)
- [ ] Target: 20% Tier 1 ratio (MVP baseline)

**Algorithm:**
```python
def classify_tier(item: Item) -> int:
    score = 0
    score += source_reputation(item.source_id)  # 0-3 points
    score += keyword_relevance(item.content)     # 0-4 points
    score += timeliness_score(item.published_at) # 0-2 points

    if score >= 8.0:
        return 1  # Tier 1
    elif score >= 5.0:
        return 2  # Tier 2
    else:
        return 3  # Tier 3
```

**Files to Create:**
- `src/ingestion/classification/__init__.py`
- `src/ingestion/classification/rule_based.py`
- `src/ingestion/classification/scoring.py`
- `config/hot_topics.yaml`
- `tests/test_tier_classification.py`

**Dependencies:**
- Issue #21 (Database schema)

---

#### Issue #23: [INGESTION] Minimal AM Briefing (Email-Only)
**Labels:** `enhancement`, `ingestion`, `briefing`, `phase-1`
**Effort:** 1 week

**Description:**
Generate minimal AM briefing (email-only, 10 items).

**Acceptance Criteria:**
- [ ] Select top 10 Tier 1 items
- [ ] Markdown template rendering
- [ ] Email delivery (SMTP or SendGrid)
- [ ] Delivery time: 6:45 AM
- [ ] Subject line: "AM Intelligence Briefing - [DATE]"

**Email Template:**
```markdown
# AM Intelligence Briefing - 2025-11-16
**Delivered:** 6:45 AM | **Items:** 10 (Tier 1)

## TOP INTELLIGENCE (10 items)

### [Item Title]
- **Source:** Reuters API
- **Published:** 6 hours ago
- **Summary:** [First 200 characters of content]
- **Link:** [URL]

...
```

**Files to Create:**
- `src/ingestion/briefing/__init__.py`
- `src/ingestion/briefing/generator.py`
- `src/ingestion/briefing/email_sender.py`
- `templates/briefing_email.md`
- `tests/test_briefing_generation.py`

**Dependencies:**
- Issue #22 (Tier classification)
- SMTP credentials (Gmail, SendGrid, etc.)

---

### PHASE 2: ENHANCEMENT (Weeks 4-6)

#### Issue #24: [INGESTION] Gemini 2.0 Pro NLP Integration
**Labels:** `enhancement`, `ingestion`, `gemini`, `phase-2`
**Effort:** 2 weeks

**Description:**
Replace rule-based classification with Gemini 2.0 Pro NLP.

**Acceptance Criteria:**
- [ ] Gemini API client wrapper
- [ ] Prompt engineering for relevance scoring
- [ ] Batch processing (50 items/request for efficiency)
- [ ] Relevance score: 0-10 scale
- [ ] Target: 31% Tier 1 ratio (vs. 20% rule-based)
- [ ] Cost: <$12/month (batched API calls)

**Gemini Prompt:**
```
Analyze the following intelligence item for relevance to strategic decision-making:

Title: {title}
Source: {source}
Content: {content}

Rate relevance on 0-10 scale:
- 9-10: Critical, actionable intelligence (Tier 1)
- 7-8: Important, contextual information (Tier 2)
- 5-6: Useful background (Tier 2)
- 0-4: Low-value noise (Tier 3)

Output format: {"relevance_score": 8.5, "reasoning": "..."}
```

**Files to Create:**
- `src/ingestion/classification/gemini_nlp.py`
- `src/ingestion/prompts/relevance_scoring.py`
- `src/ingestion/batching.py`
- `tests/test_gemini_classification.py`

**Dependencies:**
- Gemini API key (env var: `GEMINI_API_KEY`)
- Issue #22 (Rule-based baseline for comparison)

---

#### Issue #25: [INGESTION] Expanded Sources (News APIs)
**Labels:** `enhancement`, `ingestion`, `news`, `phase-2`
**Effort:** 1 week

**Description:**
Add News API collectors (AP, Reuters, NYT, BBC, Al Jazeera).

**Acceptance Criteria:**
- [ ] 5 news source collectors
- [ ] API integration (NewsAPI, Reuters Connect, etc.)
- [ ] Target: 215 items/day from news sources
- [ ] Ethical compliance (API rate limits)
- [ ] Duplicate detection (same story from multiple sources)

**News Sources:**
1. **Associated Press (AP)** - API or RSS
2. **Reuters Connect** - Premium API
3. **New York Times** - NYT API
4. **BBC News** - RSS feeds
5. **Al Jazeera** - RSS feeds

**Files to Create:**
- `collectors/news/Dockerfile`
- `collectors/news/collector.py`
- `collectors/news/sources/ap.py`
- `collectors/news/sources/reuters.py`
- `collectors/news/sources/nyt.py`
- `collectors/news/sources/bbc.py`
- `collectors/news/sources/aljazeera.py`
- `tests/test_news_collectors.py`

**Dependencies:**
- NewsAPI key (if using NewsAPI aggregator)
- Reuters Connect credentials (if premium)

---

#### Issue #26: [INGESTION] RSS Feed Collector
**Labels:** `enhancement`, `ingestion`, `rss`, `phase-2`
**Effort:** 0.5 weeks

**Description:**
Generic RSS feed collector for industry newsletters, blogs.

**Acceptance Criteria:**
- [ ] RSS/Atom feed parsing
- [ ] Configurable feed list (YAML)
- [ ] Target: 68 items/day from RSS feeds
- [ ] Duplicate detection (by GUID or link)
- [ ] Ethical: Respect crawl-delay in RSS

**RSS Configuration:**
```yaml
feeds:
  - url: https://example.com/feed.xml
    name: Industry Newsletter
    category: industry
    tier_boost: 0.5  # Slightly boost Tier 1 probability
  - url: https://blog.example.com/rss
    name: Tech Blog
    category: industry
    tier_boost: 0.0
```

**Files to Create:**
- `collectors/rss/Dockerfile`
- `collectors/rss/collector.py`
- `collectors/rss/config.yaml`
- `tests/test_rss_collector.py`

**Dependencies:**
- None (RSS is open standard)

---

#### Issue #27: [INGESTION] Reddit Collector
**Labels:** `enhancement`, `ingestion`, `reddit`, `phase-2`
**Effort:** 1 week

**Description:**
Collect from targeted subreddits (r/worldnews, r/technology, etc.).

**Acceptance Criteria:**
- [ ] Reddit API integration (OAuth 2.0)
- [ ] Subreddit monitoring (5 subreddits)
- [ ] Hot/top posts collection
- [ ] Rate limiting (60 requests/min)
- [ ] Target: subset of 380 social media items/day

**Subreddits:**
- r/worldnews (high priority)
- r/technology
- r/geopolitics
- r/cybersecurity
- r/AI

**Files to Create:**
- `collectors/reddit/Dockerfile`
- `collectors/reddit/collector.py`
- `collectors/reddit/config.yaml`
- `tests/test_reddit_collector.py`

**Dependencies:**
- Reddit API credentials (client ID, client secret)

---

#### Issue #28: [INGESTION] Ethical Compliance Module
**Labels:** `enhancement`, `ingestion`, `ethics`, `phase-2`
**Effort:** 1 week

**Description:**
Enforce 100% robots.txt compliance and rate limiting.

**Acceptance Criteria:**
- [ ] robots.txt pre-flight check (before every crawl)
- [ ] Rate limiting enforcement (1 req/sec default, configurable)
- [ ] User-Agent transparency (custom user-agent string)
- [ ] Crawl-delay respect (if specified in robots.txt)
- [ ] Automated alerts (if violation detected)
- [ ] Audit log (all crawl attempts)

**User-Agent:**
```
User-Agent: GeminiIngestionBot/1.0 (+https://pnkln.ai/ingestion-policy; contact@pnkln.ai)
```

**Files to Create:**
- `src/ingestion/ethics/__init__.py`
- `src/ingestion/ethics/robots_txt.py`
- `src/ingestion/ethics/rate_limiter.py`
- `src/ingestion/ethics/audit.py`
- `tests/test_ethical_compliance.py`

**Dependencies:**
- None (built-in)

---

#### Issue #29: [INGESTION] Performance Optimization
**Labels:** `enhancement`, `ingestion`, `performance`, `phase-2`
**Effort:** 1 week

**Description:**
Optimize nightly runtime from 78 min → 52 min.

**Acceptance Criteria:**
- [ ] Parallel container execution (all collectors start simultaneously)
- [ ] Connection pooling (reuse HTTP connections)
- [ ] Async I/O (asyncio for network requests)
- [ ] PostgreSQL bulk inserts (batch 100 items/insert)
- [ ] Redis caching (source metadata, hot topics)
- [ ] Runtime: <52 min for 620 items/day

**Optimizations:**
- Multi-threading within collectors (if GIL allows)
- HTTP/2 connection reuse
- Database connection pooling (psycopg2 pool)

**Files to Create:**
- `src/ingestion/optimizations/__init__.py`
- `src/ingestion/optimizations/parallel.py`
- `src/ingestion/optimizations/async_io.py`
- `src/ingestion/optimizations/batching.py`
- `benchmarks/runtime_test.py`

**Dependencies:**
- Redis instance

---

### PHASE 3: PRODUCTION (Weeks 7-9)

#### Issue #30: [INGESTION] Multi-Source Coverage Complete (24+ Sources)
**Labels:** `enhancement`, `ingestion`, `sources`, `phase-3`
**Effort:** 2 weeks

**Description:**
Reach 24+ source coverage (LinkedIn, Mastodon, Gov, Academic).

**Acceptance Criteria:**
- [ ] LinkedIn collector (job postings, articles)
- [ ] Mastodon collector (hashtag streams)
- [ ] Government collector (FedReg, DoD releases)
- [ ] Academic collector (arXiv, PubMed)
- [ ] Vimeo, Rumble collectors (video)
- [ ] Podcast transcript collector
- [ ] Target: 850 items/day total

**New Sources:**
- **LinkedIn:** API (if available) or scraper
- **Mastodon:** Public API (open federation)
- **FedReg:** RSS feed
- **DoD Releases:** RSS/HTML scraping
- **arXiv:** API (arXiv.org/help/api)
- **PubMed:** E-utilities API

**Files to Create:**
- `collectors/linkedin/`
- `collectors/mastodon/`
- `collectors/government/`
- `collectors/academic/`
- `collectors/video/vimeo.py`
- `collectors/video/rumble.py`
- `collectors/podcast/`

**Dependencies:**
- API credentials for each source

---

#### Issue #31: [INGESTION] AM Briefing Automation (Slack + PDF + Dashboard)
**Labels:** `enhancement`, `ingestion`, `briefing`, `phase-3`
**Effort:** 1 week

**Description:**
Expand AM briefing to Slack, PDF, and web dashboard.

**Acceptance Criteria:**
- [ ] Slack webhook integration (formatted message)
- [ ] PDF generation (WeasyPrint or ReportLab)
- [ ] Web dashboard (React + API endpoint)
- [ ] Stakeholder customization (item count, topics)
- [ ] Delivery channels: Email, Slack, Dashboard (all 3)
- [ ] Target: 8.5/10 stakeholder satisfaction

**Slack Message Format:**
```
🌅 *AM Intelligence Briefing - 2025-11-16*
📊 *Items:* 25 (Tier 1: 18, Tier 2: 7)
⏰ *Delivered:* 6:45 AM

🔴 *TIER 1 - ACTIONABLE INTELLIGENCE*

*1. [Item Title]*
📰 Reuters API | ⏱️ 6 hours ago | ⭐ 8.9/10
[Two-sentence summary]
🔗 [Link]

...
```

**Files to Create:**
- `src/ingestion/briefing/slack_sender.py`
- `src/ingestion/briefing/pdf_generator.py`
- `src/ingestion/briefing/dashboard_api.py`
- `templates/briefing.html` (for PDF)
- `dashboard/frontend/src/pages/Briefing.tsx`
- `tests/test_multi_channel_briefing.py`

**Dependencies:**
- Slack webhook URL
- PDF library (WeasyPrint, wkhtmltopdf, or ReportLab)

---

#### Issue #32: [INGESTION] Quality Gates Enforcement
**Labels:** `enhancement`, `ingestion`, `quality`, `phase-3`
**Effort:** 1 week

**Description:**
Automated quality gate checks with alerts.

**Acceptance Criteria:**
- [ ] Daily checks: Items/day ≥750, Sources ≥20, Cost/item ≤$0.50
- [ ] Relevance score ≥7.0/10 average
- [ ] Tier 1 ratio ≥35%
- [ ] Runtime ≤60 min
- [ ] Ethical compliance = 100%
- [ ] Automated alerts (Slack, email if gate fails)

**Quality Gate Logic:**
```python
def check_quality_gates(metrics: Metrics) -> GateResult:
    gates = {
        "items_per_day": metrics.items_count >= 750,
        "sources_active": metrics.sources_count >= 20,
        "cost_per_item": metrics.cost_per_item <= 0.50,
        "relevance_score": metrics.avg_relevance >= 7.0,
        "tier_1_ratio": metrics.tier_1_ratio >= 0.35,
        "runtime": metrics.runtime_minutes <= 60,
        "ethical_compliance": metrics.ethical_compliance == 1.0
    }

    if all(gates.values()):
        return GateResult.PASSED
    else:
        send_alert(failed_gates=[k for k, v in gates.items() if not v])
        return GateResult.FAILED
```

**Files to Create:**
- `src/ingestion/quality/__init__.py`
- `src/ingestion/quality/gates.py`
- `src/ingestion/quality/alerting.py`
- `tests/test_quality_gates.py`

**Dependencies:**
- Issue #21 (Metrics storage)

---

## IMPLEMENTATION PLAN

### Parallel Development Strategy

**Team Structure:**
- **Team A (Judge #6):** 3 engineers
- **Team B (Ingestion Layer):** 2 engineers
- **Shared:** 1 DevOps engineer (GKE, PostgreSQL, Redis)

### Week-by-Week Schedule

| Week | Judge #6 (Team A) | Ingestion Layer (Team B) | Shared (DevOps) |
|------|-------------------|--------------------------|-----------------|
| 1 | Issue #1 (JR Engine), #2 (ATP Schema) | Issue #17 (GKE), #18 (CronJob), #19 (YouTube) | GKE cluster setup |
| 2 | Issue #3 (Gemini), #4 (API) | Issue #20 (Twitter), #21 (DB), #22 (Classification) | PostgreSQL setup |
| 3 | Testing, Documentation | Issue #23 (Briefing) | Redis setup |
| 4 | Issue #5 (Hybrid), #6 (Performance) | Issue #24 (Gemini NLP), #25 (News) | Monitoring setup |
| 5 | Issue #7 (Policies), #8 (Audit) | Issue #26 (RSS), #27 (Reddit) | Integration testing |
| 6 | Testing, Documentation | Issue #28 (Ethics), #29 (Performance) | Integration testing |
| 7 | Issue #9 (Multi-framework), #10 (Custom Policies) | Issue #30 (24 sources - part 1) | Load testing |
| 8 | Issue #11 (Dashboard), #12 (SLA) | Issue #30 (24 sources - part 2) | Security audit |
| 9 | Testing, Documentation | Issue #31 (Briefing multi-channel), #32 (Quality Gates) | E2E testing |
| 10 | Issue #13 (Scaling), #14 (Analytics) | Optimization, Tuning | Scaling tests |
| 11 | Issue #15 (Rate Limiting), #16 (Reports) | Optimization, Tuning | Performance tests |
| 12 | Testing, Documentation, Launch Prep | Testing, Documentation, Launch Prep | Launch checklist |

---

## DEPENDENCIES & INTEGRATION POINTS

### Critical Path

```
Ingestion Layer → Judge #6 → Analysis Services → AM Briefing
```

**Week 3 Integration:**
- Ingestion collects 280 items/day
- Judge #6 validates items (35% policy coverage)
- Feedback loop: Judge #6 → Ingestion (source quality)

**Week 6 Integration:**
- Ingestion: 620 items/day, Gemini NLP classification
- Judge #6: 78% policy coverage, hybrid enforcement
- E2E latency: <10 sec (ingestion → validation → storage)

**Week 9 Integration:**
- Ingestion: 850 items/day, 24 sources, 6:45 AM briefing
- Judge #6: 94% policy coverage, <200ms latency
- Full PNKLN stack operational

---

## RISK MITIGATION

### High-Risk Items

| Risk | Mitigation | Owner |
|------|------------|-------|
| **Gemini API quota exceeded** | Implement batching, caching | Team A & B |
| **Source API deprecation** | Build 24+ sources (redundancy) | Team B |
| **GKE cost overrun** | Auto-scaling limits, spot instances | DevOps |
| **Integration latency >10sec** | Optimize database writes, async | Team A & B |
| **Ethical compliance violation** | Pre-flight robots.txt checks | Team B |

---

## SUCCESS CRITERIA

### Week 12 Targets

**Judge #6:**
- [ ] 94% policy coverage
- [ ] <200ms p99 latency
- [ ] 150 validations/sec throughput
- [ ] 3.2% false positive rate
- [ ] ATP 5-19 certified

**Gemini Ingestion Layer:**
- [ ] 850 items/day
- [ ] 24+ sources active
- [ ] 38% Tier 1 ratio
- [ ] <45 min runtime
- [ ] $77/month cost
- [ ] 8.9/10 stakeholder satisfaction

**PNKLN Core Stack™:**
- [ ] End-to-end integration complete
- [ ] Ingestion → Judge #6 latency <5 min
- [ ] Feedback loop operational
- [ ] 4 analysis services consuming data
- [ ] AM briefing delivery 6:45 AM

---

## COST TRACKING

| Component | Dev Cost | Operational Cost/Month |
|-----------|----------|------------------------|
| Judge #6 | $175K (36 person-weeks) | $350 |
| Ingestion Layer | $145K (24 person-weeks) | $77 |
| Shared Infra (GKE, PostgreSQL, Redis) | $50K (8 person-weeks) | $250 |
| **TOTAL** | **$370K** | **$677/month** |

**ROI:**
- Combined savings: $926K/year ($397K + $529K)
- Combined value: $9.5M/year ($6.6M + $2.9M)
- Payback period: 0.5 months
- ROI multiple: 15× average (12× + 18×) / 2

---

**END OF IMPLEMENTATION TICKETS**

*For detailed technical specs, see component inception analyses.*
*For GKE manifests, see Issue #18 and kubernetes/ directory.*
*For JR Engine prototype, see Issue #1 implementation.*
