# Phase 1 Deployment: Multi-Agent Infrastructure

> **Deploy Pinkln Multi-Agent Ecosystem - Week 1-2**
> **Date**: 2025-11-17
> **Estimated Time**: 4-6 hours
> **Prerequisites**: GKE cluster deployed (from Quick Start)

---

## Overview

Phase 1 deploys the foundation for the Pinkln multi-agent ecosystem:

1. ✅ **Multi-Agent Node Pool** (4× A100, 0-8 nodes)
2. ✅ **Redis** (agent communication + Glicko backend)
3. ✅ **Glicko-2 Rating Service** (agent performance tracking)
4. ✅ **DTE Orchestration** (Debate-Test-Evolve framework)
5. ✅ **Continuous Benchmarks** (HumanEval every 6h, SWE-bench daily)

---

## Prerequisites

### 1. Verify Existing Infrastructure

```bash
# Check GKE cluster is running
gcloud container clusters list --project=ShadowTag-production

# Get credentials
gcloud container clusters get-credentials ShadowTag-production-gpu \
  --region us-central1 \
  --project ShadowTag-production

# Verify existing node pools
kubectl get nodes -L workload,gpu

# Should see: inference, fine-tuning, training, batch pools
```

### 2. Check GPU Quotas

```bash
# Check A100 quota
gcloud compute project-info describe --project=ShadowTag-production | \
  grep -A 2 "NVIDIA_A100_GPUS"

# You need:
# - Current: 32 GPUs (existing pools)
# - Phase 1 adds: 32 GPUs (multi-agent pool, 8 nodes × 4 GPUs)
# - Total required: 64 GPUs

# If insufficient, request quota increase:
# https://console.cloud.google.com/iam-admin/quotas?project=ShadowTag-production
```

### 3. Required Tools

```bash
# Verify tool versions
terraform version  # >= 1.5.0
kubectl version --client  # >= 1.28
helm version  # >= 3.12
```

---

## Step 1: Deploy Multi-Agent Node Pool (30 min)

### 1.1 Update Terraform Configuration

The multi-agent node pool has already been added to `k8s/terraform/main.tf`.

Verify the configuration:

```bash
cd k8s/terraform

# Review the new pool
grep -A 15 "multi_agent_a100" main.tf
```

Expected output:
```hcl
multi_agent_a100 = {
  name               = "multi-agent-a100-pool"
  machine_type       = "a2-highgpu-4g"      # 4× A100
  accelerator_type   = "nvidia-tesla-a100"
  accelerator_count  = 4
  disk_size_gb       = 500
  disk_type          = "pd-ssd"
  min_nodes          = 0
  max_nodes          = 8                     # 32 GPUs max
  initial_nodes      = 0
  preemptible        = false
  workload_label     = "multi-agent"
}
```

### 1.2 Plan and Apply

```bash
# Initialize (if not already done)
terraform init

# Review changes
terraform plan

# Expected: 1 new node pool resource to be added
# Should see: module.gpu_node_pools["multi_agent_a100"]

# Apply changes
terraform apply

# Type 'yes' to confirm
# Deployment takes ~10-15 minutes
```

### 1.3 Verify Node Pool

```bash
# Check node pool created
gcloud container node-pools list \
  --cluster=ShadowTag-production-gpu \
  --region=us-central1 \
  --project=ShadowTag-production

# Should see: multi-agent-a100-pool

# Initially 0 nodes (auto-scales on demand)
kubectl get nodes -l workload=multi-agent
# (empty initially)
```

---

## Step 2: Deploy Redis (Agent Communication) (10 min)

### 2.1 Create Pinkln System Namespace

```bash
# Deploy Redis (includes namespace creation)
kubectl apply -f ../../manifests/multi-agent/redis.yaml

# Verify namespace
kubectl get namespace pinkln-system

# Check Redis deployment
kubectl get pods -n pinkln-system -l app=redis

# Wait for Redis to be ready
kubectl wait --for=condition=Ready pod -l app=redis \
  -n pinkln-system --timeout=5m
```

### 2.2 Test Redis Connection

```bash
# Use redis-cli pod to test
kubectl exec -it redis-cli -n pinkln-system -- redis-cli -h redis-master ping

# Expected: PONG

# Check Redis info
kubectl exec -it redis-cli -n pinkln-system -- redis-cli -h redis-master info server

# Should show: Redis version 7.x
```

### 2.3 Verify Persistence

```bash
# Check PVC created
kubectl get pvc -n pinkln-system

# Should see: redis-data-pvc (20Gi)

# Check data directory in Redis
kubectl exec -it redis-master-* -n pinkln-system -- ls -lh /data

# Should see: appendonly.aof (Redis persistence file)
```

---

## Step 3: Deploy Glicko-2 Rating Service (15 min)

### 3.1 Deploy Service

```bash
# Deploy Glicko service
kubectl apply -f ../../manifests/multi-agent/glicko-service.yaml

# Check deployment
kubectl get deployments -n pinkln-system -l app=glicko-service

# Wait for replicas
kubectl wait --for=condition=Available deployment/glicko-service \
  -n pinkln-system --timeout=5m

# Check pods
kubectl get pods -n pinkln-system -l app=glicko-service
```

### 3.2 Test Glicko API

```bash
# Port-forward to local machine
kubectl port-forward -n pinkln-system svc/glicko-service 8080:8080 &

# Wait a few seconds, then test health endpoint
curl http://localhost:8080/health

# Expected: {"status": "healthy", "redis": "connected"}

# Test rating endpoint (should return initial ratings)
curl http://localhost:8080/api/v1/ratings

# Expected: JSON with 5 agents at rating 1500

# Stop port-forward
pkill -f "port-forward.*glicko-service"
```

### 3.3 Verify Auto-Scaling

```bash
# Check HPA created
kubectl get hpa -n pinkln-system glicko-service-hpa

# Should show: minReplicas: 2, maxReplicas: 10

# Check current replicas
kubectl get deployment glicko-service -n pinkln-system -o jsonpath='{.status.replicas}'

# Should be: 2 (initial replicas)
```

---

## Step 4: Deploy DTE Orchestration (15 min)

### 4.1 Create Shared Memory PVC

```bash
# Deploy DTE infrastructure
kubectl apply -f ../../manifests/multi-agent/dte-debate-job.yaml

# Check PVC for agent communication
kubectl get pvc -n pinkln-system agent-shared-memory-pvc

# Should show: 100Gi ReadWriteMany
```

### 4.2 Create Agent Container Images

**Note**: You'll need to build the agent container images. For now, create placeholder:

```bash
# Create a simple Dockerfile for testing
cat > /tmp/Dockerfile.agent <<'EOF'
FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir \
    redis \
    requests \
    numpy

# Placeholder agent script
RUN echo 'print("Agent ready")' > /app/dte_runner.py

WORKDIR /app
CMD ["python", "dte_runner.py"]
EOF

# Build and push (replace with your GCR path)
# docker build -f /tmp/Dockerfile.agent -t gcr.io/ShadowTag-production/pinkln-agent:latest .
# docker push gcr.io/ShadowTag-production/pinkln-agent:latest

# For Phase 1, we'll skip the actual DTE job execution
echo "Agent images will be built in Phase 2"
```

### 4.3 Verify DTE Configuration

```bash
# Check ConfigMap
kubectl get configmap -n pinkln-system dte-config -o yaml

# Verify configuration:
# - group_size: 8
# - kernels available
# - evolution enabled

# Check CronJob created (won't run until images are ready)
kubectl get cronjobs -n pinkln-system dte-debate-continuous

# Should show: SCHEDULE: "0 */6 * * *" (every 6 hours)
```

---

## Step 5: Deploy Benchmark Runners (20 min)

### 5.1 Deploy HumanEval Runner

```bash
# Deploy HumanEval
kubectl apply -f ../../manifests/benchmarks/humaneval-runner.yaml

# Check CronJob
kubectl get cronjobs -n pinkln-system humaneval-benchmark

# Verify config
kubectl get configmap -n pinkln-system humaneval-config -o yaml

# Should show:
# - 164 problems
# - agents: code-crafter, deep-reasoning
# - pass@k scoring
```

### 5.2 Deploy SWE-bench Runner

First, create a GitHub token for SWE-bench:

```bash
# Create GitHub personal access token:
# https://github.com/settings/tokens/new
# Scopes needed: repo (read), public_repo

# Update secret with your token
kubectl create secret generic github-creds \
  --from-literal=token=YOUR_GITHUB_TOKEN_HERE \
  -n pinkln-system \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy SWE-bench
kubectl apply -f ../../manifests/benchmarks/swe-bench-runner.yaml

# Check CronJob
kubectl get cronjobs -n pinkln-system swe-bench-daily

# Should show: SCHEDULE: "0 2 * * *" (daily at 2 AM)
```

### 5.3 Create Placeholder Benchmark Images

```bash
# Similar to agent images, create placeholders

# HumanEval runner
cat > /tmp/Dockerfile.humaneval <<'EOF'
FROM python:3.11-slim
RUN pip install --no-cache-dir requests
RUN echo 'print("HumanEval benchmark ready")' > /app/run_humaneval.py
WORKDIR /app
CMD ["python", "run_humaneval.py"]
EOF

# SWE-bench runner
cat > /tmp/Dockerfile.swebench <<'EOF'
FROM python:3.11-slim
RUN pip install --no-cache-dir requests docker
RUN echo 'print("SWE-bench ready")' > /app/run_swe_bench.py
WORKDIR /app
CMD ["python", "run_swe_bench.py"]
EOF

# Build and push (to be done in Phase 2)
echo "Benchmark images will be built in Phase 2"
```

---

## Step 6: Validate Deployment (10 min)

### 6.1 Check All Resources

```bash
# Verify all resources deployed
kubectl get all -n pinkln-system

# Should see:
# - deployment/redis-master (1/1 ready)
# - deployment/glicko-service (2/2 ready)
# - service/redis-master
# - service/glicko-service
# - cronjob/dte-debate-continuous
# - cronjob/humaneval-benchmark
# - cronjob/swe-bench-daily
```

### 6.2 Check Resource Allocations

```bash
# Check PVCs
kubectl get pvc -n pinkln-system

# Should see:
# - redis-data-pvc (20Gi)
# - agent-shared-memory-pvc (100Gi)

# Check ConfigMaps
kubectl get configmap -n pinkln-system

# Should see:
# - redis-config
# - glicko-config
# - dte-config
# - humaneval-config
# - swe-bench-config
```

### 6.3 Test End-to-End Flow

```bash
# Port-forward Glicko service
kubectl port-forward -n pinkln-system svc/glicko-service 8080:8080 &

# Initialize agent ratings
curl -X POST http://localhost:8080/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "code-crafter",
    "specialty": "humaneval",
    "initial_rating": 1500
  }'

# Check agent was created
curl http://localhost:8080/api/v1/agents/code-crafter

# Expected: {"name": "code-crafter", "rating": 1500, "rd": 350, "vol": 0.06}

# Submit a mock result
curl -X POST http://localhost:8080/api/v1/results \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "code-crafter",
    "benchmark": "humaneval",
    "score": 0.68,
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Check rating updated
curl http://localhost:8080/api/v1/agents/code-crafter

# Stop port-forward
pkill -f "port-forward.*glicko-service"
```

---

## Step 7: Monitor and Verify (15 min)

### 7.1 Set Up Monitoring

```bash
# Check Glicko service metrics
kubectl port-forward -n pinkln-system svc/glicko-service 9090:9090 &

# View Prometheus metrics
curl http://localhost:9090/metrics | grep glicko

# Stop port-forward
pkill -f "port-forward.*9090"
```

### 7.2 Check Logs

```bash
# Redis logs
kubectl logs -n pinkln-system deployment/redis-master --tail=50

# Glicko service logs
kubectl logs -n pinkln-system deployment/glicko-service --tail=50

# Should show: "Service started", "Connected to Redis"
```

### 7.3 Verify Node Pool Auto-Scaling

```bash
# Currently no nodes (no workloads scheduled)
kubectl get nodes -l workload=multi-agent

# To test auto-scaling, manually trigger a job
kubectl create job --from=cronjob/dte-debate-continuous \
  test-dte-debate -n pinkln-system

# Wait 2-3 minutes, check nodes
kubectl get nodes -l workload=multi-agent -w

# Should see: Nodes provisioning (takes 5-7 min)

# Check job status
kubectl get jobs -n pinkln-system test-dte-debate

# Delete test job
kubectl delete job test-dte-debate -n pinkln-system

# Nodes will scale down to 0 after 10-15 minutes of idle
```

---

## Step 8: Cost Verification (5 min)

### 8.1 Check Current Costs

```bash
# View node pool configurations
gcloud container node-pools describe multi-agent-a100-pool \
  --cluster=ShadowTag-production-gpu \
  --region=us-central1 \
  --project=ShadowTag-production

# Machine type: a2-highgpu-4g
# Cost: ~$12/hour per node (4× A100)
# Max nodes: 8
# Max cost: $96/hour = $69,120/month (if running 24/7)

# Current cost: $0 (0 nodes provisioned)
```

### 8.2 Set Up Cost Alerts

```bash
# Verify budget alert exists
gcloud billing budgets list \
  --billing-account=$(gcloud billing accounts list --format='value(name)' | head -1) \
  --filter="displayName:'GPU Compute Budget'"

# Should show: $50,000/month budget with 50%, 80%, 100% thresholds
```

---

## Phase 1 Complete! 🎉

### What You've Deployed

| Component | Status | Resources | Purpose |
|-----------|--------|-----------|---------|
| **Multi-Agent Node Pool** | ✅ Ready | 0-8 nodes, 4× A100 each | GRPO training, DTE debates |
| **Redis** | ✅ Running | 1 pod, 20Gi PVC | Agent communication, Glicko backend |
| **Glicko Service** | ✅ Running | 2 pods, auto-scale 2-10 | Agent performance tracking |
| **DTE Framework** | ✅ Configured | CronJob every 6h | Debate-Test-Evolve automation |
| **HumanEval** | ✅ Configured | CronJob every 6h | Code generation benchmark |
| **SWE-bench** | ✅ Configured | CronJob daily | Software engineering benchmark |

### Current State

- ✅ Infrastructure deployed and tested
- ✅ Glicko ratings initialized (5 agents at 1500)
- ✅ Auto-scaling enabled (scales to 0 when idle)
- ✅ Continuous benchmarks configured (will run when images ready)
- ⏳ **Next**: Build agent container images (Phase 2)

### Current Costs

| Component | Cost | Notes |
|-----------|------|-------|
| Existing GKE cluster | $4,591/mo | From v1.0 deployment |
| Redis + Glicko | ~$150/mo | 3 pods, 20Gi PVC |
| Multi-agent pool | $0/mo | 0 nodes (scales on demand) |
| **Total Phase 1** | **$4,741/mo** | **+$150 over baseline** |

**When workloads run**:
- DTE debate (8 agents, 1h): ~$12
- HumanEval (1 GPU, 2h): ~$6
- SWE-bench (2 GPUs, 4h): ~$24
- **Estimated monthly**: +$2,880 (4h/day average)

---

## Troubleshooting

### Issue: Node pool not created

```bash
# Check Terraform state
terraform state list | grep multi_agent

# If missing, re-apply
terraform apply -target=module.gpu_node_pools[\"multi_agent_a100\"]
```

### Issue: Redis not connecting

```bash
# Check Redis logs
kubectl logs -n pinkln-system deployment/redis-master

# Test connection
kubectl exec -it redis-cli -n pinkln-system -- redis-cli -h redis-master

# If connection refused, check service
kubectl get svc -n pinkln-system redis-master
```

### Issue: Glicko service not ready

```bash
# Check logs
kubectl logs -n pinkln-system deployment/glicko-service

# Common issues:
# - Redis not accessible (check service name)
# - ConfigMap not mounted (check volume mounts)

# Restart deployment
kubectl rollout restart deployment/glicko-service -n pinkln-system
```

### Issue: PVC not binding

```bash
# Check PVC status
kubectl get pvc -n pinkln-system

# If pending, check storage class
kubectl get storageclass

# For ReadWriteMany (agent-shared-memory-pvc), need Filestore
# May need to enable Filestore CSI driver

gcloud container clusters update ShadowTag-production-gpu \
  --update-addons GcpFilestoreCsiDriver=ENABLED \
  --region=us-central1
```

---

## Next Steps

### Phase 2: Core Agents (Weeks 3-4)

Now that infrastructure is deployed, proceed to Phase 2:

1. **Build Agent Container Images**:
   - `pinkln-agent:latest` (DTE runner)
   - `humaneval-runner:latest` (HumanEval benchmark)
   - `swe-bench-runner:latest` (SWE-bench benchmark)
   - `glicko-service:latest` (Rating API)

2. **Implement Agent Logic**:
   - Kernel-chaining framework (CoT, ToT, RCR, etc.)
   - GRPO training loop
   - DTE debate orchestration
   - Glicko-2 rating calculations

3. **Deploy Initial Agents**:
   - Code Crafter (HumanEval specialist)
   - Deep Reasoning (BigCodeBench)
   - Wealth Accelerator (revenue optimization)
   - Panel Debate (consensus building)

4. **Run First DTE Debate**:
   - Trigger manual debate on HumanEval
   - Measure baseline performance
   - Update Glicko ratings
   - Document results

**See**: `docs/deployment/PHASE2_DEPLOYMENT.md` (to be created)

---

## Validation Checklist

Before proceeding to Phase 2, verify:

- [ ] Multi-agent node pool visible in GKE console
- [ ] Redis running and accepting connections
- [ ] Glicko service responds to health checks
- [ ] Agent ratings can be created via API
- [ ] PVCs bound and ready
- [ ] CronJobs created (even if not executing yet)
- [ ] Auto-scaling works (tested with manual job)
- [ ] Costs tracked in GCP billing
- [ ] Budget alerts configured

---

## Summary

**Time Spent**: ~4-6 hours (including verification)
**Resources Deployed**: 15+ Kubernetes resources
**Cost Impact**: +$150/mo baseline, +$2,880/mo when active
**Status**: ✅ Phase 1 Complete - Ready for Phase 2

---

**Document Status**: ✅ Phase 1 Deployment Guide
**Last Updated**: 2025-11-17
**Next**: Phase 2 - Core Agents & First DTE Debate
