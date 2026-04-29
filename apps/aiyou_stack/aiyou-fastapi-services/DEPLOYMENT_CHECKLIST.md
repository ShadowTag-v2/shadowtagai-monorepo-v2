# PNKLN GKE Deployment Checklist

## KERNEL Success Criteria Validation

### ✅ K - Keep it Simple

- [x] 3 directories: `infra/`, `deploy/`, `validate/`
- [x] No complex dependencies (Terraform + kubectl only)
- [x] Single command deploys: `terraform apply`, `kubectl apply -f .`

### ✅ E - Easy to Verify

```bash
# Test 1: Terraform validation
cd infra && terraform init && terraform plan  # Expected: Zero errors

# Test 2: Kubernetes deployment
cd deploy && kubectl apply -f . && kubectl wait --for=condition=ready pod -l app=Claude_Code_6 -n pnkln --timeout=300s  # Expected: All pods ready

# Test 3: Latency SLA
cd validate && python test_latency.py --p99-target-ms=90  # Expected: PASS (exit 0)
```

### ✅ R - Reproducible

- [x] Terraform state management (GCS backend)
- [x] Versioned Kubernetes manifests
- [x] Deterministic testing harness

### ✅ N - Narrow Scope

- [x] Single workload: Judge 6 inference
- [x] Single SLA: p99 ≤90ms
- [x] Single platform: GKE Hypercomputer
- [x] Single constraint: ≤$65K/mo budget

### ✅ E - Explicit

- [x] All costs documented (see README.md)
- [x] All secrets managed (GCP Secret Manager)
- [x] All constraints defined (variables.tf)
- [x] All configurations exposed (ConfigMap)

### ✅ L - Logical Structure

```
Purpose (Deploy platform)  → infra/   (Terraform)
Reasons (Run inference)    → deploy/  (K8s manifests)
Brakes (Meet SLA)          → validate/ (Testing harness)
```

## Pre-Deployment Checklist

### GCP Project Setup

- [ ] GCP project created with billing enabled
- [ ] APIs enabled (container, compute, storage, secretmanager, monitoring)
- [ ] GPU quota requested and approved
  - [ ] NVIDIA_L4_GPUS: 3 in us-central1
  - [ ] NVIDIA_H100_80GB_GPUS: 2 in us-central1

### Tools Installation

- [ ] Terraform >= 1.8.0 installed
- [ ] kubectl installed and configured
- [ ] gcloud CLI installed
- [ ] Python 3.9+ installed
- [ ] Git installed (for version control)

### Authentication

- [ ] `gcloud auth login` completed
- [ ] `gcloud auth application-default login` completed
- [ ] Project set: `gcloud config set project PROJECT_ID`

### Configuration Files

- [ ] `infra/terraform.tfvars` created from example
- [ ] `project_id` set in terraform.tfvars
- [ ] `model_bucket_name` set (globally unique)
- [ ] `master_authorized_networks` updated with Vertex AI IPs
- [ ] GCS bucket name verified as unique

### Model Preparation

- [ ] Judge 6 model files ready
- [ ] Model size verified (fits in GPU memory)
- [ ] Model format compatible with vLLM/inference server

## Deployment Steps

### Phase 1: Infrastructure (20 min)

- [ ] `cd infra`
- [ ] `terraform init`
- [ ] `terraform plan` (verify zero errors)
- [ ] `terraform apply` (approve and wait ~15 min)
- [ ] Verify outputs: cluster_name, kubectl_config_command
- [ ] Configure kubectl with provided command

### Phase 2: Model Upload (5 min)

- [ ] Get bucket name: `terraform output model_bucket_name`
- [ ] Upload model: `gsutil -m cp -r MODEL_PATH gs://BUCKET/models/Claude_Code_6/`
- [ ] Verify upload: `gsutil ls gs://BUCKET/models/Claude_Code_6/`

### Phase 3: Workload Deployment (10 min)

- [ ] `cd ../deploy`
- [ ] Update `02-service-account.yaml` with PROJECT_ID
- [ ] Update `03-configmap.yaml` with bucket name
- [ ] Update `04-Claude_Code_6-deployment.yaml` with bucket name and GPU type
- [ ] Deploy: `kubectl apply -f .`
- [ ] Wait for ready: `kubectl wait --for=condition=ready pod -l app=Claude_Code_6 -n pnkln --timeout=600s`
- [ ] Verify pods: `kubectl get pods -n pnkln`
- [ ] Verify HPA: `kubectl get hpa -n pnkln`

### Phase 4: Validation (5 min)

- [ ] `cd ../validate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Health check: `bash test_health.sh`
- [ ] Latency test: `python test_latency.py --num-requests 100 --p99-target-ms 90`
- [ ] Verify: Exit code 0 and "✅ PASS" in output

## Post-Deployment Verification

### Infrastructure Health

- [ ] All Terraform resources created successfully
- [ ] VPC and subnet configured
- [ ] Cloud NAT operational
- [ ] GKE cluster running (Regional)
- [ ] CPU node pool active (1+ nodes)
- [ ] GPU node pools created (0 nodes until workload needs)

### Workload Health

- [ ] Namespace `pnkln` exists
- [ ] All pods in `Running` state
- [ ] Service `Claude_Code_6` has ClusterIP
- [ ] HPA shows current/desired replicas
- [ ] PodDisruptionBudget configured
- [ ] NetworkPolicy applied

### Performance Validation

- [ ] Health endpoint responding: `/health`
- [ ] Metrics endpoint responding: `/metrics`
- [ ] p99 latency ≤ 90ms
- [ ] Success rate ≥ 99%
- [ ] GPU utilization visible in logs

### Cost Validation

- [ ] GPU nodes scale to zero when idle (wait 10 min)
- [ ] Actual costs align with estimates
- [ ] Budget alerts configured (optional)

## Monitoring Setup

### Cloud Console

- [ ] Navigate to GKE → Workloads → Claude_Code_6
- [ ] Verify metrics visible (CPU, Memory, Network)
- [ ] Check logs for errors

### Prometheus (Optional)

- [ ] Port forward metrics: `kubectl port-forward -n pnkln svc/Claude_Code_6-metrics 8080:8080`
- [ ] Access metrics: `curl localhost:8080/metrics`
- [ ] Verify vLLM metrics present

### Alerting (Recommended)

- [ ] Create Cloud Monitoring alert for p99 > 90ms
- [ ] Create alert for pod failures
- [ ] Create alert for GPU node scale-up failures
- [ ] Configure notification channels

## Rollback Plan

### If Deployment Fails

```bash
# Remove workloads
cd deploy && kubectl delete -f .

# Check logs
kubectl logs -n pnkln -l app=Claude_Code_6

# Fix issues and redeploy
kubectl apply -f .
```

### If Infrastructure Fails

```bash
# Destroy partial infrastructure
cd infra && terraform destroy

# Fix terraform.tfvars and redeploy
terraform apply
```

### If Latency SLA Violated

1. Check GPU type (consider H100 upgrade)
2. Enable quantization (AWQ or FP8)
3. Verify Flash Attention enabled
4. Reduce batch size to 1
5. Increase HPA min replicas

## Security Hardening (Production)

### Pre-Production

- [ ] Enable private GKE endpoint
- [ ] Update master authorized networks (remove 0.0.0.0/0)
- [ ] Enable Binary Authorization
- [ ] Configure Secret Manager secrets
- [ ] Enable VPC Flow Logs
- [ ] Set up Cloud Armor

### Production

- [ ] Regular security audits
- [ ] Key rotation schedule (90 days)
- [ ] Access logging enabled
- [ ] Network policy reviewed
- [ ] Resource quotas configured

## Troubleshooting Guide

### GPU Nodes Not Scaling Up

**Check**: `kubectl get nodes -l cloud.google.com/gke-accelerator`
**Fix**: Verify GPU quota, check node pool autoscaling config

### Pods Pending

**Check**: `kubectl describe pod -n pnkln <pod-name>`
**Fix**: Look for quota, taint, or resource issues

### High Latency

**Check**: `kubectl logs -n pnkln -l app=Claude_Code_6`
**Fix**: Review ConfigMap, enable optimizations, check GPU utilization

### GCS Access Denied

**Check**: Workload Identity binding
**Fix**: Verify service account IAM permissions

## Cleanup Procedure

### Complete Teardown

```bash
# 1. Delete workloads
cd deploy && kubectl delete -f .

# 2. Wait for GPU nodes to scale down (optional, saves $)
sleep 300

# 3. Destroy infrastructure
cd ../infra && terraform destroy

# 4. Verify cleanup
gcloud compute instances list
gcloud container clusters list
gcloud storage buckets list --filter="name:pnkln-*"

# 5. Delete manually if needed
gcloud storage buckets delete gs://BUCKET_NAME --force
```

### Partial Cleanup (Keep Infrastructure)

```bash
# Scale down workloads to zero
kubectl scale deployment Claude_Code_6 -n pnkln --replicas=0

# GPU nodes will auto-scale to zero after ~10 minutes
```

## Success Criteria Summary

Deployment is successful when:

1. ✅ **Infrastructure**: `terraform plan` shows zero errors
2. ✅ **Deployment**: All pods Running, HPA active
3. ✅ **Latency**: `test_latency.py` returns exit code 0 (p99 ≤90ms)
4. ✅ **Cost**: Idle state ~$162/mo, GPU pools scale to zero
5. ✅ **Monitoring**: Metrics visible in Cloud Console

## Support

For issues:

1. Check logs: `kubectl logs -n pnkln -l app=Claude_Code_6`
2. Review events: `kubectl get events -n pnkln --sort-by='.lastTimestamp'`
3. Consult component READMEs:
   - `infra/README.md`
   - `deploy/README.md`
   - `validate/README.md`
4. Refer to main README.md troubleshooting section

---

**Checklist Version**: 1.0
**Last Updated**: 2025-11-08
**Compatible With**: Terraform 1.8+, GKE 1.27+, Python 3.9+
