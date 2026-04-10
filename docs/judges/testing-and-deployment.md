# Judge #6 HITL System - Testing & Deployment Guide

## Quick Start

### Running Tests

```bash
# Run all tests (unit + integration + latency validation)
./run_tests.sh

# Run with full performance benchmarks
./run_tests.sh --full

# Run specific test suites
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
python tests/performance/latency_validation.py  # Latency validation
python tests/performance/benchmark.py    # Performance benchmarks
```

### Test Coverage

```bash
# Generate coverage report
pytest tests/unit/ --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Suite Overview

### Unit Tests (`tests/unit/`)

**test_risk_matrix.py** - ATP 5-19 Risk Matrix

- Matrix lookup correctness (all 20 combinations)
- Approval authority determination
- Risk assessment flow
- Mitigation logic
- Edge cases

**test_semantic_compression.py** - Audit Trail Compression

- Compression/decompression
- Trail ID generation
- Compression ratio (10:1 target)
- Validation rules
- Edge cases

**test_judges.py** - All Judge Verticals

- FinJudge: Wire transfer approval, vendor verification
- CaseJudge: Case acceptance, conflict checks, settlement
- LawJudge: EU AI Act, GDPR, CA SB 53, export control
- FraudJudge: Fraud scoring, identity verification, indicators
- Cross-judge consistency

**Coverage Target**: ≥90%

### Integration Tests (`tests/integration/`)

**test_judge_api.py** - FastAPI Endpoints

- Health checks
- /judges/evaluate endpoint (all verticals)
- Audit trail retrieval
- Metrics endpoints
- Recent decisions
- End-to-end flows
- Error handling

**Coverage**: All API endpoints

### Performance Tests (`tests/performance/`)

**latency_validation.py** - Latency Validation

- Validates p99 ≤90ms requirement
- Tests 1000 samples per vertical
- Generates latency distribution (p50, p90, p95, p99, p100)
- Exports results to JSON/CSV

**Usage**:

```bash
python tests/performance/latency_validation.py --samples 1000
python tests/performance/latency_validation.py --samples 1000 --export-json --export-csv
```

**benchmark.py** - Performance Benchmarks

- Throughput (target: 100 decisions/sec)
- Memory usage
- Cold start vs warm cache
- Decision complexity comparison

**Usage**:

```bash
python tests/performance/benchmark.py
```

## Latency Validation Results

### Expected Results

```
OVERALL RESULTS
============================================================
Total samples:  1000
Mean latency:   ~30ms
Std deviation:  ~10ms

LATENCY DISTRIBUTION:
  p50 (median): ~30ms
  p90:          ~50ms
  p95:          ~65ms
  p99:          ~85ms  ✓ PASS
  p100 (max):   ~120ms

============================================================
✓ VALIDATION PASSED: p99 = 85ms ≤ 90ms
============================================================
```

### Interpreting Results

**Pass Criteria**: p99 ≤90ms

**If validation fails**:

1. Check CPU/memory resources
2. Verify no external API calls in critical path
3. Profile hot spots with cProfile
4. Consider optimization of risk matrix lookup
5. Optimize semantic compression

## Production Deployment

### Docker Build

```bash
# Build image
docker build -t gcr.io/PROJECT_ID/judge-hitl:v1.0.0 .

# Run locally
docker run -p 8001:8001 gcr.io/PROJECT_ID/judge-hitl:v1.0.0

# Test
curl http://localhost:8001/judges/health

# Push to registry
docker push gcr.io/PROJECT_ID/judge-hitl:v1.0.0
```

### Kubernetes Deployment

**Prerequisites**:

- GKE cluster
- kubectl configured
- Secrets created (Gemini API key, database URL)

**Deploy**:

```bash
# Create namespace
kubectl create namespace pnkln-judges

# Create secrets
kubectl create secret generic judge-secrets \
  --from-literal=gemini_api_key=YOUR_KEY \
  --from-literal=database_url=postgresql://... \
  --namespace pnkln-judges

# Deploy
kubectl apply -f k8s/judge-deployment.yaml

# Verify
kubectl get pods -n pnkln-judges
kubectl get svc -n pnkln-judges

# Check logs
kubectl logs -f deployment/judge-hitl -n pnkln-judges

# Port forward for testing
kubectl port-forward svc/judge-hitl-service 8001:80 -n pnkln-judges
```

**Deployment includes**:

- 3 replicas (HA)
- Horizontal Pod Autoscaler (3-10 pods)
- Resource limits (256Mi-512Mi memory, 250m-500m CPU)
- Liveness/readiness probes
- Pod Disruption Budget (min 2 available)
- Network policies
- Non-root user security

### Scaling

**Horizontal Pod Autoscaler (HPA)**:

- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target memory: 80%

**Manual scaling**:

```bash
kubectl scale deployment judge-hitl --replicas=5 -n pnkln-judges
```

### Monitoring

**Health checks**:

```bash
# Service health
kubectl exec -it deployment/judge-hitl -n pnkln-judges -- \
  curl http://localhost:8001/judges/health

# Metrics
kubectl exec -it deployment/judge-hitl -n pnkln-judges -- \
  curl http://localhost:8001/judges/stats/overview
```

**Prometheus metrics** (to be added):

```yaml
- judge_decisions_total{judge_type, decision}
- judge_latency_seconds{judge_type, quantile}
- judge_errors_total{judge_type, error_type}
```

### Production Checklist

- [ ] Unit tests pass (≥90% coverage)
- [ ] Integration tests pass
- [ ] Latency validation passes (p99 ≤90ms)
- [ ] Docker image built and pushed
- [ ] Secrets configured in k8s
- [ ] Database connection tested
- [ ] Gemini API key configured
- [ ] HPA tested under load
- [ ] Logging configured (Stackdriver)
- [ ] Monitoring dashboards created (Grafana)
- [ ] Alerts configured (p99 latency, error rate)
- [ ] Backup strategy implemented (audit trails)
- [ ] Disaster recovery plan documented
- [ ] Load testing completed (100 req/sec)
- [ ] Security scan passed (container vulnerabilities)
- [ ] Compliance audit scheduled (EU AI Act + CA SB 53)

## Continuous Integration

### GitHub Actions (Suggested)

```yaml
name: Judge #6 HITL CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/unit/ --cov=src
      - run: pytest tests/integration/
      - run: python tests/performance/latency_validation.py --quiet

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: false
          tags: judge-hitl:test
```

## Troubleshooting

### Tests Failing

**Unit tests fail**:

- Check Python version (requires 3.11+)
- Verify dependencies: `pip install -r requirements.txt`
- Clear **pycache**: `find . -type d -name __pycache__ -exec rm -r {} +`

**Integration tests fail**:

- Check if API is running: `curl http://localhost:8001/judges/health`
- Verify no port conflicts (8001)
- Check logs for errors

**Latency validation fails**:

- Run on dedicated hardware (no shared CPU)
- Close resource-intensive applications
- Increase sample size for statistical significance
- Check for I/O bottlenecks (disk, network)

### Deployment Issues

**Pods not starting**:

```bash
kubectl describe pod <pod-name> -n pnkln-judges
kubectl logs <pod-name> -n pnkln-judges
```

**Common issues**:

- Missing secrets → Create judge-secrets
- Image pull errors → Verify GCR permissions
- Resource constraints → Increase limits
- Liveness probe failing → Check /judges/health endpoint

**Database connection fails**:

- Verify DATABASE_URL secret
- Check Cloud SQL proxy (if using)
- Verify network policies allow egress to port 5432

## Performance Tuning

### Optimization Targets

1. **p50 latency**: ~30ms
2. **p99 latency**: ≤90ms (hard requirement)
3. **Throughput**: 100 decisions/sec per vertical
4. **Memory**: <512Mi per pod
5. **CPU**: <500m per pod under normal load

### Profiling

```bash
# Profile latency bottlenecks
python -m cProfile -o profile.stats tests/performance/latency_validation.py
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumtime'); p.print_stats(20)"

# Memory profiling (requires memory_profiler)
pip install memory_profiler
python -m memory_profiler tests/performance/benchmark.py
```

### Optimization Strategies

1. **Cache judge instances** (JudgeFactory singleton) ✓
2. **Pre-compile regex patterns** (if added)
3. **Optimize risk matrix lookup** (already O(1))
4. **Minimize allocations in hot path** (BaseJudge.judge())
5. **Async database writes** (audit trails)
6. **Connection pooling** (PostgreSQL)
7. **Redis caching** (for metrics)

## Development Workflow

### Adding New Tests

1. **Unit test**: Add to `tests/unit/test_judges.py`
2. **Integration test**: Add to `tests/integration/test_judge_api.py`
3. **Run tests**: `./run_tests.sh`
4. **Check coverage**: `pytest --cov=src --cov-report=html`

### Pre-commit Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/
mypy src/

# Run tests
./run_tests.sh
```

### Release Process

1. Update version in `src/api/judges.py` and `k8s/judge-deployment.yaml`
2. Run full test suite: `./run_tests.sh --full`
3. Build Docker image: `docker build -t gcr.io/PROJECT_ID/judge-hitl:vX.Y.Z .`
4. Push to registry: `docker push gcr.io/PROJECT_ID/judge-hitl:vX.Y.Z`
5. Update k8s manifests with new version
6. Deploy: `kubectl apply -f k8s/judge-deployment.yaml`
7. Verify: `kubectl rollout status deployment/judge-hitl -n pnkln-judges`
8. Monitor metrics and logs
9. Tag release in Git: `git tag vX.Y.Z && git push origin vX.Y.Z`

---

**Last Updated**: 2025-11-17
**Version**: 1.0.0
