# Pinkln Multi-Agent Infrastructure Manifests

Kubernetes manifests for the Pinkln multi-agent ecosystem Phase 1 deployment.

## Overview

This directory contains the core infrastructure for running self-evolving multi-agent debates with Glicko-2 ratings and continuous benchmarking.

## Files

| File | Purpose | Resources Created |
|------|---------|-------------------|
| **redis.yaml** | Agent communication & state | Namespace, Deployment, Service, PVC (20Gi), ConfigMap |
| **glicko-service.yaml** | Agent rating system | Deployment (2 replicas), Service, HPA, ServiceMonitor, ConfigMap |
| **dte-debate-job.yaml** | Debate-Test-Evolve orchestration | Job template, CronJob (every 6h), PVC (100Gi ReadWriteMany), ConfigMap |

## Quick Deploy

### Prerequisites

- GKE cluster with GPU node pools deployed
- kubectl configured
- Namespace: `pinkln-system` (created automatically)

### Deploy All Components

```bash
# Deploy in order
kubectl apply -f redis.yaml
kubectl apply -f glicko-service.yaml
kubectl apply -f dte-debate-job.yaml

# Wait for ready
kubectl wait --for=condition=Ready pods --all -n pinkln-system --timeout=5m
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n pinkln-system

# Test Redis
kubectl exec -it redis-cli -n pinkln-system -- redis-cli -h redis-master ping
# Expected: PONG

# Test Glicko service
kubectl port-forward -n pinkln-system svc/glicko-service 8080:8080 &
curl http://localhost:8080/health
# Expected: {"status": "healthy"}
```

## Architecture

```
в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ
в”Ӯ         Pinkln System (Namespace)            в”Ӯ
в”Ӯ                                              в”Ӯ
в”Ӯ  в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ  в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җ  в”Ңв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”җв”Ӯ
в”Ӯ  в”Ӯ  Redis   в”ӮвҶ’в”Ӯ Glicko Serviceв”ӮвҶ’в”Ӯ  DTE   в”Ӯв”Ӯ
в”Ӯ  в”Ӯ(Backend) в”Ӯ  в”Ӯ (Ratings API) в”Ӯ  в”Ӯ (Jobs) в”Ӯв”Ӯ
в”Ӯ  в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ  в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ  в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳв”Ӯ
в”Ӯ       вҶ“              вҶ“                вҶ“     в”Ӯ
в”Ӯ  [20Gi PVC]    [Auto-scale 2-10]  [100Gi]  в”Ӯ
в””в”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”Җв”ҳ
         вҶ“                    вҶ“
   [Agent State]      [Performance Ratings]
```

## Components

### 1. Redis (Agent Communication)

**Purpose**: Shared state for multi-agent debates and Glicko backend

**Resources**:
- Deployment: 1 replica
- Storage: 20Gi PVC (persistent ratings)
- Config: 2GB memory, LRU eviction, AOF persistence

**Usage**:
```bash
# Connect to Redis
kubectl exec -it redis-cli -n pinkln-system -- redis-cli -h redis-master

# Check keys
redis-master:6379> KEYS agent:*
redis-master:6379> GET agent:code-crafter:rating
```

### 2. Glicko-2 Rating Service

**Purpose**: Manage sophisticated agent performance ratings

**Resources**:
- Deployment: 2-10 replicas (HPA)
- Service: ClusterIP on port 8080
- Metrics: Prometheus endpoint on port 9090

**API Endpoints**:

```bash
# Health check
GET /health

# List all agents
GET /api/v1/agents

# Get specific agent
GET /api/v1/agents/{agent_name}

# Create agent
POST /api/v1/agents
{
  "name": "code-crafter",
  "specialty": "humaneval",
  "initial_rating": 1500
}

# Submit result (updates rating)
POST /api/v1/results
{
  "agent": "code-crafter",
  "benchmark": "humaneval",
  "score": 0.68,
  "opponents": ["deep-reasoning"],
  "timestamp": "2025-11-17T10:00:00Z"
}

# Get leaderboard
GET /api/v1/leaderboard?benchmark=humaneval
```

**Initial Agents** (configured):
- `wealth-accelerator` (revenue optimization)
- `deep-reasoning` (BigCodeBench)
- `code-crafter` (HumanEval)
- `ultrathink-designer` (architecture)
- `panel-debate` (consensus)

### 3. DTE (Debate-Test-Evolve) Framework

**Purpose**: Orchestrate multi-agent debates with automatic evolution

**Resources**:
- Job template: 8 parallel agents per debate
- CronJob: Every 6 hours continuous debates
- PVC: 100Gi ReadWriteMany for agent communication

**Configuration** (dte-config ConfigMap):
```yaml
debate:
  group_size: 8
  rounds: 3
  timeout_seconds: 300

kernels:
  available: [cot, tot, rcr, rtf, tag, bab, care, rise]
  default_chain: "cot-tot-rcr"

evolution:
  enabled: true
  mutation_rate: 0.1
  crossover_rate: 0.3
```

**Manual Trigger**:
```bash
# Create one-time debate job
kubectl create job --from=cronjob/dte-debate-continuous \
  manual-debate-$(date +%s) -n pinkln-system

# Monitor
kubectl logs -f job/manual-debate-* -n pinkln-system
```

## Container Images Required

**Note**: These images must be built and pushed before jobs will run successfully.

| Image | Purpose | Dockerfile Location |
|-------|---------|---------------------|
| `gcr.io/ShadowTag-production/glicko-service:latest` | Rating API | `src/agents/glicko/Dockerfile` |
| `gcr.io/ShadowTag-production/pinkln-agent:latest` | DTE agent runner | `src/agents/dte/Dockerfile` |

Build commands (to be run from repo root):

```bash
# Glicko service
docker build -f src/agents/glicko/Dockerfile -t gcr.io/ShadowTag-production/glicko-service:latest .
docker push gcr.io/ShadowTag-production/glicko-service:latest

# Pinkln agent
docker build -f src/agents/dte/Dockerfile -t gcr.io/ShadowTag-production/pinkln-agent:latest .
docker push gcr.io/ShadowTag-production/pinkln-agent:latest
```

## Monitoring

### Metrics

Glicko service exposes Prometheus metrics:

```bash
# View metrics
kubectl port-forward -n pinkln-system svc/glicko-service 9090:9090 &
curl http://localhost:9090/metrics
```

**Available Metrics**:
- `glicko_rating_updates_total` - Total rating updates
- `glicko_agent_rating` - Current agent ratings
- `glicko_agent_rd` - Rating deviation
- `glicko_agent_volatility` - Rating volatility
- `glicko_api_request_duration_seconds` - API latency

### Logs

```bash
# Redis logs
kubectl logs -f -n pinkln-system deployment/redis-master

# Glicko service logs
kubectl logs -f -n pinkln-system deployment/glicko-service

# DTE job logs (when running)
kubectl logs -f -n pinkln-system job/dte-debate-*
```

### Dashboards

If using Prometheus Operator, ServiceMonitor is automatically configured.

Import Grafana dashboard for Glicko metrics:
- Panel 1: Agent ratings over time (line chart)
- Panel 2: Rating deviation (lower = more certain)
- Panel 3: API request rate
- Panel 4: Redis memory usage

## Cost Tracking

**Baseline** (always running):
- Redis: ~1 vCPU, 2GB RAM = $50/mo
- Glicko service: ~4 vCPU, 8GB RAM = $100/mo
- **Total**: ~$150/mo

**Variable** (when jobs run):
- DTE debate (8 agents Г— 1 GPU Г— 1h): ~$12/run
- Continuous (every 6h): 4 runs/day = ~$48/day = $1,440/mo

**Total Phase 1**: $150 baseline + $1,440 active = **$1,590/mo**

## Troubleshooting

### Issue: Glicko service can't connect to Redis

```bash
# Check Redis service
kubectl get svc -n pinkln-system redis-master

# Test connectivity from Glicko pod
kubectl exec -it deployment/glicko-service -n pinkln-system -- \
  nc -zv redis-master 6379

# If fails, check network policies
kubectl get networkpolicies -n pinkln-system
```

### Issue: DTE jobs pending (no nodes)

```bash
# Check multi-agent node pool
kubectl get nodes -l workload=multi-agent

# If empty, node pool is scaling up (takes 5-7 min)

# Force node creation
kubectl scale deployment test-deployment --replicas=1 -n pinkln-system

# Or check node pool configuration
gcloud container node-pools describe multi-agent-a100-pool \
  --cluster=ShadowTag-production-gpu \
  --region=us-central1
```

### Issue: PVC not binding (agent-shared-memory)

```bash
# Check PVC status
kubectl describe pvc agent-shared-memory-pvc -n pinkln-system

# ReadWriteMany requires Filestore CSI driver

# Enable Filestore
gcloud container clusters update ShadowTag-production-gpu \
  --update-addons GcpFilestoreCsiDriver=ENABLED \
  --region=us-central1

# Or change to ReadWriteOnce (single-node only)
# Edit dte-debate-job.yaml:
#   accessModes:
#     - ReadWriteOnce
```

## Next Steps

1. **Build Container Images** (see above)
2. **Initialize Agents**:
   ```bash
   # Port-forward Glicko service
   kubectl port-forward -n pinkln-system svc/glicko-service 8080:8080 &

   # Create agents
   for agent in code-crafter deep-reasoning wealth-accelerator; do
     curl -X POST http://localhost:8080/api/v1/agents \
       -H "Content-Type: application/json" \
       -d "{\"name\":\"$agent\",\"initial_rating\":1500}"
   done
   ```

3. **Run First Debate**:
   ```bash
   kubectl create job --from=cronjob/dte-debate-continuous \
     first-debate -n pinkln-system

   kubectl logs -f job/first-debate -n pinkln-system
   ```

4. **Monitor Evolution**:
   ```bash
   # Check ratings after debate
   curl http://localhost:8080/api/v1/leaderboard
   ```

## Related Documentation

- [Phase 1 Deployment Guide](../../../docs/deployment/PHASE1_DEPLOYMENT.md)
- [Pinkln Multi-Agent Architecture](../../../docs/architecture/pinkln-multi-agent-evolution.md)
- [GKE GPU Integration](../../../docs/architecture/gke-gpu-integration.md)

## Support

For issues or questions:
- **Internal**: #pinkln-platform Slack channel
- **Docs**: `docs/deployment/PHASE1_DEPLOYMENT.md`
- **GKE**: https://cloud.google.com/kubernetes-engine/docs
