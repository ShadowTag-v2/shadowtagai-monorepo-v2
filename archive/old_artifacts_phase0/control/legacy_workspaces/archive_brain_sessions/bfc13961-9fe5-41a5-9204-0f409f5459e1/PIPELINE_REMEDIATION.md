# PIPELINE REMEDIATION PLAN (Night Pipeline Fixes)

## Critique Summary
The user identified critical flaws in the current `deploy.sh` script:
1.  **Hardcoded Assumptions**: `PROJECT_ID="pnkln-prod"` is brittle.
2.  **Weak Idempotency**: BQ table checks use `|| echo`, masking errors.
3.  **Secret Failures**: No checks for missing secrets; leads to silent runtime death.
4.  **IAM Race Conditions**: Service Account creation/binding is not atomic or verified.
5.  **Scheduler Risks**: Deletes existing jobs blindly (downtime risk). Use update.
6.  **No Rollback**: Failure leaves partial zombie resources.
7.  **No Versioning**: Cloud Run deploys distinct tags, not just `latest`.

## Remediation Logic

### 1. Dynamic Configuration
```bash
# BAD
PROJECT_ID="pnkln-prod"

# GOOD
PROJECT_ID="${1:-${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}}"
if [[ -z "$PROJECT_ID" ]]; then echo "❌ PROJECT_ID required"; exit 1; fi
```

### 2. Strict Idempotency (BigQuery)
```bash
# BAD
bq mk ... 2>/dev/null || echo "exists"

# GOOD
if ! bq show "$PROJECT_ID:$DATASET.$TABLE" >/dev/null 2>&1; then
  bq mk ...
else
  echo "✅ Table $TABLE exists"
fi
```

### 3. Secret Pre-Flight
```bash
# Check required secrets before starting
REQUIRED_SECRETS=("hf-token" "db-creds")
for sec in "${REQUIRED_SECRETS[@]}"; do
  if ! gcloud secrets describe "$sec" --project "$PROJECT_ID" >/dev/null 2>&1; then
    echo "❌ Missing secret: $sec"
    read -p "Create now? (y/n) " -n 1 -r
    # ... logic to create ...
  fi
done
```

### 4. Safer Scheduler Updates
```bash
# BAD
gcloud scheduler jobs delete ... || true
gcloud scheduler jobs create ...

# GOOD
if gcloud scheduler jobs describe ... >/dev/null 2>&1; then
  gcloud scheduler jobs update ...
else
  gcloud scheduler jobs create ...
fi
```

### 5. Atomic Deploy & Tagging
*   Use `git rev-parse --short HEAD` for image tags.
*   Deploy with `--tag` traffic splitting (e.g., 0% to new revision first).
*   Wrap in `trap 'cleanup_function' ERR` block.

## Action Item
Implement these fixes in the next iteration of `infrastructure/scripts/deploy_pipeline.sh`.
