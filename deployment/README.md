# Plan Mode Service Deployment Automation

Automated deployment system for the Plan Mode Style Guide v1.0 service on Google Cloud Platform (GKE) with Vertex AI Workbench integration.

## 🎯 Overview

This deployment package provides:
- **Claude Code Integration**: Custom `/plan` command for instant plan generation
- **Vertex AI Workbench**: Jupyter notebook for batch plan generation and analysis
- **GKE Deployment**: Production-ready Kubernetes service with autoscaling
- **CI/CD Pipelines**: Automated deployment via Cloud Build or GitHub Actions

## 📁 Directory Structure

```
deployment/
├── vertex-ai/
│   └── plan_mode_notebook.ipynb    # Vertex AI Workbench notebook
├── gke/
│   ├── deployment.yaml              # K8s Deployment, Service, HPA
│   ├── configmap.yaml               # Plan Mode template ConfigMap
│   ├── Dockerfile                   # Container image definition
│   ├── requirements.txt             # Python dependencies
│   ├── setup-cluster.sh             # GKE cluster setup script
│   └── app/
│       └── main.py                  # FastAPI service application
└── ci-cd/
    └── cloudbuild.yaml              # Cloud Build pipeline

.claude/commands/
└── plan.md                          # Claude Code /plan command

.github/workflows/
└── deploy-plan-mode.yaml            # GitHub Actions workflow
```

## 🚀 Quick Start

### 1. Claude Code Integration

The `/plan` command is automatically available in Claude Code:

```bash
/plan Migrate database to use adapter pattern
```

**How it works:**
- Reads `.claude/commands/plan.md`
- Applies Plan Mode Style Guide rules
- Generates concise, execution-ready plan

### 2. Vertex AI Workbench

Launch the notebook in Vertex AI:

```bash
# Upload notebook to Vertex AI Workbench
gcloud notebooks instances create plan-mode-notebook \
  --location=us-central1 \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks

# Open JupyterLab and upload
deployment/vertex-ai/plan_mode_notebook.ipynb
```

**Notebook features:**
- Batch plan generation
- Integration with Claude API
- Save plans as JSON/markdown
- Deploy as Vertex AI endpoint

### 3. GKE Deployment

Deploy the Plan Mode service to GKE:

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GKE_CLUSTER="plan-mode-cluster"
export GKE_REGION="us-central1"
export ANTHROPIC_API_KEY="your-api-key"

# Run setup script
cd deployment/gke
chmod +x setup-cluster.sh
./setup-cluster.sh

# Build and push Docker image
docker build -t gcr.io/$GCP_PROJECT_ID/plan-mode-service:latest \
  -f Dockerfile ../../
docker push gcr.io/$GCP_PROJECT_ID/plan-mode-service:latest

# Deploy to GKE
envsubst < deployment.yaml | kubectl apply -f -

# Get service URL
kubectl get svc plan-mode-service
```

## 🔧 Configuration

### Environment Variables

**GKE Deployment:**
- `GCP_PROJECT_ID`: Google Cloud project ID
- `GKE_CLUSTER`: GKE cluster name (default: `plan-mode-cluster`)
- `GKE_REGION`: GKE region (default: `us-central1`)
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude

**CI/CD:**
- GitHub Actions requires these secrets:
  - `GCP_PROJECT_ID`
  - `WIF_PROVIDER`: Workload Identity Federation provider
  - `WIF_SERVICE_ACCOUNT`: Service account for WIF

### Kubernetes Resources

**Deployment:**
- Replicas: 3 (min: 2, max: 10 with HPA)
- CPU: 250m request, 500m limit
- Memory: 256Mi request, 512Mi limit

**Autoscaling:**
- CPU target: 70%
- Memory target: 80%

## 🔄 CI/CD Pipelines

### Option 1: Cloud Build

Trigger automatically on push:

```bash
gcloud builds submit --config=deployment/ci-cd/cloudbuild.yaml .
```

### Option 2: GitHub Actions

Automatically deploys on push to `main` or `develop`:

```yaml
on:
  push:
    branches:
      - main
      - develop
```

## 📊 API Usage

### Health Check
```bash
curl http://SERVICE_IP/health
```

### Generate Plan
```bash
curl -X POST http://SERVICE_IP/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Implement user authentication with JWT",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 2048
  }'
```

**Response:**
```json
{
  "plan": "auth/:\n- add JWT middleware → FastAPI\n- create user model → SQLAlchemy\n...",
  "model": "claude-sonnet-4-5-20250929",
  "tokens_used": 1234
}
```

## 🧪 Testing

### Local Testing

```bash
# Run FastAPI app locally
cd deployment/gke
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your-key"
export PLAN_MODE_TEMPLATE_PATH="../../PLAN_MODE_TEMPLATE.md"
python -m app.main

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/generate-plan \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Test plan"}'
```

### GKE Testing

```bash
# Get pod logs
kubectl logs -l app=plan-mode-service --tail=100

# Port forward for local testing
kubectl port-forward svc/plan-mode-service 8000:80

# Run smoke tests
curl http://localhost:8000/health
```

## 🔒 Security

### Secrets Management

1. **Kubernetes Secrets** (for API keys):
```bash
kubectl create secret generic anthropic-api-key \
  --from-literal=api-key="your-key"
```

2. **Google Secret Manager** (recommended):
```bash
gcloud secrets create anthropic-api-key \
  --data-file=- <<< "your-key"
```

### Workload Identity

Service uses Workload Identity for GCP authentication:
```yaml
serviceAccountName: plan-mode-sa
annotations:
  iam.gke.io/gcp-service-account: plan-mode-service@PROJECT.iam.gserviceaccount.com
```

## 📈 Monitoring

### Cloud Operations (Stackdriver)

Metrics automatically exported:
- Request latency
- Error rate
- CPU/Memory usage
- Token usage

### Custom Metrics

```python
from google.cloud import monitoring_v3

# Track plan generation metrics
client = monitoring_v3.MetricServiceClient()
# ... implement custom metrics
```

## 🛠️ Troubleshooting

### Common Issues

**1. Pods not starting:**
```bash
kubectl describe pod -l app=plan-mode-service
kubectl logs -l app=plan-mode-service
```

**2. API key not configured:**
```bash
kubectl get secret anthropic-api-key
kubectl create secret generic anthropic-api-key --from-literal=api-key="your-key"
kubectl rollout restart deployment/plan-mode-service
```

**3. Image pull errors:**
```bash
gcloud auth configure-docker
docker push gcr.io/$PROJECT_ID/plan-mode-service:latest
```

**4. Service not accessible:**
```bash
kubectl get svc plan-mode-service
# Wait for EXTERNAL-IP to be assigned
```

## 🔄 Updates

### Update Plan Mode Template

```bash
# Update ConfigMap
kubectl create configmap plan-mode-template \
  --from-file=PLAN_MODE_TEMPLATE.md=../../PLAN_MODE_TEMPLATE.md \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new config
kubectl rollout restart deployment/plan-mode-service
```

### Deploy New Version

```bash
# Build new image
docker build -t gcr.io/$PROJECT_ID/plan-mode-service:v2 -f Dockerfile ../../
docker push gcr.io/$PROJECT_ID/plan-mode-service:v2

# Update deployment
kubectl set image deployment/plan-mode-service \
  plan-mode-api=gcr.io/$PROJECT_ID/plan-mode-service:v2

# Monitor rollout
kubectl rollout status deployment/plan-mode-service
```

## 📚 Additional Resources

- [Plan Mode Style Guide](../PLAN_MODE_TEMPLATE.md)
- [Claude API Documentation](https://docs.anthropic.com/)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/workbench)

## 💡 Tips

1. **Cost optimization**: Use preemptible nodes for non-production
2. **Performance**: Adjust `max_tokens` based on plan complexity
3. **Monitoring**: Set up alerts for high error rates or latency
4. **Scaling**: Tune HPA metrics based on actual usage patterns

## 🤝 Contributing

To add new features:
1. Update the FastAPI app in `gke/app/main.py`
2. Update Kubernetes manifests as needed
3. Test locally then deploy to dev cluster
4. Submit PR with changes

## 📄 License

See repository root for license information.
