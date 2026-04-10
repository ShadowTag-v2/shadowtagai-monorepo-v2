# GKE Inference Deployment Checklist

**Complete this checklist before and after deployment to ensure production readiness.**

## Pre-Deployment

### GCP Project Setup

- [ ] GCP project created
- [ ] Billing account linked
- [ ] Project ID documented: `__________________`
- [ ] IAM permissions verified for deploying user
- [ ] Organization policies reviewed (if applicable)

### Quota Verification

Navigate to: `https://console.cloud.google.com/iam-admin/quotas`

- [ ] NVIDIA_L4_GPUS: ≥32 (current: `____`)
- [ ] CPUS: ≥1000 (current: `____`)
- [ ] IN_USE_ADDRESSES: ≥1000 (current: `____`)
- [ ] Quota increase requests submitted (if needed)
- [ ] Quota increase approved (if needed)

### Tool Installation

- [ ] `gcloud` CLI installed (version: `____`)
- [ ] `kubectl` installed (version ≥1.28: `____`)
- [ ] `terraform` installed (version ≥1.8.0: `____`)
- [ ] `jq` installed
- [ ] `git` installed

### Authentication

- [ ] `gcloud auth login` completed
- [ ] `gcloud config set project PROJECT_ID` executed
- [ ] Service account created for Terraform (if using CI/CD)
- [ ] Service account key secured (if applicable)

### API Enablement

Run preflight script or manually enable:

- [ ] container.googleapis.com
- [ ] compute.googleapis.com
- [ ] aiplatform.googleapis.com
- [ ] artifactregistry.googleapis.com
- [ ] monitoring.googleapis.com
- [ ] logging.googleapis.com
- [ ] storage.googleapis.com
- [ ] certificatemanager.googleapis.com
- [ ] networkservices.googleapis.com

### Terraform Backend

- [ ] GCS bucket for state created: `gs://PROJECT_ID-terraform-state`
- [ ] Bucket versioning enabled
- [ ] Bucket location set to: `____`
- [ ] IAM permissions on bucket configured

### Configuration Files

- [ ] `terraform/terraform.tfvars` created from example
- [ ] Project ID updated in tfvars
- [ ] Region configured: `____`
- [ ] Cluster name configured: `____`
- [ ] Environment variables exported

### Cost Planning

- [ ] Monthly budget approved: $`____`
- [ ] Cost alerts configured
- [ ] Budget threshold set at: `____`%
- [ ] Billing export to BigQuery enabled

### Security Review

- [ ] VPC design reviewed
- [ ] Firewall rules documented
- [ ] Private cluster decision confirmed
- [ ] Workload Identity strategy approved
- [ ] Secret management plan defined

### Model Preparation

- [ ] Model weights downloaded/prepared
- [ ] Model format verified (compatible with vLLM)
- [ ] Quantization applied (if needed)
- [ ] Model upload plan documented
- [ ] GCS bucket for models created

## Deployment Phase

### Preflight Execution

- [ ] `./scripts/preflight.sh` executed successfully
- [ ] All checks passed
- [ ] Warnings reviewed and addressed

### Terraform Deployment

- [ ] `cd terraform` executed
- [ ] `terraform init` completed without errors
- [ ] Backend initialized successfully
- [ ] `terraform plan` reviewed
- [ ] Resource count verified: `____` to add
- [ ] Cost estimate reviewed
- [ ] `terraform apply` executed
- [ ] Apply completed successfully
- [ ] Outputs captured:
  - Cluster endpoint: `____`
  - Gateway IP: `____`
  - Artifact Registry: `____`

### Cluster Verification

- [ ] `kubectl` credentials configured
- [ ] `kubectl cluster-info` succeeds
- [ ] `kubectl get nodes` shows nodes
- [ ] Node pools created:
  - [ ] system-pool
  - [ ] judge-l4-pool
  - [ ] llm-prefill-l4-pool
  - [ ] llm-decode-l4-pool

### Kubernetes Deployments

- [ ] Namespaces created
- [ ] GKE Inference Gateway deployed
- [ ] Gateway status: Programmed
- [ ] Gateway IP allocated: `____`
- [ ] LLM prefill deployment created
- [ ] LLM decode deployment created
- [ ] Pods running (check with `kubectl get pods -A`)
- [ ] HPA configured
- [ ] Services exposed

### Model Upload

- [ ] Model weights uploaded to GCS
- [ ] Bucket path: `gs://____`
- [ ] CSI driver mounted successfully in pods
- [ ] Model loading verified in logs

## Post-Deployment Validation

### Health Checks

- [ ] All deployments available
- [ ] All pods running and ready
- [ ] Gateway health check passing
- [ ] vLLM health endpoints responding

```bash
kubectl get deployments -A
kubectl get pods -A
kubectl get gateway -n cognitive-stack-v5
```

### Connectivity Tests

- [ ] Gateway IP responds to HTTP requests
- [ ] `/health` endpoint returns 200
- [ ] Sample inference request succeeds
- [ ] Response time acceptable

```bash
# Test health endpoint
curl http://GATEWAY_IP/health

# Test inference
curl -X POST http://GATEWAY_IP/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "pnkln-hybrid-model", "prompt": "Hello", "max_tokens": 5}'
```

### Performance Validation

- [ ] Latency test executed
- [ ] P99 latency ≤90ms: `____`ms
- [ ] Throughput test passed
- [ ] GPU utilization reasonable (40-80%)
- [ ] Cache hit rate measured: `____`%

### Monitoring Setup

- [ ] Prometheus metrics visible
- [ ] GKE monitoring dashboard accessible
- [ ] Custom metrics appearing in HPA
- [ ] Logs flowing to Cloud Logging

```bash
kubectl get hpa -A
kubectl top pods -A
kubectl top nodes
```

### Autoscaling Tests

- [ ] HPA status checked
- [ ] Current/target metrics visible
- [ ] Manual scale test performed
- [ ] Scale-up observed (if load applied)
- [ ] Scale-down behavior verified

### Cost Tracking

- [ ] BigQuery dataset created for GKE usage
- [ ] Cost allocation tags applied
- [ ] First day's costs visible in billing
- [ ] Spot instance usage confirmed
- [ ] Actual vs. estimated cost reviewed

### Security Validation

- [ ] Workload Identity functioning
- [ ] RBAC policies applied
- [ ] Network policies tested
- [ ] Pod Security Standards enforced
- [ ] Secrets encrypted at rest
- [ ] No exposed credentials in logs

## Production Readiness

### Documentation

- [ ] Deployment notes captured
- [ ] Architecture diagram updated
- [ ] Runbook created
- [ ] Troubleshooting guide reviewed
- [ ] Contact information documented

### Backup & Recovery

- [ ] GKE cluster backup enabled
- [ ] Terraform state backed up
- [ ] Model weights have versioning
- [ ] Disaster recovery plan documented
- [ ] Recovery tested (optional for v1)

### Alerting

- [ ] Alert policies created
- [ ] Notification channels configured
- [ ] On-call rotation defined
- [ ] Escalation policy documented
- [ ] Test alert sent and received

### DNS & SSL

- [ ] DNS record created: `api.pnkln.ai` → `GATEWAY_IP`
- [ ] DNS propagation verified
- [ ] SSL certificate requested
- [ ] HTTPS enabled
- [ ] HTTP → HTTPS redirect configured

### Load Testing

- [ ] Load testing tool selected
- [ ] Test scenarios defined
- [ ] Baseline load test executed
- [ ] Results documented: `____` RPS sustained
- [ ] Breaking point identified: `____` RPS

### Rollout Plan

- [ ] Phased rollout strategy defined
- [ ] Canary deployment plan (if applicable)
- [ ] Traffic split configuration
- [ ] Rollback procedure documented
- [ ] Rollback tested (optional)

## Ongoing Operations

### Daily Checks

- [ ] Monitor GKE dashboard
- [ ] Review alert history
- [ ] Check cost anomalies
- [ ] Verify backup status

### Weekly Reviews

- [ ] Analyze P99 latency trends
- [ ] Review GPU utilization
- [ ] Check for pod evictions
- [ ] Review security scan results
- [ ] Update capacity planning

### Monthly Tasks

- [ ] Update dependencies
- [ ] Review and optimize costs
- [ ] Audit access logs
- [ ] Review and update documentation
- [ ] Terraform state health check

## Sign-Off

### Deployment Team

- [ ] Infrastructure Lead: `________________` Date: `____`
- [ ] ML Engineer: `________________` Date: `____`
- [ ] Security Engineer: `________________` Date: `____`
- [ ] DevOps Lead: `________________` Date: `____`

### Stakeholder Approval

- [ ] Engineering Manager: `________________` Date: `____`
- [ ] Finance (Cost Approval): `________________` Date: `____`
- [ ] Product Owner: `________________` Date: `____`

### Production Go/No-Go

**Final Decision**: [ ] GO [ ] NO-GO

**Authorized by**: `____________________`

**Date**: `____________________`

**Notes**:

```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

---

**Checklist Version**: 1.0
**Last Updated**: 2025-11-08
**Next Review**: 2025-12-08
