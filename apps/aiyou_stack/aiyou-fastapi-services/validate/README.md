# PNKLN Latency Validation Harness

Comprehensive testing suite for validating Judge #6 inference latency against **p99 ≤90ms** SLA.

## Tools

### 1. test_latency.py - SLA Validation

Primary tool for verifying p99 latency SLA compliance.

**Features**:
- Asynchronous concurrent requests
- Percentile analysis (p50, p90, p95, p99, p99.9)
- Pass/fail validation against SLA
- Detailed JSON reports
- Exit code 0 (pass) or 1 (fail) for CI/CD

**Usage**:

```bash
# Basic test (100 requests, 10 concurrent)
python test_latency.py

# Custom endpoint and SLA target
python test_latency.py \
  --endpoint http://judge6.pnkln.svc.cluster.local \
  --p99-target-ms 90

# Larger test (1000 requests, 50 concurrent)
python test_latency.py \
  --num-requests 1000 \
  --concurrency 50

# Save results to JSON
python test_latency.py --output results.json

# With API key authentication
python test_latency.py --api-key YOUR_API_KEY

# Custom prompt
python test_latency.py \
  --prompt "Your custom inference prompt here"
```

**Example Output**:

```
🔬 Starting latency test...
   Endpoint: http://judge6.pnkln.svc.cluster.local
   Requests: 100
   Concurrency: 10

⏳ Warming up endpoint...
🚀 Running 100 requests...

Requests: 100%|████████████████████| 100/100 [00:15<00:00,  6.45req/s]

======================================================================
📊 LATENCY TEST REPORT
======================================================================

🎯 Target: p99 ≤ 90ms
📍 Endpoint: http://judge6.pnkln.svc.cluster.local
🕒 Timestamp: 2025-11-08T14:30:00

📦 Requests:
Total        100
Successful   100 (100.0%)
Failed       0
Duration     15.50s
Throughput   6.45 QPS

📈 Latency Percentiles (ms):
Min           42.15
p50 (Median)  58.32
p90           72.18
p95           78.44
p99           84.92
p99.9         87.11
Max           89.23
Mean          60.12
Std Dev       10.34

🎯 SLA Validation:
Target    p99 ≤ 90ms
Actual    p99 = 84.92ms
Margin    +5.08ms
Status    ✅ PASS

💡 Recommendations:
   ✅ SLA target met!
   ⚠️  Tight margin: 5.1ms headroom
   → Consider optimizations to improve stability

======================================================================

💾 Report saved to: latency_report_20251108_143000.json
```

### 2. test_health.sh - Endpoint Health Check

Quick health check before running latency tests.

**Usage**:

```bash
# Default endpoint
bash test_health.sh

# Custom endpoint
ENDPOINT=http://judge6.pnkln.svc.cluster.local bash test_health.sh
```

**Example**:

```
🏥 Health Check for Judge #6
================================
Endpoint: http://judge6.pnkln.svc.cluster.local

Attempt 1/30: ✅ Healthy

✅ Service is healthy and ready for testing

📊 Service Information:
{
  "status": "healthy",
  "model": "pnkln-judge6-v1",
  "gpu": "NVIDIA L4"
}
```

### 3. stress_test.py - Capacity Testing

Progressive load test to find maximum capacity within SLA.

**Features**:
- Incremental QPS increases
- Automatic stopping when SLA violated
- Capacity limit identification

**Usage**:

```bash
# Basic stress test (10 → 200 QPS, 10 QPS steps)
python stress_test.py

# Custom range
python stress_test.py \
  --start-qps 20 \
  --max-qps 300 \
  --step-qps 20 \
  --duration 30

# Tighter SLA
python stress_test.py --p99-target-ms 50
```

**Example Output**:

```
======================================================================
🔥 STRESS TEST - Progressive Load
======================================================================
Target SLA: p99 ≤ 90ms
Load range: 10 → 200 QPS
Step size: 10 QPS
Duration per step: 60s
======================================================================

📈 Testing at 10 QPS...
   p99: 55.23ms (target: ≤90ms)
   QPS: 10.12
   Success rate: 100.0%
   ✅ SLA met

📈 Testing at 20 QPS...
   p99: 61.45ms (target: ≤90ms)
   QPS: 20.05
   Success rate: 100.0%
   ✅ SLA met

📈 Testing at 30 QPS...
   p99: 74.18ms (target: ≤90ms)
   QPS: 29.98
   Success rate: 100.0%
   ✅ SLA met

📈 Testing at 40 QPS...
   p99: 92.34ms (target: ≤90ms)
   QPS: 39.87
   Success rate: 99.8%
   ❌ SLA violated at 40 QPS

======================================================================
📊 STRESS TEST SUMMARY
======================================================================

✅ Maximum QPS within SLA: 30.0

📈 Load vs Latency:
QPS        p99 (ms)     Success %    Status
--------------------------------------------------
10.1       55.23        100.0        ✅
20.1       61.45        100.0        ✅
30.0       74.18        100.0        ✅
39.9       92.34        99.8         ❌

======================================================================
```

## Setup

### 1. Install Dependencies

```bash
cd validate
pip install -r requirements.txt
```

### 2. Make Scripts Executable

```bash
chmod +x test_health.sh
```

### 3. Configure kubectl (for in-cluster testing)

```bash
gcloud container clusters get-credentials pnkln-gke-cluster \
  --region us-central1 \
  --project YOUR_PROJECT_ID
```

## Testing Workflows

### Pre-Deployment Validation

Before deploying to production:

```bash
# 1. Check health
bash test_health.sh

# 2. Quick latency check (100 requests)
python test_latency.py --num-requests 100

# 3. Full validation (1000 requests)
python test_latency.py --num-requests 1000 --concurrency 50

# 4. Stress test to find limits
python stress_test.py --max-qps 100
```

### CI/CD Integration

Use in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Deploy to GKE
  run: |
    kubectl apply -f deploy/
    kubectl wait --for=condition=ready pod -l app=judge6 -n pnkln --timeout=300s

- name: Health Check
  run: bash validate/test_health.sh

- name: Latency SLA Validation
  run: |
    cd validate
    python test_latency.py \
      --num-requests 500 \
      --p99-target-ms 90 \
      --output ci_results.json

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: latency-report
    path: validate/ci_results.json
```

### Local Testing from Vertex AI Workbench

```bash
# Port forward service to localhost
kubectl port-forward -n pnkln svc/judge6 8000:80

# Test against local port
python test_latency.py \
  --endpoint http://localhost:8000 \
  --num-requests 100
```

### Production Monitoring

Run periodic validation:

```bash
# Cron job: Every hour
0 * * * * cd /path/to/validate && python test_latency.py --output /var/log/pnkln/latency_$(date +\%Y\%m\%d_\%H\%M).json
```

## Interpreting Results

### SLA Status

- **✅ PASS**: p99 ≤ 90ms → SLA met
- **❌ FAIL**: p99 > 90ms → SLA violated

### Margin Analysis

- **>20ms margin**: Excellent, stable
- **10-20ms margin**: Good, monitoring recommended
- **5-10ms margin**: Acceptable, optimization recommended
- **<5ms margin**: Risky, optimization critical
- **Negative margin**: SLA violated

### Failure Rates

- **0% failures**: Healthy
- **<1% failures**: Acceptable (transient errors)
- **1-5% failures**: Warning (investigate)
- **>5% failures**: Critical (deployment issue)

## Troubleshooting

### Connection Errors

```
Error: Cannot connect to endpoint
```

**Solutions**:

1. Check service is running:
   ```bash
   kubectl get svc -n pnkln judge6
   ```

2. Verify pods are ready:
   ```bash
   kubectl get pods -n pnkln -l app=judge6
   ```

3. Check endpoint URL:
   ```bash
   # In-cluster
   curl http://judge6.pnkln.svc.cluster.local/health

   # Via port-forward
   kubectl port-forward -n pnkln svc/judge6 8000:80
   curl http://localhost:8000/health
   ```

### High Latency (p99 > 90ms)

**Diagnostic steps**:

1. **Check GPU utilization**:
   ```bash
   kubectl exec -n pnkln <pod-name> -- nvidia-smi
   ```

2. **Review pod logs**:
   ```bash
   kubectl logs -n pnkln -l app=judge6 --tail=100
   ```

3. **Check resource limits**:
   ```bash
   kubectl describe pod -n pnkln <pod-name>
   ```

4. **Verify configuration**:
   ```bash
   kubectl get cm judge6-config -n pnkln -o yaml
   ```

**Optimization checklist**:

- [ ] Flash Attention enabled
- [ ] Quantization enabled (AWQ or FP8)
- [ ] Batch size = 1 (for lowest latency)
- [ ] KV cache enabled
- [ ] GPU memory utilization ≥ 0.9
- [ ] Using appropriate GPU (L4 or H100)

### Timeout Errors

```
Error: Timeout
```

**Solutions**:

1. Increase timeout in test:
   ```python
   # In test_latency.py, line ~85
   timeout=aiohttp.ClientTimeout(total=60.0)  # Increase from 30s
   ```

2. Check pod startup time:
   ```bash
   kubectl get pods -n pnkln -w
   ```

3. Review startup probe configuration in deployment

## Advanced Usage

### Custom Prompts

Test with production-like prompts:

```bash
python test_latency.py \
  --prompt "$(cat sample_prompts/security_analysis.txt)"
```

### Load Distribution Analysis

Test different concurrency levels:

```bash
for concurrency in 1 5 10 20 50; do
  echo "Testing concurrency: $concurrency"
  python test_latency.py \
    --num-requests 100 \
    --concurrency $concurrency \
    --output "results_c${concurrency}.json"
done
```

### Multi-Region Testing

Test from different locations:

```bash
# Region A
ENDPOINT=http://judge6-us-central.example.com python test_latency.py

# Region B
ENDPOINT=http://judge6-us-east.example.com python test_latency.py
```

## Metrics Reference

### Latency Percentiles

- **p50 (Median)**: Typical user experience
- **p90**: 90% of users faster than this
- **p95**: 95% of users faster than this
- **p99**: SLA target (99% faster than 90ms)
- **p99.9**: Worst-case outliers

### Throughput (QPS)

Queries per second the system handles.

**Typical benchmarks**:
- L4 GPU: 50-100 QPS @ p99 <90ms
- H100 GPU: 150-300 QPS @ p99 <90ms

### Success Rate

Percentage of requests that complete successfully.

**Targets**:
- Production: ≥99.9%
- Development: ≥95%

## Cost Estimation

### Test Costs

Assuming 2 GPU pods running during tests:

**L4 (Spot)**:
- Hourly: $0.80 (2 nodes × $0.40)
- Per test run (5 min): ~$0.07

**H100 (On-demand)**:
- Hourly: $5.00 (2 nodes × $2.50)
- Per test run (5 min): ~$0.42

### Recommendations

1. Use **L4 spot** for routine validation
2. Use **H100** for capacity/stress testing
3. Scale down between test runs
4. Run comprehensive tests during off-peak hours

## References

- [vLLM Metrics](https://docs.vllm.ai/en/latest/serving/metrics.html)
- [GKE Load Testing Best Practices](https://cloud.google.com/architecture/best-practices-for-load-testing)
- [Latency Optimization Guide](../deploy/README.md#performance-tuning)

## Support

Issues with validation tools? Check:

1. Logs: `kubectl logs -n pnkln -l app=judge6`
2. Events: `kubectl get events -n pnkln --sort-by='.lastTimestamp'`
3. Metrics: Port-forward and access `/metrics` endpoint
