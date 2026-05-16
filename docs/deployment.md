# Deployment Guide - Pnkln Ultrathink Framework

**Target:** GKE Native (Google Cloud exclusive)
**Philosophy:** Production-grade, ruthlessly simple, obsessively detailed

## Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- GKE cluster created and configured
- Docker installed locally
- `kubectl` configured for your GKE cluster

## Deployment Phases

### Phase 1: Local Development (CURRENT)

**Status:** ✓ Complete

```bash
# 1. Clone repository
git clone <repo_url>
cd aiyou-fastapi-services

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run tests
python tests/test_orchestrator.py

# 4. Start local server
uvicorn api.main:app --reload --port 8000

# 5. Access API
open http://localhost:8000/docs
```

### Phase 2: Containerization

**Status:** Ready for implementation

#### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY pnkln/ ./pnkln/
COPY api/ ./api/
COPY data/ ./data/

# Create non-root user
RUN useradd -m -u 1000 pnkln && chown -R pnkln:pnkln /app
USER pnkln

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Build and Test

```bash
# Build
docker build -t pnkln-api:1.0.0 .

# Test locally
docker run -p 8000:8000 pnkln-api:1.0.0

# Verify
curl http://localhost:8000/health
```

### Phase 3: Google Cloud Setup

#### Configure gcloud

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Create Artifact Registry repository
gcloud artifacts repositories create pnkln-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Pnkln ultrathink framework images"

# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

#### Push Image to Artifact Registry

```bash
# Tag image
docker tag pnkln-api:1.0.0 \
  us-central1-docker.pkg.dev/YOUR_PROJECT_ID/pnkln-repo/pnkln-api:1.0.0

# Push
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/pnkln-repo/pnkln-api:1.0.0
```

### Phase 4: GKE Deployment

#### Create GKE Cluster (if not exists)

```bash
gcloud container clusters create pnkln-cluster \
    --zone=us-central1-a \
    --num-nodes=3 \
    --machine-type=e2-standard-2 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=5 \
    --enable-autorepair \
    --enable-autoupgrade

# Get credentials
gcloud container clusters get-credentials pnkln-cluster --zone=us-central1-a
```

#### Kubernetes Manifests

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pnkln-api
  labels:
    app: pnkln-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pnkln-api
  template:
    metadata:
      labels:
        app: pnkln-api
    spec:
      containers:
      - name: pnkln-api
        image: us-central1-docker.pkg.dev/YOUR_PROJECT_ID/pnkln-repo/pnkln-api:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pnkln-api-service
spec:
  type: LoadBalancer
  selector:
    app: pnkln-api
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
```

#### Deploy

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods
kubectl get services

# Get external IP
kubectl get service pnkln-api-service

# Test
curl http://EXTERNAL_IP/health
```

### Phase 5: Monitoring & Logging

#### Enable Google Cloud Monitoring

```bash
# View logs
gcloud logging read "resource.type=k8s_container AND resource.labels.cluster_name=pnkln-cluster" \
  --limit 50 \
  --format json

# Create log-based metric
gcloud logging metrics create pnkln_requests \
  --description="Pnkln API requests" \
  --log-filter='resource.type="k8s_container" AND resource.labels.cluster_name="pnkln-cluster"'
```

#### Set Up Alerts

```bash
# Create alerting policy (via Cloud Console or Terraform)
# Monitor:
# - API error rate
# - Response latency
# - Pod restarts
# - Memory usage
```

### Phase 6: CI/CD (Optional)

#### Cloud Build Configuration

**cloudbuild.yaml:**

```yaml
steps:
  # Run tests
  - name: python:3.11-slim
    entrypoint: /bin/bash
    args:
      - -c
      - |
        pip install -r requirements.txt
        python tests/test_orchestrator.py

  # Build Docker image
  - name: gcr.io/cloud-builders/docker
    args:
      - build
      - -t
      - us-central1-docker.pkg.dev/$PROJECT_ID/pnkln-repo/pnkln-api:$SHORT_SHA
      - -t
      - us-central1-docker.pkg.dev/$PROJECT_ID/pnkln-repo/pnkln-api:latest
      - .

  # Push to Artifact Registry
  - name: gcr.io/cloud-builders/docker
    args:
      - push
      - us-central1-docker.pkg.dev/$PROJECT_ID/pnkln-repo/pnkln-api:$SHORT_SHA

  # Deploy to GKE
  - name: gcr.io/cloud-builders/kubectl
    args:
      - set
      - image
      - deployment/pnkln-api
      - pnkln-api=us-central1-docker.pkg.dev/$PROJECT_ID/pnkln-repo/pnkln-api:$SHORT_SHA
    env:
      - CLOUDSDK_COMPUTE_ZONE=us-central1-a
      - CLOUDSDK_CONTAINER_CLUSTER=pnkln-cluster

options:
  logging: CLOUD_LOGGING_ONLY
```

#### Create Build Trigger

```bash
gcloud builds triggers create github \
  --repo-name=aiyou-fastapi-services \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Production Checklist

- [ ] GKE cluster created and configured
- [ ] Artifact Registry repository created
- [ ] Docker image built and pushed
- [ ] Kubernetes manifests created
- [ ] Deployment applied to cluster
- [ ] Service exposed with LoadBalancer
- [ ] External IP obtained and tested
- [ ] Monitoring and logging configured
- [ ] Alerts set up for critical metrics
- [ ] CI/CD pipeline configured (optional)
- [ ] SSL/TLS certificate configured (if using custom domain)
- [ ] API authentication implemented
- [ ] Rate limiting configured
- [ ] Backup strategy implemented for audit trail

## Cost Optimization

### GKE Cluster Sizing

**Development:**
- Nodes: 1-2
- Machine type: `e2-small`
- Cost: ~$25-50/month

**Production:**
- Nodes: 3-5 (with autoscaling)
- Machine type: `e2-standard-2`
- Cost: ~$150-250/month

### Cost Monitoring

```bash
# Set budget alerts
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Pnkln Monthly Budget" \
  --budget-amount=300USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Rollback Strategy

```bash
# View deployment history
kubectl rollout history deployment/pnkln-api

# Rollback to previous version
kubectl rollout undo deployment/pnkln-api

# Rollback to specific revision
kubectl rollout undo deployment/pnkln-api --to-revision=2
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Service not accessible

```bash
kubectl get endpoints pnkln-api-service
kubectl describe service pnkln-api-service
```

### High memory usage

```bash
kubectl top pods
kubectl top nodes
```

## Security Best Practices

1. **Secrets Management** - Use Google Secret Manager
2. **Network Policies** - Restrict pod-to-pod traffic
3. **Service Accounts** - Use minimal permissions
4. **Image Scanning** - Enable Artifact Registry vulnerability scanning
5. **HTTPS Only** - Configure SSL/TLS termination
6. **Rate Limiting** - Implement API rate limits

## Next Steps After Deployment

1. Configure custom domain and SSL
2. Set up authentication (OAuth, API keys)
3. Implement request rate limiting
4. Configure backup for audit trail data
5. Set up performance monitoring dashboard
6. Document runbooks for common operations
7. Create disaster recovery plan

---

**Philosophy:** Deploy with confidence, monitor obsessively, iterate ruthlessly.

**Status:** Phase 1 Complete ✓
**Next:** Containerization (Phase 2)
