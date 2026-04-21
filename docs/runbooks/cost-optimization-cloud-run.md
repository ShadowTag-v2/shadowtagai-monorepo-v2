# Cloud Run Cost Optimization Report — CounselConduit

## Current Configuration
| Parameter | Production | Staging |
|-----------|-----------|---------|
| CPU | 2 vCPU | 1 vCPU |
| Memory | 1 GiB | 512 MiB |
| Min Instances | 1 | 0 |
| Max Instances | 10 | 3 |
| CPU Boost | Enabled | Disabled |
| Concurrency | 80 | 80 |

## Monthly Cost Estimate (Current)

### Production
| Component | Cost |
|-----------|------|
| CPU (2 vCPU × 1 min instance × 730 hrs) | ~$69.35 |
| Memory (1 GiB × 730 hrs) | ~$5.11 |
| Request handling | ~$0.40/M requests |
| CPU Boost surcharge | ~$3-5 |
| **Subtotal** | **~$78/mo** |

### Staging
| Component | Cost |
|-----------|------|
| Pay-per-request (0 min instances) | ~$0.50-2.00 |
| **Subtotal** | **~$2/mo** |

### Total Cloud Run: **~$80/month**

## Optimization Opportunities

### 1. Right-size CPU (Savings: ~$35/mo)
Current p95 latency is 173ms with 2 vCPU. Test with 1 vCPU:
```bash
gcloud run services update counselconduit \
  --cpu=1 --memory=512Mi
```
If latency stays <500ms, save ~50% on CPU costs.

### 2. Reduce Min Instances During Off-Hours (Savings: ~$20/mo)
```bash
# Scale to 0 during 12am-6am UTC
gcloud scheduler jobs create http counselconduit-scale-down \
  --schedule="0 0 * * *" --time-zone="UTC" \
  --uri="https://run.googleapis.com/v2/projects/.../services/counselconduit" \
  --http-method=PATCH \
  --body='{"template":{"scaling":{"minInstanceCount":0}}}'
```

### 3. CPU Allocation: Request-Only (Savings: ~$30/mo)
If background processing isn't needed:
```bash
gcloud run services update counselconduit \
  --cpu-throttling  # CPU only during request processing
```

### 4. Committed Use Discounts (Savings: 17-52%)
For sustained workloads, purchase CUDs via GCP Console.

## Other Service Costs
| Service | Monthly Estimate |
|---------|-----------------|
| Firestore (nam5) | $5-15 (reads/writes) |
| Cloud Tasks | $0 (first 1M tasks free) |
| Cloud Scheduler | $0 (3 jobs × $0.10) |
| Cloud Monitoring | $0 (first 150MB free) |
| Cloud Logging | $0 (first 50GiB free) |
| BigQuery (new sink) | $0-5 (depends on volume) |
| Cloud Armor | $5/mo per policy |
| Secret Manager | $0.06 per 10K accesses |
| **Estimated Total** | **$90-110/mo** |

## Action Items
1. [ ] Test 1 vCPU on staging — verify p95 <500ms
2. [ ] Implement off-hours scaling (scheduler)
3. [ ] Evaluate CPU throttling for request-only billing
4. [ ] Review Cloud Monitoring for idle resources
5. [ ] Set up billing alert at $150/mo
