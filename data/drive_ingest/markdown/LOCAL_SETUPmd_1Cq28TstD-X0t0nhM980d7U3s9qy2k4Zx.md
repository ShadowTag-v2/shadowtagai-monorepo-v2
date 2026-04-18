# Local Development Setup

Quick guide to run the File Search service locally for testing.

## Option A: Mock Mode (No GCP Credentials Required) - 5 Minutes

This runs the service with mocked Vertex AI calls for immediate testing.

### Step 1: Create Mock Environment

```bash
# Copy example and configure for mock mode
cp .env.example .env

# These are the minimum settings for mock mode
cat > .env <<EOF
# Mock Mode - No real GCP calls
GCP_PROJECT_ID=mock-project
GCP_REGION=us-central1
GCP_STORAGE_BUCKET=gs://mock-bucket

# Service Configuration
SERVICE_PORT=8000
SERVICE_HOST=0.0.0.0
LOG_LEVEL=DEBUG

# Use mock mode (we'll set this up)
MOCK_MODE=true
EOF
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Step 3: Run with Mock Mode

```bash
# Run the service
MOCK_MODE=true python -m pnkln_file_search.main
```

The service will start with mocked Vertex AI responses on http://localhost:8000

### Step 4: Test Endpoints

```bash
# In another terminal

# 1. Check service is up
curl http://localhost:8000/

# 2. Health check
curl http://localhost:8000/health

# 3. List verticals
curl http://localhost:8000/api/v1/verticals | jq .

# 4. Test query (with mock response)
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can we export technical specifications to NATO allies?",
    "vertical": "defense"
  }' | jq .

# 5. Check metrics
curl http://localhost:8000/metrics | grep -E "file_search|judge"

# 6. Kill switch status
curl http://localhost:8000/api/v1/monitoring/health | jq .
```

---

## Option B: Real GCP Credentials - 15 Minutes

Use this when you want to test with actual Vertex AI.

### Step 1: Get GCP Credentials

```bash
# Install gcloud CLI if not already installed
# See: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set project
export PROJECT_ID="your-gcp-project-id"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
gcloud services enable aiplatform.googleapis.com storage-api.googleapis.com
```

### Step 2: Create Service Account (Optional but Recommended)

```bash
# Create service account
gcloud iam service-accounts create pnkln-file-search-dev \
  --display-name="Pnkln File Search Dev"

# Grant permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:pnkln-file-search-dev@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Download key
gcloud iam service-accounts keys create ~/pnkln-dev-key.json \
  --iam-account=pnkln-file-search-dev@${PROJECT_ID}.iam.gserviceaccount.com
```

### Step 3: Configure Environment

```bash
cat > .env <<EOF
# Real GCP Configuration
GCP_PROJECT_ID=${PROJECT_ID}
GCP_REGION=us-central1
GCP_STORAGE_BUCKET=gs://your-bucket-name

# Path to service account key
GOOGLE_APPLICATION_CREDENTIALS=${HOME}/pnkln-dev-key.json

# Vertex AI
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-3.1-flash-exp

# Service
SERVICE_PORT=8000
LOG_LEVEL=DEBUG
EOF
```

### Step 4: Create Test Bucket (Optional)

```bash
# Create a test bucket
export BUCKET_NAME="${PROJECT_ID}-file-search-test"
gsutil mb -l us-central1 gs://${BUCKET_NAME}/

# Update .env with bucket name
sed -i "s|gs://your-bucket-name|gs://${BUCKET_NAME}|g" .env
```

### Step 5: Run Service

```bash
source venv/bin/activate
python -m pnkln_file_search.main
```

---

## Quick Testing Script

Save this as `test_local.sh`:

```bash
#!/bin/bash
set -e

BASE_URL="http://localhost:8000"

echo "=== Testing Pnkln File Search Local Instance ==="
echo ""

echo "1. Root endpoint..."
curl -s ${BASE_URL}/ | jq .
echo ""

echo "2. Health check..."
curl -s ${BASE_URL}/health | jq .
echo ""

echo "3. Liveness check..."
curl -s ${BASE_URL}/health/live | jq .
echo ""

echo "4. List verticals (first 3)..."
curl -s ${BASE_URL}/api/v1/verticals | jq '.[0:3]'
echo ""

echo "5. Get defense vertical..."
curl -s ${BASE_URL}/api/v1/verticals/defense | jq .
echo ""

echo "6. Test query..."
curl -s -X POST ${BASE_URL}/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can we share classified information with contractors?",
    "vertical": "defense"
  }' | jq '.enforcement, .timing'
echo ""

echo "7. Kill switch status..."
curl -s ${BASE_URL}/api/v1/monitoring/health | jq '.state, .healthy'
echo ""

echo "=== All tests complete! ==="
```

Make it executable:
```bash
chmod +x test_local.sh
./test_local.sh
```

---

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e .
```

### Port Already in Use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
SERVICE_PORT=8001 python -m pnkln_file_search.main
```

### Vertex AI Authentication Errors

```bash
# Check if credentials are set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Re-authenticate
gcloud auth application-default login

# Verify
gcloud auth application-default print-access-token
```

### Module Not Found

```bash
# Make sure you're in the right directory
cd /home/user/ShadowTag-v2-fastapi-services

# Install with all dependencies
pip install -r requirements.txt
pip install -e .
```

---

## Next Steps After Local Testing

Once you verify it works locally:

1. **Add Mock Mode** - Implement mock responses for development
2. **Upload Test Documents** - Add a few sample PDFs to GCS
3. **Initialize Test Corpus** - Create one corpus to test file search
4. **Test Real Query** - Try actual file search retrieval
5. **Implement Judge #6** - Add your Judge layers
6. **Deploy to GKE** - Follow DEPLOYMENT_STEP_BY_STEP.md
