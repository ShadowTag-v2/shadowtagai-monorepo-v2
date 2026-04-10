# SKILL: Technical Depth Defaulter

## ALWAYS ASSUME MAXIMUM TECHNICAL DEPTH

### DEFAULT INCLUSIONS:
- Actual code, not pseudocode
- Real commands, not descriptions
- Specific version numbers
- Memory/CPU requirements
- Latency measurements
- Cost calculations
- Error handling
- Kill switches

### NEVER EXPLAIN:
- What Kubernetes is
- What LLMs are
- Basic Python/Go concepts
- What CI/CD means
- Cloud computing basics
- What JSON/YAML is

### ALWAYS INCLUDE:
```yaml
# Deployment example - always this specific:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: judge-6-hybrid
  namespace: ShadowTag-v2jr-governance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: judge-6
  template:
    spec:
      containers:
      - name: gemini-layer
        image: gcr.io/pnkln-core/judge-6-gemini:v0.53
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        env:
        - name: P99_LATENCY_MS
          value: "90"
        - name: KILL_SWITCH_ENABLED
          value: "true"
```
