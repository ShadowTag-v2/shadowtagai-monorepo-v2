---
description: Deploy Pnkln services to GKE with comprehensive validation
---

You are assisting with deploying the Pnkln FastAPI services to Google Kubernetes Engine (GKE).

## Deployment Process

Follow these steps to deploy to GKE:

### 1. Pre-Deployment Validation
- Verify all required environment variables are set
- Check GKE cluster connectivity: `gcloud container clusters get-credentials pnkln-cluster --region=us-central1`
- Validate Kubernetes manifests: `kubectl apply --dry-run=client -f k8s/`
- Run linting and security checks
- Verify Docker images are built and pushed to registry

### 2. Build and Push Images
- Build Docker images for all services
- Tag images with version and latest: `docker build -t gcr.io/pnkln-project/[service]:[version] .`
- Push to Google Container Registry: `docker push gcr.io/pnkln-project/[service]:[version]`
- Verify image push: `gcloud container images list --repository=gcr.io/pnkln-project`

### 3. Deploy to GKE
- Apply Kubernetes configurations: `kubectl apply -f k8s/`
- Update deployments with new image versions
- Monitor rollout status: `kubectl rollout status deployment/[service-name]`
- Verify pods are running: `kubectl get pods -n pnkln`

### 4. Post-Deployment Validation
- Check service health endpoints
- Verify ingress/load balancer configuration
- Run smoke tests against deployed services
- Monitor logs for errors: `kubectl logs -f deployment/[service-name] -n pnkln`

### 5. Rollback Plan
- If deployment fails, rollback: `kubectl rollout undo deployment/[service-name]`
- Document any issues encountered
- Alert team of deployment status

## Services to Deploy
- **API Gateway**: Main FastAPI service
- **Authentication Service**: User auth and JWT management
- **Data Processing Service**: Background job processing
- **Monitoring Service**: Metrics and health checks

## Environment-Specific Configurations
- **Development**: `pnkln-dev` namespace
- **Staging**: `pnkln-staging` namespace
- **Production**: `pnkln-prod` namespace

## Safety Checks
- Never deploy directly to production without staging validation
- Always create a backup before deployment
- Verify rollback procedures are in place
- Ensure monitoring and alerting are active

After completing the deployment, provide a summary including:
- Services deployed
- Image versions
- Deployment status
- Any warnings or errors encountered
- Next steps or recommendations
