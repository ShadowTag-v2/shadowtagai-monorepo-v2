# Judge #6 Deployment Guide

## Production Deployment on GKE with Vertex AI

**Author**: Pnkln Infrastructure Team
**Last Updated**: 2025-11-07
**Status**: Production-Ready

---

## Prerequisites

### Required Tools

```bash
# Google Cloud SDK
gcloud --version  # >= 450.0.0

# Terraform
terraform --version  # >= 1.5.0

# kubectl
kubectl version --client  # >= 1.28.0

# Docker (for local testing)
docker --version  # >= 24.0.0
```

### Required Permissions

GCP IAM roles needed:

- `roles/container.admin` - GKE cluster management
- `roles/compute.networkAdmin` - VPC and networking
- `roles/iam.serviceAccountAdmin` - Service account creation
- `roles/aiplatform.admin` - Vertex AI resources
- `roles/documentai.admin` - Document AI processors
- `roles/storage.admin` - Cloud Storage buckets

---

## Phase 1: Infrastructure Provisioning (30 minutes)

### Step 1: Configure GCP Project

```bash
# Set project
export PROJECT_ID="pnkln-prod"
export REGION="us-central1"
export ZONE="${REGION}-a"

gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${REGION}
gcloud config set compute/zone ${ZONE}

# Enable billing (if not already enabled)
gcloud beta billing projects link ${PROJECT_ID} \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### Step 2: Create Terraform State Bucket

```bash
# Create bucket for Terraform state
gsutil mb -p ${PROJECT_ID} -c STANDARD -l ${REGION} gs://${PROJECT_ID}-terraform-state
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Enable Object Versioning for disaster recovery
gsutil lifecycle set - gs://${PROJECT_ID}-terraform-state <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"numNewerVersions": 10}
      }
    ]
  }
}
EOF
```

### Step 3: Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
vim terraform.tfvars

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Review plan carefully
terraform show tfplan

# Apply infrastructure
terraform apply tfplan

# Save outputs
terraform output -json > outputs.json
```

**Expected Duration**: 15-20 minutes for GKE Autopilot cluster creation

### Step 4: Configure kubectl

```bash
# Get cluster credentials
gcloud container clusters get-credentials judge-6-inference \
  --region=${REGION} \
  --project=${PROJECT_ID}

# Verify connection
kubectl cluster-info
kubectl get nodes
```

---

## Phase 2: Application Deployment (20 minutes)

### Step 1: Update Kubernetes Manifests

```bash
cd infrastructure/kubernetes

# Replace PROJECT_ID placeholders
export PROJECT_ID="pnkln-prod"
find . -type f -name "*.yaml" -exec sed -i "s/PROJECT_ID/${PROJECT_ID}/g" {} +

# Verify changes
grep -r "pnkln-prod" .
```

### Step 2: Deploy to GKE

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create service account
kubectl apply -f serviceaccount.yaml

# Verify Workload Identity binding
kubectl describe sa judge-6-sa -n judge-6

# Deploy vLLM model server
kubectl apply -f vllm-deployment.yaml

# Wait for deployment
kubectl rollout status deployment/judge-6-vllm -n judge-6 --timeout=10m
```

### Step 3: Verify Model Server

```bash
# Check pods
kubectl get pods -n judge-6

# Check logs
kubectl logs -n judge-6 -l app=judge-6 --tail=100

# Port-forward for testing
kubectl port-forward -n judge-6 svc/judge-6-vllm 8000:8000

# Test inference (in another terminal)
curl http://localhost:8000/health
curl http://localhost:8000/v1/models
```

### Step 4: Deploy LangGraph Orchestrator

```bash
# Build Docker image
cd ../../src
docker build -t gcr.io/${PROJECT_ID}/judge6-orchestrator:v1.0.0 -f judge6/Dockerfile .

# Push to Google Container Registry
docker push gcr.io/${PROJECT_ID}/judge6-orchestrator:v1.0.0

# Deploy to GKE
kubectl apply -f ../infrastructure/kubernetes/langgraph-deployment.yaml

# Verify
kubectl get deployment -n judge-6
kubectl get pods -n judge-6 -l app=judge-6,component=orchestrator
```

---

## Phase 3: Document AI Integration (15 minutes)

### Step 1: Deploy Cloud Function

```bash
cd ../src/aiurcm

# Create requirements.txt for Cloud Function
cat > requirements.txt <<EOF
google-cloud-documentai==2.35.0
google-cloud-storage==2.20.0
google-cloud-pubsub==2.27.1
EOF

# Deploy Cloud Function
gcloud functions deploy process-compliance-document \
  --gen2 \
  --runtime=python311 \
  --region=${REGION} \
  --source=. \
  --entry-point=process_compliance_document \
  --trigger-bucket=${PROJECT_ID}-compliance-docs \
  --set-env-vars GCP_PROJECT_ID=${PROJECT_ID} \
  --timeout=540s \
  --memory=2GB \
  --service-account=judge-6-workload-sa@${PROJECT_ID}.iam.gserviceaccount.com

# Verify deployment
gcloud functions describe process-compliance-document --region=${REGION}
```

### Step 2: Test Document Processing Pipeline

```bash
# Upload test document
gsutil cp ../../test/data/sample-fda-policy.pdf \
  gs://${PROJECT_ID}-compliance-docs/intake/

# Check Cloud Function logs
gcloud functions logs read process-compliance-document --region=${REGION} --limit=50

# Verify Pub/Sub message
gcloud pubsub subscriptions pull langgraph-consumer --auto-ack --limit=1
```

---

## Phase 4: Monitoring & Observability (10 minutes)

### Step 1: Create Monitoring Dashboards

```bash
# Import pre-built dashboard
gcloud monitoring dashboards create --config-from-file=../../infrastructure/monitoring/judge-6-dashboard.json

# Verify
gcloud monitoring dashboards list
```

### Step 2: Configure Alerting

```bash
# Create uptime check
gcloud monitoring uptime create judge-6-health \
  --resource-type=k8s-service \
  --resource-labels=project_id=${PROJECT_ID},location=${REGION},cluster_name=judge-6-inference,namespace_name=judge-6,service_name=judge-6-vllm

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Judge #6 High Latency" \
  --condition-threshold-value=500 \
  --condition-threshold-duration=300s \
  --condition-display-name="p99 latency > 500ms"
```

### Step 3: Configure Log-based Metrics

```bash
# Create log-based metric for errors
gcloud logging metrics create judge6_errors \
  --description="Count of Judge #6 errors" \
  --log-filter='resource.type="k8s_container"
resource.labels.namespace_name="judge-6"
severity>=ERROR'
```

---

## Phase 5: Validation & Testing (15 minutes)

### End-to-End Test

```bash
# 1. Upload compliance document
gsutil cp ../../test/data/sample-sec-filing.pdf \
  gs://${PROJECT_ID}-compliance-docs/intake/

# 2. Monitor Cloud Function
gcloud functions logs read process-compliance-document --region=${REGION} --follow &

# 3. Monitor orchestrator logs
kubectl logs -n judge-6 -l component=orchestrator --follow &

# 4. Check Firestore for results
gcloud firestore export gs://${PROJECT_ID}-firestore-exports --collection-ids=judge6_workflows

# 5. Verify workflow completion
# Query Firestore via console: https://console.cloud.google.com/firestore
```

### Load Testing

```bash
# Generate 100 concurrent requests
cd ../../test/load
python generate_load.py --qps=10 --duration=60s --endpoint=http://judge-6-vllm.judge-6.svc.cluster.local:8000

# Monitor autoscaling
watch kubectl get hpa -n judge-6

# Monitor resource usage
kubectl top pods -n judge-6
```

---

## Troubleshooting

### Common Issues

#### 1. Pods Stuck in Pending

```bash
# Check events
kubectl describe pod POD_NAME -n judge-6

# Common causes:
# - Insufficient GPU quota → Request quota increase
# - Node not ready → Check GKE cluster health
# - Image pull errors → Verify GCR permissions
```

#### 2. Model Loading Timeout

```bash
# Increase readiness probe delay
kubectl edit deployment judge-6-vllm -n judge-6
# Update: initialDelaySeconds: 300

# Check Cloud Storage FUSE logs
kubectl logs POD_NAME -n judge-6 -c gke-gcsfuse-sidecar

# Verify bucket access
kubectl exec -it POD_NAME -n judge-6 -- ls -la /models
```

#### 3. High Latency

```bash
# Check HPA scaling
kubectl get hpa judge-6-vllm-hpa -n judge-6

# Force scale up
kubectl scale deployment judge-6-vllm --replicas=5 -n judge-6

# Check inference metrics
kubectl port-forward -n judge-6 svc/judge-6-vllm 8000:8000
curl http://localhost:8000/metrics | grep latency
```

#### 4. Pub/Sub Backlog

```bash
# Check subscription backlog
gcloud pubsub subscriptions describe langgraph-consumer

# Scale orchestrator
kubectl scale deployment judge-6-orchestrator --replicas=10 -n judge-6

# Purge dead letters
gcloud pubsub subscriptions seek langgraph-consumer --time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## Rollback Procedure

### Application Rollback

```bash
# Rollback vLLM deployment
kubectl rollout undo deployment/judge-6-vllm -n judge-6

# Rollback orchestrator
kubectl rollout undo deployment/judge-6-orchestrator -n judge-6

# Verify rollback
kubectl rollout status deployment/judge-6-vllm -n judge-6
kubectl rollout history deployment/judge-6-vllm -n judge-6
```

### Infrastructure Rollback

```bash
cd infrastructure/terraform

# Show current state
terraform show

# Revert to previous version
git checkout HEAD~1 -- .

# Apply previous configuration
terraform plan -out=rollback.tfplan
terraform apply rollback.tfplan
```

---

## Maintenance Windows

### Scheduled Maintenance

GKE maintenance windows: **Sundays 3:00-5:00 AM UTC**

Pre-maintenance checklist:

- [ ] Backup Firestore data
- [ ] Verify auto-scaling policies active
- [ ] Notify stakeholders
- [ ] Monitor error rates post-update

### Emergency Maintenance

For critical security patches:

```bash
# Drain node for patching
kubectl drain NODE_NAME --ignore-daemonsets --delete-emptydir-data

# Verify pod redistribution
kubectl get pods -n judge-6 -o wide

# Uncordon node after patching
kubectl uncordon NODE_NAME
```

---

## Cost Optimization

### Current Baseline Costs

| Component                | Monthly Cost (estimate) |
| ------------------------ | ----------------------- |
| GKE Autopilot (2 pods)   | $360                    |
| NVIDIA L4 GPUs (2x 24/7) | $1,224                  |
| Cloud Storage FUSE       | $20                     |
| Networking (egress)      | $120                    |
| **Total**                | **$1,724**              |

### Optimization Strategies

```bash
# 1. Enable autoscaling to zero during off-hours
kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '{"spec":{"minReplicas":0}}'

# 2. Use Spot VMs for batch processing (in standard GKE)
# (Note: Not applicable in Autopilot, consider standard GKE for cost sensitivity)

# 3. Implement request batching
# Update vLLM deployment with larger batch sizes

# 4. Use INT8 quantization
# Update MODEL env var to use quantized model variant
```

---

## Security Hardening

### Post-Deployment Security Checklist

- [ ] Binary Authorization enabled
- [ ] Workload Identity configured
- [ ] Network policies applied
- [ ] Secret Manager for credentials
- [ ] Audit logging enabled
- [ ] VPC Service Controls (for highly sensitive data)

```bash
# Verify Binary Authorization
gcloud container binauthz policy export

# Check Network Policies
kubectl get networkpolicies -n judge-6

# Audit IAM bindings
gcloud projects get-iam-policy ${PROJECT_ID} --flatten="bindings[].members" --filter="bindings.members:judge-6*"
```

---

## Disaster Recovery

### Backup Strategy

**RPO**: 0 seconds (continuous replication)
**RTO**: 5 minutes (automated failover)

```bash
# Firestore auto-backup (enabled by default)
gcloud firestore backups schedules list

# Cloud Storage versioning (enabled in Terraform)
gsutil versioning get gs://${PROJECT_ID}-compliance-docs

# GKE cluster config backup
kubectl get all -n judge-6 -o yaml > backup-$(date +%Y%m%d).yaml
```

### DR Testing

Monthly DR drill:

```bash
# 1. Simulate region failure
gcloud container clusters update judge-6-inference --region=${REGION} --maintenance-window-start=now

# 2. Deploy to secondary region
export REGION="us-east1"
terraform apply -var="region=${REGION}"

# 3. Verify failover
kubectl get pods -n judge-6
curl http://SECONDARY_ENDPOINT/health

# 4. Measure RTO (target: <5 minutes)
```

---

## Next Steps

1. **Production Hardening** (Week 1)
   - Enable Binary Authorization
   - Implement CMEK for data encryption
   - Configure VPC Service Controls

2. **Performance Optimization** (Week 2)
   - INT8 quantization for cost reduction
   - Prefix caching optimization
   - Custom metrics fine-tuning

3. **Multi-Tenant Support** (Week 3-4)
   - Namespace isolation per customer
   - Resource quotas
   - Cost attribution

4. **Observability Enhancement** (Ongoing)
   - Custom SLIs/SLOs
   - Advanced tracing
   - Business metrics dashboards

---

## Support & Escalation

**Internal Documentation**: https://docs.pnkln.io/judge-6
**On-Call Runbooks**: `/docs/runbooks/`
**Incident Management**: PagerDuty integration

For deployment issues, contact:

- **Infrastructure**: infra@pnkln.io
- **Application**: dev@pnkln.io
- **Emergency**: Use PagerDuty escalation policy

---

**Deployment Checklist**:

- [ ] Phase 1: Infrastructure ✓
- [ ] Phase 2: Application ✓
- [ ] Phase 3: Document AI ✓
- [ ] Phase 4: Monitoring ✓
- [ ] Phase 5: Validation ✓
- [ ] Security hardening
- [ ] DR testing
- [ ] Stakeholder notification

**Status**: Production-Ready
**Last Validated**: 2025-11-07
