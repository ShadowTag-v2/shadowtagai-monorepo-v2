# Multi-Region Failover Plan

## Current Architecture
- **Primary**: `us-central1` (Cloud Run, Firestore, Cloud Tasks)
- **Failover**: Not yet deployed (planned: `us-east1`)

## Failover Strategy

### Phase 1: DNS-Level (Current)
- Cloud Run URLs are regional but accessed via Google's global LB
- Firebase Hosting CDN provides global edge caching for static assets
- Firestore multi-region (`nam5`) already spans multiple US regions

### Phase 2: Active-Active (Planned)
1. Deploy Cloud Run service to `us-east1`
2. Set up Cloud DNS with health-checked routing
3. Configure Firestore multi-region (already `nam5`)
4. Replicate Cloud Tasks queues to secondary region

### Failover Procedure

#### Automatic (DNS Health Check)
```bash
# Create health-checked DNS routing
gcloud dns record-sets create api.counselconduit.com \
  --type=A \
  --routing-policy-type=FAILOVER \
  --routing-policy-primary-data="REGION_PRIMARY_IP" \
  --routing-policy-backup-data-type=GEO \
  --routing-policy-backup-data="us-east1=BACKUP_IP"
```

#### Manual Failover
```bash
# Point all traffic to backup region
gcloud run services update-traffic counselconduit \
  --project=shadowtag-omega-v4 \
  --region=us-east1 \
  --to-latest=100

# Update DNS or load balancer
gcloud compute url-maps set-default-service counselconduit-urlmap \
  --default-service=counselconduit-backend-us-east1
```

### Data Considerations
- Firestore `nam5` multi-region = automatic failover
- Cloud Tasks: queues are regional, need separate queue in backup region
- Session pins: short-lived, acceptable to lose on failover
- Stripe webhooks: update endpoint in Stripe dashboard

### RTO/RPO Targets
| Component | RTO | RPO |
|-----------|-----|-----|
| API (Cloud Run) | 5 min (manual), 30s (DNS) | 0 (stateless) |
| Database (Firestore) | 0 (multi-region) | 0 (synchronous) |
| Queues (Cloud Tasks) | 15 min | 0 (at-least-once) |
| Sessions | N/A | Sessions re-created |
