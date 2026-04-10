# Deployment Guide - Pnkln Ultrathink Framework

Complete step-by-step guide to deploying pnkln orchestrator to Google Kubernetes Engine.

## Prerequisites

### Required Tools

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Install kubectl
gcloud components install kubectl

# Install Terraform
brew install terraform  # macOS
# or download from https://www.terraform.io/downloads

# Install Skaffold
brew install skaffold  # macOS
# or download from https://skaffold.dev/docs/install/
```

### Required Permissions

Your GCP account needs:

- `roles/owner` (or equivalent granular roles)
- Billing account access
- Ability to enable APIs

## Step-by-Step Deployment

### Phase 1: GCP Project Setup

```bash
# 1. Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# 2. Set default project
gcloud config set project $PROJECT_ID

# 3. Enable billing (if not already enabled)
# Visit: https://console.cloud.google.com/billing

# 4. Verify project
gcloud projects describe $PROJECT_ID
```

### Phase 2: Infrastructure Provisioning

```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Create terraform.tfvars
cp terraform.tfvars.example terraform.tfvars

# 3. Edit terraform.tfvars
nano terraform.tfvars

# Add your values:
# project_id                  = "your-project-id"
# region                      = "us-central1"
# anthropic_vertex_project_id = "your-anthropic-vertex-project-id"

# 4. Initialize Terraform
terraform init

# 5. Review plan
terraform plan

# 6. Apply infrastructure
terraform apply

# Type 'yes' to confirm
```

**This will create:**

- GKE cluster with Workload Identity
- VPC network with private subnets
- Cloud NAT for egress
- Node pools (Spot + On-demand)
- Artifact Registry repository
- Service accounts with IAM bindings
- Secrets in Secret Manager

### Phase 3: Configure kubectl

```bash
# Get cluster credentials
gcloud container clusters get-credentials pnkln-production \
  --region $REGION \
  --project $PROJECT_ID

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### Phase 4: Update Kubernetes Manifests

```bash
# 1. Update ServiceAccount with your project ID
# Edit k8s/base/serviceaccount.yaml

# Replace YOUR_PROJECT_ID with your actual project ID:
sed -i "s/YOUR_PROJECT_ID/$PROJECT_ID/g" k8s/base/serviceaccount.yaml

# 2. Update kustomization.yaml
sed -i "s/PROJECT_ID/$PROJECT_ID/g" k8s/base/kustomization.yaml
```

### Phase 5: Create Kubernetes Secret

```bash
# Create secret from Secret Manager
kubectl create secret generic pnkln-secrets \
  --from-literal=project-id="$(gcloud secrets versions access latest --secret=anthropic-vertex-project-id)" \
  --namespace=pnkln-production
```

### Phase 6: Set Up Cloud Build

```bash
# Run setup script
./scripts/setup-cloud-build-trigger.sh $PROJECT_ID

# Follow prompts to connect GitHub repository
```

### Phase 7: Set Up Monitoring

```bash
# Run setup script
./scripts/setup-monitoring.sh $PROJECT_ID

# Enter your email when prompted for alerts
```

### Phase 8: Deploy Application

#### Option A: Via Cloud Build (Recommended for Production)

```bash
# Push to main branch
git add .
git commit -m "Initial deployment"
git push origin main

# Monitor build
gcloud builds list --ongoing

# Watch build logs
gcloud builds log BUILD_ID --stream
```

#### Option B: Via Skaffold (For Testing)

```bash
# Development deployment with hot reload
skaffold dev

# Production deployment
skaffold run -p production
```

#### Option C: Manual Deployment

```bash
# Build and push image
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/pnkln/orchestrator:v1 .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/pnkln/orchestrator:v1

# Deploy to GKE
kubectl apply -k k8s/base
```

### Phase 9: Verify Deployment

```bash
# Check pods
kubectl get pods -n pnkln-production

# Check deployment status
kubectl rollout status deployment/pnkln-orchestrator -n pnkln-production

# Check logs
kubectl logs -f deployment/pnkln-orchestrator -n pnkln-production

# Check service
kubectl get svc -n pnkln-production

# Test health endpoint
kubectl port-forward svc/pnkln-orchestrator 8080:80 -n pnkln-production
curl http://localhost:8080/health
```

### Phase 10: Set Up Ingress (Optional)

```bash
# 1. Reserve static IP
gcloud compute addresses create pnkln-orchestrator-ip \
  --global \
  --project $PROJECT_ID

# 2. Get IP address
gcloud compute addresses describe pnkln-orchestrator-ip --global --format="value(address)"

# 3. Create DNS A record pointing to this IP
# (Use your DNS provider)

# 4. Wait for Ingress to provision (5-10 minutes)
kubectl get ingress -n pnkln-production -w

# 5. Verify certificate
kubectl describe managedcertificate pnkln-cert -n pnkln-production

# 6. Test via domain
curl https://api.pnkln.io/health
```

## Post-Deployment Configuration

### Enable Workload Identity Annotation

```bash
# Annotate Kubernetes ServiceAccount
kubectl annotate serviceaccount pnkln-orchestrator \
  -n pnkln-production \
  iam.gke.io/gcp-service-account=pnkln-orchestrator@$PROJECT_ID.iam.gserviceaccount.com
```

### Set Up Log Routing (Optional)

```bash
# Create log sink for long-term storage
gcloud logging sinks create pnkln-logs \
  gs://your-logs-bucket/pnkln \
  --log-filter='resource.type="k8s_pod" AND resource.labels.namespace_name="pnkln-production"' \
  --project=$PROJECT_ID
```

### Configure Budget Alerts

```bash
# Set up budget alert
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="Pnkln Monthly Budget" \
  --budget-amount=500USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Testing the Deployment

### 1. Health Check

```bash
curl https://api.pnkln.io/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-08T...",
  "uptime": 12345,
  "version": "1.0.0",
  "vertex": true
}
```

### 2. Execute Request

```bash
curl -X POST https://api.pnkln.io/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What is the best way to optimize costs for a GKE deployment?"
  }'
```

### 3. Check Metrics

```bash
curl https://api.pnkln.io/metrics
```

## Scaling Configuration

### Adjust HPA Limits

```bash
# Edit HPA
kubectl edit hpa pnkln-orchestrator -n pnkln-production

# Or apply updated configuration
kubectl apply -f k8s/base/hpa.yaml
```

### Add More Node Pools

```terraform
# Edit terraform/main.tf
# Add new node pool resource
# Apply changes
terraform plan
terraform apply
```

## Rollback Procedure

### Rollback to Previous Deployment

```bash
# Check rollout history
kubectl rollout history deployment/pnkln-orchestrator -n pnkln-production

# Rollback to previous version
kubectl rollout undo deployment/pnkln-orchestrator -n pnkln-production

# Rollback to specific revision
kubectl rollout undo deployment/pnkln-orchestrator -n pnkln-production --to-revision=2
```

### Emergency Rollback

```bash
# Scale to zero
kubectl scale deployment pnkln-orchestrator --replicas=0 -n pnkln-production

# Deploy previous image
kubectl set image deployment/pnkln-orchestrator \
  orchestrator=us-central1-docker.pkg.dev/$PROJECT_ID/pnkln/orchestrator:PREVIOUS_TAG \
  -n pnkln-production

# Scale back up
kubectl scale deployment pnkln-orchestrator --replicas=3 -n pnkln-production
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod POD_NAME -n pnkln-production

# Common issues:
# - ImagePullBackOff: Check Artifact Registry permissions
# - CrashLoopBackOff: Check logs for application errors
# - Pending: Check node resources
```

### Workload Identity Issues

```bash
# Verify binding
gcloud iam service-accounts get-iam-policy \
  pnkln-orchestrator@$PROJECT_ID.iam.gserviceaccount.com

# Verify annotation
kubectl get sa pnkln-orchestrator -n pnkln-production -o yaml | grep iam.gke.io
```

### High Costs

```bash
# Check node pool usage
kubectl top nodes

# Check pod resource usage
kubectl top pods -n pnkln-production

# Review GCP billing
gcloud billing accounts list
```

## Maintenance

### Regular Updates

```bash
# Update GKE cluster (via Terraform)
cd terraform
terraform plan
terraform apply

# Update application (via CI/CD)
git push origin main
```

### Certificate Renewal

GCP Managed Certificates renew automatically, but verify:

```bash
kubectl describe managedcertificate pnkln-cert -n pnkln-production
```

### Log Retention

```bash
# Cloud Logging retains logs for 30 days by default
# For longer retention, configure log sinks
```

## Clean Up

### Remove Application

```bash
# Delete Kubernetes resources
kubectl delete -k k8s/base

# Or delete namespace
kubectl delete namespace pnkln-production
```

### Destroy Infrastructure

```bash
cd terraform
terraform destroy

# Type 'yes' to confirm
```

## Troubleshooting

**Questions?** Open an issue on GitHub or contact support@pnkln.io
