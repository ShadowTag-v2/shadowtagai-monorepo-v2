# CounselConduit SLO Definitions

## SLO 1: Availability
- **Objective**: 99.5% of requests return non-5xx responses
- **Window**: 30-day rolling
- **Error budget**: 0.5% = ~3.6 hours of downtime/month
- **Alert thresholds**:
  - 50% budget consumed → WARNING alert
  - 80% budget consumed → CRITICAL alert
  - 100% budget consumed → FREEZE deployments

## SLO 2: Latency
- **Objective**: p95 latency < 500ms for dispatch endpoint
- **Window**: 30-day rolling
- **Measurement**: Cloud Monitoring `run.googleapis.com/request_latencies`
- **Alert**: p95 > 500ms for 10 min → WARNING

## SLO 3: Throughput
- **Objective**: Handle ≥100 RPM sustained without degradation
- **Measurement**: k6 nightly load test
- **Alert**: Nightly test failure → GitHub Actions notification

## Monitoring
- **Dashboard**: "CounselConduit Error Budget & SLO Burn Rate" (Cloud Monitoring)
- **Alerts**: 2 error budget policies (50% + 80%)
- **Nightly validation**: k6 load test via GitHub Actions

## Error Budget Policy
| Budget Remaining | Action |
|-----------------|--------|
| >50% | Normal operations |
| 20-50% | Reduce deploy frequency to 1/day |
| 5-20% | Freeze non-critical deploys |
| <5% | Emergency: only critical fixes |
| 0% | Full freeze until budget replenishes |

## Burn Rate Calculation
```
burn_rate = (error_count / total_requests) / slo_target_error_rate
```
- burn_rate = 1.0 → burning at exactly the SLO rate
- burn_rate > 1.0 → will exhaust budget before window ends
- burn_rate > 14.4 → 1-hour alert (fast burn)
- burn_rate > 6.0 → 6-hour alert (medium burn)
