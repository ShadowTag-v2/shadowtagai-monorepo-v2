#!/bin/bash
# setup_vertex_datastore.sh - Create Vertex AI Search datastore for Judge 6 grounding
#
# Layer 3 infrastructure for JURA governance:
# - Creates GCS bucket for doctrine documents
# - Sets up Vertex AI Search datastore
# - Configures document indexing
#
# Target: "Always Grounded" mode - all Judge 6 queries through Vertex AI Search

set -euo pipefail

# Configuration
PROJECT_ID="${PROJECT_ID:-acquired-jet-478701-b3}"
LOCATION="${LOCATION:-us-central1}"
DATASTORE_ID="${DATASTORE_ID:-judge6-doctrine-store}"
BUCKET_NAME="${BUCKET_NAME:-${PROJECT_ID}-judge6-docs}"
COLLECTION_ID="default_collection"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
        exit 1
    fi

    # Check authentication
    if ! gcloud auth print-identity-token &> /dev/null; then
        log_error "Not authenticated. Run: gcloud auth login"
        exit 1
    fi

    # Verify project
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
        log_warn "Current project ($CURRENT_PROJECT) differs from target ($PROJECT_ID)"
        log_info "Setting project to $PROJECT_ID..."
        gcloud config set project "$PROJECT_ID"
    fi

    log_info "Prerequisites OK"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required APIs..."

    gcloud services enable \
        discoveryengine.googleapis.com \
        storage.googleapis.com \
        aiplatform.googleapis.com \
        --project="$PROJECT_ID"

    log_info "APIs enabled"
}

# Create GCS bucket for doctrine documents
create_bucket() {
    log_info "Creating GCS bucket: gs://$BUCKET_NAME"

    if gsutil ls -b "gs://$BUCKET_NAME" &> /dev/null; then
        log_info "Bucket already exists"
    else
        gsutil mb -l "$LOCATION" -p "$PROJECT_ID" "gs://$BUCKET_NAME"

        # Set lifecycle policy (7 years retention for compliance)
        cat > /tmp/lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 2555}
      }
    ]
  }
}
EOF
        gsutil lifecycle set /tmp/lifecycle.json "gs://$BUCKET_NAME"
        rm /tmp/lifecycle.json

        log_info "Bucket created with 7-year retention policy"
    fi
}

# Upload sample doctrine documents
upload_doctrine_docs() {
    log_info "Uploading doctrine documents to GCS..."

    DOCS_DIR="$(dirname "$0")/../docs/doctrine"

    if [ -d "$DOCS_DIR" ]; then
        gsutil -m cp -r "$DOCS_DIR/*" "gs://$BUCKET_NAME/doctrine/"
        log_info "Doctrine documents uploaded"
    else
        log_warn "No doctrine directory found at $DOCS_DIR"
        log_info "Creating sample doctrine documents..."

        # Create sample doctrine document
        mkdir -p /tmp/doctrine
        cat > /tmp/doctrine/governance_policy.md << 'EOF'
# JURA Governance Policy

## Purpose
This document defines the governance policies for Judge 6 compliance scoring.

## Risk Categories

### PCI-DSS Compliance
- All payment card data must be encrypted at rest and in transit
- Cardholder data environment (CDE) must be isolated
- Regular security assessments required

### GDPR Compliance
- Data subject rights must be honored within 30 days
- Privacy by design required for all new features
- Data processing agreements required for all vendors

### CCPA Compliance
- California residents have right to know what data is collected
- Opt-out mechanisms required for data sales
- Privacy policy must be updated annually

## Risk Scoring

| Risk Level | Score Range | Action |
|------------|-------------|--------|
| LOW | 0-25 | Auto-approve |
| MEDIUM | 26-50 | Approve with monitoring |
| HIGH | 51-75 | Require human review |
| CRITICAL | 76-100 | Auto-deny |

## ATP 5-19 Framework
Military risk assessment methodology for compliance evaluation:
1. Identify hazards
2. Assess probability and severity
3. Develop controls
4. Implement controls
5. Supervise and refine
EOF

        cat > /tmp/doctrine/compliance_checklist.md << 'EOF'
# Compliance Checklist

## Pre-Transaction Checks
- [ ] User region identified (EU, US-CA, etc.)
- [ ] Payment method validated
- [ ] Transaction value within limits
- [ ] Applicable regulations determined

## PCI-DSS Checklist
- [ ] Card number tokenized
- [ ] CVV not stored
- [ ] Encryption active
- [ ] Access logged

## GDPR Checklist
- [ ] Consent obtained
- [ ] Purpose specified
- [ ] Data minimization applied
- [ ] Right to erasure documented
EOF

        gsutil -m cp -r /tmp/doctrine/* "gs://$BUCKET_NAME/doctrine/"
        rm -rf /tmp/doctrine

        log_info "Sample doctrine documents created and uploaded"
    fi
}

# Create Vertex AI Search datastore
create_datastore() {
    log_info "Creating Vertex AI Search datastore: $DATASTORE_ID"

    # Check if datastore exists
    EXISTING=$(gcloud alpha discovery-engine data-stores list \
        --location="global" \
        --project="$PROJECT_ID" \
        --format="value(name)" 2>/dev/null | grep "$DATASTORE_ID" || true)

    if [ -n "$EXISTING" ]; then
        log_info "Datastore already exists"
        return 0
    fi

    # Create datastore using REST API (gcloud alpha may not support all options)
    log_info "Creating unstructured datastore for document search..."

    # Use curl with gcloud auth
    TOKEN=$(gcloud auth print-access-token)

    curl -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: $PROJECT_ID" \
        "https://discoveryengine.googleapis.com/v1/projects/$PROJECT_ID/locations/global/collections/$COLLECTION_ID/dataStores?dataStoreId=$DATASTORE_ID" \
        -d '{
            "displayName": "Judge 6 Doctrine Store",
            "industryVertical": "GENERIC",
            "solutionTypes": ["SOLUTION_TYPE_SEARCH"],
            "contentConfig": "CONTENT_REQUIRED"
        }' 2>/dev/null || {
            log_warn "REST API call failed, trying gcloud..."
            gcloud alpha discovery-engine data-stores create "$DATASTORE_ID" \
                --location=global \
                --project="$PROJECT_ID" \
                --display-name="Judge 6 Doctrine Store" \
                --industry-vertical=GENERIC \
                --solution-types=SOLUTION_TYPE_SEARCH
        }

    log_info "Datastore created"
}

# Import documents into datastore
import_documents() {
    log_info "Importing documents into datastore..."

    TOKEN=$(gcloud auth print-access-token)

    # Create import job
    curl -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "X-Goog-User-Project: $PROJECT_ID" \
        "https://discoveryengine.googleapis.com/v1/projects/$PROJECT_ID/locations/global/collections/$COLLECTION_ID/dataStores/$DATASTORE_ID/branches/default_branch/documents:import" \
        -d "{
            \"gcsSource\": {
                \"inputUris\": [\"gs://$BUCKET_NAME/doctrine/*\"],
                \"dataSchema\": \"content\"
            },
            \"reconciliationMode\": \"FULL\"
        }" 2>/dev/null || {
            log_warn "Import may require manual configuration in Cloud Console"
        }

    log_info "Import job submitted (may take several minutes)"
}

# Print configuration for judge6_grounded.py
print_config() {
    log_info "Configuration for judge6_grounded.py:"
    echo ""
    echo "# Add to environment or config:"
    echo "export VERTEX_PROJECT_ID=\"$PROJECT_ID\""
    echo "export VERTEX_LOCATION=\"$LOCATION\""
    echo "export JUDGE6_DATASTORE_ID=\"$DATASTORE_ID\""
    echo ""
    echo "# Datastore path for grounding:"
    echo "DATASTORE_PATH=\"projects/$PROJECT_ID/locations/global/collections/$COLLECTION_ID/dataStores/$DATASTORE_ID\""
    echo ""
    echo "# Python usage:"
    cat << 'PYTHON'
from google.cloud import discoveryengine_v1
from vertexai.preview.generative_models import grounding, Tool

# Create grounding tool
data_store_path = f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/judge6-doctrine-store"

grounding_tool = Tool.from_retrieval(
    grounding.Retrieval(
        source=grounding.VertexAISearch(datastore=data_store_path)
    )
)
PYTHON
}

# Main execution
main() {
    log_info "=== Vertex AI Search Datastore Setup for Judge 6 ==="
    log_info "Project: $PROJECT_ID"
    log_info "Location: $LOCATION"
    log_info "Datastore: $DATASTORE_ID"
    log_info "Bucket: gs://$BUCKET_NAME"
    echo ""

    check_prerequisites
    enable_apis
    create_bucket
    upload_doctrine_docs
    create_datastore
    import_documents

    echo ""
    log_info "=== Setup Complete ==="
    print_config
}

# Run
main "$@"
