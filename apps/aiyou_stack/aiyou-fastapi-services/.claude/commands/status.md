---
description: Check comprehensive status of Pnkln services on GKE
---

You are assisting with checking the status of Pnkln FastAPI services deployed on GKE.

## Status Check Procedures

### 1. Quick Status Overview
Get a quick snapshot of all services:
```bash
# Check all deployments
kubectl get deployments -n pnkln

# Check all pods
kubectl get pods -n pnkln

# Check all services
kubectl get services -n pnkln

# Check ingress
kubectl get ingress -n pnkln
```

### 2. Detailed Pod Status
For in-depth pod analysis:
```bash
# Detailed pod information
kubectl describe pods -n pnkln

# Pod resource usage
kubectl top pods -n pnkln

# Pod events
kubectl get events -n pnkln --sort-by='.lastTimestamp'
```

### 3. Service Health Checks
Verify each service's health:
```bash
# Check service endpoints
kubectl get endpoints -n pnkln

# Port-forward to test locally
kubectl port-forward -n pnkln svc/[service-name] 8080:80

# Check service logs
kubectl logs -f deployment/[service-name] -n pnkln --tail=100
```

### 4. Cluster Health
Check overall cluster status:
```bash
# Node status
kubectl get nodes

# Node resource usage
kubectl top nodes

# Cluster info
kubectl cluster-info

# Check for node issues
kubectl describe nodes | grep -i "condition\|pressure"
```

## Service-Specific Checks

### API Gateway
- **Endpoints**: Check `/health`, `/ready`, `/metrics`
- **Response time**: Should be < 200ms
- **Error rate**: Should be < 1%
- **Availability**: Should be 99.9%+

### Authentication Service
- **Token validation**: Test JWT generation/validation
- **Database connectivity**: Verify DB connections
- **Redis cache**: Check cache hit rate
- **Session management**: Validate session store

### Data Processing Service
- **Queue depth**: Monitor job queue size
- **Processing rate**: Check jobs/second
- **Failed jobs**: Review error logs
- **Worker health**: Verify worker processes

### Monitoring Service
- **Metrics collection**: Verify Prometheus scraping
- **Alerting**: Check AlertManager status
- **Dashboards**: Validate Grafana connectivity
- **Log aggregation**: Check log pipeline

## Status Indicators

### Healthy Service
- ✅ All pods in `Running` state
- ✅ All containers ready (e.g., `2/2`)
- ✅ Health endpoints returning 200
- ✅ No recent restart events
- ✅ Resource usage within limits

### Degraded Service
- ⚠️ Some pods in `Running` but restarts detected
- ⚠️ High resource usage (>80%)
- ⚠️ Slow response times
- ⚠️ Intermittent errors in logs

### Critical Service
- ❌ Pods in `CrashLoopBackOff`
- ❌ Pods in `Error` or `ImagePullBackOff`
- ❌ Health endpoints failing
- ❌ No pods available
- ❌ Service unreachable

## Automated Status Report

Generate a comprehensive status report including:

1. **Service Overview**
   - Deployment status (desired vs. current replicas)
   - Pod states
   - Service availability

2. **Resource Utilization**
   - CPU usage per service
   - Memory usage per service
   - Node capacity

3. **Recent Events**
   - Deployment events (last 24h)
   - Pod events (last 24h)
   - Warnings or errors

4. **Performance Metrics**
   - Request rates
   - Response times
   - Error rates
   - Throughput

5. **Health Checks**
   - Liveness probe status
   - Readiness probe status
   - Startup probe status

6. **Alerts**
   - Active alerts
   - Recently resolved alerts
   - Alert trends

## Troubleshooting Commands

If issues are detected:

```bash
# Check pod logs
kubectl logs -f [pod-name] -n pnkln

# Get previous logs (after crash)
kubectl logs [pod-name] -n pnkln --previous

# Execute commands in pod
kubectl exec -it [pod-name] -n pnkln -- /bin/bash

# Check resource constraints
kubectl describe pod [pod-name] -n pnkln | grep -i limit

# View deployment history
kubectl rollout history deployment/[service-name] -n pnkln
```

After completing status checks, provide a summary including:
- Overall system health (Healthy/Degraded/Critical)
- Services status breakdown
- Resource utilization summary
- Any issues or anomalies detected
- Recommended actions (if any)
