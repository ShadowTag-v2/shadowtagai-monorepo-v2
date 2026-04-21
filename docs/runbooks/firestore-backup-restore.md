# Firestore Backup & Restore Drill

## Automated Backups
- **Schedule**: Daily at 3am UTC via Cloud Scheduler (`firestore-daily-backup`)
- **Destination**: `gs://shadowtag-omega-v4-firestore-backups/scheduled/`
- **Retention**: 30 days (GCS lifecycle policy)

## Manual Backup

### Full Export
```bash
gcloud firestore export gs://shadowtag-omega-v4-firestore-backups/manual/$(date +%Y%m%d-%H%M) \
  --project=shadowtag-omega-v4
```

### Specific Collections
```bash
gcloud firestore export gs://shadowtag-omega-v4-firestore-backups/manual/$(date +%Y%m%d-%H%M) \
  --project=shadowtag-omega-v4 \
  --collection-ids=session_pins,firm_policies,kovel_attestations
```

## Restore Drill (Quarterly)

### Step 1: List Available Backups
```bash
gsutil ls -la gs://shadowtag-omega-v4-firestore-backups/scheduled/ | tail -10
```

### Step 2: Restore to TEST Database
**NEVER restore to (default) in production!**
```bash
# Create test database first
gcloud firestore databases create --database=restore-test \
  --project=shadowtag-omega-v4 \
  --location=nam5

# Import backup
gcloud firestore import gs://shadowtag-omega-v4-firestore-backups/scheduled/TIMESTAMP/ \
  --project=shadowtag-omega-v4 \
  --database=restore-test
```

### Step 3: Verify Data
```bash
# Count documents
gcloud firestore documents list \
  --database=restore-test \
  --collection=firm_policies \
  --limit=5
```

### Step 4: Cleanup
```bash
gcloud firestore databases delete --database=restore-test \
  --project=shadowtag-omega-v4
```

## Disaster Recovery
| Scenario | Procedure | RTO |
|----------|-----------|-----|
| Accidental deletion | Restore from latest backup | 15 min |
| Data corruption | Restore from known-good backup | 30 min |
| Full database loss | Restore from GCS export | 1 hour |

## Drill Schedule
- **Quarterly**: Full restore drill to test database
- **Monthly**: Verify backup existence in GCS
- **Weekly**: Verify Cloud Scheduler job is running
