# Judge #6 GKE Platform - Quick Start Guide

## 🚀 Fastest Path to Production (30-45 minutes)

### Prerequisites

- Google Cloud SDK installed
- kubectl installed
- Active GCP project with billing enabled

### Step-by-Step Deployment

#### 1. Pre-Flight Validation (2 minutes)

**ALWAYS run this first** to catch issues before deployment:

```bash
# Set your project ID
export PNKLN_PROJECT_ID="your-project-id"
export REGION="us-central1"

# Run pre-flight checks
./preflight-check.sh
```

Expected output:

```
╔═══════════════════════════════════════════════════════════════════╗
║   ✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

**If checks fail:**

- Review the detailed output
- Fix any errors (enable APIs, request quotas, etc.)
- Re-run `./preflight-check.sh` until all checks pass

#### 2. Deploy Infrastructure (30-45 minutes)

Once pre-flight checks pass:

```bash
# Option A: Standalone bash script (recommended for first deployment)
./pnkln-gke-deploy.sh

# Option B: Using Makefile
make deploy

# Option C: Terraform (for infrastructure-as-code)
cd terraform
terraform init
terraform apply
```

The script will:

- ✅ Create GKE cluster (v1.32+, rapid channel)
- ✅ Configure GPU node pools (L4, 0-20 nodes)
- ✅ Set up Artifact Registry
- ✅ Configure Secret Manager
- ✅ Enable monitoring and logging
- ✅ Set up Vertex AI Workbench

#### 3. Configure API Keys (CRITICAL - 5 minutes)

**Deployment will fail without valid API keys:**

```bash
# Anthropic Claude API
echo -n "sk-ant-api03-xxxx" | \
  gcloud secrets versions add anthropic-api-key \
  --data-file=- --project=$PNKLN_PROJECT_ID

# OpenAI GPT API
echo -n "sk-xxxx" | \
  gcloud secrets versions add openai-api-key \
  --data-file=- --project=$PNKLN_PROJECT_ID

# xAI Grok API
echo -n "xai-xxxx" | \
  gcloud secrets versions add xai-api-key \
  --data-file=- --project=$PNKLN_PROJECT_ID

# Mistral API (optional)
echo -n "xxxx" | \
  gcloud secrets versions add mistral-api-key \
  --data-file=- --project=$PNKLN_PROJECT_ID

# Google Cloud (uses ADC, no key needed)
# Vertex AI uses Workload Identity automatically
```

#### 4. Deploy Judge #6 Application (5 minutes)

```bash
# Get cluster credentials
gcloud container clusters get-credentials judge6-inference \
  --region=$REGION --project=$PNKLN_PROJECT_ID

# Deploy the application
kubectl apply -f judge-deployment.yaml

# Wait for deployment to complete
kubectl rollout status deployment/judge-inference -n pnkln-judge

# Verify pods are running
kubectl get pods -n pnkln-judge
```

Expected output:

```
NAME                               READY   STATUS    RESTARTS   AGE
judge-inference-7d9f8b6c5d-abc12   3/3     Running   0          2m
judge-inference-7d9f8b6c5d-def34   3/3     Running   0          2m
judge-inference-7d9f8b6c5d-ghi56   3/3     Running   0          2m
```

#### 5. Validate SLA Compliance (2 minutes)

```bash
# One-time check
./monitor-sla.sh --once

# Continuous monitoring (recommended for production)
./monitor-sla.sh --continuous &
```

Expected output:

```
✅ P99 Latency: 85ms (threshold: ≤90ms)
✅ P95 Latency: 45ms (threshold: ≤50ms)
✅ P50 Latency: 18ms (threshold: ≤20ms)
✅ Success Rate: 99.8%
```

#### 6. Access Vertex AI Workbench (Development)

```bash
# Open Workbench UI
make workbench

# Or manually
gcloud notebooks instances list \
  --location=$REGION --project=$PNKLN_PROJECT_ID

# Upload pnkln-workbench.ipynb for interactive development
```

## 🎯 Verification Checklist

After deployment, verify:

- [ ] Pre-flight checks passed
- [ ] GKE cluster created and healthy
- [ ] GPU node pool configured (0-20 L4 nodes)
- [ ] API keys stored in Secret Manager
- [ ] Judge #6 pods running (3/3 ready)
- [ ] SLA targets met (p99≤90ms)
- [ ] Cost tracking enabled
- [ ] Monitoring dashboards accessible
- [ ] Vertex AI Workbench accessible

## 🔍 Troubleshooting

### Pre-flight Check Failures

**Error: "Billing not enabled"**

```bash
# Link billing account
gcloud beta billing accounts list
gcloud beta billing projects link $PNKLN_PROJECT_ID \
  --billing-account=<ACCOUNT_ID>
```

**Error: "L4 GPU quota: 0"**

```bash
# Request quota increase
open "https://console.cloud.google.com/iam-admin/quotas?project=$PNKLN_PROJECT_ID"
# Search: "NVIDIA L4 GPUs" in us-central1
# Request: 20 GPUs
```

**Error: "API not enabled"**

```bash
# Enable all required APIs
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  --project=$PNKLN_PROJECT_ID
```

### Deployment Failures

**Error: "Insufficient quota for GPUs"**

- Run `./preflight-check.sh` to verify quotas
- Request quota increase (takes 1-2 business days)
- Temporarily reduce `max-nodes` in deployment script

**Error: "Cannot pull container images"**

```bash
# Configure Docker authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

**Error: "Secrets not found"**

- Verify API keys are stored: `gcloud secrets list --project=$PNKLN_PROJECT_ID`
- Re-run step 3 to add missing secrets

### SLA Violations

**P99 latency > 90ms:**

```bash
# Scale up replicas
kubectl scale deployment judge-inference -n pnkln-judge --replicas=5

# Check GPU node utilization
kubectl top nodes -l gpu-type=nvidia-l4

# Review logs for bottlenecks
kubectl logs -n pnkln-judge -l app=judge6 --tail=100
```

**High error rate:**

```bash
# Check API key validity
gcloud secrets versions access latest --secret=anthropic-api-key

# Review pod events
kubectl describe pods -n pnkln-judge

# Check service mesh connectivity
kubectl get networkpolicies -n pnkln-judge
```

## 💰 Cost Management

### Daily Cost Tracking

```bash
# Current costs
make cost-estimate

# Set up billing alerts
gcloud alpha billing budgets create \
  --billing-account=<ACCOUNT_ID> \
  --display-name="Judge6 Daily Budget" \
  --budget-amount=500 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

### Cost Optimization

```bash
# Development mode (lower costs)
kubectl scale deployment judge-inference -n pnkln-judge --replicas=1

# Production mode (full scale)
kubectl scale deployment judge-inference -n pnkln-judge --replicas=5

# Check GPU utilization
kubectl top nodes -l gpu-type=nvidia-l4
```

## 🔒 Security Best Practices

### Post-Deployment Security Hardening

1. **Rotate API Keys Regularly**

   ```bash
   # Update secrets
   echo -n "new-key" | gcloud secrets versions add anthropic-api-key --data-file=-

   # Restart deployment to pick up new secrets
   kubectl rollout restart deployment/judge-inference -n pnkln-judge
   ```

2. **Review IAM Permissions**

   ```bash
   # List service account permissions
   gcloud projects get-iam-policy $PNKLN_PROJECT_ID

   # Apply least-privilege principle
   ```

3. **Enable Audit Logging**

   ```bash
   # Verify audit logs are enabled
   gcloud logging read "protoPayload.serviceName=container.googleapis.com" \
     --project=$PNKLN_PROJECT_ID --limit=10
   ```

4. **Network Security**

   ```bash
   # Verify network policies are applied
   kubectl get networkpolicies -n pnkln-judge

   # Check private node configuration
   gcloud container clusters describe judge6-inference \
     --region=$REGION --format="value(privateClusterConfig)"
   ```

## 📊 Monitoring & Observability

### Access Monitoring Dashboards

```bash
# Open Cloud Console Monitoring
open "https://console.cloud.google.com/monitoring?project=$PNKLN_PROJECT_ID"

# View GKE cluster metrics
open "https://console.cloud.google.com/kubernetes/clusters?project=$PNKLN_PROJECT_ID"

# Access Prometheus metrics (if configured)
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

### Key Metrics to Monitor

- **Latency**: p50, p95, p99 response times
- **Throughput**: Requests per second
- **Error Rate**: Failed requests / total requests
- **GPU Utilization**: % GPU memory and compute used
- **Cost**: Daily spend vs. budget
- **Node Autoscaling**: GPU nodes scaled 0-20

## 🚀 Next Steps

1. **Load Testing**

   ```bash
   # Run validation tests
   cd validation/
   python validate_latency.py
   ```

2. **Custom Configuration**
   - Adjust HPA settings in `judge-deployment.yaml`
   - Tune LLM weights in orchestrator
   - Configure alert thresholds

3. **Production Promotion**
   - Review all security settings
   - Enable continuous monitoring
   - Set up on-call rotations
   - Document runbooks

4. **Team Onboarding**
   - Share access to GCP project
   - Distribute Vertex AI Workbench access
   - Set up CI/CD pipelines

## 📚 Additional Resources

- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [GPU Optimization Guide](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
- [Cost Optimization](https://cloud.google.com/kubernetes-engine/docs/how-to/cost-optimization)

## 🆘 Support

For issues or questions:

1. Check `./preflight-check.sh` output
2. Review logs: `kubectl logs -n pnkln-judge -l app=judge6`
3. Run diagnostics: `make diagnose`
4. Consult `DEPLOYMENT_SUMMARY.txt` for detailed architecture

---

**Project**: PNKLN Judge #6 GKE Inference Platform
**Version**: 1.0.0
**Last Updated**: 2025-01-08
**Deployment Time**: 30-45 minutes (automated)
**SLA Target**: p99≤90ms, p95≤50ms, p50≤20ms
**Cost Range**: $50-500/day (dev to prod scale)
