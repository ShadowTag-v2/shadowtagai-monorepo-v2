# Plan Mode Automation Guide

Complete automation setup for Plan Mode Style Guide v1.0 across Claude Code, Vertex AI Workbench, and GKE deployments.

## 🎯 Quick Reference

| Platform | Method | Command |
|----------|--------|---------|
| **Claude Code** | Slash command | `/plan <task description>` |
| **Vertex AI** | Jupyter notebook | Upload `deployment/vertex-ai/plan_mode_notebook.ipynb` |
| **GKE** | REST API | `POST http://SERVICE_IP/generate-plan` |
| **Local Dev** | FastAPI | `./deployment/gke/run-local.sh` |

## 📋 Prerequisites

### Required Tools
- `gcloud` CLI (Google Cloud SDK)
- `kubectl` (Kubernetes CLI)
- Docker
- Python 3.11+
- Git

### Required Accounts
- Google Cloud Platform account with billing enabled
- Anthropic API key

### Required Permissions
- GCP Project Owner or Editor
- Ability to create GKE clusters
- Container Registry push access

## 🚀 Setup Instructions

### 1. Claude Code Integration

**No setup required!** The `/plan` command is ready to use.

```bash
# In Claude Code, simply type:
/plan Implement user authentication with OAuth2
```

**How it works:**
1. Reads `.claude/commands/plan.md`
2. Loads `PLAN_MODE_TEMPLATE.md`
3. Applies style guide rules
4. Generates plan in seconds

**Customization:**
Edit `.claude/commands/plan.md` to modify behavior:
- Adjust token limits
- Change model version
- Add custom rules

---

### 2. Vertex AI Workbench Setup

#### Step 1: Create Notebook Instance

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"

gcloud notebooks instances create plan-mode-notebook \
  --location=$REGION \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --project=$PROJECT_ID
```

#### Step 2: Upload Notebook

1. Open JupyterLab:
```bash
gcloud notebooks instances describe plan-mode-notebook \
  --location=$REGION \
  --format="value(proxyUri)"
```

2. Upload `deployment/vertex-ai/plan_mode_notebook.ipynb`

3. Set environment variable:
```python
import os
os.environ['ANTHROPIC_API_KEY'] = 'your-api-key'
```

#### Step 3: Run Notebook

Execute cells to:
- Generate individual plans
- Batch process multiple tasks
- Save plans to Cloud Storage
- Deploy as Vertex AI endpoint

**Batch Example:**
```python
tasks = [
    "Set up GKE cluster with autoscaling",
    "Configure Cloud Build CI/CD pipeline",
    "Implement monitoring with Cloud Operations"
]

for task in tasks:
    plan = generate_plan(task)
    print(plan)
```

---

### 3. GKE Deployment (Production)

#### Step 1: Environment Setup

```bash
export GCP_PROJECT_ID="your-project-id"
export GKE_CLUSTER="plan-mode-cluster"
export GKE_REGION="us-central1"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

#### Step 2: Run Setup Script

```bash
cd deployment/gke
./setup-cluster.sh
```

This script:
- ✅ Enables required GCP APIs
- ✅ Creates GKE cluster with autoscaling
- ✅ Configures Workload Identity
- ✅ Creates Kubernetes secrets
- ✅ Applies ConfigMaps

#### Step 3: Build and Push Container

```bash
# Build Docker image
docker build -t gcr.io/$GCP_PROJECT_ID/plan-mode-service:latest \
  -f deployment/gke/Dockerfile ../../

# Push to Google Container Registry
docker push gcr.io/$GCP_PROJECT_ID/plan-mode-service:latest
```

#### Step 4: Deploy to GKE

```bash
# Deploy all resources
envsubst < deployment/gke/deployment.yaml | kubectl apply -f -

# Wait for deployment
kubectl rollout status deployment/plan-mode-service

# Get service URL
kubectl get svc plan-mode-service
```

#### Step 5: Test Deployment

```bash
# Get external IP
SERVICE_IP=$(kubectl get svc plan-mode-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test health endpoint
curl http://$SERVICE_IP/health

# Test plan generation
curl -X POST http://$SERVICE_IP/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Implement rate limiting for API endpoints",
    "model": "claude-sonnet-4-5-20250929"
  }'
```

---

### 4. Local Development Setup

#### Step 1: Install Dependencies

```bash
cd deployment/gke
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 2: Set Environment Variables

```bash
export ANTHROPIC_API_KEY="your-api-key"
export PLAN_MODE_TEMPLATE_PATH="../../PLAN_MODE_TEMPLATE.md"
export PORT=8000
```

#### Step 3: Run Service

**Option A: Using helper script**
```bash
./run-local.sh
```

**Option B: Manual start**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 4: Access Service

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 🔄 CI/CD Automation

### Option 1: Cloud Build (Recommended for GCP)

#### Setup Cloud Build Trigger

```bash
gcloud builds triggers create github \
  --repo-name=aiyou-fastapi-services \
  --repo-owner=ehanc69 \
  --branch-pattern="^main$" \
  --build-config=deployment/ci-cd/cloudbuild.yaml \
  --included-files="deployment/gke/**,PLAN_MODE_TEMPLATE.md"
```

#### Manual Trigger

```bash
gcloud builds submit --config=deployment/ci-cd/cloudbuild.yaml .
```

**Pipeline Steps:**
1. Build Docker image
2. Push to GCR
3. Update ConfigMap
4. Deploy to GKE
5. Update deployment image
6. Wait for rollout
7. Run smoke tests

---

### Option 2: GitHub Actions

#### Setup Secrets

In GitHub repository settings, add:
- `GCP_PROJECT_ID`: Your GCP project ID
- `WIF_PROVIDER`: Workload Identity Federation provider
- `WIF_SERVICE_ACCOUNT`: Service account email

#### Configure Workload Identity Federation

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-pool \
  --location=global

# Create provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --workload-identity-pool=github-pool \
  --issuer-uri=https://token.actions.githubusercontent.com \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --location=global

# Grant permissions
gcloud iam service-accounts add-iam-policy-binding \
  plan-mode-service@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/ehanc69/aiyou-fastapi-services"
```

#### Automatic Deployment

Push to `main` or `develop` branch:
```bash
git push origin main
```

GitHub Actions will:
1. Authenticate to GCP
2. Build and push image
3. Deploy to GKE
4. Run smoke tests

---

## 📊 Usage Examples

### Claude Code

```bash
# Basic usage
/plan Add caching layer to FastAPI endpoints

# Complex feature
/plan Implement multi-tenant architecture with row-level security

# Refactoring
/plan Migrate from SQLAlchemy to Prisma ORM
```

### Vertex AI Notebook

```python
# Single plan
plan = generate_plan("Set up Redis caching")
print(plan)

# Batch processing
deployment_tasks = [
    "Configure load balancing",
    "Set up SSL certificates",
    "Implement health checks"
]

plans = {task: generate_plan(task) for task in deployment_tasks}

# Save to Cloud Storage
import json
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('plan-mode-outputs')
blob = bucket.blob('plans.json')
blob.upload_from_string(json.dumps(plans, indent=2))
```

### REST API (GKE/Local)

```bash
# Generate plan
curl -X POST http://localhost:8000/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Implement OAuth2 authentication",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 2048
  }' | jq '.plan'

# Health check
curl http://localhost:8000/health

# Service info
curl http://localhost:8000/
```

### Python SDK

```python
import requests

# Generate plan
response = requests.post(
    "http://SERVICE_IP/generate-plan",
    json={
        "task_description": "Add rate limiting to API",
        "model": "claude-sonnet-4-5-20250929"
    }
)

plan = response.json()['plan']
print(plan)
```

---

## 🔧 Configuration Options

### Model Selection

```python
# Default: Claude Sonnet 4.5
"model": "claude-sonnet-4-5-20250929"

# For faster responses (lower cost):
"model": "claude-3-5-haiku-20241022"

# For complex planning:
"model": "claude-opus-4-20250514"
```

### Token Limits

```python
# Short plans (500-1000 tokens)
"max_tokens": 1024

# Standard plans (1000-2000 tokens)
"max_tokens": 2048

# Detailed plans (2000-4000 tokens)
"max_tokens": 4096
```

### Autoscaling

Edit `deployment/gke/deployment.yaml`:

```yaml
spec:
  minReplicas: 2      # Minimum pods
  maxReplicas: 10     # Maximum pods
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70  # Target CPU %
```

---

## 🛠️ Troubleshooting

### Claude Code

**Issue:** `/plan` command not found
- **Solution:** Ensure `.claude/commands/plan.md` exists
- Check file permissions: `chmod 644 .claude/commands/plan.md`

### Vertex AI

**Issue:** Import error for `anthropic`
```python
!pip install anthropic -q
```

**Issue:** Template not found
```python
# Use absolute path
PLAN_MODE_TEMPLATE_PATH = '/home/jupyter/PLAN_MODE_TEMPLATE.md'
```

### GKE

**Issue:** Pods not starting
```bash
kubectl describe pod -l app=plan-mode-service
kubectl logs -l app=plan-mode-service --tail=50
```

**Issue:** API key not working
```bash
# Recreate secret
kubectl delete secret anthropic-api-key
kubectl create secret generic anthropic-api-key \
  --from-literal=api-key="your-new-key"
kubectl rollout restart deployment/plan-mode-service
```

**Issue:** Image pull errors
```bash
# Reconfigure Docker auth
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/plan-mode-service:latest
```

### Local Development

**Issue:** Module not found
```bash
pip install -r deployment/gke/requirements.txt
```

**Issue:** Port already in use
```bash
export PORT=8080
./run-local.sh
```

---

## 📈 Monitoring & Observability

### Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=k8s_container AND resource.labels.container_name=plan-mode-api" \
  --limit 50 \
  --format json

# Stream logs
kubectl logs -f -l app=plan-mode-service
```

### Cloud Monitoring

```bash
# Create uptime check
gcloud monitoring uptime create plan-mode-service-health \
  --resource-type=uptime-url \
  --host=$SERVICE_IP \
  --path=/health
```

### Metrics

Key metrics to monitor:
- Request latency (p50, p95, p99)
- Error rate
- Token usage
- Pod CPU/Memory
- Autoscaling events

---

## 🔐 Security Best Practices

### 1. Secret Management

**Don't:**
```bash
# Never hardcode API keys
ANTHROPIC_API_KEY="sk-ant-..."
```

**Do:**
```bash
# Use Google Secret Manager
gcloud secrets create anthropic-api-key --data-file=-
```

### 2. Network Security

```yaml
# Add network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: plan-mode-network-policy
spec:
  podSelector:
    matchLabels:
      app: plan-mode-service
  ingress:
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 8000
```

### 3. RBAC

```yaml
# Least privilege service account
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: plan-mode-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
```

---

## 💰 Cost Optimization

### GKE

- Use **preemptible nodes** for dev/test: `--preemptible`
- Enable **cluster autoscaling**: `--enable-autoscaling`
- Use **regional clusters** for HA, zonal for dev
- Consider **GKE Autopilot** for managed scaling

### Anthropic API

- Cache common plans to reduce API calls
- Use **Haiku model** for simple plans (lower cost)
- Implement rate limiting to prevent runaway costs
- Monitor token usage with Cloud Monitoring

### Storage

- Use **lifecycle policies** on Cloud Storage
- Enable **GCR image pruning**
- Clean up old deployment artifacts

---

## 🎓 Next Steps

1. **Customize Plans**: Edit `PLAN_MODE_TEMPLATE.md` for your team's style
2. **Add Monitoring**: Set up alerts for errors and latency
3. **Scale Up**: Tune autoscaling based on usage patterns
4. **Integrate**: Add plan generation to your existing workflows
5. **Extend**: Build custom endpoints for specialized planning

---

## 📚 Resources

- [Plan Mode Style Guide](./PLAN_MODE_TEMPLATE.md)
- [Deployment Documentation](./deployment/README.md)
- [Claude API Docs](https://docs.anthropic.com/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/workbench)

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting guide above
2. Review deployment logs
3. Consult documentation links
4. Open an issue in the repository

**Happy Planning! 🎯**
