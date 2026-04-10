# ShadowTag-v2 Governance System - Quickstart Guide

**Get your agent-based governance running in 15 minutes.**

## Prerequisites

- Python 3.11+
- Google Cloud Project with Vertex AI enabled
- kubectl configured for your GKE cluster (for production)
- Docker (optional, for containerized deployment)

## Local Development Setup

### 1. Clone and Install

```bash
# Clone repository
cd ShadowTag-v2-fastapi-services

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
# OR: pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Minimum required:
# - GOOGLE_CLOUD_PROJECT
# - GOOGLE_API_KEY (for Gemini)
```

### 3. Run Locally

```bash
# Start the governance gateway
make run
# OR: python -m uvicorn src.gateway.main:app --reload --host 0.0.0.0 --port 8000

# Server will start at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Make a governance decision
curl -X POST http://localhost:8000/governance/decide \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_test_001",
    "user_id": "user_123",
    "action": "approve_expense",
    "resource": {
      "type": "expense",
      "id": "exp_001",
      "amount": 5000.00
    },
    "context": {
      "user_role": "engineer"
    },
    "financial_value": 5000.00,
    "source_system": "test-api"
  }'

# Get routing explanation (dry run)
curl -X POST http://localhost:8000/governance/decide/explain \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_test_002",
    "user_id": "user_123",
    "action": "delete_production_data",
    "resource": {"type": "database"},
    "financial_value": 50000.00,
    "source_system": "test-api"
  }'
```

## GKE Production Deployment

### 1. Build and Push Docker Image

```bash
# Set your GCP project
export PROJECT_ID=your-gcp-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  container.googleapis.com \
  aiplatform.googleapis.com \
  containerregistry.googleapis.com

# Build and push to GCR
make docker-build
make docker-push
```

### 2. Create GKE Cluster (if needed)

```bash
# Create Autopilot cluster (recommended)
gcloud container clusters create-auto governance-cluster \
  --region=us-central1 \
  --project=$PROJECT_ID

# Get credentials
gcloud container clusters get-credentials governance-cluster \
  --region=us-central1 \
  --project=$PROJECT_ID
```

### 3. Deploy to GKE

```bash
# Deploy namespaces
kubectl apply -f k8s/namespaces/governance-namespaces.yaml

# Deploy OPA
kubectl apply -f k8s/deployments/opa.yaml

# Deploy Governance Gateway
# First update PROJECT_ID in k8s/deployments/governance-gateway.yaml
kubectl apply -f k8s/deployments/governance-gateway.yaml

# Check deployment status
kubectl get pods -n governance
kubectl logs -f -n governance -l app=governance-gateway
```

### 4. Expose Service (optional)

```bash
# Create LoadBalancer service (for external access)
kubectl expose deployment governance-gateway \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8000 \
  -n governance

# Get external IP
kubectl get svc governance-gateway -n governance
```

## Architecture Verification

### Test Fast Path (OPA)

High-risk actions should route to OPA (<10ms):

```bash
curl -X POST http://localhost:8000/governance/decide/explain \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_fast_001",
    "user_id": "user_123",
    "action": "delete_production_data",
    "resource": {"type": "database"},
    "source_system": "test"
  }'

# Expected: routing.path = "fast_path"
```

### Test Slow Path (Agent)

Medium-risk actions should route to Agent (2-5s):

```bash
curl -X POST http://localhost:8000/governance/decide/explain \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_slow_001",
    "user_id": "user_123",
    "action": "approve_expense",
    "resource": {"type": "expense", "amount": 5000},
    "financial_value": 5000.00,
    "source_system": "test"
  }'

# Expected: routing.path = "slow_path"
```

## Performance Targets

✅ **Fast Path (OPA)**: <10ms latency
✅ **Slow Path (Agent)**: 1-2s simple, 2-5s complex
✅ **Cost per decision**: $0.0003 - $0.0012
✅ **Availability**: 99.9% with circuit breakers

## Monitoring

### Check Metrics

```bash
# Prometheus-compatible metrics
curl http://localhost:8000/metrics
```

### View Logs

```bash
# Local
tail -f logs/governance.log

# GKE
kubectl logs -f -n governance -l app=governance-gateway --tail=100
```

### Health Status

```bash
# Detailed health check
curl http://localhost:8000/health

# Response includes OPA, Agent Engine, Vector DB status
```

## Common Issues

### Issue: "OPA client unavailable"

**Solution**: Ensure OPA is running:

```bash
# Local
docker run -d -p 8181:8181 openpolicyagent/opa:latest run --server

# GKE
kubectl get pods -n governance | grep opa
```

### Issue: "Agent evaluation failed"

**Solution**: Check Vertex AI credentials:

```bash
# Test Vertex AI access
gcloud auth application-default login

# Verify project ID
echo $GOOGLE_CLOUD_PROJECT
```

### Issue: "High latency (>5s)"

**Solution**: Check network connectivity to Vertex AI:

```bash
# Test API latency
time curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/us-central1/publishers/google/models/gemini-2.5-flash:streamGenerateContent" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)"
```

## Next Steps

1. **Configure Policies**: Add policy documents to `policies/` directory
2. **Enable RAG**: Set up Vertex AI Vector Search for policy retrieval
3. **Add Observability**: Configure AgentOps and Cloud Trace
4. **Shadow Mode**: Deploy shadow mode for validation
5. **Production Migration**: Follow 4-phase rollout plan

## Resources

- [Architecture Documentation](./architecture.md)
- [API Reference](./api.md)
- [ATP 5-19 Risk Framework](./atp-5-19.md)
- [Deployment Runbooks](./runbooks/)
- [Main README](../README.md)

## Support

For issues, questions, or contributions:

- GitHub Issues: [ehanc69/ShadowTag-v2-fastapi-services](https://github.com/ehanc69/ShadowTag-v2-fastapi-services)
- Documentation: Full docs in `/docs` directory

---

**Status**: 🚀 Ready for local development
**Production Ready**: Phase 1 (Shadow Mode POC)
**Last Updated**: 2025-11-17
