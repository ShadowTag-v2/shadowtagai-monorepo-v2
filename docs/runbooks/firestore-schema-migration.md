# Firestore Schema Migration Runbook

## Principles
Firestore is schemaless — "migrations" are data transformations, not DDL statements.

## Migration Patterns

### Pattern 1: Additive Field (Zero-Downtime)
Adding a new field to existing documents. No migration needed.
```python
# Code handles missing field with default
policy = doc.get("new_field", default_value)
```

### Pattern 2: Lazy Migration
Transform documents on read. Old docs get updated when accessed.
```python
async def get_firm_policy(firm_id: str):
    doc = await db.collection("firm_policies").document(firm_id).get()
    data = doc.to_dict()
    if "schema_version" not in data or data["schema_version"] < 2:
        data = migrate_v1_to_v2(data)
        await doc.reference.update(data)
    return data
```

### Pattern 3: Batch Migration (Background)
Use Cloud Tasks for bulk transformation.
```python
async def batch_migrate_collection(collection: str, batch_size: int = 500):
    docs = db.collection(collection).limit(batch_size).stream()
    batch = db.batch()
    count = 0
    async for doc in docs:
        data = doc.to_dict()
        if needs_migration(data):
            batch.update(doc.reference, transform(data))
            count += 1
            if count >= batch_size:
                await batch.commit()
                batch = db.batch()
                count = 0
    if count:
        await batch.commit()
```

### Pattern 4: Dual-Write (Breaking Change)
1. Deploy code that writes to both old AND new format
2. Run batch migration for existing docs
3. Deploy code that reads from new format only
4. Remove old format writes

## Pre-Migration Checklist
- [ ] Backup database: `gcloud firestore export gs://shadowtag-omega-v4-firestore-backups/pre-migration/`
- [ ] Test migration script in staging
- [ ] Verify rollback procedure
- [ ] Schedule maintenance window (if batch)
- [ ] Update schema version in affected documents

## Schema Registry
| Collection | Current Version | Last Migration |
|------------|----------------|----------------|
| firm_policies | v1 | Initial |
| session_pins | v1 | Initial |
| kovel_attestations | v1 | Initial |
| audit_logs | v1 | Initial |
