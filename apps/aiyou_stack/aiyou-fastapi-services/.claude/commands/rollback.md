---
description: Rollback Pnkln services to previous stable version on GKE
---

You are assisting with rolling back the Pnkln FastAPI services deployment on GKE.

## Rollback Process

### 1. Identify Current State
- Check current deployment revision: `kubectl rollout history deployment/[service-name] -n pnkln`
- Review recent changes: `kubectl describe deployment/[service-name] -n pnkln`
- Identify the stable version to rollback to

### 2. Pre-Rollback Validation
- Verify the target revision is valid
- Check if rollback is safe (no breaking schema changes)
- Notify team of planned rollback
- Document the reason for rollback

### 3. Execute Rollback
- Rollback to previous revision: `kubectl rollout undo deployment/[service-name] -n pnkln`
- OR rollback to specific revision: `kubectl rollout undo deployment/[service-name] --to-revision=[N] -n pnkln`
- Monitor rollback progress: `kubectl rollout status deployment/[service-name] -n pnkln`

### 4. Post-Rollback Validation
- Verify pods are running: `kubectl get pods -n pnkln`
- Check service health endpoints
- Review logs for errors: `kubectl logs -f deployment/[service-name] -n pnkln`
- Run smoke tests to verify functionality

### 5. Root Cause Analysis
- Identify what caused the need for rollback
- Document issues in incident report
- Plan fixes for the next deployment
- Update deployment procedures if needed

## Rollback Scenarios

### Scenario 1: Failed Deployment
If pods are crash-looping or failing to start:
```bash
kubectl rollout undo deployment/[service-name] -n pnkln
```

### Scenario 2: Performance Degradation
If services are slow or unresponsive:
```bash
# First, check metrics
kubectl top pods -n pnkln
# Then rollback if needed
kubectl rollout undo deployment/[service-name] -n pnkln
```

### Scenario 3: Data Integrity Issues
If data corruption or loss is detected:
```bash
# IMMEDIATELY rollback
kubectl rollout undo deployment/[service-name] -n pnkln
# Restore from backup if needed
```

## Safety Measures
- Always validate health endpoints after rollback
- Keep deployment history: `kubectl rollout history` shows last 10 revisions
- Document all rollback actions
- Never rollback across breaking schema changes without migration plan

After completing the rollback, provide a summary including:
- Services rolled back
- Previous and current versions
- Rollback status
- Root cause (if known)
- Remediation plan
