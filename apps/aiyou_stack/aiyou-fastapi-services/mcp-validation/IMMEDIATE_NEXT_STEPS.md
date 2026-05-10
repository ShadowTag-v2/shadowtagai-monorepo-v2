# MCP Integration - Immediate Next Steps

## Hour 0-4 Execution Guide

**Status:** Ready to execute
**Decision:** Awaiting your GO approval
**Timeline:** 72 hours to GO/NO-GO decision

---

## YOU ARE HERE

```

┌─────────────────────────────────────────────────────────┐
│  HOUR 0: YOU JUST SAID "GO"                            │
│  All validation files created and ready to deploy       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │  HOUR 0-4: Setup        │  ← YOU ARE HERE
            │  Deploy infrastructure  │
            └─────────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │  HOUR 4-24: Testing     │
            │  Latency + security     │
            └─────────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │  HOUR 24-48: Audit      │
            │  3PAO scoping           │
            └─────────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │  HOUR 48-72: Design     │
            │  Architecture review    │
            └─────────────────────────┘
                          │
                          ▼
            ┌─────────────────────────┐
            │  HOUR 72: DECISION      │
            │  GO / PIVOT / ABORT     │
            └─────────────────────────┘

```

---

## CRITICAL: WHAT YOU NEED RIGHT NOW

Before you can start Hour 0, you need these approvals and resources:

### 1. Budget Approvals (REQUIRED)

```

[ ] $150K integration budget (12-week timeline)
[ ] $150-250K security audit budget (FedRAMP 3PAO)
[ ] Total: $300-400K approved for Year 1

Decision maker: CFO
Timeline: Need approval NOW (blocks all work)

```

### 2. GCP Resources (REQUIRED)

```

[ ] GCP project ID with billing enabled
[ ] Project owner permissions for deployment engineer
[ ] BigQuery API enabled
[ ] GKE API enabled
[ ] Vertex AI API enabled

Decision maker: Infrastructure lead
Timeline: Can be set up in 1 hour (non-blocking if started now)

```

### 3. Anthropic API Access (REQUIRED)

```

[ ] Anthropic API key (Production tier)
[ ] 10K RPM rate limit (negotiate with Anthropic)
[ ] Mention regulated market use case (may get priority support)

Decision maker: You (Erik) or CTO
Timeline: Contact Anthropic NOW (may take 24-48 hours)
Action: Email partnerships@anthropic.com with:
  Subject: "Regulated AI Infrastructure - MCP Code Execution Evaluation"
  Body: "We are evaluating MCP code execution for FedRAMP-regulated AI
         infrastructure. Need 10K RPM for 72-hour validation sprint.
         Timeline: Starting [DATE], need access ASAP."

```

### 4. Engineering Resources (REQUIRED)

```

[ ] 1× DevOps engineer (GKE deployment, full-time Week 1)
[ ] 1× ML engineer (validation testing, full-time Week 1)
[ ] 1× Security engineer (compliance, 50% time Week 1-2)
[ ] 1× Principal engineer (architecture review, 25% time Week 2-3)

Decision maker: Engineering manager
Timeline: Need resource allocation NOW

```

### 5. Vendor Contacts (RECOMMENDED for Hour 24-48)

```

[ ] 3PAO partner shortlist (NuBex, Kratos SecureInfo, Coalfire)
[ ] FedRAMP PMO liaison (schedule pre-consultation call)
[ ] Internal security/compliance team (CISO + compliance lead)

Decision maker: Compliance lead
Timeline: Week 1 (non-blocking for Hour 0-4)

```

---

## HOUR 0-1: IMMEDIATE ACTIONS (DO THIS NOW)

### Action 1: Reply "APPROVED" or Raise Objections

**Owner:** You (Erik)
**Timeline:** NOW (next 15 minutes)

Reply to this message with one of:

```

APPROVED - Proceed with full validation sprint
OBJECTION - [Specific concern: budget/timeline/risk]
QUESTION - [Specific question before approval]

```

If APPROVED, I will immediately start Hour 0-4 setup.

---

### Action 2: Contact Anthropic (Parallel with everything else)

**Owner:** You or CTO
**Timeline:** Within 1 hour

**Email Template:**

```

To: partnerships@anthropic.com
Subject: Regulated AI Infrastructure - MCP Code Execution Evaluation

Hi Anthropic team,

We're Erik Hansen (ehanc69) evaluating Anthropic MCP code execution
for production deployment in FedRAMP-regulated AI infrastructure
(Judge 6 v2.0 governance system).

Request:


- 10K RPM rate limit for 72-hour validation sprint


- Starting: [DATE]


- Use case: Replacing traditional tool calls with code generation


- Target: p99 ≤75ms latency, FedRAMP Moderate compliance

This is a high-value regulated market deployment. If successful,
we become first-mover in AI code execution for federal agencies.

Can you expedite API access and provide technical support during
validation?

Thanks,
Erik Hansen
GitHub: @ehanc69

```

**Expected Response Time:** 24-48 hours (mention urgency)

---

### Action 3: Approve Budget ($300-400K)

**Owner:** CFO (you approve, CFO signs off)
**Timeline:** Within 4 hours

**Budget Breakdown:**

```

Integration (12 weeks):


- 2× contractors @ $150/hr × 40hr/week × 12 weeks = $144K


- Infrastructure (GKE, Vertex AI) = $6K


- Total integration: $150K

Security Audit (6 months):


- 3PAO assessment (NuBex/Kratos/Coalfire) = $150-250K


- Internal security team (allocated from existing budget)


- Total audit: $150-250K

Year 1 Total: $300-400K
Year 1 Savings: $400K (if successful)
Year 1 Net: $0-100K

5-Year NPV: +$1.85M (assuming success)

```

**Approval Process:**


1. Forward this budget breakdown to CFO


2. Request signature on budget allocation


3. Confirm contractor hiring approved

---

### Action 4: Allocate Engineering Resources

**Owner:** Engineering Manager
**Timeline:** Within 4 hours

**Resource Needs:**

```

Week 1 (Hour 0-24): Setup + Validation


- DevOps engineer: Full-time (GKE deployment)


- ML engineer: Full-time (validation testing)


- Total: 2 FTE-weeks

Week 2-3 (Hour 24-72): Audit + Architecture


- Security engineer: 50% time (compliance scoping)


- Principal engineer: 25% time (architecture review)


- Total: 1.5 FTE-weeks

Week 1-12: Integration (if GO decision)


- 2× contractors: Full-time (implementation)


- 1× internal engineer: 50% time (oversight)


- Total: 30 FTE-weeks

Total commitment: 33.5 FTE-weeks over 12 weeks

```

**Approval Process:**


1. Confirm DevOps + ML engineers available Week 1


2. Allocate their time (block calendars)


3. Notify them of validation sprint kickoff

---

## HOUR 1-2: GCP INFRASTRUCTURE SETUP

**Owner:** DevOps Engineer
**Prerequisites:** GCP project ID, budget approved

### Step 1: Set GCP Project

```bash

# Replace PROJECT_ID with your actual GCP project

export PROJECT_ID="your-gcp-project"
export REGION="us-central1"
export ZONE="us-central1-a"

gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

```

### Step 2: Enable Required APIs

```bash
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable notebooks.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

```

### Step 3: Create GKE Cluster with gVisor

```bash

# Create GKE cluster (3 nodes, gVisor enabled)

gcloud container clusters create mcp-dev-cluster \
  --zone=$ZONE \
  --machine-type=n1-standard-4 \
  --num-nodes=3 \
  --enable-sandbox \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=10 \
  --addons=Istio,CloudRun,HorizontalPodAutoscaling \
  --workload-pool=$PROJECT_ID.svc.id.goog \
  --enable-stackdriver-kubernetes

# This takes ~10-15 minutes

```

### Step 4: Verify gVisor Enabled

```bash

# Check that gVisor runtime class exists

kubectl get runtimeclass

# Expected output:

# NAME     HANDLER   AGE

# gvisor   runsc     1m

```

If `gvisor` runtime class is missing, this is a **SHOWSTOPPER**. Stop and escalate.

### Step 5: Create BigQuery Dataset

```bash

# Create dataset for audit logs

bq mk \
  --dataset \
  --location=US \
  --description="MCP code execution audit logs" \
  $PROJECT_ID:mcp_audit_logs

# Create table schema

bq mk \
  --table \
  $PROJECT_ID:mcp_audit_logs.code_executions \
  timestamp:TIMESTAMP,user_id:STRING,session_id:STRING,code_hash:STRING,code_length:INTEGER,execution_time_ms:FLOAT,success:BOOLEAN,error:STRING,security_violations:STRING,resource_usage:STRING,sandbox_id:STRING

```

### Step 6: Create Service Account for MCP Server

```bash

# Create service account

gcloud iam service-accounts create mcp-server \
  --display-name="MCP Code Execution Server" \
  --description="Service account for MCP server with BigQuery write access"

# Grant BigQuery data editor role (write access to audit logs)

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mcp-server@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# Set up Workload Identity (so Kubernetes pods can use this service account)

gcloud iam service-accounts add-iam-policy-binding \
  mcp-server@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[mcp-system/mcp-server-sa]"

```

---

## HOUR 2-3: BUILD AND DEPLOY MCP SERVER

**Owner:** DevOps Engineer
**Prerequisites:** GKE cluster created, gVisor verified

### Step 1: Build Docker Image

```bash
cd mcp-validation

# Create Dockerfile

cat > Dockerfile <<'EOF'
FROM python:3.11-slim

# Install dependencies

WORKDIR /app
COPY mcp_server.py .
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    pydantic==2.5.0 \
    prometheus-client==0.19.0 \
    google-cloud-bigquery==3.13.0 \
    httpx==0.25.1

# Run as non-root user

RUN useradd -m -u 1000 mcp && chown -R mcp:mcp /app
USER mcp

# Expose port

EXPOSE 8080

# Start server

CMD ["python", "mcp_server.py"]
EOF

# Build and push image

docker build -t gcr.io/$PROJECT_ID/mcp-server:latest .
docker push gcr.io/$PROJECT_ID/mcp-server:latest

```

### Step 2: Update Deployment Manifest

```bash

# Replace PROJECT_ID placeholder in deployment manifest

sed -i "s/PROJECT_ID/$PROJECT_ID/g" architecture/mcp-server-deployment.yaml

```

### Step 3: Deploy to GKE

```bash

# Apply all Kubernetes resources

kubectl apply -f architecture/mcp-server-deployment.yaml

# Wait for deployment to be ready

kubectl rollout status deployment/mcp-server -n mcp-system

# Expected output:

# deployment "mcp-server" successfully rolled out

```

### Step 4: Verify Deployment

```bash

# Check pods are running

kubectl get pods -n mcp-system

# Expected output:

# NAME                          READY   STATUS    RESTARTS   AGE

# mcp-server-xxxxx-xxxxx        2/2     Running   0          1m

# mcp-server-xxxxx-xxxxx        2/2     Running   0          1m

# mcp-server-xxxxx-xxxxx        2/2     Running   0          1m

# Check health endpoint

kubectl run test -it --rm --image=curlimages/curl -- \
  curl http://mcp-server.mcp-system/health

# Expected output:

# {"status":"healthy","sandbox_pool_size":10,"timestamp":"..."}

```

**If any pods are not Running, this is a BLOCKER. Check logs:**

```bash
kubectl logs -n mcp-system -l app=mcp-server --tail=50

```

---

## HOUR 3-4: CREATE VERTEX AI WORKBENCH

**Owner:** ML Engineer
**Prerequisites:** Vertex AI API enabled

### Step 1: Create Vertex AI Workbench Instance

```bash

# Create Workbench instance (with A100 GPU for fast execution)

gcloud notebooks instances create mcp-validation \
  --location=$ZONE \
  --machine-type=n1-standard-16 \
  --accelerator-type=NVIDIA_TESLA_A100 \
  --accelerator-core-count=1 \
  --install-gpu-driver \
  --async

# This takes ~5-10 minutes

```

### Step 2: Wait for Instance to be Ready

```bash

# Check status

gcloud notebooks instances describe mcp-validation \
  --location=$ZONE \
  --format="value(state)"

# Expected output: ACTIVE

# Get Jupyter URL

gcloud notebooks instances describe mcp-validation \
  --location=$ZONE \
  --format="value(proxyUri)"

# Open this URL in browser

```

### Step 3: Upload Validation Notebook

```bash

# Once Jupyter is open, upload:

# - notebooks/01_mcp_validation.py

# Or clone entire repository:

git clone https://github.com/ShadowTag-v2/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services/mcp-validation

```

### Step 4: Install Dependencies in Workbench

```bash

# In Jupyter terminal, install required packages

pip install httpx asyncio

```

---

## HOUR 4: VALIDATION READY ✓

At this point, you should have:

```

✓ GKE cluster running with gVisor
✓ MCP server deployed (3 replicas, health check passing)
✓ BigQuery audit dataset created
✓ Vertex AI Workbench instance ready
✓ Validation notebook uploaded

Next step: HOUR 4-24 Latency + Security Testing

```

---

## TROUBLESHOOTING (If Things Go Wrong)

### Problem: gVisor runtime class not found

```bash

# Symptom: kubectl get runtimeclass shows no "gvisor"

# Cause: GKE cluster created without --enable-sandbox flag

# Solution: Recreate cluster with gVisor enabled

gcloud container clusters delete mcp-dev-cluster --zone=$ZONE
gcloud container clusters create mcp-dev-cluster \
  --zone=$ZONE \
  --enable-sandbox \
  [... rest of flags ...]

```

### Problem: MCP server pods not starting

```bash

# Check logs

kubectl logs -n mcp-system -l app=mcp-server --tail=100

# Common causes:

# 1. Docker image not pushed: Re-run docker push

# 2. Workload Identity not configured: Re-run Step 6 of GCP setup

# 3. BigQuery permissions: Re-run service account IAM binding

```

### Problem: Health check returns 503

```bash

# Cause: Sandbox pool not initialized

# Check logs for initialization errors

kubectl logs -n mcp-system -l app=mcp-server | grep "Sandbox pool"

# If you see errors about gVisor runtime, verify runtime class exists

kubectl get runtimeclass gvisor

```

### Problem: Anthropic API key not working

```bash

# Symptom: Validation tests fail with authentication error

# Solution:

# 1. Verify API key is correct (test with curl)

# 2. Check rate limits (10K RPM required)

# 3. Contact Anthropic support if rate limited

```

---

## STOP CONDITIONS (Abort Hour 0-4)

If you encounter any of these, **STOP and escalate to Erik:**



1. ❌ gVisor cannot be enabled on GKE (showstopper)


2. ❌ GCP project does not have budget/permissions (blocker)


3. ❌ Anthropic API access denied (blocker)


4. ❌ Engineering resources not available Week 1 (timeline risk)


5. ❌ Budget not approved within 4 hours (timeline risk)

**Escalation:** Stop all work, schedule decision call with Erik + CTO.

---

## SUCCESS CRITERIA FOR HOUR 0-4

At the end of Hour 4, you should be able to run this test:

```bash

# Test MCP server from Vertex AI Workbench

python mcp-validation/notebooks/01_mcp_validation.py \
  --mcp-url http://mcp-server.mcp-system \
  --runs 10

# Expected output:

# Starting validation with 10 runs...

# ✓ MCP server is healthy

# Running 10 functional tests...

# Running 5 security tests...

# ✓ All validation tests completed

#

# GO/NO-GO DECISION

# Decision:   [Will be determined after 1000 runs in Hour 4-24]

```

If this test passes, **Hour 0-4 is COMPLETE** and you can proceed to Hour 4-24.

---

## WHAT HAPPENS NEXT (HOUR 4-24)

Once Hour 0-4 is complete, the ML engineer will:



1. Run full validation (1000 test cases)


2. Collect latency metrics (p50, p90, p99, p99.9)


3. Run security tests (sandbox escape attempts)


4. Analyze results and generate report

**Timeline:** 8-20 hours (mostly automated, overnight run)

**Deliverable:** Validation report with GO/PIVOT/ABORT recommendation

---

## QUESTIONS?

If you have questions during Hour 0-4:



1. Check troubleshooting section above


2. Review 00_VALIDATION_SPRINT.md for context


3. Ask me (Claude) for clarification


4. Escalate blockers to Erik immediately

**DO NOT wait until Hour 72 to discover blockers. Fail fast.**

---

## YOUR DECISION: WHAT NOW?

Reply with one of:



1. **"APPROVED - Start Hour 0"** → I'll guide DevOps engineer through setup


2. **"OBJECTION: [specific concern]"** → I'll address your concern


3. **"QUESTION: [specific question]"** → I'll clarify before you approve

**The 72-hour clock starts when you say GO.**
