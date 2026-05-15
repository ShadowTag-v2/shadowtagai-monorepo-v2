# Firestore Cross-Region Architecture

## Current Configuration
- **Database**: `(default)`
- **Location**: `nam5` (multi-region, US)
- **Type**: FIRESTORE_NATIVE
- **Concurrency**: OPTIMISTIC

## What nam5 Already Provides
The `nam5` multi-region location automatically replicates data across
multiple US data centers. This includes:

- **Synchronous replication** across ≥2 regions
- **Automatic failover** (zero RPO, near-zero RTO)
- **Strong consistency** for all reads

## Read Replicas (Not Needed Currently)
Firestore `nam5` already provides multi-region redundancy.
Traditional "read replicas" are a SQL concept — Firestore handles
this transparently via its distributed architecture.

### When to Consider Additional Databases
| Scenario | Solution |
|----------|----------|
| Data residency (EU) | Create separate `eur3` database |
| Workload isolation | Create named database (`analytics`) |
| Read scaling | Firestore auto-scales (no manual replica needed) |
| Cross-continental latency | Create regional database in target region |

### Creating a Regional Database
```bash
gcloud firestore databases create \
  --database=counselconduit-eu \
  --location=eur3 \
  --type=FIRESTORE_NATIVE
```

## Recommendation
**No action needed.** `nam5` multi-region already provides:
- 99.999% availability SLA
- Automatic failover
- Strong consistency
- Infinite read scaling
