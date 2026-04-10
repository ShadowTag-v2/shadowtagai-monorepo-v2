# PNKLN CORE STACK™ - DEPLOYMENT RUNBOOK

**Purpose**: Ship Judge #6 + GKE infrastructure THIS WEEK
**Owner**: Erik Hancock
**Decision Framework**: Purpose=Revenue enablement, Reasons=Bootstrap discipline, Brakes=Cost gates + kill switch
**Last Updated**: 2025-11-17

---

## TABLE OF CONTENTS

1. [Pre-Deployment Checklist](#1-pre-deployment-checklist)
2. [Environment Setup](#2-environment-setup)
3. [Terraform Infrastructure Deployment](#3-terraform-infrastructure-deployment)
4. [Container Image Build & Push](#4-container-image-build--push)
5. [Kubernetes Deployment](#5-kubernetes-deployment)
6. [Judge #6 Validation](#6-judge-6-validation)
7. [Cost Monitoring Setup](#7-cost-monitoring-setup)
8. [Rollback Procedures](#8-rollback-procedures)
9. [Troubleshooting](#9-troubleshooting)
10. [Post-Deployment](#10-post-deployment)

---

## 1. PRE-DEPLOYMENT CHECKLIST

### Prerequisites

- [ ] **GCP Account**: Active with billing enabled
- [ ] **Billing Account ID**: Retrieved from GCP Console → Billing
- [ ] **GPU Quota**: Request L4 GPU quota in us-central1 (minimum 5)
  - Navigate to: IAM & Admin → Quotas → Filter "nvidia-l4"
  - Request increase to at least 10 GPUs per region
- [ ] **CLI Tools Installed**:
  ```bash
  gcloud --version  # ≥456.0.0
  terraform --version  # ≥1.8.0
  kubectl --version  # ≥1.30.0
  docker --version  # ≥24.0.0
  ```

### Decision Gate: Bootstrap Discipline

**Question**: Is this deployment survivable if it costs $2,500/month and generates $0 revenue for 3 months?

- **If YES**: Proceed with deployment
- **If NO**: Scale down node pool configs in `terraform.tfvars` OR delay deployment until revenue model is validated

**Break-even Calculation**:

- Monthly cost: $2,500
- Required MRR for 3× ROI: $7,500
- LTV:CAC target: 4:1
- Implied CAC: $625 per customer

---

## 2. ENVIRONMENT SETUP

### Step 1: Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set application default credentials (for Terraform)
gcloud auth application-default login
```

### Step 2: Create GCP Project

```bash
# Set variables
export PROJECT_ID="pnkln-core-stack-prod"
export REGION="us-central1"
export BILLING_ACCOUNT_ID="YOUR_BILLING_ACCOUNT_ID"  # Replace with your ID

# Create project
gcloud projects create ${PROJECT_ID} \
  --name="Pnkln Core Stack" \
  --set-as-default

# Link billing
gcloud billing projects link ${PROJECT_ID} \
  --billing-account=${BILLING_ACCOUNT_ID}

# Set project
gcloud config set project ${PROJECT_ID}
```

### Step 3: Enable Required APIs

```bash
# Enable all required GCP APIs (takes ~2 minutes)
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  artifactregistry.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  aiplatform.googleapis.com \
  iap.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  servicenetworking.googleapis.com
```

### Step 4: Create Terraform State Bucket

```bash
# Create GCS bucket for Terraform state
gsutil mb -p ${PROJECT_ID} -l ${REGION} \
  gs://${PROJECT_ID}-terraform-state

# Enable versioning (for rollback)
gsutil versioning set on \
  gs://${PROJECT_ID}-terraform-state

# Set lifecycle policy (keep last 5 versions)
cat <<EOF | gsutil lifecycle set - gs://${PROJECT_ID}-terraform-state
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"numNewerVersions": 5}
      }
    ]
  }
}
EOF
```

---

## 3. TERRAFORM INFRASTRUCTURE DEPLOYMENT

### Step 1: Configure Terraform Variables

```bash
cd terraform/

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
vim terraform.tfvars
```

**Required Changes in `terraform.tfvars`**:

```hcl
project_id         = "pnkln-core-stack-prod"  # Your actual project ID
billing_account_id = "XXXXXX-XXXXXX-XXXXXX"   # Your billing account
budget_alert_emails = ["your-email@example.com"]  # Your email for alerts
```

**Update backend.tf**:

```bash
# Replace placeholder in backend.tf
sed -i "s/REPLACE_WITH_PROJECT_ID/${PROJECT_ID}/g" backend.tf
```

### Step 2: Initialize Terraform

```bash
terraform init

# Expected output:
# Terraform has been successfully initialized!
```

### Step 3: Plan Infrastructure

```bash
terraform plan -out=tfplan

# Review carefully:
# - Expected resources: ~50-60
# - Monthly cost: $1,350-1,950 baseline
# - GPU quotas: Check that you have L4 quota
```

**CRITICAL DECISION GATE**:

- Review the plan output
- Verify cost estimates align with budget
- Check GPU node pool configuration (min_nodes = 1 for judge-gpu pool)
- Ensure all resource names are correct

### Step 4: Apply Infrastructure

```bash
# Apply the plan (takes 15-20 minutes)
terraform apply tfplan

# Monitor progress - watch for errors
```

**Common Issues**:

- **Quota Exceeded**: Request GPU quota increase (see Step 1)
- **API Not Enabled**: Run enable APIs command again
- **Billing Not Linked**: Verify billing account link

### Step 5: Configure kubectl

```bash
# Get cluster credentials
gcloud container clusters get-credentials pnkln-core-stack \
  --region ${REGION} \
  --project ${PROJECT_ID}

# Verify
kubectl get nodes

# Expected output: 1-3 nodes (system pool)
```

### Step 6: Verify GPU Nodes

```bash
# Check GPU availability
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\\.com/gpu

# Expected: At least 1 node with GPU count = 1 (L4)
```

---

## 4. CONTAINER IMAGE BUILD & PUSH

### Step 1: Configure Docker for Artifact Registry

```bash
# Configure Docker auth
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

### Step 2: Build Judge Layer 1 (Gemini)

```bash
cd /home/user/ShadowTag-v2-fastapi-services

# Build image
docker build \
  -f docker/judge-layer1/Dockerfile \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/judge-layer1:latest \
  .

# Push to Artifact Registry
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/judge-layer1:latest
```

### Step 3: Build Judge Layer 3 (Go Rules Engine)

```bash
# Build image
docker build \
  -f docker/judge-layer3/Dockerfile \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/judge-layer3:latest \
  .

# Push
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/judge-layer3:latest
```

### Step 4: Build Aggregator

```bash
# Build image
docker build \
  -f docker/aggregator/Dockerfile \
  -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/aggregator:latest \
  .

# Push
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/aggregator:latest
```

---

## 5. KUBERNETES DEPLOYMENT

### Step 1: Create Namespaces

```bash
kubectl apply -f k8s/base/namespace.yaml

# Verify
kubectl get namespaces | grep pnkln
```

### Step 2: Deploy Judge Layer 3 (Fastest to validate)

```bash
# NOTE: Full K8s manifests are in k8s/base/ directory
# For now, test with minimal deployment:

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: judge-layer3-sa
  namespace: pnkln-judge
  annotations:
    iam.gke.io/gcp-service-account: judge-layer3-gke@${PROJECT_ID}.iam.gserviceaccount.com

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: judge-layer3
  namespace: pnkln-judge
spec:
  replicas: 2
  selector:
    matchLabels:
      app: judge-layer3
  template:
    metadata:
      labels:
        app: judge-layer3
    spec:
      serviceAccountName: judge-layer3-sa
      containers:
      - name: judge-layer3
        image: ${REGION}-docker.pkg.dev/${PROJECT_ID}/pnkln-containers/judge-layer3:latest
        ports:
        - containerPort: 8082
        env:
        - name: PORT
          value: "8082"
        - name: REDIS_HOST
          value: "10.10.0.3"  # Replace with actual Redis IP from Terraform output
        - name: REDIS_PORT
          value: "6379"
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"

---
apiVersion: v1
kind: Service
metadata:
  name: judge-layer3
  namespace: pnkln-judge
spec:
  selector:
    app: judge-layer3
  ports:
  - port: 80
    targetPort: 8082
  type: ClusterIP
EOF
```

### Step 3: Verify Deployment

```bash
# Watch pods come up
kubectl get pods -n pnkln-judge --watch

# Check logs
kubectl logs -n pnkln-judge -l app=judge-layer3 --tail=50
```

---

## 6. JUDGE #6 VALIDATION

### Step 1: Port-Forward for Testing

```bash
# Port-forward Judge Layer 3
kubectl port-forward -n pnkln-judge svc/judge-layer3 8082:80 &
```

### Step 2: Test Layer 3 Endpoint

```bash
# Health check
curl http://localhost:8082/healthz

# Expected: {"status":"healthy"}

# Test inference
curl -X POST http://localhost:8082/infer \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "action": "read",
    "resource": "public_data",
    "context": {"user_role": "user"},
    "risk_category": "NEGLIGIBLE"
  }'

# Expected: {"layer":3,"decision":"PASS",...}
```

### Step 3: Test CATASTROPHIC Gate

```bash
curl -X POST http://localhost:8082/infer \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "action": "delete",
    "resource": "critical_system",
    "context": {},
    "risk_category": "CATASTROPHIC"
  }'

# Expected: {"layer":3,"decision":"FAIL","rationale":"CATASTROPHIC risk category requires manual approval"}
```

### Step 4: Latency Validation

```bash
# Run 100 requests and measure p99
for i in {1..100}; do
  curl -X POST http://localhost:8082/infer \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test","action":"read","resource":"data","context":{},"risk_category":"MODERATE"}' \
    -w "%{time_total}\n" \
    -o /dev/null -s
done | sort -n | tail -1

# Expected: p99 < 0.020 seconds (20ms)
```

---

## 7. COST MONITORING SETUP

### Step 1: Verify Budget Alerts

```bash
# Check budget configuration
gcloud billing budgets list --billing-account=${BILLING_ACCOUNT_ID}

# Expected: pnkln-core-stack budget with $2,500 limit
```

### Step 2: Monitor Daily Spend

```bash
# View current month's costs
gcloud billing projects describe ${PROJECT_ID} --format="value(billingAccountName)"

# Access billing dashboard
echo "https://console.cloud.google.com/billing/${BILLING_ACCOUNT_ID}/reports?project=${PROJECT_ID}"
```

### Step 3: Set Cost Alerts

Budget alerts are configured at:

- 50% ($1,250)
- 80% ($2,000)
- 100% ($2,500)
- Forecast 100%

**CRITICAL**: If you receive 100% alert, assess:

1. Is traffic higher than expected?
2. Are GPU nodes autoscaling correctly?
3. Is this sustainable for current revenue?

**Kill Switch**: If costs exceed budget and revenue = $0:

```bash
# Scale down GPU nodes immediately
kubectl scale deployment -n pnkln-judge --all --replicas=0

# Or destroy entire infrastructure
cd terraform/
terraform destroy
```

---

## 8. ROLLBACK PROCEDURES

### Terraform Rollback

```bash
# List state versions
gsutil ls -a gs://${PROJECT_ID}-terraform-state/gke-core-stack/default.tfstate

# Restore previous version
gsutil cp gs://${PROJECT_ID}-terraform-state/gke-core-stack/default.tfstate#VERSION \
  terraform.tfstate

# Apply previous state
terraform apply
```

### Kubernetes Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/judge-layer3 -n pnkln-judge

# Check rollout status
kubectl rollout status deployment/judge-layer3 -n pnkln-judge
```

---

## 9. TROUBLESHOOTING

### Issue: GPU Nodes Not Starting

**Symptoms**: Nodes stuck in "Pending" state

**Fix**:

```bash
# Check node pool status
gcloud container node-pools describe judge-gpu \
  --cluster=pnkln-core-stack \
  --region=${REGION}

# Check quotas
gcloud compute project-info describe --project=${PROJECT_ID}

# Request quota increase if needed
```

### Issue: Pods CrashLoopBackOff

**Symptoms**: Pods restarting repeatedly

**Fix**:

```bash
# Check logs
kubectl logs -n pnkln-judge <pod-name> --previous

# Check events
kubectl describe pod -n pnkln-judge <pod-name>

# Common causes:
# 1. Missing environment variables
# 2. Redis connection failed
# 3. Vertex AI endpoint not configured
```

### Issue: High Latency (p99 > 90ms)

**Symptoms**: Judge #6 SLA violated

**Fix**:

```bash
# Scale up replicas
kubectl scale deployment judge-layer3 -n pnkln-judge --replicas=5

# Check resource utilization
kubectl top pods -n pnkln-judge

# Review Prometheus metrics
kubectl port-forward -n pnkln-observability svc/prometheus 9090:9090
# Navigate to: http://localhost:9090
```

---

## 10. POST-DEPLOYMENT

### Next Steps

1. **Deploy Remaining Layers**:
   - Judge Layer 1 (Gemini): Requires Vertex AI fine-tuning
   - Judge Layer 2 (PyTorch): Requires model training
   - Aggregator: Deploy after all 3 layers are ready

2. **Set Up Observability**:
   - Deploy Prometheus & Grafana
   - Configure SLO dashboards
   - Set up alerting (PagerDuty integration)

3. **Revenue Acceleration**:
   - Identify first vertical to deploy (Digital Freeway, ShadowTag, etc.)
   - Set up customer onboarding flow
   - Configure billing integration (Stripe/Paddle)

4. **Security Hardening**:
   - Enable Binary Authorization
   - Rotate service account keys
   - Audit IAM permissions
   - Set up VPC Service Controls

### Success Criteria

- [ ] **Infrastructure Deployed**: GKE cluster running with GPU nodes
- [ ] **Judge Layer 3 Validated**: <20ms p99 latency
- [ ] **Cost Monitoring Active**: Budget alerts configured
- [ ] **Rollback Tested**: Can destroy/recreate infrastructure
- [ ] **Documentation Complete**: Runbook updated with actual values

### Bootstrap Discipline Gates

**18-Month ROI Gate**:

- Target: ≥3× ROI ($2,500 cost → $7,500 revenue)
- Track: Monthly MRR, CAC, LTV
- Kill switch: If ROI < 2× at 12 months, reassess

**LTV:CAC Gate** (12 months):

- Target: ≥4:1
- Calculate: LTV = ARPU × avg customer lifespan / CAC
- Action: If < 3:1, optimize funnel or reduce CAC

---

## SUPPORT

### Decision Framework (JR Engine)

For any infrastructure decision:

1. **Purpose**: Does this advance PNKLN revenue?
2. **Reasons**: Is the change defensible with evidence?
3. **Brakes**: Is p99 outcome survivable? (cost, risk, recovery time)

### Getting Help

1. **GCP Issues**: Check Cloud Logging, Error Reporting
2. **Terraform Issues**: Review state file, check provider versions
3. **Kubernetes Issues**: Check pod logs, describe resources
4. **Cost Issues**: Review billing dashboard, check autoscaling

### Emergency Contacts

- **Owner**: Erik Hancock (erik@pnkln.com)
- **GCP Support**: console.cloud.google.com/support
- **Terraform Docs**: terraform.io/docs

---

**Last Updated**: 2025-11-17
**Maintainer**: Erik Hancock (Pnkln Core Stack)
**License**: Proprietary - Internal Use Only

---

**SHIP IT. 🚀**
