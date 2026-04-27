"""
Step-by-Step Deployment Guide for GKE

This guide walks through deploying the File Search service to GKE from scratch.
"""

# ==============================================================================

# PHASE 1: GCP PREREQUISITES (15 minutes)

# ==============================================================================

"""
Step 1.1: Enable Required APIs
"""

# Enable Vertex AI, GKE, GCR, and Cloud Storage

gcloud services enable \
 aiplatform.googleapis.com \
 container.googleapis.com \
 containerregistry.googleapis.com \
 storage-api.googleapis.com \
 compute.googleapis.com

"""
Step 1.2: Create GCS Bucket for Policy Documents
"""

# Create bucket in same region as Vertex AI

export PROJECT_ID="pnkln-core-gke"
export REGION="us-central1"
export BUCKET_NAME="pnkln-policy-corpus"

gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${BUCKET_NAME}/

# Create directories for each vertical

for vertical in defense healthcare finance; do
gsutil -m cp /dev/null gs://${BUCKET_NAME}/${vertical}/.keep
done

"""
Step 1.3: Create Service Account
"""

# Create service account

gcloud iam service-accounts create pnkln-file-search \
 --display-name="Pnkln File Search Service" \
 --project=${PROJECT_ID}

# Grant permissions

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:pnkln-file-search@${PROJECT_ID}.iam.gserviceaccount.com" \
 --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:pnkln-file-search@${PROJECT_ID}.iam.gserviceaccount.com" \
 --role="roles/storage.objectViewer"

# Download key for local testing (optional)

gcloud iam service-accounts keys create ~/pnkln-file-search-key.json \
 --iam-account=pnkln-file-search@${PROJECT_ID}.iam.gserviceaccount.com

# ==============================================================================

# PHASE 2: GKE CLUSTER SETUP (20 minutes)

# ==============================================================================

"""
Step 2.1: Create GKE Cluster
"""

gcloud container clusters create pnkln-core \
 --project=${PROJECT_ID} \
  --region=${REGION} \
 --num-nodes=3 \
 --machine-type=n1-standard-4 \
 --disk-size=50 \
 --enable-autoscaling \
 --min-nodes=3 \
 --max-nodes=10 \
 --enable-autorepair \
 --enable-autoupgrade \
 --enable-ip-alias \
 --network="default" \
 --subnetwork="default" \
 --enable-stackdriver-kubernetes \
 --enable-workload-identity \
 --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

"""
Step 2.2: Get Cluster Credentials
"""

gcloud container clusters get-credentials pnkln-core \
 --region=${REGION} \
  --project=${PROJECT_ID}

# Verify connection

kubectl cluster-info
kubectl get nodes

"""
Step 2.3: Configure Workload Identity
"""

# Create Kubernetes namespace

kubectl create namespace pnkln-core

# Create Kubernetes service account

kubectl create serviceaccount pnkln-file-search \
 --namespace=pnkln-core

# Bind K8s SA to GCP SA

gcloud iam service-accounts add-iam-policy-binding \
 pnkln-file-search@${PROJECT_ID}.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:${PROJECT_ID}.svc.id.goog[pnkln-core/pnkln-file-search]"

# Annotate K8s service account

kubectl annotate serviceaccount pnkln-file-search \
 --namespace=pnkln-core \
 iam.gke.io/gcp-service-account=pnkln-file-search@${PROJECT_ID}.iam.gserviceaccount.com

# ==============================================================================

# PHASE 3: UPLOAD POLICY DOCUMENTS (30 minutes)

# ==============================================================================

"""
Step 3.1: Prepare Policy Documents
"""

# Example structure:

# policy_docs/

# ├── defense/

# │ ├── ITAR_2024.pdf

# │ ├── CMMC_Level2.pdf

# │ └── DFARS_252.pdf

# ├── healthcare/

# │ ├── HIPAA_Privacy_Rule.pdf

# │ ├── HIPAA_Security_Rule.pdf

# │ └── FDA_21CFR11.pdf

# └── finance/

# ├── FINRA_Rules.pdf

# ├── SOX_Compliance.pdf

# └── GDPR_Summary.pdf

"""
Step 3.2: Upload to GCS
"""

# Upload all policy documents

gsutil -m cp -r policy_docs/\* gs://${BUCKET_NAME}/

# Verify uploads

gsutil ls -r gs://${BUCKET_NAME}/

# Set public read (if needed for corpus access)

gsutil -m acl ch -r -u pnkln-file-search@${PROJECT_ID}.iam.gserviceaccount.com:R \
  gs://${BUCKET_NAME}/

"""
Step 3.3: Initialize Corpora
"""

# Set environment variables

export GCP_PROJECT_ID=${PROJECT_ID}
export GCP_REGION=${REGION}
export GCP_STORAGE_BUCKET=gs://${BUCKET_NAME}
export GOOGLE_APPLICATION_CREDENTIALS=~/pnkln-file-search-key.json

# Install Python dependencies locally

cd ShadowTag-v2-fastapi-services
pip install -r requirements.txt
pip install -e .

# Run corpus initialization

./scripts/setup_file_search.sh

# Or for specific verticals

./scripts/setup_file_search.sh --vertical defense
./scripts/setup_file_search.sh --vertical healthcare
./scripts/setup_file_search.sh --vertical finance

# ==============================================================================

# PHASE 4: BUILD AND PUSH DOCKER IMAGE (10 minutes)

# ==============================================================================

"""
Step 4.1: Authenticate with GCR
"""

gcloud auth configure-docker

"""
Step 4.2: Build Docker Image
"""

# Build image

docker build -t gcr.io/${PROJECT_ID}/file-search:latest .

# Tag with version

docker tag gcr.io/${PROJECT_ID}/file-search:latest \
  gcr.io/${PROJECT_ID}/file-search:v0.1.0

"""
Step 4.3: Push to Google Container Registry
"""

docker push gcr.io/${PROJECT_ID}/file-search:latest
docker push gcr.io/${PROJECT_ID}/file-search:v0.1.0

# Verify image

gcloud container images list --repository=gcr.io/${PROJECT_ID}
gcloud container images describe gcr.io/${PROJECT_ID}/file-search:latest

# ==============================================================================

# PHASE 5: DEPLOY TO GKE (15 minutes)

# ==============================================================================

"""
Step 5.1: Update Kubernetes Manifests
"""

# Update deployment.yaml with your project ID

sed -i "s/pnkln-core-gke/${PROJECT_ID}/g" k8s/deployment.yaml

# Verify the changes

cat k8s/deployment.yaml | grep "gcr.io"
cat k8s/deployment.yaml | grep "GCP_PROJECT_ID"

"""
Step 5.2: Deploy Application
"""

# Apply deployment

kubectl apply -f k8s/deployment.yaml

# Wait for rollout

kubectl rollout status deployment/pnkln-file-search -n pnkln-core

# Check pods

kubectl get pods -n pnkln-core

"""
Step 5.3: Deploy Autoscaling
"""

kubectl apply -f k8s/hpa.yaml

# Verify HPA

kubectl get hpa -n pnkln-core

"""
Step 5.4: Deploy Ingress (Optional)
"""

# Install nginx ingress controller first

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx \
 --namespace ingress-nginx \
 --create-namespace

# Wait for external IP

kubectl get svc -n ingress-nginx

# Update ingress.yaml with your domain

sed -i "s/file-search.pnkln.ai/YOUR_DOMAIN/g" k8s/ingress.yaml

# Apply ingress

kubectl apply -f k8s/ingress.yaml

# ==============================================================================

# PHASE 6: VERIFY DEPLOYMENT (10 minutes)

# ==============================================================================

"""
Step 6.1: Check Pod Status
"""

kubectl get pods -n pnkln-core
kubectl logs -f deployment/pnkln-file-search -n pnkln-core

"""
Step 6.2: Port Forward for Testing
"""

kubectl port-forward -n pnkln-core svc/pnkln-file-search 8000:80

"""
Step 6.3: Test Health Endpoints
"""

# Liveness check

curl http://localhost:8000/health/live

# Readiness check

curl http://localhost:8000/health/ready

# Full health check

curl http://localhost:8000/health

# Detailed monitoring health

curl http://localhost:8000/api/v1/monitoring/health

"""
Step 6.4: Test Query Processing
"""

curl -X POST http://localhost:8000/api/v1/query \
 -H "Content-Type: application/json" \
 -d '{
"query": "Can we share technical specifications with NATO allies?",
"vertical": "defense"
}' | jq .

"""
Step 6.5: Test Corpus Management
"""

# List all corpora

curl http://localhost:8000/api/v1/corpus | jq .

# List verticals

curl http://localhost:8000/api/v1/verticals | jq .

# Get specific vertical

curl http://localhost:8000/api/v1/verticals/defense | jq .

# ==============================================================================

# PHASE 7: MONITORING SETUP (20 minutes)

# ==============================================================================

"""
Step 7.1: Install Prometheus Stack
"""

helm repo add prometheus-community \
 https://prometheus-community.github.io/helm-charts

helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
 --namespace monitoring \
 --create-namespace \
 --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

"""
Step 7.2: Create ServiceMonitor
"""

kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
name: pnkln-file-search
namespace: pnkln-core
labels:
app: pnkln-file-search
spec:
selector:
matchLabels:
app: pnkln-file-search
endpoints: - port: http
path: /metrics
interval: 30s
EOF

"""
Step 7.3: Access Prometheus UI
"""

kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Open http://localhost:9090

"""
Step 7.4: Access Grafana
"""

# Get Grafana password

kubectl get secret -n monitoring prometheus-grafana \
 -o jsonpath="{.data.admin-password}" | base64 --decode; echo

# Port forward

kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Open http://localhost:3000

# Username: admin

# Password: [from above]

"""
Step 7.5: Key Metrics to Monitor
"""

# File search latency P99

histogram_quantile(0.99, rate(file_search_latency_seconds_bucket[5m]))

# Judge Layer 1 latency P99

histogram_quantile(0.99, rate(judge_layer1_latency_seconds_bucket[5m]))

# Error rate

rate(file_search_errors_total[5m])

# Request throughput

rate(http_requests_total{job="pnkln-file-search"}[5m])

# ==============================================================================

# PHASE 8: LOAD TESTING (30 minutes)

# ==============================================================================

"""
Step 8.1: Install k6 Load Testing Tool
"""

# macOS

brew install k6

# Linux

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

"""
Step 8.2: Create Load Test Script
"""

cat > load_test.js <<'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
stages: [
{ duration: '2m', target: 10 }, // Ramp up to 10 users
{ duration: '5m', target: 10 }, // Stay at 10 users
{ duration: '2m', target: 50 }, // Ramp up to 50 users
{ duration: '5m', target: 50 }, // Stay at 50 users
{ duration: '2m', target: 0 }, // Ramp down
],
thresholds: {
http_req_duration: ['p(99)<1000'], // 99% of requests under 1s
},
};

export default function () {
const payload = JSON.stringify({
query: 'Can we export technical data to allied countries?',
vertical: 'defense',
});

const params = {
headers: {
'Content-Type': 'application/json',
},
};

const res = http.post('http://localhost:8000/api/v1/query', payload, params);

check(res, {
'status is 200': (r) => r.status === 200,
'response has enforcement': (r) => JSON.parse(r.body).enforcement !== undefined,
'latency under 1s': (r) => r.timings.duration < 1000,
});

sleep(1);
}
EOF

"""
Step 8.3: Run Load Test
"""

# Run test

k6 run load_test.js

# Monitor metrics in Grafana during test

# ==============================================================================

# PHASE 9: PRODUCTION READINESS (Checklist)

# ==============================================================================

"""
Deployment Checklist
"""

# Infrastructure

[ ] GKE cluster created with autoscaling
[ ] Workload Identity configured
[ ] Service account has minimal permissions
[ ] Network policies applied
[ ] Resource limits set

# Application

[ ] All 30 corpora initialized
[ ] Policy documents uploaded to GCS
[ ] Judge #6 layers implemented
[ ] Environment variables configured
[ ] Health checks passing

# Monitoring

[ ] Prometheus collecting metrics
[ ] Grafana dashboards configured
[ ] Alerting rules created
[ ] Log aggregation enabled (Cloud Logging)

# Security

[ ] TLS/HTTPS configured
[ ] Secrets in Secret Manager
[ ] Non-root container user
[ ] Network policies enforced
[ ] Security scan passed

# Testing

[ ] Unit tests passing
[ ] Integration tests passing
[ ] Load testing completed
[ ] Performance targets met (Judge ≤90ms p99)

# Operations

[ ] Runbook created
[ ] Incident response plan
[ ] Backup strategy tested
[ ] Rollback plan verified

# ==============================================================================

# TROUBLESHOOTING COMMON ISSUES

# ==============================================================================

"""
Issue 1: Pods Not Starting
"""

# Check pod events

kubectl describe pod <pod-name> -n pnkln-core

# Check logs

kubectl logs <pod-name> -n pnkln-core

# Common fixes:

# - Workload Identity not configured: Re-run Phase 2 Step 2.3

# - Image pull error: Re-run Phase 4

# - Resource limits too low: Increase in deployment.yaml

"""
Issue 2: File Search Returning Errors
"""

# Check Vertex AI quota

gcloud alpha services quota list \
 --service=aiplatform.googleapis.com \
 --filter="metric.type:aiplatform.googleapis.com"

# Check GCS access

kubectl exec -n pnkln-core deployment/pnkln-file-search -- \
 gsutil ls gs://${BUCKET_NAME}/

"""
Issue 3: High Latency
"""

# Check kill switch status

curl http://localhost:8000/api/v1/monitoring/health

# Scale up manually

kubectl scale deployment pnkln-file-search -n pnkln-core --replicas=6

# Check metrics

curl http://localhost:8000/metrics | grep latency

# ==============================================================================

# NEXT STEPS

# ==============================================================================

"""
After successful deployment:

1. Implement Judge #6 layers (see JUDGE_IMPLEMENTATION_GUIDE.md)
2. Configure vertical-specific rules
3. Set up alerting (PagerDuty, Slack, etc.)
4. Create Grafana dashboards
5. Document runbooks
6. Train team on operations
7. Gradually increase traffic
8. Monitor and optimize
   """
