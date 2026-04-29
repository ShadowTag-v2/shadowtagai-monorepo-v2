#!/bin/bash
# DEPLOY_UNIFICATION.SH
# CLASSIFICATION: TIER 30 // SOVEREIGN DEPLOYMENT
# TARGET: Google Cloud Platform (Dataflow + Cloud Run)

# 1. PRE-FLIGHT CHECKS
echo ">>> 🚀 INITIATING MASSIVE CONSOLIDATION DEPLOYMENT..."
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
BUCKET_NAME="shadowtag-sovereign-lake-$PROJECT_ID"

# 2. API ENABLEMENT (The Foundation)
echo ">>> 🔓 UNLOCKING GOOGLE APIs..."
gcloud services enable \
    dataflow.googleapis.com \
    managedkafka.googleapis.com \
    secretmanager.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com

# 3. STORAGE PROVISIONING (The Lake)
echo ">>> 🌊 PROVISIONING SOVEREIGN LAKE..."
if ! gcloud storage buckets describe gs://$BUCKET_NAME > /dev/null 2>&1; then
    gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION
    echo "✅ Bucket $BUCKET_NAME created."
else
    echo "✅ Bucket $BUCKET_NAME exists."
fi

# 4. DATAFLOW PIPELINE SUBMISSION (Server-Side Flex Template)
# This avoids local Python compilation issues (Arrow/Beam on Mac/Python 3.14)
echo ">>> 🧠 BUILDING DATAFLOW REFINERY (FLEX TEMPLATE)..."

TEMPLATE_PATH="gs://$BUCKET_NAME/templates/omega-refinery-v1.json"
IMAGE_GCR="gcr.io/$PROJECT_ID/omega-refinery:latest"

# Submit Build to Cloud Build
gcloud builds submit --tag $IMAGE_GCR .

# Run the Template
echo ">>> 🚀 LAUNCHING DATAFLOW JOB..."
gcloud dataflow flex-template run "omega-pubsub-refinery" \
    --template-file-gcs-location "$TEMPLATE_PATH" \
    --parameters sdk_container_image="$IMAGE_GCR" \
    --parameters project="$PROJECT_ID" \
    --parameters region="$REGION" \
    --parameters input_subscription="projects/$PROJECT_ID/subscriptions/trinity-worker-sub" \
    --parameters output_table="$PROJECT_ID:Claude_Code_6_memory.event_ledger" \
    --region "$REGION"

# 5. CLOUD RUN JOB (The Harvester)
echo ">>> 🚜 DEPLOYING HARVESTER (CLOUD RUN JOB)..."
gcloud run jobs deploy harvester-prime \
    --source . \
    --command "python3" \
    --args "scripts/harvest_docs_producer.py" \
    --region $REGION \
    --service-account="shadowtag-agent@$PROJECT_ID.iam.gserviceaccount.com" \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,PYTHONUNBUFFERED=1"

echo ">>> ⚡ EXECUTING HARVESTER HYDRATION..."
gcloud run jobs execute harvester-prime --region $REGION

echo ">>> 🏁 MASSIVE CONSOLIDATION COMPLETE. SYSTEM IS LIVE."
