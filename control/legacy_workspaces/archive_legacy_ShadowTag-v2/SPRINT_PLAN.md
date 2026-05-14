# Full Integration Sprint Plan - PNKLN Core Stack™ + VCO

**Status**: In Progress
**Timeline**: 15-20 hours across 6 phases
**Target**: Production-ready unified stack

---

## Sprint Overview

### Financial Targets
- **Operational Cost**: $389/month (VCO $50 + Ingestion $77 + LLM $262)
- **Revenue**: $490/month (10 customers × $49 AM Briefing)
- **Profit**: $101/month (26% margin)
- **ROI**: 401% combined (271% VCO + 532% PNKLN)

### Technical Targets
- **Ingestion**: ~45 min/night runtime, 1000+ items/day
- **Judge #6**: p99 ≤90ms latency, 50% error reduction with VCO
- **LLM Serving**: 3-5x model density on A100
- **Quality**: 95%+ quality gate pass rate, 60% Tier 1/2 data

---

## Phase 1: PNKLN Ingestion Layer (5-6 hours)

### 1.1 Database Models ✅ COMPLETE
**Status**: 9 files created, ~400 lines
- [x] Base model (SQLAlchemy 2.0)
- [x] IngestionJob (job execution tracking)
- [x] SourceCoverage (multi-source metrics with Voice support)
- [x] EthicalCompliance (robots.txt, rate limiting)
- [x] TierClassification (Tier 1/2/3 distribution)
- [x] QualityGate (6-dimensional validation)
- [x] MonthlyCost (budget tracking, $77 baseline)
- [x] BriefingDelivery (AM delivery metrics)

### 1.2 Ethical Compliance Engine (1 hour)
**Files**: `services/ingestion/app/services/ethical_compliance.py`
- [ ] robots.txt parser and checker
- [ ] Rate limiting engine (per-source configurable)
- [ ] User agent manager ("PNKLNBot/1.0")
- [ ] Violation tracking and scoring (target: ≥95%)

### 1.3 Multi-Source Integrations (2 hours)
**Files**: `services/ingestion/app/sources/*.py`
- [ ] YouTube API integration (youtube.py)
- [ ] Twitter/X API integration (twitter.py)
- [ ] News APIs integration (news.py)
- [ ] RSS feed parser (rss.py)
- [ ] Voice Consensus transcripts (voice.py) - NEW

### 1.4 Tier Classification System (30 min)
**Files**: `services/ingestion/app/services/tier_classifier.py`
- [ ] Tier 1: Authoritative sources (≥20% target)
- [ ] Tier 2: Verified sources (30-50%)
- [ ] Tier 3: General sources (≤50%)
- [ ] ML-based quality scoring

### 1.5 Quality Gates (6-dimensional) (45 min)
**Files**: `services/ingestion/app/services/quality_gates.py`
- [ ] Daily items ≥ 1,000
- [ ] Source diversity ≥ 5
- [ ] Cost/item ≤ $0.10
- [ ] Avg quality score ≥ 70
- [ ] Tier 1% ≥ 20%
- [ ] Ethical compliance ≥ 95%

### 1.6 REST API Endpoints (15 total) (1.5 hours)
**Files**: `services/ingestion/app/main.py`, `app/routes/*.py`
- [ ] GET /ingestion/summary
- [ ] GET /ingestion/report
- [ ] GET /ingestion/runtime-efficiency
- [ ] GET /ingestion/quality-gates
- [ ] GET /ingestion/source-coverage
- [ ] GET /ingestion/source-coverage/gaps
- [ ] GET /ingestion/source-coverage/{type}
- [ ] GET /ingestion/tier-distribution
- [ ] GET /ingestion/ethical-compliance
- [ ] GET /ingestion/ethical-compliance/score
- [ ] GET /ingestion/ethical-compliance/violations
- [ ] POST /ingestion/check-robots-txt
- [ ] POST /ingestion/check-rate-limit
- [ ] GET /ingestion/costs/monthly
- [ ] GET /ingestion/briefing-delivery

---

## Phase 2: Judge #6 Consensus Validation (3-4 hours)

### 2.1 Consensus Validator (1.5 hours)
**Files**: `services/judge-6/app/validators/consensus_validator.py`
- [ ] VCO integration (Simple + Atomic modes)
- [ ] Cost-aware routing (low/medium/high risk)
- [ ] Agreement scoring (unanimous/majority/split)
- [ ] Multi-model result aggregation

### 2.2 ATP 5-19 Risk Assessment Engine (1.5 hours)
**Files**: `services/judge-6/app/risk/atp_5_19.py`
- [ ] Probability matrix (A-E: Almost Certain → Unlikely)
- [ ] Severity matrix (I-IV: Catastrophic → Negligible)
- [ ] Risk levels (EH/H/M/L)
- [ ] Purpose/Reason/Brakes validation

### 2.3 Cost-Aware Routing Logic (1 hour)
**Files**: `services/judge-6/app/routing/cost_router.py`
- [ ] Low risk: Single Gemini ($0.01)
- [ ] Medium risk: Gemini + PyTorch ($0.05)
- [ ] High risk: VCO Simple Consensus ($0.15-$0.50)
- [ ] Catastrophic risk: VCO Atomic Consensus ($0.50-$2.00)

---

## Phase 3: Voice Intelligence + Cost Tracking (2-3 hours)

### 3.1 Voice Intelligence Source (1.5 hours)
**Files**: `services/ingestion/app/sources/voice.py`
- [ ] Connect to VCO transcript archive (SQLite + GCS)
- [ ] Auto Tier 1 classification for consensus results
- [ ] Quality scoring from multi-model agreement
- [ ] Full-text search integration

### 3.2 Unified Cost Tracker (1.5 hours)
**Files**: `services/ingestion/app/services/unified_cost_tracker.py`
- [ ] Integrate VCO cost tracking API
- [ ] PNKLN baseline tracking ($77)
- [ ] LLM serving tracking ($262)
- [ ] VCO queries tracking ($50 for 100 queries)
- [ ] Composite budget monitoring ($389 total)
- [ ] Budget alerts (75%, 90%, 100%)

---

## Phase 4: GKE Deployment (2-3 hours)

### 4.1 Kubernetes Manifests (1.5 hours)
**Files**: `k8s/base/**/*.yaml`

**Ingestion Layer**:
- [ ] CronJob (nightly 2:00 AM UTC, schedule: `0 2 * * *`)
- [ ] Deployment (API, replicas: 3, autoscaling 3-10)
- [ ] Service (ClusterIP + LoadBalancer)
- [ ] ConfigMap (source configs, rate limits)
- [ ] Secret (API keys)

**Voice Consensus**:
- [ ] Deployment (API, replicas: 2, autoscaling 2-6)
- [ ] Service (ClusterIP + LoadBalancer)
- [ ] ConfigMap (model configs, GCS bucket)

**Judge #6**:
- [ ] Deployment (API, replicas: 3, autoscaling 3-12)
- [ ] Service (ClusterIP)
- [ ] HPA (CPU 70%, memory 80%)

**Shared Infrastructure**:
- [ ] Cloud SQL Proxy (PostgreSQL connection)
- [ ] Ingress (Load Balancer with TLS)
- [ ] PersistentVolumeClaim (memory sync)
- [ ] ServiceMonitor (Prometheus)

### 4.2 Docker Images (1.5 hours)
**Files**: `services/*/Dockerfile`, `.dockerignore`
- [ ] Ingestion Layer (Python 3.11-slim)
- [ ] Voice Consensus (Python 3.11-slim)
- [ ] Judge #6 (Python 3.11-slim)
- [ ] Multi-stage builds for optimization

---

## Phase 5: Memory Sync + Monitoring (2-3 hours)

### 5.1 GCS Memory Sync System (1.5 hours)
**Files**: `k8s/base/shared/memory-sync-cronjob.yaml`, `scripts/sync_memory.py`
- [ ] Create GCS bucket: `gs://consensus-memory/`
- [ ] Memory sync CronJob (every 15 min)
- [ ] Init containers for pod startup sync
- [ ] Vertex Notebook startup script
- [ ] Local ↔ GCS bidirectional sync

### 5.2 Monitoring and Observability (1.5 hours)
**Files**: `k8s/base/shared/monitoring.yaml`, `dashboards/*.json`

**Metrics (Prometheus)**:
- [ ] Ingestion: runtime_minutes, items_per_day, source_diversity
- [ ] Judge #6: latency_p99, throughput_rps, consensus_cost
- [ ] VCO: query_cost, agreement_level, model_failures
- [ ] Costs: monthly_total, budget_utilization

**Dashboards (Grafana)**:
- [ ] Executive Dashboard (daily items, quality gates, costs)
- [ ] Technical Dashboard (service health, resource usage)
- [ ] Cost Dashboard (per-service breakdown, budget alerts)

---

## Phase 6: CI/CD + Production Hardening (3-4 hours)

### 6.1 CI/CD Pipeline (2 hours)
**Files**: `.github/workflows/*.yml`

**Build & Test**:
- [ ] Python services: lint (ruff), type-check (mypy), test (pytest)
- [ ] Coverage gates: ≥80%
- [ ] Security scanning: Trivy for Docker images

**Deploy**:
- [ ] Build Docker images on push to main
- [ ] Push to GCR: `gcr.io/${PROJECT_ID}/*`
- [ ] Deploy to GKE (staging on PR, production on main merge)
- [ ] Rollout verification (kubectl rollout status)

### 6.2 Integration Tests (1 hour)
**Files**: `tests/integration/*.py`
- [ ] End-to-end ingestion flow (source → storage → briefing)
- [ ] Judge #6 consensus validation
- [ ] Voice intelligence ingestion
- [ ] Cost tracking accuracy
- [ ] API endpoint smoke tests

### 6.3 Deploy to GKE and Validate (1 hour)
**Commands**:
```bash
# Create GKE cluster
gcloud container clusters create pnkln-core-stack \
  --region us-central1 --num-nodes 3 \
  --machine-type e2-standard-4

# Deploy all services
kubectl apply -k k8s/overlays/production/

# Verify deployments
kubectl get pods -n pnkln-core
kubectl get svc -n pnkln-core
kubectl get cronjob -n pnkln-core

# Run integration tests
pytest tests/integration/ -v

# Monitor metrics
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

---

## Delivery Milestones

### Milestone 1: Core Infrastructure (Hours 0-6)
- ✅ Phase 1.1: Database models
- [ ] Phase 1.2-1.6: Ingestion Layer complete
- **Deliverable**: Working Ingestion Layer with 15 API endpoints

### Milestone 2: Consensus Integration (Hours 6-10)
- [ ] Phase 2.1-2.3: Judge #6 with VCO
- [ ] Phase 3.1-3.2: Voice source + unified costs
- **Deliverable**: 50% error reduction on high-risk validations

### Milestone 3: Deployment Ready (Hours 10-13)
- [ ] Phase 4.1-4.2: GKE manifests + Docker images
- **Deliverable**: Deployable Kubernetes stack

### Milestone 4: Production Hardening (Hours 13-20)
- [ ] Phase 5.1-5.2: Memory sync + monitoring
- [ ] Phase 6.1-6.3: CI/CD + tests + deployment
- **Deliverable**: Production-ready PNKLN + VCO stack

---

## Success Criteria

### Technical KPIs
- [x] Database models (7) with Voice support
- [ ] Ingestion runtime ≤45 min/night
- [ ] Quality gate pass rate ≥95%
- [ ] Judge #6 latency p99 ≤90ms
- [ ] VCO consensus 50% error reduction
- [ ] API uptime ≥99.9%

### Financial KPIs
- [ ] Monthly cost ≤$389 (VCO + Ingestion + LLM)
- [ ] Cost per item ≤$0.10
- [ ] Budget utilization ≤100%
- [ ] ROI ≥401% (combined VCO + PNKLN)

### Quality KPIs
- [ ] Tier 1 percentage ≥20%
- [ ] Ethical compliance ≥95%
- [ ] Source diversity ≥5
- [ ] False positive rate ≤5% (Judge #6)

---

## Risk Mitigation (ATP 5-19)

| Risk | Probability | Severity | Level | Mitigation |
|------|-------------|----------|-------|------------|
| **Scope creep** | B (Likely) | III (Moderate) | M | Strict phase gates, MVP focus |
| **Integration failures** | C (Possible) | II (Critical) | H | Incremental testing, rollback plan |
| **Cost overrun** | C (Possible) | III (Moderate) | M | Budget alerts, cost-aware routing |
| **Deployment issues** | D (Unlikely) | II (Critical) | M | Staging environment, canary deploys |

---

## Next Steps

**Current Status**: Phase 1.1 complete (database models)
**Next Action**: Continue with Phase 1.2 (ethical compliance engine)

**Commit Strategy**:
1. Commit after each phase completion
2. Tag milestones (e.g., `v0.1.0-milestone-1`)
3. Push incrementally to enable rollback

**Recommended Workflow**:
- Implement Phases 1.2-1.6 (complete Ingestion Layer)
- Test locally with `uvicorn app.main:app --reload`
- Commit and push
- Continue with Judge #6 integration
- Deploy to GKE for end-to-end validation

---

**Sprint Started**: 2025-11-17
**Target Completion**: 2025-11-19 (assuming 8 hours/day over 2.5 days)
**Current Progress**: 5% (Phase 1.1/18 total phases)
