---
description: View and analyze logs from Pnkln services on GKE
---

You are assisting with viewing and analyzing logs from Pnkln FastAPI services deployed on GKE.

## Log Viewing Commands

### 1. Real-Time Logs
Stream logs in real-time:
```bash
# Follow logs from a specific deployment
kubectl logs -f deployment/[service-name] -n pnkln

# Follow logs from all pods with a label
kubectl logs -f -l app=[service-name] -n pnkln

# Follow logs from multiple containers
kubectl logs -f [pod-name] -c [container-name] -n pnkln
```

### 2. Historical Logs
View past logs:
```bash
# Last 100 lines
kubectl logs deployment/[service-name] -n pnkln --tail=100

# Logs since timestamp
kubectl logs deployment/[service-name] -n pnkln --since=1h

# Logs since specific time
kubectl logs deployment/[service-name] -n pnkln --since-time=2025-11-08T10:00:00Z

# Previous container logs (after restart)
kubectl logs [pod-name] -n pnkln --previous
```

### 3. Advanced Log Filtering
Filter logs using grep and other tools:
```bash
# Search for errors
kubectl logs deployment/[service-name] -n pnkln | grep -i error

# Search for specific patterns
kubectl logs deployment/[service-name] -n pnkln | grep -E "ERROR|CRITICAL|FATAL"

# Count error occurrences
kubectl logs deployment/[service-name] -n pnkln | grep -i error | wc -l

# Extract timestamps
kubectl logs deployment/[service-name] -n pnkln --timestamps
```

## Service-Specific Log Analysis

### API Gateway Logs
Key patterns to monitor:
- **Request logs**: HTTP method, path, status code, response time
- **Error logs**: 4xx/5xx errors, stack traces
- **Performance logs**: Slow queries (>1s)
- **Security logs**: Authentication failures, suspicious requests

Example queries:
```bash
# Find slow requests
kubectl logs deployment/api-gateway -n pnkln | grep "response_time" | awk '$NF > 1000'

# Count errors by status code
kubectl logs deployment/api-gateway -n pnkln | grep "status_code" | sort | uniq -c

# Find authentication failures
kubectl logs deployment/api-gateway -n pnkln | grep -i "auth.*fail"
```

### Authentication Service Logs
Key patterns to monitor:
- **Login attempts**: Successful/failed logins
- **Token operations**: JWT creation, validation, expiration
- **Session management**: Session creation, expiration
- **Security events**: Brute force attempts, unusual patterns

Example queries:
```bash
# Failed login attempts
kubectl logs deployment/auth-service -n pnkln | grep "login_failed"

# Token validation errors
kubectl logs deployment/auth-service -n pnkln | grep "token.*invalid"

# Concurrent sessions
kubectl logs deployment/auth-service -n pnkln | grep "session_created" | cut -d' ' -f1 | sort | uniq -c
```

### Data Processing Service Logs
Key patterns to monitor:
- **Job execution**: Start, progress, completion
- **Failures**: Failed jobs, retry attempts
- **Queue metrics**: Queue depth, processing rate
- **Resource usage**: Memory, CPU during processing

Example queries:
```bash
# Failed jobs
kubectl logs deployment/data-processor -n pnkln | grep "job_failed"

# Job execution time
kubectl logs deployment/data-processor -n pnkln | grep "execution_time"

# Queue depth trends
kubectl logs deployment/data-processor -n pnkln | grep "queue_depth"
```

### Monitoring Service Logs
Key patterns to monitor:
- **Metrics collection**: Scrape success/failure
- **Alert triggers**: Alert creation, resolution
- **System health**: Component status
- **Performance**: Query execution time

## Log Analysis Workflows

### Workflow 1: Investigate Error Spike
```bash
# 1. Check error count in last hour
kubectl logs deployment/[service] -n pnkln --since=1h | grep -i error | wc -l

# 2. Get error details
kubectl logs deployment/[service] -n pnkln --since=1h | grep -i error

# 3. Group by error type
kubectl logs deployment/[service] -n pnkln --since=1h | grep -i error | sort | uniq -c | sort -rn

# 4. Check if errors correlate with deployment
kubectl rollout history deployment/[service] -n pnkln
```

### Workflow 2: Performance Investigation
```bash
# 1. Find slow requests
kubectl logs deployment/api-gateway -n pnkln --since=30m | grep "response_time" | awk '$NF > 1000'

# 2. Identify endpoints
kubectl logs deployment/api-gateway -n pnkln --since=30m | grep "slow" | grep -oP '(?<=path=")[^"]*' | sort | uniq -c

# 3. Check resource usage during slow period
kubectl top pods -n pnkln

# 4. Review recent changes
kubectl get events -n pnkln --sort-by='.lastTimestamp' | head -20
```

### Workflow 3: Security Audit
```bash
# 1. Failed authentication attempts
kubectl logs deployment/auth-service -n pnkln --since=24h | grep -i "auth.*fail"

# 2. Unusual access patterns
kubectl logs deployment/api-gateway -n pnkln --since=24h | grep -E "40[13]|429"

# 3. IP-based analysis
kubectl logs deployment/api-gateway -n pnkln --since=24h | grep -oP 'ip=\K[0-9.]+' | sort | uniq -c | sort -rn

# 4. Check for injection attempts
kubectl logs deployment/api-gateway -n pnkln --since=24h | grep -iE "sql|script|injection"
```

## Log Aggregation (Cloud Logging)

### Using Google Cloud Logging
```bash
# Query logs using gcloud
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=pnkln" --limit 50 --format json

# Filter by severity
gcloud logging read "resource.type=k8s_container AND severity>=ERROR AND resource.labels.namespace_name=pnkln" --limit 50

# Export logs to BigQuery for analysis
gcloud logging sinks create pnkln-logs bigquery.googleapis.com/projects/[PROJECT]/datasets/[DATASET] --log-filter='resource.type=k8s_container AND resource.labels.namespace_name=pnkln'
```

## Best Practices

1. **Structured Logging**: Use JSON format for easier parsing
2. **Log Levels**: Use appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. **Correlation IDs**: Include request IDs for tracing across services
4. **Sensitive Data**: Never log passwords, tokens, or PII
5. **Log Rotation**: Ensure logs are rotated to prevent disk issues
6. **Retention**: Configure appropriate retention periods (e.g., 30 days)
7. **Centralization**: Use centralized logging for multi-service analysis

## Troubleshooting with Logs

Common issues and log investigation approaches:

### Issue: Service Unavailable
```bash
kubectl logs deployment/[service] -n pnkln --tail=100 | grep -iE "error|exception|fatal"
```

### Issue: High Latency
```bash
kubectl logs deployment/[service] -n pnkln | grep "response_time" | awk '{sum+=$NF; count++} END {print sum/count}'
```

### Issue: Memory Leak
```bash
kubectl logs deployment/[service] -n pnkln | grep -i "memory\|oom"
kubectl top pods -n pnkln --sort-by=memory
```

### Issue: Database Connection Issues
```bash
kubectl logs deployment/[service] -n pnkln | grep -iE "database|connection|pool"
```

After reviewing logs, provide a summary including:
- Log analysis period
- Total log entries reviewed
- Key findings (errors, warnings, patterns)
- Anomalies or suspicious activity
- Recommended actions
- Follow-up investigations needed
