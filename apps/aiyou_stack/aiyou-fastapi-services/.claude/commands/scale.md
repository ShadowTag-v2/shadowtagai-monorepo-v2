---
description: Scale Pnkln services on GKE up or down based on demand
---

You are assisting with scaling the Pnkln FastAPI services on GKE.

## Scaling Operations

### 1. Manual Scaling
Scale a specific deployment to desired replica count:
```bash
kubectl scale deployment/[service-name] --replicas=[N] -n pnkln
```

### 2. Check Current Scale
View current replica counts:
```bash
kubectl get deployments -n pnkln
kubectl get hpa -n pnkln  # Horizontal Pod Autoscalers
```

### 3. Auto-Scaling Configuration
Set up Horizontal Pod Autoscaler:
```bash
kubectl autoscale deployment/[service-name] \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n pnkln
```

## Scaling Recommendations

### API Gateway
- **Minimum replicas**: 2 (high availability)
- **Maximum replicas**: 20
- **CPU threshold**: 70%
- **Memory threshold**: 80%
- **Scale up**: During peak hours (9am-5pm)
- **Scale down**: During off-peak hours

### Authentication Service
- **Minimum replicas**: 2 (critical service)
- **Maximum replicas**: 10
- **CPU threshold**: 60%
- **Memory threshold**: 75%

### Data Processing Service
- **Minimum replicas**: 1
- **Maximum replicas**: 15
- **CPU threshold**: 80%
- **Memory threshold**: 85%
- **Queue-based scaling**: Consider scaling based on job queue depth

### Monitoring Service
- **Minimum replicas**: 1
- **Maximum replicas**: 3
- **CPU threshold**: 70%
- **Memory threshold**: 80%

## Scaling Scenarios

### Scenario 1: Traffic Spike
If experiencing high traffic:
```bash
# Scale up API gateway immediately
kubectl scale deployment/api-gateway --replicas=10 -n pnkln

# Monitor resource usage
kubectl top pods -n pnkln

# Check if auto-scaling is keeping up
kubectl get hpa -n pnkln -w
```

### Scenario 2: Cost Optimization
During low-traffic periods:
```bash
# Scale down to minimum
kubectl scale deployment/api-gateway --replicas=2 -n pnkln
kubectl scale deployment/data-processor --replicas=1 -n pnkln

# Verify services remain healthy
kubectl get pods -n pnkln
```

### Scenario 3: Maintenance Window
Before maintenance:
```bash
# Scale up for redundancy
kubectl scale deployment/api-gateway --replicas=4 -n pnkln

# Perform rolling maintenance
kubectl drain [node-name] --ignore-daemonsets
```

## Pre-Scaling Checks
- Check cluster capacity: `kubectl describe nodes`
- Verify resource quotas: `kubectl describe quota -n pnkln`
- Review current resource usage: `kubectl top nodes`
- Check pod resource requests/limits

## Post-Scaling Validation
- Verify desired replica count: `kubectl get deployments -n pnkln`
- Check pod status: `kubectl get pods -n pnkln`
- Monitor resource usage: `kubectl top pods -n pnkln`
- Test service availability
- Review auto-scaling metrics: `kubectl get hpa -n pnkln`

## Safety Guardrails
- Never scale below minimum required replicas for HA
- Monitor costs when scaling up significantly
- Set up alerts for resource saturation
- Use PodDisruptionBudgets to prevent total outages
- Test scaling procedures in staging first

After completing scaling operations, provide a summary including:
- Services scaled
- Previous and new replica counts
- Resource utilization metrics
- Auto-scaling configuration (if applicable)
- Recommendations for optimization
