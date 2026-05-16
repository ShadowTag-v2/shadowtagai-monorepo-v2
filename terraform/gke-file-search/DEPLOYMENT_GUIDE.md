# Pnkln Core Stack - Deployment Guide

> **Step-by-step guide for deploying GKE + File Search integration from scratch**

## 📝 Pre-Deployment Checklist

- [ ] GCP project created
- [ ] Billing account linked to project
- [ ] gcloud CLI installed and authenticated
- [ ] Terraform >= 1.5.0 installed
- [ ] kubectl installed
- [ ] Python 3.8+ installed
- [ ] Sufficient GCP quotas (check: `gcloud compute project-info describe`)

## 🚀 Deployment Steps

### Phase 1: GCP Project Setup (15 minutes)

```bash
# Set project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Set as default project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  notebooks.googleapis.com \
  ml.googleapis.com \
  --project=$PROJECT_ID

# Verify APIs are enabled
gcloud services list --enabled --project=$PROJECT_ID
```

**Expected Output:**
```
NAME                              TITLE
aiplatform.googleapis.com         Vertex AI API
container.googleapis.com          Kubernetes Engine API
...
```

### Phase 2: Terraform Deployment (10-15 minutes)

```bash
# Navigate to terraform directory
cd terraform/gke-file-search

# Create terraform.tfvars from example
cp terraform.tfvars.example terraform.tfvars

# Edit configuration
vim terraform.tfvars
# Update: project_id, region, environment

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Apply configuration
terraform apply
```

**Terraform will create:**
- GKE cluster (3 nodes minimum)
- 30 GCS buckets for policy corpus
- Service accounts and IAM bindings
- Workload Identity configuration
- Monitoring alerts

**Expected Output:**
```
Apply complete! Resources: 47 added, 0 changed, 0 destroyed.

Outputs:

cluster_name = "pnkln-core-cluster"
corpus_buckets = {
  "defense" = "pnkln-policy-corpus-defense"
  "healthcare" = "pnkln-policy-corpus-healthcare"
  ...
}
```

### Phase 3: Kubernetes Setup (5 minutes)

```bash
# Configure kubectl
gcloud container clusters get-credentials pnkln-core-cluster \
  --region $REGION \
  --project $PROJECT_ID

# Verify cluster access
kubectl get nodes

# Create namespace and service account
kubectl apply -f k8s-manifests/namespace.yaml
kubectl apply -f k8s-manifests/service-account.yaml

# Verify Workload Identity binding
kubectl describe serviceaccount pnkln-file-search-sa -n pnkln-core
```

**Expected Output:**
```
NAME                                   STATUS   ROLES    AGE   VERSION
gke-pnkln-core-cluster-pool-1-xxxxx    Ready    <none>   5m    v1.27.x
gke-pnkln-core-cluster-pool-1-xxxxx    Ready    <none>   5m    v1.27.x
gke-pnkln-core-cluster-pool-1-xxxxx    Ready    <none>   5m    v1.27.x
```

### Phase 4: RAG Corpus Initialization (10 minutes)

```bash
# Install Python dependencies
python3 -m pip install --upgrade \
  google-cloud-aiplatform \
  google-cloud-storage

# Run corpus initialization script
./scripts/setup_file_search.sh \
  --project $PROJECT_ID \
  --region $REGION
```

**Expected Output:**
```
[INFO] Initializing RAG corpora...
✓ Created corpus: pnkln_defense_policies
✓ Created corpus: pnkln_healthcare_policies
✓ Created corpus: pnkln_finance_policies
...

Results:
  ✓ Created:  30 corpora
  ✗ Failed:   0 corpora
```

**Verify corpora creation:**
```bash
# List all corpora
python3 scripts/corpus_import.py --list-corpora \
  --project $PROJECT_ID \
  --region $REGION
```

### Phase 5: Upload Policy Documents (varies)

```bash
# Example: Upload defense vertical regulations

# 1. Upload to GCS bucket
gsutil cp /path/to/itar_regulations.pdf \
  gs://pnkln-policy-corpus-defense/regulatory/

gsutil cp /path/to/cmmc_2.0_guide.pdf \
  gs://pnkln-policy-corpus-defense/regulatory/

# 2. Import into RAG corpus
python3 scripts/corpus_import.py \
  --vertical defense \
  --path gs://pnkln-policy-corpus-defense/regulatory/*.pdf \
  --project $PROJECT_ID \
  --region $REGION
```

**Expected Output:**
```
Importing files to corpus: pnkln_defense_policies
Source: gs://pnkln-policy-corpus-defense/regulatory/*.pdf

Importing from: gs://pnkln-policy-corpus-defense/regulatory/*.pdf
Chunk size: 512, Overlap: 100

✓ Import successful!
  Corpus: pnkln_defense_policies
  Files imported: 2
```

**Repeat for all verticals:**
```bash
# Healthcare
gsutil cp hipaa_regulations.pdf gs://pnkln-policy-corpus-healthcare/regulatory/
python3 scripts/corpus_import.py --vertical healthcare --path gs://...

# Finance
gsutil cp finra_rules.pdf gs://pnkln-policy-corpus-finance/regulatory/
python3 scripts/corpus_import.py --vertical finance --path gs://...

# ... etc for remaining verticals
```

### Phase 6: Deploy Application Workloads (5 minutes)

```bash
# Customize deployment-example.yaml for your application
vim k8s-manifests/deployment-example.yaml

# Update:
#   - container image
#   - environment variables
#   - resource limits

# Deploy orchestrator
kubectl apply -f k8s-manifests/deployment-example.yaml

# Verify deployment
kubectl get pods -n pnkln-core
kubectl get svc -n pnkln-core
```

**Expected Output:**
```
NAME                                   READY   STATUS    RESTARTS   AGE
pnkln-orchestrator-5c8b7d9f8d-abcde    1/1     Running   0          1m
pnkln-orchestrator-5c8b7d9f8d-fghij    1/1     Running   0          1m
pnkln-orchestrator-5c8b7d9f8d-klmno    1/1     Running   0          1m
```

### Phase 7: Validation & Testing (10 minutes)

#### Test 1: Workload Identity

```bash
# Exec into pod
kubectl exec -it deployment/pnkln-orchestrator -n pnkln-core -- bash

# Inside pod, verify GCP access
gcloud auth list
# Should show: pnkln-gke-sa@{project}.iam.gserviceaccount.com

# Test GCS access
gsutil ls gs://pnkln-policy-corpus-defense/
```

#### Test 2: File Search Query

```bash
# Query defense corpus
python3 scripts/corpus_import.py \
  --vertical defense \
  --query "What are ITAR export control requirements for AI models?" \
  --project $PROJECT_ID \
  --region $REGION
```

**Expected Output:**
```
Querying corpus: pnkln_defense_policies
Query: What are ITAR export control requirements for AI models?

✓ Query Results:

Response:
ITAR (International Traffic in Arms Regulations) export controls for AI models
fall under USML Category XXI... [detailed response based on corpus]

Source Citations:
  [1] itar_regulations.pdf, page 42
  [2] cmmc_2.0_guide.pdf, section 3.4
```

#### Test 3: Monitoring & Alerting

```bash
# Check Cloud Monitoring
gcloud monitoring dashboards list --project=$PROJECT_ID

# View recent metrics
gcloud monitoring time-series list \
  --filter='metric.type="aiplatform.googleapis.com/prediction/latencies"' \
  --project=$PROJECT_ID

# Test alert policy
gcloud alpha monitoring policies list --project=$PROJECT_ID
```

### Phase 8: Performance Validation

#### Latency Testing

Create a simple load test:

```bash
# Install hey (HTTP load testing tool)
# macOS: brew install hey
# Linux: wget https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64

# Get service endpoint
export ORCHESTRATOR_IP=$(kubectl get svc pnkln-orchestrator -n pnkln-core -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Run load test
hey -n 1000 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"query": "Check HIPAA compliance", "vertical": "healthcare"}' \
  http://$ORCHESTRATOR_IP:8080/query
```

**Expected Metrics:**
```
Summary:
  Total:        8.5042 secs
  Slowest:      0.9234 secs   # Should be < 1.0s (850ms target)
  Fastest:      0.4123 secs
  Average:      0.6789 secs

Latency distribution:
  10% in 0.5123 secs
  25% in 0.5987 secs
  50% in 0.6543 secs
  75% in 0.7234 secs
  90% in 0.8123 secs   # P90
  95% in 0.8567 secs   # P95
  99% in 0.9012 secs   # P99 (target: < 850ms)
```

## ✅ Post-Deployment Verification

### Checklist

- [ ] All 3+ GKE nodes are `Ready`
- [ ] All 30 GCS buckets created
- [ ] All 30 RAG corpora initialized
- [ ] Workload Identity binding working (pods can access GCP)
- [ ] At least one vertical has policy documents uploaded
- [ ] File Search queries return relevant results
- [ ] Monitoring alerts configured and active
- [ ] Application pods running (3+ replicas)
- [ ] Latency targets met (p99 < 850ms)

### Common Issues

**Issue 1: "Insufficient quota" error**

```bash
# Check quotas
gcloud compute project-info describe --project=$PROJECT_ID | grep CPUS

# Request increase at:
# https://console.cloud.google.com/iam-admin/quotas
```

**Issue 2: Workload Identity not working**

```bash
# Verify IAM binding
gcloud iam service-accounts get-iam-policy \
  pnkln-gke-sa@$PROJECT_ID.iam.gserviceaccount.com

# Re-apply if missing
terraform apply -target=module.iam
```

**Issue 3: RAG corpus import fails**

```bash
# Check API enabled
gcloud services list --enabled | grep aiplatform

# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:pnkln-gke-sa@"
```

## 🎯 Next Steps

1. **Populate Remaining Verticals**
   - Upload policy documents for all 30 verticals
   - Import into respective RAG corpora

2. **Configure Application**
   - Integrate File Search API into Judge #6 orchestrator
   - Implement parallel execution (File Search + Judge Layer 1)
   - Add latency monitoring

3. **Production Hardening**
   - Enable private cluster
   - Configure Binary Authorization policies
   - Set up backup and disaster recovery
   - Implement GitOps for deployments

4. **Cost Optimization**
   - Review resource usage after 1 week
   - Adjust node pool min/max based on traffic
   - Implement GCS lifecycle policies
   - Set up budget alerts

## 📊 Monitoring Dashboard

Access your deployment:
- **GKE Console:** https://console.cloud.google.com/kubernetes/clusters
- **Vertex AI:** https://console.cloud.google.com/vertex-ai
- **Cloud Monitoring:** https://console.cloud.google.com/monitoring
- **Cloud Logging:** https://console.cloud.google.com/logs

## 🔧 Using Makefile

For convenience, use the included Makefile:

```bash
# Full deployment
make deploy-all

# Individual operations
make gke-connect        # Configure kubectl
make corpus-init        # Initialize corpora
make k8s-deploy         # Deploy K8s resources
make k8s-logs           # View logs
make corpus-query VERTICAL=defense QUERY="your question"
```

## 📝 Deployment Log Template

Keep a deployment log for audit purposes:

```
DEPLOYMENT LOG - PNKLN CORE STACK
=================================

Date: 2025-11-07
Operator: [Your Name]
Project: pnkln-core-gke
Region: us-central1

Phase 1: GCP Setup ✅
  - APIs enabled: [timestamp]
  - Quotas verified: [timestamp]

Phase 2: Terraform ✅
  - Applied at: [timestamp]
  - Resources created: 47
  - GKE cluster: pnkln-core-cluster

Phase 3: Kubernetes ✅
  - Kubectl configured: [timestamp]
  - Namespace created: pnkln-core
  - Workload Identity: verified

Phase 4: RAG Corpora ✅
  - Initialized: 30/30
  - Failed: 0/30

Phase 5: Policy Upload ✅
  - Defense: 5 documents
  - Healthcare: 3 documents
  - Finance: 4 documents
  - [... other verticals]

Phase 6: Application ✅
  - Deployed at: [timestamp]
  - Replicas: 3/3 running
  - Service: LoadBalancer IP assigned

Phase 7: Validation ✅
  - Workload Identity: PASS
  - File Search query: PASS
  - Monitoring: PASS

Phase 8: Performance ✅
  - P99 latency: 823ms (target: <850ms) ✅
  - Error rate: 0.02% ✅

Sign-off: [Your signature]
```

---

**Total Deployment Time:** ~60-90 minutes (excluding policy document preparation)

**Status:** Production Ready ✅
