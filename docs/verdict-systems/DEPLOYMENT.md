# Verdict Systems - Deployment Guide

## Google Cloud Platform Deployment

### Prerequisites

- Google Cloud account
- GKE cluster (or create new)
- PostgreSQL database (Cloud SQL)
- Redis instance (Memorystore)
- Domain name (optional)

---

## Quick Deploy to GKE

### 1. Build and Push Container

```bash
# Build Docker image
docker build -t gcr.io/[PROJECT_ID]/verdict-systems:v1.0.0 -f Dockerfile.verdict .

# Push to Google Container Registry
docker push gcr.io/[PROJECT_ID]/verdict-systems:v1.0.0
```

### 2. Configure Secrets

```bash
# Create namespace
kubectl create namespace verdict-systems

# Create database secret
kubectl create secret generic verdict-db \
  --from-literal=postgres_user=verdict \
  --from-literal=postgres_password=YOUR_PASSWORD \
  --from-literal=postgres_host=10.0.0.1 \
  --from-literal=postgres_db=verdict_systems \
  --namespace verdict-systems

# Create Redis secret
kubectl create secret generic verdict-redis \
  --from-literal=redis_host=10.0.0.2 \
  --from-literal=redis_port=6379 \
  --namespace verdict-systems
```

### 3. Deploy to GKE

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/verdict-systems/

# Check deployment status
kubectl get pods -n verdict-systems
kubectl logs -f deployment/verdict-systems -n verdict-systems
```

---

## Local Development

### Using Docker Compose

```bash
# Start all services (API, PostgreSQL, Redis)
docker-compose -f docker-compose.verdict.yml up

# Access API at http://localhost:8001/docs
```

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_USER=verdict
export POSTGRES_PASSWORD=password
export POSTGRES_DB=verdict_systems
export REDIS_HOST=localhost

# Run database migrations
alembic upgrade head

# Start API
uvicorn src.verdict_systems.api.main:app --reload --port 8001
```

---

## Database Migrations

### Create Migration

```bash
alembic revision --autogenerate -m "Add new table"
```

### Apply Migration

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

---

## Monitoring & Alerting

### Health Checks

```bash
# API health
curl http://localhost:8001/health

# Database connectivity
psql -h $POSTGRES_HOST -U verdict -d verdict_systems -c "SELECT 1"

# Redis connectivity
redis-cli -h $REDIS_HOST ping
```

### Prometheus Metrics

Metrics exposed at `/metrics`:

- `verdict_tasks_total{status,vertical}`: Total tasks
- `verdict_lockouts_active`: Active lockouts
- `verdict_urgency_critical`: Critical urgency tasks
- `verdict_api_requests_total`: API requests

### Grafana Dashboards

Import dashboards from `dashboards/verdict-systems/`:

- Task Urgency Distribution
- Lockout Events
- User Activity
- AI Tutor Usage

---

## Scaling

### Horizontal Scaling

```bash
# Scale API replicas
kubectl scale deployment verdict-systems --replicas=5 -n verdict-systems
```

### Vertical Scaling

Edit `k8s/verdict-systems/deployment.yaml`:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi
```

---

## Security

### TLS/SSL

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply certificate issuer
kubectl apply -f k8s/verdict-systems/certificate.yaml
```

### Network Policies

```bash
kubectl apply -f k8s/verdict-systems/network-policy.yaml
```

---

## Backup & Recovery

### Database Backup

```bash
# Automated daily backups (Cloud SQL)
gcloud sql backups create --instance=verdict-db

# Manual backup
pg_dump -h $POSTGRES_HOST -U verdict verdict_systems > backup.sql
```

### Restore

```bash
psql -h $POSTGRES_HOST -U verdict verdict_systems < backup.sql
```

---

## Troubleshooting

### Common Issues

**API won't start:**

```bash
# Check logs
kubectl logs deployment/verdict-systems -n verdict-systems

# Check database connectivity
kubectl exec -it deployment/verdict-systems -n verdict-systems -- \
  psql -h $POSTGRES_HOST -U verdict -d verdict_systems -c "SELECT 1"
```

**High memory usage:**

```bash
# Check memory usage
kubectl top pods -n verdict-systems

# Restart pods
kubectl rollout restart deployment/verdict-systems -n verdict-systems
```

---

## Cost Optimization

### GKE Autopilot

Use GKE Autopilot for automatic resource optimization:

```bash
gcloud container clusters create-auto verdict-cluster \
  --region us-central1
```

### Cloud SQL

- Use shared-core instances for dev/test
- Enable automatic storage increase
- Schedule backups during off-peak hours

### Redis

- Use basic tier for dev/test
- Enable persistence only if needed

---

## Support

- **Deployment Issues**: ops@verdict.systems
- **Documentation**: https://docs.verdict.systems/deployment
- **Status**: https://status.verdict.systems
