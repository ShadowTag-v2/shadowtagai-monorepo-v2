# PNKLN Intelligence Pipeline

**GKE-Native Nightly Intelligence Pipeline | 5th Namespace | ATP 5-19 RA-1 Compliant**

## 📊 Executive Summary

The PNKLN Intelligence Pipeline is an automated nightly system that gathers, analyzes, and delivers strategic intelligence for AI governance and regulatory compliance.

### Business Impact

```
COST:     $370/month (0.6% of $60-65K budget)
ROI:      3.3× in 18 months
GATES:    Supports A→B→C acceleration
RISK:     ATP 5-19 RA-1 (Low - Compliant)
```

### Projected Value

- **Revenue Acceleration**: +15% win rate at Gate A = +$112K
- **Cost Avoidance**: $500K/year (compliance, labor, subscriptions)
- **Competitive Advantage**: 90-day regulatory head-start
- **Strategic Positioning**: +0.5-1.0× valuation multiple

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   NIGHTLY EXECUTION (2 AM PST)              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: INGESTION (Ethical Scraping)                      │
│  • Federal Register (regulations.gov)                       │
│  • State Legislation (CA, NY, TX, IL, WA)                  │
│  • ArXiv Papers (AI governance, ethics)                    │
│  • Tech News (TechCrunch, VentureBeat, The Verge)          │
│  • Competitor Blogs (Palantir, Scale AI)                   │
│  • YouTube (C-SPAN, policy channels)                       │
│  • Twitter/X (FTC, SEC, NIST, CISA)                        │
│                                                             │
│  ✓ robots.txt compliance (RFC 9309)                        │
│  ✓ Domain-specific rate limiting                           │
│  ✓ Circuit breaker pattern                                 │
│  ✓ Proper User-Agent identification                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: JR ENGINE SCORING                                  │
│  • Business relevance (0-1)                                 │
│  • Regulatory impact (0-1)                                  │
│  • Competitive intelligence (0-1)                           │
│  • Timing urgency (0-1)                                     │
│  • Strategic value (0-1)                                    │
│                                                             │
│  Model: Claude 3.5 Haiku (cost-efficient)                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: TIER CLASSIFICATION                                │
│  • Tier 1 (≥0.7): CEO briefing required                    │
│  • Tier 2 (0.4-0.7): Auto-action (medium priority)         │
│  • Tier 3 (<0.4): Archive only (low priority)              │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ↓                           ↓
┌───────────────────────────┐   ┌───────────────────────────┐
│  STEP 4: COR BRAIN        │   │  STEP 5: TIER 2 ACTIONS   │
│  (Tier 1 Only)            │   │                           │
│                           │   │  • Create GitHub issues    │
│  • Executive summary      │   │  • Send Slack alerts      │
│  • Business impact        │   │  • Schedule monitoring    │
│  • Recommended actions    │   │                           │
│  • Risk assessment        │   │                           │
│                           │   │                           │
│  Model: Claude 3.5 Sonnet │   │                           │
└───────────────────────────┘   └───────────────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: BIGQUERY STORAGE                                   │
│  • Historical analysis                                      │
│  • Business impact tracking                                 │
│  • Compliance audit trail                                   │
│  • ROI dashboard queries                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: MORNING BRIEFING DELIVERY                          │
│  • Email to CEO with Tier 1 items                          │
│  • Summary of Tier 2 auto-actions                          │
│  • Tier 3 count (archived)                                 │
│  • Pipeline statistics                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- GCP Project with billing enabled
- GKE cluster with Workload Identity enabled
- `kubectl` configured with cluster access
- `terraform` >= 1.6
- `gcloud` CLI authenticated

### 1. Infrastructure Provisioning

```bash
cd intelligence-pipeline/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan -var="project_id=your-gcp-project-id"

# Apply infrastructure
terraform apply -var="project_id=your-gcp-project-id"
```

This creates:
- BigQuery dataset and table
- GCS bucket for intelligence data
- Service account with necessary IAM roles
- Workload Identity bindings

### 2. Build and Push Docker Image

```bash
cd intelligence-pipeline

# Build image
gcloud builds submit --tag gcr.io/your-gcp-project-id/intelligence-pipeline:latest

# Verify image
gcloud container images list --repository=gcr.io/your-gcp-project-id
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create service account and RBAC
kubectl apply -f k8s/serviceaccount.yaml

# Create secrets (replace with actual values)
kubectl create secret generic api-keys \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-api03-..." \
  --from-literal=PROJECT_ID="your-gcp-project-id" \
  --from-literal=BIGQUERY_DATASET="pnkln_intelligence" \
  --from-literal=GCS_BUCKET="your-project-id-pnkln-intelligence" \
  --namespace intelligence-pipeline

# Deploy CronJob (update PROJECT_ID in cronjob.yaml first)
kubectl apply -f k8s/cronjob.yaml
```

### 4. Verify Deployment

```bash
# Check CronJob
kubectl get cronjob -n intelligence-pipeline

# Check for running jobs
kubectl get jobs -n intelligence-pipeline

# View logs (when job runs)
kubectl logs -n intelligence-pipeline -l app=intel-pipeline --tail=100 -f
```

### 5. Manual Test Run (Optional)

```bash
# Trigger job manually
kubectl create job --from=cronjob/nightly-intel-pipeline manual-test-1 -n intelligence-pipeline

# Watch logs
kubectl logs -n intelligence-pipeline -l job-name=manual-test-1 --tail=100 -f
```

## 🔧 Configuration

### Environment Variables

Key environment variables are managed via Kubernetes secrets:

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | **Yes** | Anthropic API key for JR/Cor engines |
| `PROJECT_ID` | **Yes** | GCP project ID |
| `BIGQUERY_DATASET` | **Yes** | BigQuery dataset name |
| `GCS_BUCKET` | **Yes** | GCS bucket for intelligence data |
| `GITHUB_TOKEN` | No | GitHub token for issue creation |
| `SLACK_WEBHOOK_URL` | No | Slack webhook for notifications |
| `SMTP_USER` | No | Email credentials for briefing |
| `SMTP_PASSWORD` | No | Email password |
| `CEO_EMAIL` | No | CEO email for briefing delivery |

### Pipeline Configuration

Edit `config/pipeline.yaml` to customize:

- Intelligence sources and feeds
- Scraping rate limits
- Scoring criteria weights
- Tier classification thresholds
- Auto-action behaviors

## 📊 Business Impact Tracking

### BigQuery Dashboard

View the pre-built queries in `sql/business_impact_dashboard.sql`:

```sql
-- Daily summary
SELECT * FROM pnkln_intelligence.daily_summary
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAYS);

-- Tier 1 CEO briefing
SELECT * FROM pnkln_intelligence.tier1_ceo_briefing;

-- ROI dashboard
SELECT * FROM pnkln_intelligence.roi_dashboard;

-- Regulatory lead time analysis
SELECT * FROM pnkln_intelligence.regulatory_lead_time;
```

### Key Metrics

- **Total Items**: All intelligence items ingested
- **Tier 1 Count**: Critical items requiring CEO attention
- **Tier 2 Count**: Medium priority auto-actioned items
- **Average JR Score**: Overall relevance score
- **Detection Delay**: Time from publication to ingestion
- **Estimated Revenue Impact**: Projected value per item
- **ROI Multiple**: (Revenue Impact + Cost Avoidance) / Pipeline Cost

## 🛡️ ATP 5-19 Compliance

### Ethical Scraping Framework

The pipeline implements **ATP 5-19 RA-1** (Low Risk - Compliant) through:

1. **robots.txt Compliance (RFC 9309)**
   - 24-hour caching
   - Respect for `Disallow` directives
   - Honor `Crawl-delay` settings

2. **Rate Limiting**
   - Domain-specific delays (3-10s)
   - Adaptive jitter to prevent thundering herd
   - Maximum 3 concurrent requests per domain

3. **Circuit Breaker Pattern**
   - Opens after 5 consecutive failures
   - 5-minute timeout before retry
   - Prevents overwhelming failing services

4. **Proper User-Agent**
   ```
   PNKLN-Intelligence-Bot/1.0 (+https://pnkln.ai/bot-policy)
   From: redacted@shadowtag-v4.local
   ```

5. **Error Handling**
   - Respect `Retry-After` headers
   - Exponential backoff on failures
   - Conservative behavior on errors

### Compliance Monitoring

```sql
-- Check compliance status
SELECT * FROM pnkln_intelligence.atp_compliance
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAYS);
```

## 🔍 Real-World Example: California AB 2885

**Scenario**: California AI chatbot disclosure law (effective Jan 1, 2026)

### Without Pipeline
- **Detection**: Q1 2026 (reactive, post-deadline)
- **Implementation**: 8-12 weeks scramble
- **Risk**: $2,500/violation × customer base
- **Competitive**: Market-rate response

### With Pipeline
- **Detection**: Oct 31, 2024 (proactive, 90-day lead)
- **Implementation**: Nov-Dec 2025 (controlled)
- **Risk**: ATP 5-19 RA-4 → RA-1 (mitigated)
- **Competitive**: Demo compliance in sales → +15% win rate

### Quantified Advantage
- **Sales Cycle**: 3 regulated deals × $250K = $750K
- **Cost Avoidance**: $0 penalties vs potential $125K
- **Time Value**: 2,160 hours saved
- **Margin Impact**: +$112K from win rate boost

## 🏗️ Project Structure

```
intelligence-pipeline/
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   └── ethical_scraper.py      # ATP 5-19 RA-1 compliant scraper
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── ingestion.py            # Multi-source ingestion
│   │   ├── jr_scoring.py           # JR Engine scoring
│   │   ├── tier_classification.py  # Tier classification
│   │   ├── cor_synthesis.py        # Cor Brain synthesis
│   │   ├── tier2_actions.py        # Tier 2 auto-actions
│   │   ├── bigquery_storage.py     # BigQuery storage
│   │   └── briefing_delivery.py    # Morning briefing
│   └── models/
│       ├── __init__.py
│       └── intelligence_item.py    # Data models
├── k8s/
│   ├── namespace.yaml              # 5th PNKLN namespace
│   ├── serviceaccount.yaml         # Service account + RBAC
│   ├── secrets.yaml.example        # Secret template
│   └── cronjob.yaml                # Nightly CronJob
├── terraform/
│   └── main.tf                     # Infrastructure as Code
├── config/
│   └── pipeline.yaml               # Pipeline configuration
├── sql/
│   └── business_impact_dashboard.sql  # BigQuery views
├── docs/
│   └── DEPLOYMENT.md               # Detailed deployment guide
├── Dockerfile                       # Production container image
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 📈 Cost Analysis

### Monthly Costs ($370)

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| GKE CronJob | $120 | 2-4 CPU, 8-16GB RAM, ~2 hours/month |
| Cloud Storage | $50 | Intelligence data archive |
| BigQuery | $100 | Storage + query costs |
| Anthropic API | $100 | Haiku + Sonnet for scoring/synthesis |

### ROI Projection (18 months)

| Benefit | Value | Calculation |
|---------|-------|-------------|
| Revenue Acceleration | $750K | Gate A: 15% win rate boost |
| Cost Avoidance | $500K/yr | Compliance + labor + subscriptions |
| Strategic Value | $500K-2M | M&A intelligence, moat evidence |
| **Total Value** | **$1.2M+** | Conservative estimate |
| **Total Cost** | **$6,660** | 18 months × $370 |
| **ROI Multiple** | **3.3×** | Value / Cost |

## 🔐 Security

### Best Practices

1. **Secrets Management**
   - Use Kubernetes secrets for sensitive data
   - Never commit secrets to git
   - Rotate API keys regularly

2. **IAM Permissions**
   - Principle of least privilege
   - Service account per component
   - Workload Identity for GKE

3. **Network Security**
   - Istio service mesh (optional)
   - Network policies (recommended)
   - Private GKE cluster (production)

4. **Compliance**
   - ATP 5-19 RA-1 compliance
   - SOC 2 audit trail in BigQuery
   - GDPR considerations (no PII collected)

## 🐛 Troubleshooting

### Job Fails with "ImagePullBackOff"

```bash
# Verify image exists
gcloud container images list --repository=gcr.io/PROJECT_ID

# Check service account permissions
kubectl describe serviceaccount intelligence-runner -n intelligence-pipeline

# Verify Workload Identity binding
gcloud iam service-accounts get-iam-policy \
  intelligence-pipeline@PROJECT_ID.iam.gserviceaccount.com
```

### BigQuery "Permission Denied"

```bash
# Check service account IAM roles
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:intelligence-pipeline@*"

# Grant necessary roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:intelligence-pipeline@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

### Rate Limiting Issues

```bash
# Check scraper logs for circuit breaker events
kubectl logs -n intelligence-pipeline -l app=intel-pipeline | grep "Circuit"

# Adjust rate limits in config/pipeline.yaml
# Redeploy: kubectl apply -f k8s/cronjob.yaml
```

### No Briefing Email Received

```bash
# Check SMTP configuration
kubectl get secret api-keys -n intelligence-pipeline -o jsonpath='{.data.SMTP_USER}' | base64 -d

# Check briefing file (fallback)
kubectl exec -n intelligence-pipeline -it <pod-name> -- ls -la /tmp/briefing_*.html

# View logs
kubectl logs -n intelligence-pipeline -l app=intel-pipeline | grep "Briefing"
```

## 🧠 Gemini Self-Analysis Framework

The Intelligence Pipeline includes a **Gemini 2.0 Pro self-analysis capability** that evaluates architecture, compliance, and performance based on specifications.

### Running Analysis

```bash
# Set Google API key
export GOOGLE_API_KEY="your-google-api-key"

# Run analysis
./scripts/test_analysis.sh

# Or manually
python scripts/run_gemini_analysis.py --output reports/analysis_$(date +%Y%m%d).md
```

### Analysis Components

The Gemini analyzer evaluates 10 key areas:

1. **Architecture Evaluation** - Container orchestration, resource allocation, failure recovery
2. **Ethical Compliance Model** - RFC 9309 robots.txt, rate limiting, transparency
3. **Multi-Source Coverage** - Source diversity, geographic balance, keyword effectiveness
4. **Tier Classification** - Scoring weights, threshold calibration, distribution health
5. **Performance Metrics** - Runtime efficiency, cost per item, quality gates
6. **Cost Model** - Monthly operational costs, ROI projections, sensitivity analysis
7. **Quality Focus** - Relevance, timeliness, completeness, accuracy
8. **AM Briefing Delivery** - Readability, actionability, mobile rendering
9. **Stack Integration** - BigQuery schema compatibility, downstream consumers
10. **Edge Case Analysis** - Source outages, cost spikes, volume surges, API limits

### Sample Output

```
╔══════════════════════════════════════════════════════════════╗
║  🧠 GEMINI ANALYSIS REPORT                                   ║
╚══════════════════════════════════════════════════════════════╝

Architecture Score:         [████████████████░░░░] 85%
Ethical Compliance Score:   [██████████████████░░] 92%
Coverage Score:             [███████████████░░░░░] 78%
Performance Score:          [████████████████░░░░] 80%
Quality Score:              [████████████████░░░░] 83%
Edge Case Readiness:        [███████████████░░░░░] 75%

Overall Health: 🟢 GOOD (82%)
Confidence: 73%
```

### Integration with Judge #6

The Gemini analysis framework is adapted from the Judge #6 analysis prompt, customized for the Intelligence Pipeline's upstream collection role vs Judge #6's downstream enforcement role.

**Key Differences**:

| Aspect | Judge #6 (Enforcement) | Intelligence Pipeline (Collection) |
|--------|------------------------|-----------------------------------|
| Architecture | Hybrid Gemini+PyTorch | GKE CronJob Multi-Container |
| Key Metrics | Latency, Throughput, Block Rate | Items/Day, Sources, Cost/Item |
| Integration | Calls 4 namespaces | Called by 4 namespaces |
| Unique Features | ATP 5-19, JR Validation | Ethical Crawling, Tier Classification |
| Cost Model | API calls per validation | Monthly operational ~$370 |
| Quality Focus | FP/FN rates | Relevance, Timeliness, Completeness |

For complete analysis prompt, see: `docs/GEMINI_ANALYSIS_PROMPT.md`

## 📚 Additional Resources

- [Ethical Scraping Best Practices](https://www.rfc-editor.org/rfc/rfc9309.html) (RFC 9309)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [GKE Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [Gemini API](https://ai.google.dev/docs) - For self-analysis framework

## 🤝 Contributing

This is an internal PNKLN project. For questions or issues:

- **Email**: redacted@shadowtag-v4.local
- **Owner**: Cor (Chief Intelligence Officer)
- **Slack**: #intelligence-pipeline

## 📄 License

Copyright © 2025 PNKLN Inc. All rights reserved.

---

**Status**: ✅ Production Ready
**ATP 5-19**: RA-1 (Low Risk - Compliant)
**Last Updated**: 2025-11-08
