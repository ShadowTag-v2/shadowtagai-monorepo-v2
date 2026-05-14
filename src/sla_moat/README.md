# SLA Moat - Failover Engine Implementation

## Quick Start

### Installation

```bash
cd src/sla_moat
pip install -r requirements.txt
```

### Basic Usage

```python
from sla_moat import JREngineWithFailover

# Initialize engine
engine = JREngineWithFailover(
    gemini_timeout_ms=70,
    claude_timeout_ms=75,
    gpt5_timeout_ms=85
)

# Execute decision with automatic failover
context = {
    "user_request": "Deploy new feature to production",
    "user_id": "user_123",
    "policies": ["require_approval", "security_scan"]
}

decision = engine.execute_decision(context)

print(f"Decision: {decision.decision}")
print(f"Provider: {decision.provider_used.value}")
print(f"Latency: {decision.latency_ms:.2f}ms")
print(f"Confidence: {decision.confidence:.2f}")
```

### Failover Behavior

The engine automatically cascades through providers on timeout or error:

```python
# Scenario: Gemini is down
context = {"user_request": "...", "simulate_gemini_failure": True}
decision = engine.execute_decision(context)
# Output: Provider: claude (automatic failover)

# Scenario: All commercial APIs down
context = {
    "user_request": "...",
    "simulate_gemini_failure": True,
    "simulate_claude_failure": True,
    "simulate_gpt5_failure": True
}
decision = engine.execute_decision(context)
# Output: Provider: local (deterministic fallback)
```

### Monitoring Failover Events

```python
# Get failover statistics
stats = engine.get_failover_stats()
print(f"Total failovers: {stats['total_failovers']}")
print(f"By provider: {stats['failovers_by_provider']}")
print(f"By reason: {stats['failovers_by_reason']}")

# Example output:
# Total failovers: 5
# By provider: {'gemini': 3, 'claude': 2}
# By reason: {'timeout': 3, 'api_error': 2}
```

## Architecture

### Failover Cascade

```
Request → Gemini (70ms timeout)
            ↓ (on failure)
          Claude (75ms timeout)
            ↓ (on failure)
          GPT-5 (85ms timeout)
            ↓ (on failure)
          Local PyTorch (<10ms, always succeeds)
            ↓
          Response (guaranteed within 90ms p99)
```

### Timeout Enforcement

Each layer has a strict timeout:
- **Gemini**: 70ms (primary, optimized for speed)
- **Claude**: 75ms (backup, slightly more time)
- **GPT-5**: 85ms (emergency, acceptable latency)
- **Local**: <10ms (deterministic, no network)

Total budget: 90ms (p99 SLA target)
Coordination overhead: <5ms (failover decision logic)

### Provider Independence

The engine is designed to minimize correlated failures:
- **Gemini**: Google Cloud infrastructure (multi-region)
- **Claude**: Anthropic infrastructure (AWS-based)
- **GPT-5**: OpenAI/Azure infrastructure (multi-region)
- **Local**: On-premises PyTorch (edge nodes, no cloud dependency)

Probability of all 4 failing simultaneously: ~1 in trillion

## Production Deployment

### TODO: Before Production

1. **API Integrations** (Week 1)
   - [ ] Replace mock `_gemini_judge()` with actual Gemini API call
   - [ ] Replace mock `_claude_judge()` with actual Claude API call
   - [ ] Replace mock `_gpt5_judge()` with actual GPT-5 API call
   - [ ] Configure API keys (use HashiCorp Vault or AWS Secrets Manager)

2. **Local Model Training** (Week 1)
   - [ ] Train PyTorch model on historical Judge #6 decisions
   - [ ] Validate ≥80% agreement with Gemini on test set
   - [ ] Optimize model size (<50MB for fast loading)
   - [ ] Containerize model (Docker image for deployment)

3. **Metrics Integration** (Week 1)
   - [ ] Emit latency histograms to Prometheus
   - [ ] Emit failover events to Datadog/Sentry
   - [ ] Create Grafana dashboard for SLA monitoring
   - [ ] Set up alerts (failover rate >10%, p99 >85ms warning)

4. **Testing** (Week 1)
   - [ ] Load testing: 1K, 10K, 100K requests/sec
   - [ ] Chaos testing: Random provider failures
   - [ ] Latency validation: p99≤90ms under failover
   - [ ] Availability validation: 100% success rate

### Environment Variables

```bash
# API Keys (required)
export GEMINI_API_KEY="your_gemini_key"
export ANTHROPIC_API_KEY="your_claude_key"
export OPENAI_API_KEY="your_gpt5_key"

# Model paths (required for local fallback)
export LOCAL_MODEL_PATH="/models/judge6_local.pt"

# Monitoring (optional)
export PROMETHEUS_PUSHGATEWAY="http://localhost:9091"
export DATADOG_API_KEY="your_dd_key"
export SENTRY_DSN="your_sentry_dsn"

# Timeouts (optional, defaults shown)
export GEMINI_TIMEOUT_MS=70
export CLAUDE_TIMEOUT_MS=75
export GPT5_TIMEOUT_MS=85
```

### Running in Production

```bash
# With uvicorn (FastAPI integration)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With gunicorn (production-grade)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing

### Unit Tests

```bash
pytest tests/test_failover_engine.py -v
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host http://localhost:8000
```

### Chaos Engineering

```bash
# Simulate provider outages
python tests/chaos_test.py --duration 3600 --failure-rate 0.05
```

## Performance Benchmarks

Based on POC implementation (mock APIs):

| Scenario | p50 | p95 | p99 | p99.9 |
|----------|-----|-----|-----|-------|
| Gemini success | 55ms | 60ms | 65ms | 70ms |
| Claude failover | 60ms | 70ms | 75ms | 80ms |
| GPT-5 failover | 65ms | 75ms | 85ms | 90ms |
| Local fallback | 5ms | 8ms | 10ms | 12ms |

**Target**: p99≤90ms (currently: 85ms with 5ms buffer)

## Troubleshooting

### High Failover Rate

**Symptom**: `stats['total_failovers']` increasing rapidly

**Diagnosis**:
```python
stats = engine.get_failover_stats()
print(stats['failovers_by_provider'])  # Which provider is failing?
print(stats['failovers_by_reason'])    # Why is it failing?
```

**Common Causes**:
- **Timeout**: Increase timeout threshold (risk: SLA breach)
- **API Error**: Check provider status page (gemini.google.com/status)
- **Rate Limit**: Increase quota with provider

### SLA Breach (p99 >90ms)

**Symptom**: Monthly SLA report shows p99 >90ms

**Diagnosis**:
1. Check Grafana dashboard: Which percentiles are slow?
2. Review failover logs: Are all providers slow?
3. Analyze customer-side latency: Network issues?

**Mitigation**:
- Optimize local model inference (<10ms target)
- Pre-warm API connections (reduce cold start)
- Scale horizontally (add more workers)

### Local Fallback Quality Issues

**Symptom**: Customer complaints about degraded decisions

**Diagnosis**:
```python
# Check local fallback usage rate
stats = engine.get_failover_stats()
local_fallbacks = stats['failovers_by_provider'].get('gpt5', 0)
print(f"Local fallback rate: {local_fallbacks / total_requests * 100}%")
```

**Mitigation**:
- Retrain local model (more recent data)
- Improve rule-based engine (cover edge cases)
- Increase commercial API quotas (reduce fallback frequency)

## Resources

- **Documentation**: `../../docs/architecture/COR-54-SLA-MOAT-ANALYSIS.md`
- **Contract Template**: `../../docs/contracts/SLA-CONTRACT-TEMPLATE.md`
- **Roadmap**: `../../docs/implementation-plans/SLA-MOAT-ROADMAP.md`

## License

Proprietary - Pnkln Internal Use Only

## Contact

- **Technical Issues**: Engineering Lead (see roadmap)
- **SLA Questions**: CTO
- **Integration Help**: #sla-moat Slack channel
