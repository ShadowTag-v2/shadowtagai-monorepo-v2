# Judge 6 Operations Runbook

## Quick Reference

**Service**: Judge 6 AI Governance Platform
**Deployment**: GKE Autopilot + Vertex AI
**SLA**: 99.9% uptime
**Support**: 24/7 on-call rotation

---

## Table of Contents

1. [Health Checks](#health-checks)
2. [Common Alerts](#common-alerts)
3. [Incident Response](#incident-response)
4. [Performance Tuning](#performance-tuning)
5. [Scaling Operations](#scaling-operations)

---

## Health Checks

### Quick Health Check (2 minutes)

```bash
# Set context
export PROJECT_ID="pnkln-prod"
export REGION="us-central1"

# 1. GKE Cluster Health
kubectl get nodes
kubectl get pods -n judge-6

# 2. Application Health
kubectl get deployment -n judge-6
kubectl get hpa -n judge-6

# 3. Check recent errors
kubectl logs -n judge-6 -l app=judge-6 --tail=50 | grep ERROR

# 4. Vertex AI Status
gcloud ai-platform models list --region=${REGION}

# 5. Document AI Status
gcloud documentai processors list --location=us
```

**Expected Results**:

- All nodes: `Ready`
- All pods: `Running` with `1/1` ready
- HPA: Within normal replica range (2-20)
- No ERROR logs in last 50 lines

### Deep Health Check (10 minutes)

```bash
# 1. End-to-end test
gsutil cp test/data/sample-compliance.pdf gs://${PROJECT_ID}-compliance-docs/intake/health-check-$(date +%s).pdf

# 2. Monitor processing
gcloud functions logs read process-compliance-document --region=${REGION} --limit=10

# 3. Check workflow completion
gcloud firestore export gs://${PROJECT_ID}-firestore-exports --collection-ids=Cor.Claude_Code_6_workflows --async

# 4. Verify metrics
gcloud monitoring time-series list \
  --filter='metric.type="custom.googleapis.com/Cor.Claude_Code_6/workflow_duration_seconds"' \
  --interval-start-time=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --interval-end-time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## Common Alerts

### ALERT: High Pod Crash Rate

**Symptom**: CrashLoopBackOff or frequent restarts

**Diagnosis**:

```bash
# Check pod status
kubectl get pods -n judge-6

# Check recent events
kubectl get events -n judge-6 --sort-by='.lastTimestamp'

# Check pod logs
kubectl logs -n judge-6 POD_NAME --previous

# Check resource limits
kubectl describe pod POD_NAME -n judge-6 | grep -A 5 Limits
```

**Common Causes & Fixes**:

1. **Out of Memory (OOM)**

   ```bash
   # Increase memory limits
   kubectl patch deployment judge-6-vllm -n judge-6 -p '
   {
     "spec": {
       "template": {
         "spec": {
           "containers": [{
             "name": "vllm-server",
             "resources": {
               "limits": {"memory": "96Gi"}
             }
           }]
         }
       }
     }
   }'
   ```

2. **Model Loading Timeout**

   ```bash
   # Increase readiness probe delay
   kubectl edit deployment judge-6-vllm -n judge-6
   # Update: readinessProbe.initialDelaySeconds: 300
   ```

3. **GPU Allocation Failure**

   ```bash
   # Check GPU availability
   kubectl describe nodes | grep -A 10 nvidia.com/gpu

   # Request GPU quota increase
   gcloud compute project-info describe --project=${PROJECT_ID} | grep NVIDIA
   ```

### ALERT: High Inference Latency (p99 >500ms)

**Symptom**: Slow response times, timeout errors

**Diagnosis**:

```bash
# Check current latency
kubectl port-forward -n judge-6 svc/judge-6-vllm 8000:8000 &
curl http://localhost:8000/metrics | grep latency

# Check HPA scaling
kubectl get hpa judge-6-vllm-hpa -n judge-6 -o yaml

# Check GPU utilization
kubectl exec -it judge-6-vllm-XXXXX -n judge-6 -- nvidia-smi
```

**Common Causes & Fixes**:

1. **Underprovisioned Replicas**

   ```bash
   # Scale up manually
   kubectl scale deployment judge-6-vllm --replicas=10 -n judge-6

   # Or adjust HPA target
   kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '
   {
     "spec": {
       "metrics": [{
         "type": "Pods",
         "pods": {
           "metric": {"name": "p99_latency_ms"},
           "target": {
             "type": "AverageValue",
             "averageValue": "300"
           }
         }
       }]
     }
   }'
   ```

2. **Large Batch Size**

   ```bash
   # Reduce batch size for lower latency
   kubectl set env deployment/judge-6-vllm -n judge-6 MAX_NUM_SEQS=128
   ```

3. **Cold Start Delays**
   ```bash
   # Increase minimum replicas
   kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '{"spec":{"minReplicas":3}}'
   ```

### ALERT: Pub/Sub Backlog Growing

**Symptom**: `num_undelivered_messages` increasing

**Diagnosis**:

```bash
# Check subscription backlog
gcloud pubsub subscriptions describe langgraph-consumer

# Check consumer pods
kubectl get pods -n judge-6 -l component=orchestrator

# Check consumer logs for errors
kubectl logs -n judge-6 -l component=orchestrator --tail=100
```

**Common Causes & Fixes**:

1. **Slow Processing**

   ```bash
   # Scale orchestrator
   kubectl scale deployment judge-6-orchestrator --replicas=20 -n judge-6
   ```

2. **Stuck Messages**

   ```bash
   # Check dead letter queue
   gcloud pubsub subscriptions pull judge-6-dead-letter --auto-ack --limit=5

   # Manual message processing
   python scripts/reprocess_dead_letters.py --limit=100
   ```

3. **Poison Messages**

   ```bash
   # Identify problematic messages
   gcloud pubsub subscriptions pull langgraph-consumer --limit=10 --format=json

   # Purge if necessary
   gcloud pubsub subscriptions seek langgraph-consumer --time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
   ```

### ALERT: Document AI Quota Exceeded

**Symptom**: 429 errors from Document AI

**Diagnosis**:

```bash
# Check current quota usage
gcloud documentai operations list --location=us

# Check quota limits
gcloud compute project-info describe --project=${PROJECT_ID} | grep documentai
```

**Fixes**:

1. **Request Quota Increase**

   ```bash
   # Submit quota increase request
   gcloud alpha quotas update \
     --service=documentai.googleapis.com \
     --consumer=projects/${PROJECT_ID} \
     --metric=documentai.googleapis.com/document_request_count \
     --value=10000
   ```

2. **Implement Rate Limiting**

   ```python
   # In cloud function
   from google.cloud import firestore
   import time

   def rate_limit():
       db = firestore.Client()
       ref = db.collection('rate_limits').document('documentai')
       doc = ref.get()
       if doc.exists and doc.get('count') >= 1000:  # Per-minute limit
           time.sleep(60)
       ref.set({'count': firestore.Increment(1)}, merge=True)
   ```

---

## Incident Response

### Severity Levels

| Level         | Response Time     | Example                                  |
| ------------- | ----------------- | ---------------------------------------- |
| P0 - Critical | 15 min            | Complete service outage                  |
| P1 - High     | 1 hour            | Degraded performance (>50% SLA miss)     |
| P2 - Medium   | 4 hours           | Single component failure with redundancy |
| P3 - Low      | Next business day | Non-critical bug or feature request      |

### P0 - Critical Incident Response

**Symptoms**: Complete service outage, all pods down

**Immediate Actions** (First 15 minutes):

```bash
# 1. Assess scope
kubectl get all -n judge-6
gcloud container clusters describe judge-6-inference --region=${REGION}

# 2. Check for cluster-level issues
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | head -20

# 3. Engage on-call team
# Post in #incidents Slack channel
# Page SRE on-call via PagerDuty

# 4. Enable detailed logging
kubectl logs -n judge-6 --all-containers=true --prefix=true --tail=200
```

**Escalation Path**:

1. On-call SRE (immediate)
2. Lead Engineer (15 min)
3. CTO (30 min)
4. CEO (1 hour, if customer-impacting)

**Recovery Actions**:

1. **GKE Cluster Down**

   ```bash
   # Check cluster status
   gcloud container clusters describe judge-6-inference --region=${REGION}

   # If cluster is corrupted, deploy to DR region
   cd infrastructure/terraform
   terraform apply -var="region=us-east1"
   ```

2. **Vertex AI API Down**

   ```bash
   # Check GCP status
   curl https://status.cloud.google.com/incidents.json

   # Failover to backup model endpoint
   kubectl set env deployment/judge-6-vllm -n judge-6 \
     MODEL_ENDPOINT=https://backup-endpoint.vertexai.com
   ```

3. **Database Corruption**

   ```bash
   # Restore from Firestore backup
   gcloud firestore import gs://${PROJECT_ID}-firestore-backups/latest/

   # Verify data integrity
   python scripts/verify_firestore_integrity.py
   ```

### Post-Incident Review

Within 48 hours of P0/P1 incidents:

1. **Incident Timeline**
   - Detection time
   - Response time
   - Mitigation time
   - Resolution time

2. **Root Cause Analysis**
   - What happened?
   - Why did it happen?
   - How was it detected?
   - How was it resolved?

3. **Action Items**
   - Preventive measures
   - Detection improvements
   - Response improvements
   - Owner + Due date

**Template**: `/docs/templates/postmortem-template.md`

---

## Performance Tuning

### Optimize for Latency

**Target**: p99 TTFT <200ms

```bash
# 1. Enable prefix caching
kubectl set env deployment/judge-6-vllm -n judge-6 ENABLE_PREFIX_CACHING=true

# 2. Reduce batch size
kubectl set env deployment/judge-6-vllm -n judge-6 MAX_NUM_SEQS=64

# 3. Increase replicas to reduce queuing
kubectl scale deployment judge-6-vllm --replicas=5 -n judge-6

# 4. Use smaller model variant
# Update deployment to use gemini-2.0-flash-exp (faster than thinking variant)
```

### Optimize for Throughput

**Target**: 50,000 tokens/sec aggregate

```bash
# 1. Increase batch size
kubectl set env deployment/judge-6-vllm -n judge-6 MAX_NUM_BATCHED_TOKENS=32768

# 2. Enable continuous batching
kubectl set env deployment/judge-6-vllm -n judge-6 ENABLE_CONTINUOUS_BATCHING=true

# 3. Use tensor parallelism for large models
kubectl set env deployment/judge-6-vllm -n judge-6 TENSOR_PARALLEL_SIZE=2

# 4. Maximize GPU utilization
kubectl set env deployment/judge-6-vllm -n judge-6 GPU_MEMORY_UTILIZATION=0.95
```

### Optimize for Cost

**Target**: <$0.003 per 1K tokens

```bash
# 1. Use INT8 quantization
kubectl set env deployment/judge-6-vllm -n judge-6 QUANTIZATION=int8

# 2. Scale to zero during off-hours
kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '{"spec":{"minReplicas":0}}'

# 3. Use smaller GPU (L4 instead of A100)
# Already configured in deployment

# 4. Enable request batching at application layer
# Update LangGraph orchestrator to batch requests
```

---

## Scaling Operations

### Manual Scaling

```bash
# Scale specific deployment
kubectl scale deployment judge-6-vllm --replicas=10 -n judge-6

# Scale orchestrator
kubectl scale deployment judge-6-orchestrator --replicas=20 -n judge-6

# Verify scaling
kubectl get pods -n judge-6 -w
```

### Adjust Autoscaling

```bash
# Increase max replicas
kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '{"spec":{"maxReplicas":50}}'

# Adjust scaling metrics
kubectl edit hpa judge-6-vllm-hpa -n judge-6
# Update target QPS, latency, or GPU utilization

# View current autoscaling decisions
kubectl describe hpa judge-6-vllm-hpa -n judge-6
```

### Planned Traffic Spikes

**Before large customer onboarding**:

```bash
# 1. Pre-warm cluster (1 hour before)
kubectl scale deployment judge-6-vllm --replicas=20 -n judge-6

# 2. Increase resource quotas
kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '{"spec":{"maxReplicas":100}}'

# 3. Monitor closely
watch kubectl get hpa -n judge-6

# 4. Scale back after spike (12 hours after)
kubectl patch hpa judge-6-vllm-hpa -n judge-6 -p '{"spec":{"maxReplicas":20}}'
```

---

## Maintenance Operations

### Rolling Updates

```bash
# Update vLLM image
kubectl set image deployment/judge-6-vllm vllm-server=NEW_IMAGE:TAG -n judge-6

# Monitor rollout
kubectl rollout status deployment/judge-6-vllm -n judge-6

# Verify health
kubectl get pods -n judge-6
kubectl logs -n judge-6 -l app=judge-6 --tail=50

# Rollback if issues
kubectl rollout undo deployment/judge-6-vllm -n judge-6
```

### Certificate Rotation

```bash
# GKE auto-rotates certificates
# Verify certificate validity
kubectl get certificatesigningrequests

# Manual rotation (if needed)
gcloud container clusters update judge-6-inference \
  --region=${REGION} \
  --rotate-certificates
```

### Database Maintenance

```bash
# Firestore backup
gcloud firestore export gs://${PROJECT_ID}-firestore-backups/$(date +%Y%m%d)/

# Verify backup
gsutil ls -l gs://${PROJECT_ID}-firestore-backups/

# Test restore (to separate project)
gcloud firestore import gs://${PROJECT_ID}-firestore-backups/latest/ \
  --project=${TEST_PROJECT_ID}
```

---

## Emergency Procedures

### Complete Shutdown

```bash
# 1. Stop processing new documents
gcloud functions update process-compliance-document --no-allow-unauthenticated

# 2. Drain existing workload
kubectl scale deployment judge-6-orchestrator --replicas=0 -n judge-6

# 3. Wait for queue to empty
gcloud pubsub subscriptions describe langgraph-consumer

# 4. Stop model servers
kubectl scale deployment judge-6-vllm --replicas=0 -n judge-6

# 5. Notify stakeholders
python scripts/send_maintenance_notification.py
```

### Complete Restore

```bash
# 1. Restore infrastructure
cd infrastructure/terraform
terraform apply

# 2. Restore database
gcloud firestore import gs://${PROJECT_ID}-firestore-backups/latest/

# 3. Restart services
kubectl apply -f infrastructure/kubernetes/

# 4. Verify health
bash scripts/health_check.sh

# 5. Re-enable processing
gcloud functions update process-compliance-document --allow-unauthenticated
```

---

## Contact Information

**On-Call Rotation**: PagerDuty (judge-6-oncall)
**Slack Channel**: #judge-6-ops
**Escalation Email**: oncall@pnkln.io
**Documentation**: https://docs.pnkln.io/judge-6/ops

**Last Updated**: 2025-11-07
**Review Frequency**: Monthly
