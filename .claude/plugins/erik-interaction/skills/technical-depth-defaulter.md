# Technical Depth Defaulter

**Auto-activate:** Always (assume maximum technical sophistication)

## Default Technical Level

```python
ASSUME_EXPERTISE = {
    "kubernetes": "expert",
    "llms": "expert",
    "python": "expert",
    "go": "expert",
    "cloud_architecture": "expert",
    "cost_optimization": "expert",
    "devops": "expert",
    "security": "expert"
}
```

## Never Explain These Concepts

- What Kubernetes is
- What containers are
- What LLMs are / how they work
- What APIs are
- What CI/CD means
- What JSON/YAML is
- What HTTP status codes are
- What databases are
- What cache invalidation is
- What microservices are
- What observability is
- Basic Python/Go syntax
- Basic Git commands
- Cloud computing concepts
- What tokens are (LLM context)

## Always Include These Details

```python
REQUIRED_DETAILS = [
    "Exact version numbers",
    "Specific memory/CPU requirements",
    "Actual latency measurements (ms)",
    "Real cost calculations ($)",
    "Concrete error handling code",
    "Kill switches and circuit breakers",
    "Resource limits and requests",
    "Actual namespace names",
    "Real API endpoints",
    "Specific port numbers",
    "Actual environment variables",
    "Complete command-line invocations"
]
```

## Code Specificity Level

### ❌ WRONG (Too Generic)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <YOUR_APP_NAME>
spec:
  replicas: <REPLICA_COUNT>
```

### ✅ CORRECT (Specific)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: judge-6-hybrid
  namespace: ShadowTag-v2jr-governance
  labels:
    app: judge-6
    version: v0.53
    tier: validation
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: judge-6
  template:
    metadata:
      labels:
        app: judge-6
        version: v0.53
    spec:
      serviceAccountName: judge-6-sa
      containers:
      - name: gemini-layer
        image: gcr.io/pnkln-core/judge-6-gemini:v0.53.2
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        - containerPort: 9090
          name: metrics
          protocol: TCP
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        env:
        - name: MODEL_NAME
          value: "gemini-1.5-flash-002"
        - name: CONTEXT_WINDOW
          value: "2000000"
        - name: P99_TARGET_MS
          value: "90"
        - name: KILL_SWITCH_ENABLED
          value: "true"
        - name: KILL_SWITCH_THRESHOLD_SIGMA
          value: "3"
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-api-key
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
```

## Default Code Patterns

### Error Handling

Always include:

```python
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    passed: bool
    confidence: float
    latency_ms: int
    error: Optional[str] = None

def validate_with_judge(input_text: str) -> ValidationResult:
    start_time = time.perf_counter()

    try:
        response = gemini_client.generate(
            model="gemini-1.5-flash-002",
            prompt=input_text,
            max_tokens=1024,
            timeout_ms=5000
        )

        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # Kill switch: p99 latency violation
        if latency_ms > P99_TARGET_MS:
            logger.error(f"Latency {latency_ms}ms exceeds p99 target {P99_TARGET_MS}ms")
            if should_trigger_kill_switch(latency_ms):
                raise KillSwitchActivated(f"Latency kill switch at {latency_ms}ms")

        return ValidationResult(
            passed=True,
            confidence=response.confidence,
            latency_ms=latency_ms
        )

    except Exception as e:
        logger.exception(f"Validation failed: {e}")
        return ValidationResult(
            passed=False,
            confidence=0.0,
            latency_ms=int((time.perf_counter() - start_time) * 1000),
            error=str(e)
        )
```

### Infrastructure as Code

Always include:

- Resource requests AND limits
- Health checks (liveness + readiness)
- Metrics endpoints
- Kill switches / circuit breakers
- Specific secrets management
- Actual service names
- Real namespace names
- Version labels

## Assume Infrastructure Context

Default to:
- GKE cluster: `pnkln-core-us-central1`
- Region: `us-central1-a`
- Node type: `n2-standard-8` (8 vCPU, 32GB RAM)
- Registry: `gcr.io/pnkln-core`
- Namespaces: `ShadowTag-v2jr-core`, `ShadowTag-v2jr-governance`, `ShadowTag-v2jr-data`
- Service mesh: None (direct service communication)
- Monitoring: Cloud Monitoring + custom metrics on :9090/metrics
