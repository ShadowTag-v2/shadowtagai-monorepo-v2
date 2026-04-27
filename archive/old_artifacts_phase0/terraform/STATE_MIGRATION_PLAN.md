# Terraform State Migration Plan

## Current State: Manual GCP Resources

All CounselConduit GCP resources were created via `gcloud` CLI and Firebase console. No Terraform state exists.

## Migration Strategy: Import-First

### Phase 1: Create GCS State Bucket (Week 1)
```bash
gsutil mb -p shadowtag-omega-v4 -l us-central1 gs://shadowtag-omega-v4-tfstate
gsutil versioning set on gs://shadowtag-omega-v4-tfstate
```

### Phase 2: Import Core Resources (Week 1-2)
```bash
cd terraform/infrastructure-live-gcp/prod/us-central1/counselconduit
terragrunt init

# Import existing Cloud Run service
terragrunt import google_cloud_run_v2_service.main \
  projects/shadowtag-omega-v4/locations/us-central1/services/counselconduit

# Import existing Cloud Armor policy
terragrunt import google_compute_security_policy.waf \
  projects/shadowtag-omega-v4/global/securityPolicies/counselconduit-waf
```

### Phase 3: Import Supporting Resources (Week 2-3)
| Resource | Import ID |
|----------|-----------|
| Cloud Run SA | `projects/shadowtag-omega-v4/serviceAccounts/counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com` |
| Uptime checks | `projects/shadowtag-omega-v4/uptimeCheckConfigs/{check_id}` |
| Alert policies | `projects/shadowtag-omega-v4/alertPolicies/{policy_id}` |
| Cloud Scheduler | `projects/shadowtag-omega-v4/locations/us-central1/jobs/{job_name}` |
| Secret Manager | `projects/shadowtag-omega-v4/secrets/{secret_name}` |

### Phase 4: Validate (Week 3)
```bash
# Plan should show zero changes after import
terragrunt plan
# Expected: "No changes. Your infrastructure matches the configuration."
```

### Phase 5: Enable Drift Detection (Week 4)
- Enable nightly drift-detection.yml workflow
- Review first week of drift reports
- Remediate any gaps

## Risk Mitigation
- **Never apply until plan shows zero changes** after import
- Use `lifecycle { prevent_destroy = true }` on all imported resources
- Keep manual `gcloud` as rollback path until Week 4 validation
- State bucket has versioning enabled for state recovery

## Resources to Import (Estimated)
| Category | Count |
|----------|-------|
| Cloud Run services | 2 (counselconduit, kovelai) |
| Service accounts | 3 |
| Cloud Armor policies | 3 |
| Uptime checks | 9 |
| Alert policies | 19 |
| Cloud Scheduler jobs | 12 |
| Secret Manager secrets | ~15 |
| **Total** | **~63** |
