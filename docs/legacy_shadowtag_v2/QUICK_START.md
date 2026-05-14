# Quick Start Guide - Judge #6 Validation Sprint

**Time to first results: ~30 minutes**

---

## Step 1: Prerequisites (5 minutes)

### Install Tools

```bash
# macOS
brew install --cask google-cloud-sdk
brew install kubectl

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud components install kubectl

# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

### Authenticate

```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud config list
```

---

## Step 2: Clone & Configure (2 minutes)

```bash
# Clone repository
git clone https://github.com/ehanc69/pnkln-stack-fastapi-services.git
cd pnkln-stack-fastapi-services

# Set environment variables
export GCP_PROJECT_ID="pnkln-validation"  # Replace with your project
export GCP_REGION="us-central1"           # Or your preferred region
export CLUSTER_NAME="pnkln-core-stack"

# Verify
echo "Project: $GCP_PROJECT_ID"
echo "Region: $GCP_REGION"
```

---

## Step 3: Deploy Infrastructure (15 minutes)

```bash
# Make script executable (if needed)
chmod +x infrastructure/pnkln-gke-bootstrap.sh

# Run bootstrap
./infrastructure/pnkln-gke-bootstrap.sh

# Expected output:
# [INFO] Checking prerequisites...
# [INFO] Enabling required GCP APIs...
# [INFO] Creating VPC network...
# [INFO] Creating GKE Autopilot cluster...
# [INFO] Configuring kubectl credentials...
# [INFO] Bootstrap completed successfully! 🚀
```

**What this does:**
- ✓ Enables required GCP APIs
- ✓ Creates VPC network and subnets
- ✓ Deploys GKE Autopilot cluster with GPU support
- ✓ Configures Workload Identity
- ✓ Sets up namespaces

**Coffee break**: This takes ~15 minutes. Good time for a coffee! ☕

---

## Step 4: Deploy Judge #6 (3 minutes)

```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/judge/configmap.yaml
kubectl apply -f k8s/judge/rules-config.yaml
kubectl apply -f k8s/judge/deployment.yaml
kubectl apply -f k8s/judge/hpa.yaml
kubectl apply -f k8s/judge/pdb.yaml

# Verify pods are running
kubectl get pods -n pnkln-core

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# judge-6-hybrid-xxxxxxxxxx-xxxxx   4/4     Running   0          2m

# Check services
kubectl get svc -n pnkln-core

# Expected output:
# NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
# judge-6-service   ClusterIP   10.x.x.x        <none>        80/TCP,9090/TCP
```

**What this does:**
- ✓ Creates pnkln-core namespace
- ✓ Deploys Judge #6 with 3 layers (Gemini, PyTorch, Rules)
- ✓ Configures HorizontalPodAutoscaler
- ✓ Sets up PodDisruptionBudget for HA

---

## Step 5: Deploy Monitoring (5 minutes)

```bash
# Install Prometheus (using Helm)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  -n pnkln-monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Wait for Prometheus to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n pnkln-monitoring --timeout=300s

# Apply monitoring configuration
kubectl apply -f k8s/monitoring/prometheus-servicemonitor.yaml
kubectl apply -f k8s/monitoring/prometheus-rules.yaml

# Verify
kubectl get servicemonitor -n pnkln-monitoring
kubectl get prometheusrule -n pnkln-monitoring
```

**What this does:**
- ✓ Installs Prometheus + Grafana stack
- ✓ Configures ServiceMonitor for Judge #6
- ✓ Sets up SLA alerting rules

---

## Step 6: Access Dashboards (2 minutes)

### Grafana

```bash
# Port-forward Grafana
kubectl port-forward -n pnkln-monitoring svc/prometheus-grafana 3000:80 &

# Get admin password
kubectl get secret -n pnkln-monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
echo

# Open browser
# URL: http://localhost:3000
# Username: admin
# Password: <from above command>

# Import dashboard: k8s/monitoring/grafana-dashboard.json
```

### Prometheus

```bash
# Port-forward Prometheus
kubectl port-forward -n pnkln-monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &

# Open browser
# URL: http://localhost:9090
```

---

## Step 7: Run Validation Test (1 hour)

### Option A: Quick Test (5 minutes)

```bash
# Install dependencies
pip install aiohttp numpy

# Quick test (5 minutes, light load)
cd src/workload-generator
export WORKLOAD_DURATION_SEC=300
export BASE_RPS=5
export PEAK_RPS=10
export BURST_RPS=20

python synthetic_workload.py
```

### Option B: Full Validation (1 hour)

```bash
# Full test (1 hour, realistic load)
cd src/workload-generator
export WORKLOAD_DURATION_SEC=3600
export BASE_RPS=10
export PEAK_RPS=50
export BURST_RPS=100

python synthetic_workload.py
```

**Monitor in another terminal:**

```bash
# Real-time SLA monitoring
watch -n 10 ./scripts/monitor-sla.sh
```

---

## Step 8: Check Results (1 minute)

```bash
# View validation results
cat validation_results.json

# Example output:
# {
#   "results": {
#     "total_requests": 1234,
#     "latency_p99_ms": 85.2,
#     "latency_p95_ms": 58.1,
#     "error_rate_percent": 0.5
#   },
#   "sla_compliance": {
#     "overall_compliant": true
#   },
#   "recommendation": "PROCEED"
# }

# Check cost
./scripts/cost-tracker.sh

# Check SLA compliance
./scripts/monitor-sla.sh
```

---

## Step 9: Make Decision

### If SLA Compliant (p99 ≤ 90ms):
✅ **PROCEED** to Week 2 customization
```bash
# Continue with architecture customization
# See docs/VALIDATION_SPRINT.md#phase-5
```

### If SLA Breach (p99 > 90ms):
❌ **ABORT** and pivot to ground-up build
```bash
# Document learnings
# Clean up resources
gcloud container clusters delete pnkln-core-stack --region=$GCP_REGION
```

---

## Cleanup (When Done)

### Quick Cleanup (keep cluster, remove apps)
```bash
kubectl delete namespace pnkln-core
kubectl delete namespace pnkln-monitoring
kubectl delete namespace pnkln-workload
```

### Full Cleanup (delete everything)
```bash
# Delete cluster
gcloud container clusters delete $CLUSTER_NAME --region=$GCP_REGION

# Delete network
gcloud compute networks subnets delete pnkln-subnet --region=$GCP_REGION
gcloud compute networks delete pnkln-vpc

# Verify
gcloud container clusters list
gcloud compute networks list
```

---

## Common Issues

### Issue: `kubectl` not connecting

```bash
# Re-fetch credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$GCP_REGION

# Verify
kubectl cluster-info
```

### Issue: Pods stuck in Pending

```bash
# Check events
kubectl describe pod -n pnkln-core <pod-name>

# Common cause: GPU quota
# Solution: Request quota increase in GCP Console
```

### Issue: High latency

```bash
# Check layer breakdown
./scripts/monitor-sla.sh

# Scale up
kubectl scale deployment judge-6-hybrid -n pnkln-core --replicas=6
```

### Issue: Budget exceeded

```bash
# Immediate scale down
kubectl scale deployment judge-6-hybrid -n pnkln-core --replicas=1

# Or delete cluster
gcloud container clusters delete $CLUSTER_NAME --region=$GCP_REGION
```

---

## Next Steps

1. **Week 1 Complete**: Review [Kill Switch Decision](docs/VALIDATION_SPRINT.md#phase-4-kill-switch-evaluation-week-1-end)
2. **If PROCEED**: Start [Week 2 Customization](docs/VALIDATION_SPRINT.md#phase-5-architecture-customization-week-2)
3. **If ABORT**: Document findings and pivot to ground-up build

---

## Useful Commands

```bash
# Watch pods
kubectl get pods -n pnkln-core -w

# View logs
kubectl logs -n pnkln-core deployment/judge-6-hybrid -c orchestrator --tail=100 -f

# Check HPA
kubectl get hpa -n pnkln-core

# Port-forward to Judge service (for local testing)
kubectl port-forward -n pnkln-core svc/judge-6-service 8080:80

# Quick SLA check
./scripts/monitor-sla.sh

# Quick cost check
./scripts/cost-tracker.sh

# View Grafana
kubectl port-forward -n pnkln-monitoring svc/prometheus-grafana 3000:80
```

---

**Estimated Total Time**: ~30 minutes (excluding 1-hour validation test)

**Budget Impact**: ~$15-20 for quick start, ~$360/day for full validation

**Questions?** See [docs/VALIDATION_SPRINT.md](docs/VALIDATION_SPRINT.md) for detailed documentation.
