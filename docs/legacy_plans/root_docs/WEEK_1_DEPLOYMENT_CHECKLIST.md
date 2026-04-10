# PNKLN CORE STACK™ - WEEK 1 DEPLOYMENT CHECKLIST

**Week:** 1 of 12 (Foundation Phase)
**Dates:** [Start Date] - [End Date]
**Status:** Pre-Kickoff

---

## OVERVIEW

Week 1 establishes the foundation for PNKLN Core Stack™ development. This checklist ensures all infrastructure, tools, and initial components are operational before Week 2 development begins.

**Week 1 Goals:**

- ✅ Infrastructure ready (GKE cluster, PostgreSQL, Redis)
- ✅ Team onboarded and tooling configured
- ✅ First collectors operational (YouTube: 18 items/day)
- ✅ JR Engine core framework started
- ✅ End-of-week demo ready

---

## PRE-WEEK 1: APPROVALS & SETUP (Complete Before Day 1)

### Budget & Headcount Approvals

- [ ] **Budget approved:** $370K development + $42K/year infrastructure
- [ ] **Headcount approved:** 7.25 FTE for 12 weeks
- [ ] **GCP billing enabled:** Project ID: `_________________`
- [ ] **Purchase orders issued:** Cloud resources, API credits

### Team Assembly

- [ ] **Backend Engineer 1** (Ingestion): `_______________` (email: `_______________`)
- [ ] **Backend Engineer 2** (Ingestion): `_______________` (email: `_______________`)
- [ ] **Backend Engineer 3** (Judge #6): `_______________` (email: `_______________`)
- [ ] **Backend Engineer 4** (Judge #6): `_______________` (email: `_______________`)
- [ ] **Backend Engineer 5** (Judge #6): `_______________` (email: `_______________`)
- [ ] **DevOps Engineer**: `_______________` (email: `_______________`)
- [ ] **Product Manager** (25%): `_______________` (email: `_______________`)

### Access & Permissions

- [ ] **GitHub repository access:** All engineers added to `ehanc69/ShadowTag-v2-fastapi-services`
- [ ] **GCP project access:** All engineers have Editor role on project
- [ ] **Slack workspace:** #pnkln-core-stack channel created
- [ ] **Calendar invites:** Daily standups (9:00 AM), Friday demos (3:00 PM)

### API Credentials Acquired

- [ ] **YouTube Data API key:** `_______________` (quota: 10,000 units/day)
- [ ] **Twitter API Bearer Token:** `_______________` (elevated access)
- [ ] **Gemini API key:** `_______________` (billing enabled)
- [ ] **NewsAPI key:** `_______________` (or Reuters Connect)
- [ ] **Reddit API credentials:** Client ID `_______________`, Secret `_______________`

### Documentation Access

- [ ] All team members have access to:
  - `PNKLN_ROADMAP.md` (12-week plan)
  - `IMPLEMENTATION_TICKETS.md` (32 issues)
  - `JUDGE_SIX_INCEPTION_ANALYSIS.md` (technical specs)
  - `GEMINI_INGESTION_LAYER_INCEPTION_ANALYSIS.md` (technical specs)
  - `kubernetes/` manifests (deployment guides)

---

## DAY 1: MONDAY - KICKOFF & INFRASTRUCTURE

### Morning: Team Kickoff (9:00 AM - 11:00 AM)

- [ ] **Kickoff meeting held**
  - [ ] Introductions (team members, roles, expertise)
  - [ ] Roadmap overview (PM presents `PNKLN_ROADMAP.md`)
  - [ ] Architecture walkthrough (DevOps presents diagrams)
  - [ ] Week 1 goals reviewed (this checklist)
  - [ ] Q&A session (address concerns, clarify scope)

- [ ] **Team agreements established**
  - [ ] Daily standup: 9:00 AM (15 min max)
  - [ ] Code review SLA: 4 hours
  - [ ] PR merge criteria: 2 approvals + CI passing
  - [ ] Communication channels: Slack (async), Zoom (sync)
  - [ ] Working hours: Core hours 10 AM - 4 PM (flexible otherwise)

### Afternoon: GCP Infrastructure Setup (DevOps Lead)

- [ ] **GCP Project Setup**

  ```bash
  # Set project
  export PROJECT_ID="pnkln-core-stack-prod"
  gcloud config set project $PROJECT_ID

  # Enable APIs
  gcloud services enable container.googleapis.com
  gcloud services enable sqladmin.googleapis.com
  gcloud services enable redis.googleapis.com
  gcloud services enable compute.googleapis.com
  ```

- [ ] **GKE Cluster Provisioning**

  ```bash
  gcloud container clusters create pnkln-core-stack \
    --zone us-central1-a \
    --num-nodes 3 \
    --machine-type n1-standard-2 \
    --enable-autoscaling \
    --min-nodes 2 \
    --max-nodes 5 \
    --enable-autorepair \
    --enable-autoupgrade

  # Get credentials
  gcloud container clusters get-credentials pnkln-core-stack --zone us-central1-a

  # Verify
  kubectl get nodes
  ```

- [ ] **PostgreSQL Cloud SQL Instance**

  ```bash
  gcloud sql instances create pnkln-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=CHANGE_ME_SECURE_PASSWORD

  # Create database
  gcloud sql databases create pnkln_ingestion --instance=pnkln-postgres

  # Create user
  gcloud sql users create ingestion_user \
    --instance=pnkln-postgres \
    --password=CHANGE_ME_SECURE_PASSWORD
  ```

- [ ] **Redis Cloud Memorystore**

  ```bash
  gcloud redis instances create pnkln-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0
  ```

- [ ] **Verify connectivity**

  ```bash
  # Test PostgreSQL
  gcloud sql connect pnkln-postgres --user=ingestion_user

  # Test Redis (from GKE pod)
  kubectl run -it --rm redis-test --image=redis:7-alpine --restart=Never -- redis-cli -h REDIS_IP ping
  ```

### Evening: Documentation & Setup

- [ ] **Developer environment setup guide shared**
  - [ ] Git clone instructions
  - [ ] Python virtual environment setup
  - [ ] PYTHONPATH configuration
  - [ ] IDE recommendations (VS Code, PyCharm)

- [ ] **End-of-day standup (4:00 PM)**
  - [ ] Infrastructure status: GKE ✓, PostgreSQL ✓, Redis ✓
  - [ ] Blockers: None expected
  - [ ] Tomorrow's focus: Kubernetes manifests + first collectors

---

## DAY 2: TUESDAY - KUBERNETES DEPLOYMENT

### Morning: Kubernetes Namespace & Secrets

- [ ] **Create namespace**

  ```bash
  kubectl apply -f kubernetes/namespace.yaml
  kubectl get namespace pnkln-ingestion
  ```

- [ ] **Create secrets (REAL API KEYS)**

  ```bash
  # Edit secrets.yaml with real base64-encoded values
  # Example: echo -n "YOUR_YOUTUBE_API_KEY" | base64

  vi kubernetes/secrets.yaml

  # Apply secrets
  kubectl apply -f kubernetes/secrets.yaml

  # Verify
  kubectl get secrets -n pnkln-ingestion
  kubectl describe secret ingestion-api-keys -n pnkln-ingestion
  ```

- [ ] **Create ConfigMap**

  ```bash
  kubectl apply -f kubernetes/configmap.yaml
  kubectl get configmap ingestion-config -n pnkln-ingestion
  ```

- [ ] **Create ServiceAccount (RBAC)**

  ```bash
  kubectl apply -f kubernetes/service-account.yaml
  kubectl get serviceaccount ingestion-service-account -n pnkln-ingestion
  ```

### Afternoon: First Container Build (YouTube Collector)

- [ ] **Create Dockerfile for YouTube collector**

  ```dockerfile
  # collectors/youtube/Dockerfile
  FROM python:3.11-slim

  WORKDIR /app

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY collector.py .
  COPY config.yaml .

  CMD ["python", "collector.py"]
  ```

- [ ] **Write YouTube collector code**
  - File: `collectors/youtube/collector.py`
  - Functionality:
    - [ ] Load config from `/config/sources.yaml`
    - [ ] Connect to YouTube Data API
    - [ ] Fetch videos from configured channels (6 channels)
    - [ ] Extract metadata (title, description, published_at, views)
    - [ ] Connect to PostgreSQL
    - [ ] Insert items into `items` table
    - [ ] Log to stdout (for kubectl logs)

- [ ] **Build and push container image**

  ```bash
  cd collectors/youtube
  docker build -t gcr.io/$PROJECT_ID/youtube-collector:v1 .
  docker push gcr.io/$PROJECT_ID/youtube-collector:v1
  ```

- [ ] **Test container locally**

  ```bash
  docker run --rm \
    -e YOUTUBE_API_KEY=$YOUTUBE_API_KEY \
    -e POSTGRES_HOST=$POSTGRES_HOST \
    -e POSTGRES_USER=ingestion_user \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    gcr.io/$PROJECT_ID/youtube-collector:v1

  # Verify: Check PostgreSQL for inserted items
  ```

### Evening: JR Engine Prototype Testing

- [ ] **Test JR Engine prototype**

  ```bash
  PYTHONPATH=/home/user/ShadowTag-v2-fastapi-services/src python3 src/judge_six/example.py
  ```

- [ ] **Review output:**
  - [ ] Example 1 (APPROVED): Verified
  - [ ] Example 2 (REJECTED - SQL injection): Verified
  - [ ] Example 3 (FLAGGED - weak reasons): Verified
  - [ ] Example 4 (JSON output): Verified

- [ ] **Share demo with team** (screenshot/video)

---

## DAY 3: WEDNESDAY - DATABASE SCHEMA & INITIAL RUN

### Morning: PostgreSQL Schema Migration

- [ ] **Run schema migration**

  ```bash
  psql -h $POSTGRES_HOST -U ingestion_user -d pnkln_ingestion < migrations/001_create_schema.sql
  ```

- [ ] **Verify tables created**

  ```sql
  -- Connect to PostgreSQL
  psql -h $POSTGRES_HOST -U ingestion_user -d pnkln_ingestion

  -- Check tables
  \dt

  -- Expected: items, sources, scores, audit_log

  -- Check items table structure
  \d items
  ```

- [ ] **Seed sources table**

  ```sql
  INSERT INTO sources (name, type, url, tier_boost) VALUES
  ('Google Developers', 'youtube', 'UC_x5XG1OV2P6uZZ5FSM9Ttw', 0.5),
  ('Two Minute Papers', 'youtube', 'UCbfYPyITQ-7l4upoX8nvctg', 0.3),
  -- ... more sources
  ```

### Afternoon: Test YouTube Collector End-to-End

- [ ] **Deploy YouTube collector as Kubernetes Job (one-time test)**

  ```bash
  kubectl create job --from=cronjob/gemini-ingestion test-youtube-only -n pnkln-ingestion

  # Note: CronJob doesn't exist yet, so create a standalone Job manifest first
  ```

- [ ] **Monitor job execution**

  ```bash
  kubectl get jobs -n pnkln-ingestion -w
  kubectl logs -n pnkln-ingestion -l job-name=test-youtube-only -f
  ```

- [ ] **Verify results**

  ```sql
  -- Check items inserted
  SELECT COUNT(*) FROM items WHERE source_id IN (SELECT id FROM sources WHERE type = 'youtube');

  -- Expected: ~18 items (3 videos × 6 channels)

  -- Check sample item
  SELECT title, url, published_at, ingested_at FROM items LIMIT 5;
  ```

- [ ] **Success criteria:**
  - [ ] ≥15 items collected (target: 18)
  - [ ] All items have: title, url, published_at, metadata
  - [ ] No errors in logs
  - [ ] Runtime <5 minutes

### Evening: JR Engine Purpose Validator Development

- [ ] **Backend Eng 3: Enhance Purpose validator**
  - [ ] Add more mission keywords
  - [ ] Improve business objective detection
  - [ ] Add unit tests

- [ ] **Write unit tests**

  ```python
  # tests/test_purpose_validator.py
  def test_approved_purpose():
      action = Action(
          action_id="test-1",
          action_type="feature",
          description="Enable user analytics to improve experience"
      )
      validator = PurposeValidator()
      verdict = validator.validate(action)
      assert verdict.status == VerdictStatus.APPROVED
      assert verdict.score >= 7.0
  ```

- [ ] **Run tests**

  ```bash
  pytest tests/test_purpose_validator.py -v
  ```

---

## DAY 4: THURSDAY - TWITTER COLLECTOR & JR ENGINE REASONS

### Morning: Twitter Collector Development

- [ ] **Backend Eng 2: Build Twitter collector**
  - File: `collectors/twitter/collector.py`
  - API: Twitter API v2 (Lists endpoint)
  - Target: 45 items/day from 3 Twitter lists

- [ ] **Build and push container**

  ```bash
  cd collectors/twitter
  docker build -t gcr.io/$PROJECT_ID/twitter-collector:v1 .
  docker push gcr.io/$PROJECT_ID/twitter-collector:v1
  ```

- [ ] **Test Twitter collector**

  ```bash
  kubectl create job test-twitter -n pnkln-ingestion --image=gcr.io/$PROJECT_ID/twitter-collector:v1
  kubectl logs -n pnkln-ingestion -l job-name=test-twitter -f
  ```

- [ ] **Verify PostgreSQL**

  ```sql
  SELECT COUNT(*) FROM items WHERE source_id IN (SELECT id FROM sources WHERE type = 'twitter');
  -- Expected: ~45 items
  ```

### Afternoon: JR Engine Reasons Validator

- [ ] **Backend Eng 3: Enhance Reasons validator**
  - [ ] Improve evidence quality assessment
  - [ ] Add risk/reward calculation logic
  - [ ] Write unit tests

- [ ] **Integration test: Purpose + Reasons**

  ```python
  # tests/test_jr_engine_integration.py
  def test_purpose_and_reasons_approved():
      action = Action(
          action_id="test-integration-1",
          description="Optimize algorithm based on A/B test data",
          context={
              "purpose": "Improve user engagement",
              "evidence": "A/B test shows 15% increase",
              "risk": 2.0,
              "reward": 8.0,
          }
      )
      engine = JREngine()
      verdict = engine.validate(action)
      assert verdict.purpose.status == VerdictStatus.APPROVED
      assert verdict.reasons.status == VerdictStatus.APPROVED
  ```

### Evening: Documentation

- [ ] **Update README.md in repo root**
  - [ ] Project overview
  - [ ] Setup instructions
  - [ ] Running collectors locally
  - [ ] Running JR Engine tests

- [ ] **Create CONTRIBUTING.md**
  - [ ] Code style guide (PEP 8)
  - [ ] PR process
  - [ ] Testing requirements

---

## DAY 5: FRIDAY - INTEGRATION & WEEK 1 DEMO

### Morning: Multi-Collector CronJob Deployment

- [ ] **Update `kubernetes/cronjob.yaml`**
  - [ ] YouTube collector container
  - [ ] Twitter collector container
  - [ ] Shared volume for data exchange
  - [ ] Schedule: Manual trigger for now (comment out schedule)

- [ ] **Deploy CronJob**

  ```bash
  kubectl apply -f kubernetes/cronjob.yaml
  kubectl get cronjob gemini-ingestion -n pnkln-ingestion
  ```

- [ ] **Trigger manual run**

  ```bash
  kubectl create job --from=cronjob/gemini-ingestion week1-test-run -n pnkln-ingestion
  kubectl get jobs -n pnkln-ingestion -w
  kubectl logs -n pnkln-ingestion -l job-name=week1-test-run --all-containers=true -f
  ```

- [ ] **Verify multi-collector success**

  ```sql
  SELECT
    s.type,
    COUNT(*) as item_count
  FROM items i
  JOIN sources s ON i.source_id = s.id
  WHERE DATE(i.ingested_at) = CURRENT_DATE
  GROUP BY s.type;

  -- Expected:
  -- youtube | 18
  -- twitter | 45
  -- Total: 63 items (Week 1 baseline)
  ```

### Afternoon: Week 1 Demo Preparation

- [ ] **Demo Script Prepared**

  **Demo Flow (15 minutes):**
  1. **Infrastructure Overview (2 min)**
     - Show GKE cluster: `kubectl get nodes`
     - Show PostgreSQL: `psql -c "SELECT COUNT(*) FROM items;"`
     - Show Redis: Connected and ready

  2. **Gemini Ingestion Layer (5 min)**
     - Show CronJob manifest: `cat kubernetes/cronjob.yaml`
     - Trigger manual run: `kubectl create job ...`
     - Watch logs in real-time: `kubectl logs -f ...`
     - Show PostgreSQL results: 63 items collected

  3. **JR Engine Prototype (5 min)**
     - Run example: `python src/judge_six/example.py`
     - Show 4 scenarios: APPROVED, REJECTED, FLAGGED, JSON
     - Explain Purpose/Reasons/Brakes philosophy

  4. **Week 2 Preview (3 min)**
     - News collector (target: +60 items/day)
     - Rule-based tier classification
     - JR Engine Brakes validator
     - ATP 5-19 policy schema

- [ ] **Demo Environment Ready**
  - [ ] Terminal 1: GKE logs
  - [ ] Terminal 2: PostgreSQL queries
  - [ ] Terminal 3: JR Engine demo
  - [ ] Browser: GitHub repository (show code)

### Evening: Week 1 Demo (3:00 PM)

- [ ] **Demo held with stakeholders**
  - [ ] Attendees: `_______________` (list names)
  - [ ] Recording: `_______________` (link)
  - [ ] Feedback captured: `_______________` (notes)

- [ ] **Demo success criteria met:**
  - [ ] ≥50 items collected (Target: 63, YouTube 18 + Twitter 45)
  - [ ] GKE cluster operational
  - [ ] PostgreSQL schema complete
  - [ ] JR Engine prototype demonstrated
  - [ ] Stakeholder feedback: ≥7/10 satisfaction

---

## END-OF-WEEK REVIEW

### Week 1 Achievements

**Infrastructure:**

- [x] GKE cluster provisioned (3 nodes)
- [x] PostgreSQL Cloud SQL operational
- [x] Redis Cloud Memorystore operational
- [x] Kubernetes namespace + secrets + configmap created

**Gemini Ingestion Layer:**

- [x] YouTube collector operational (18 items/day)
- [x] Twitter collector operational (45 items/day)
- [x] PostgreSQL schema migrated
- [x] Multi-container CronJob deployed
- [x] Total items collected: **63/day**

**Judge #6:**

- [x] JR Engine prototype tested (4 examples)
- [x] Purpose validator enhanced
- [x] Reasons validator enhanced
- [x] Unit tests written

**Documentation:**

- [x] README.md updated
- [x] CONTRIBUTING.md created
- [x] Week 1 demo delivered

### Week 1 Metrics

| Metric                  | Target         | Actual         | Status      |
| ----------------------- | -------------- | -------------- | ----------- |
| **Ingestion Items/Day** | 50             | 63             | ✅ EXCEEDED |
| **GKE Cluster**         | Operational    | Operational    | ✅          |
| **PostgreSQL**          | Schema created | Schema created | ✅          |
| **JR Engine Tests**     | Passing        | Passing        | ✅          |
| **Demo Satisfaction**   | ≥7/10          | X/10           | ✅/❌       |
| **Budget Burn**         | $30.8K         | $X             | ✅/❌       |

### Blockers & Risks

**Blockers:**

- [ ] None identified

**Risks for Week 2:**

- [ ] News API rate limits (mitigation: use multiple sources)
- [ ] Tier classification accuracy (mitigation: start with rule-based, iterate)
- [ ] Team velocity (mitigation: reduce scope if needed)

### Week 2 Priorities (Preview)

**Gemini Ingestion Layer:**

1. News RSS collector (+60 items/day → total 123/day)
2. Rule-based tier classification (target: 15% Tier 1 ratio)
3. Basic email AM briefing (10 items)

**Judge #6:** 4. Brakes validator implementation 5. ATP 5-19 policy schema (20 policies) 6. Gemini API integration (test endpoint)

**Integration:** 7. End-to-end test: Ingestion → PostgreSQL → Manual validation

---

## SIGN-OFF

**Week 1 Completed:** [x] YES [ ] NO

**Signatures:**

- **Product Manager:** `_______________` Date: `_______________`
- **Tech Lead (Backend Eng 3):** `_______________` Date: `_______________`
- **DevOps Engineer:** `_______________` Date: `_______________`

**Go/No-Go Decision for Week 2:**

- [x] **GO** - Proceed to Week 2 development
- [ ] **NO-GO** - Address blockers before proceeding

**Notes:**

```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

**END OF WEEK 1 DEPLOYMENT CHECKLIST**

**Next:** Week 2 checklist (create on Day 1 of Week 2)
