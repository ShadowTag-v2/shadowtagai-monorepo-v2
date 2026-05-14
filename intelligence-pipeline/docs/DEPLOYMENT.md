# PNKLN Intelligence Pipeline - Deployment Guide

## Prerequisites Checklist

- [ ] GCP Project created with billing enabled
- [ ] GKE cluster running (or will create new)
- [ ] `gcloud` CLI installed and authenticated
- [ ] `kubectl` installed
- [ ] `terraform` >= 1.6 installed
- [ ] Anthropic API key obtained
- [ ] GitHub token (optional, for auto-issues)
- [ ] Slack webhook URL (optional, for notifications)

## Step-by-Step Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/ehanc69/aiyou-fastapi-services.git
cd aiyou-fastapi-services/intelligence-pipeline
```

### Step 2: Configure GCP Project

```bash
# Set project
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  container.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com
```

### Step 3: Create or Use Existing GKE Cluster

**Option A: Create New GKE Cluster (Recommended)**

```bash
gcloud container clusters create intelligence-cluster \
  --region us-central1 \
  --num-nodes 1 \
  --machine-type e2-standard-4 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 3 \
  --enable-autorepair \
  --enable-autoupgrade \
  --workload-pool=$PROJECT_ID.svc.id.goog \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing

# Get credentials
gcloud container clusters get-credentials intelligence-cluster --region us-central1
```

**Option B: Use Existing GKE Cluster**

```bash
# List clusters
gcloud container clusters list

# Get credentials
gcloud container clusters get-credentials CLUSTER_NAME --region REGION

# Ensure Workload Identity is enabled
gcloud container clusters update CLUSTER_NAME \
  --region REGION \
  --workload-pool=$PROJECT_ID.svc.id.goog
```

### Step 4: Deploy Infrastructure with Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan -var="project_id=$PROJECT_ID"

# Apply (type 'yes' when prompted)
terraform apply -var="project_id=$PROJECT_ID"

# Save outputs
terraform output > ../outputs.txt
```

**Expected Outputs:**
- BigQuery dataset: `pnkln_intelligence`
- BigQuery table: `intelligence_items`
- GCS bucket: `${PROJECT_ID}-pnkln-intelligence`
- Service account: `intelligence-pipeline@${PROJECT_ID}.iam.gserviceaccount.com`

### Step 5: Build and Push Docker Image

```bash
cd ..  # Back to intelligence-pipeline/

# Build using Cloud Build (recommended)
gcloud builds submit --tag gcr.io/$PROJECT_ID/intelligence-pipeline:latest

# Or build locally and push
# docker build -t gcr.io/$PROJECT_ID/intelligence-pipeline:latest .
# docker push gcr.io/$PROJECT_ID/intelligence-pipeline:latest

# Verify image
gcloud container images list --repository=gcr.io/$PROJECT_ID
```

### Step 6: Update Kubernetes Manifests

```bash
# Update PROJECT_ID in CronJob manifest
sed -i "s/PROJECT_ID/$PROJECT_ID/g" k8s/cronjob.yaml
sed -i "s/PROJECT_ID/$PROJECT_ID/g" k8s/serviceaccount.yaml
```

### Step 7: Create Kubernetes Namespace

```bash
kubectl apply -f k8s/namespace.yaml

# Verify
kubectl get namespace intelligence-pipeline
```

### Step 8: Create Service Account and RBAC

```bash
kubectl apply -f k8s/serviceaccount.yaml

# Annotate service account with Workload Identity
kubectl annotate serviceaccount intelligence-runner \
  --namespace intelligence-pipeline \
  iam.gke.io/gcp-service-account=intelligence-pipeline@$PROJECT_ID.iam.gserviceaccount.com

# Verify
kubectl describe serviceaccount intelligence-runner -n intelligence-pipeline
```

### Step 9: Create Secrets

**Option A: From Command Line (Recommended)**

```bash
kubectl create secret generic api-keys \
  --from-literal=ANTHROPIC_API_KEY="sk-ant-api03-your-key-here" \
  --from-literal=PROJECT_ID="$PROJECT_ID" \
  --from-literal=BIGQUERY_DATASET="pnkln_intelligence" \
  --from-literal=GCS_BUCKET="$PROJECT_ID-pnkln-intelligence" \
  --namespace intelligence-pipeline

# Optional: Add GitHub and Slack
kubectl patch secret api-keys \
  --namespace intelligence-pipeline \
  --patch='{"stringData":{"GITHUB_TOKEN":"ghp_your-token-here","SLACK_WEBHOOK_URL":"https://hooks.slack.com/services/YOUR/WEBHOOK/URL"}}'

# Optional: Add email configuration
kubectl patch secret api-keys \
  --namespace intelligence-pipeline \
  --patch='{"stringData":{"SMTP_HOST":"smtp.gmail.com","SMTP_PORT":"587","SMTP_USER":"intelligence@pnkln.ai","SMTP_PASSWORD":"your-password","CEO_EMAIL":"ceo@pnkln.ai"}}'
```

**Option B: From .env File**

```bash
# Create .env file
cat > .env <<EOF
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
PROJECT_ID=$PROJECT_ID
BIGQUERY_DATASET=pnkln_intelligence
GCS_BUCKET=$PROJECT_ID-pnkln-intelligence
GITHUB_TOKEN=ghp_your-token-here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=intelligence@pnkln.ai
SMTP_PASSWORD=your-password
CEO_EMAIL=ceo@pnkln.ai
EOF

# Create secret from file
kubectl create secret generic api-keys \
  --from-env-file=.env \
  --namespace intelligence-pipeline

# IMPORTANT: Delete .env file
rm .env
```

**Verify Secrets:**

```bash
kubectl get secret api-keys -n intelligence-pipeline
kubectl describe secret api-keys -n intelligence-pipeline
```

### Step 10: Deploy CronJob

```bash
kubectl apply -f k8s/cronjob.yaml

# Verify
kubectl get cronjob -n intelligence-pipeline

# Expected output:
# NAME                      SCHEDULE     SUSPEND   ACTIVE   LAST SCHEDULE   AGE
# nightly-intel-pipeline    0 2 * * *    False     0        <none>          1m
```

### Step 11: Manual Test Run (Recommended)

Don't wait until 2 AM! Test the pipeline now:

```bash
# Create a test job from the CronJob
kubectl create job --from=cronjob/nightly-intel-pipeline manual-test-1 -n intelligence-pipeline

# Watch the job
kubectl get jobs -n intelligence-pipeline -w

# View logs (in real-time)
kubectl logs -n intelligence-pipeline -l app=intel-pipeline --tail=100 -f
```

**Expected Log Output:**

```
╔══════════════════════════════════════════════════════════════╗
║  🧠 PNKLN NIGHTLY INTELLIGENCE PIPELINE                      ║
║  GKE-Native | 5th Namespace | ATP 5-19 RA-1 Compliant       ║
╚══════════════════════════════════════════════════════════════╝

Started: 2025-11-08T12:00:00Z

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 STEP 1: Intelligence Ingestion
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
✓ Ingestion complete: 47 items in 45.2s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 STEP 2: JR Engine Scoring
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
...
✓ JR Scoring complete in 23.1s

...

╔══════════════════════════════════════════════════════════════╗
║  ✅ PIPELINE COMPLETE                                        ║
╚══════════════════════════════════════════════════════════════╝
Completed: 2025-11-08T12:05:30Z

ATP 5-19 Risk Status: RA-1 (Low - Compliant)
```

### Step 12: Verify BigQuery Data

```bash
# List tables
bq ls pnkln_intelligence

# Query data
bq query --use_legacy_sql=false '
SELECT
  DATE(published_date) as date,
  tier,
  COUNT(*) as count
FROM `'$PROJECT_ID'.pnkln_intelligence.intelligence_items`
GROUP BY date, tier
ORDER BY date DESC
LIMIT 10
'
```

### Step 13: Set Up Business Impact Dashboard

```bash
# Create BigQuery views
bq query --use_legacy_sql=false < sql/business_impact_dashboard.sql

# Query ROI dashboard
bq query --use_legacy_sql=false '
SELECT * FROM `'$PROJECT_ID'.pnkln_intelligence.roi_dashboard`
'
```

## Verification Checklist

- [ ] CronJob created and scheduled
- [ ] Test job completed successfully
- [ ] BigQuery table has data
- [ ] Logs show all 7 steps completed
- [ ] No error messages in logs
- [ ] Briefing file created or email sent
- [ ] Business impact views created

## Monitoring

### View CronJob Status

```bash
# List all CronJobs
kubectl get cronjob -n intelligence-pipeline

# List recent jobs
kubectl get jobs -n intelligence-pipeline --sort-by=.status.startTime

# View job details
kubectl describe job <job-name> -n intelligence-pipeline
```

### View Logs

```bash
# Latest job logs
kubectl logs -n intelligence-pipeline -l app=intel-pipeline --tail=500

# Specific job logs
kubectl logs -n intelligence-pipeline -l job-name=<job-name>

# Follow logs (real-time)
kubectl logs -n intelligence-pipeline -l app=intel-pipeline -f
```

### Check Pipeline Health

```bash
# View recent executions
kubectl get jobs -n intelligence-pipeline

# Check for failures
kubectl get jobs -n intelligence-pipeline --field-selector status.failed=1

# View pod status
kubectl get pods -n intelligence-pipeline
```

## Troubleshooting

### Issue: Job Fails with ImagePullBackOff

**Solution:**

```bash
# Verify image exists
gcloud container images list --repository=gcr.io/$PROJECT_ID

# Check service account has correct permissions
kubectl describe serviceaccount intelligence-runner -n intelligence-pipeline

# Verify Workload Identity annotation
kubectl get serviceaccount intelligence-runner -n intelligence-pipeline -o yaml | grep "iam.gke.io"
```

### Issue: BigQuery Permission Denied

**Solution:**

```bash
# Check IAM roles
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:intelligence-pipeline@*"

# Grant roles if missing
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:intelligence-pipeline@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

### Issue: Anthropic API Rate Limit

**Solution:**

1. Check API key quota: https://console.anthropic.com/
2. Adjust JR Engine batch size in `src/pipeline/jr_scoring.py`
3. Add delays between API calls

### Issue: Ethical Scraping Violations

**Solution:**

```bash
# Check compliance logs
kubectl logs -n intelligence-pipeline -l app=intel-pipeline | grep -E "(robots.txt|rate limit|circuit)"

# Query compliance dashboard
bq query --use_legacy_sql=false '
SELECT * FROM `'$PROJECT_ID'.pnkln_intelligence.atp_compliance`
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAYS)
'
```

## Updating the Pipeline

### Update Code

```bash
# Make changes to src/

# Rebuild image
gcloud builds submit --tag gcr.io/$PROJECT_ID/intelligence-pipeline:v2

# Update CronJob to use new image
kubectl set image cronjob/nightly-intel-pipeline \
  pipeline=gcr.io/$PROJECT_ID/intelligence-pipeline:v2 \
  -n intelligence-pipeline
```

### Update Configuration

```bash
# Edit config/pipeline.yaml
vim config/pipeline.yaml

# Rebuild and redeploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/intelligence-pipeline:latest
kubectl rollout restart cronjob/nightly-intel-pipeline -n intelligence-pipeline
```

### Update Secrets

```bash
# Update existing secret
kubectl patch secret api-keys \
  --namespace intelligence-pipeline \
  --patch='{"stringData":{"ANTHROPIC_API_KEY":"new-key-here"}}'
```

## Cleanup

To remove the entire pipeline:

```bash
# Delete Kubernetes resources
kubectl delete namespace intelligence-pipeline

# Delete GCP resources
cd terraform
terraform destroy -var="project_id=$PROJECT_ID"

# Delete Docker images
gcloud container images delete gcr.io/$PROJECT_ID/intelligence-pipeline:latest --quiet
```

## Support

For issues or questions:

- **Email**: intelligence@pnkln.ai
- **Internal Slack**: #intelligence-pipeline
- **Documentation**: [README.md](../README.md)

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
