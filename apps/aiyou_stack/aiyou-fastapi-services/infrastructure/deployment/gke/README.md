# GKE Deployment

**Production-ready Kubernetes manifests for PNKLN FastAPI**

## Prerequisites


1. **GCP Project Setup**:

```bash
export PROJECT_ID=your-gcp-project-id
gcloud config set project $PROJECT_ID

```


2. **GKE Cluster** (if not exists):

```bash
gcloud container clusters create pnkln-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-standard-2 \
  --enable-autoscaling \
  --min-nodes=2 \
  --max-nodes=5

```


3. **Container Registry**:

```bash

# Build and push Docker image

cd ../../fast-api
docker build -t gcr.io/$PROJECT_ID/pnkln-fastapi:latest .
docker push gcr.io/$PROJECT_ID/pnkln-fastapi:latest

```


4. **API Key Secret**:

```bash
kubectl create secret generic pnkln-api-secrets \
  --from-literal=api-key=$(openssl rand -hex 32)

```

## Deployment

```bash

# Update manifest with your PROJECT_ID

sed -i "s/PROJECT_ID/$PROJECT_ID/g" fast-api-deployment.yaml

# Apply manifests

kubectl apply -f fast-api-deployment.yaml

# Verify deployment

kubectl get pods -l app=pnkln-fastapi
kubectl get svc pnkln-fastapi-service
kubectl get hpa pnkln-fastapi-hpa

```

## Access the API

```bash

# Get external IP

export EXTERNAL_IP=$(kubectl get svc pnkln-fastapi-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Get API key

export API_KEY=$(kubectl get secret pnkln-api-secrets -o jsonpath='{.data.api-key}' | base64 -d)

# Test health endpoint

curl http://$EXTERNAL_IP/health

# Test decision endpoint

curl -X POST http://$EXTERNAL_IP/decide \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "User uploaded file with PII: names, SSNs",
    "risk_tolerance": "low",
    "require_rationale": true
  }'

```

## Monitoring

```bash

# View logs

kubectl logs -l app=pnkln-fastapi -f

# Check HPA status

kubectl describe hpa pnkln-fastapi-hpa

# Get pod metrics

kubectl top pods -l app=pnkln-fastapi

```

## Architecture

```

Internet
   ↓
GCP Load Balancer (External IP)
   ↓
Service (ClusterIP)
   ↓
Deployment (2-10 replicas via HPA)
   ↓
Pods (FastAPI container)
   ↓
Health probes (liveness/readiness)

```

## Resource Limits

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 250m | 500m |
| Memory | 512Mi | 1Gi |

**HPA Scaling**:

- Min replicas: 2

- Max replicas: 10

- CPU target: 70%

- Memory target: 80%

## Security Features


- Non-root container (UID 1000)

- Read-only root filesystem

- API key via Kubernetes Secret

- No privilege escalation

- HTTPS termination at Load Balancer (configure SSL cert separately)

## Next Steps


- [ ] Add Cloud Armor for DDoS protection

- [ ] Configure Cloud CDN for caching

- [ ] Set up Cloud Logging + Monitoring alerts

- [ ] Implement Workload Identity for GCP service access

- [ ] Add Network Policy for pod-to-pod security
