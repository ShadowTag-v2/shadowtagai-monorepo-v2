#!/bin/bash
set -euo pipefail

# PNKLN Core Stack™ - Vertex AI Workbench Deployment
# Migrates rust_scriptbots/Bevy workflow from Cursor to Vertex
# Bootstrap execution: zero manual configuration

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
ZONE="${GCP_ZONE:-us-central1-a}"
REPO_URL="${RUST_SCRIPTBOTS_REPO:-}"  # Set via env or prompt

# GCS Buckets
AGENT_MAIL_BUCKET="pnkln-agent-mail"
GOVERNANCE_BUCKET="pnkln-aiyoujr-logs"
ARTIFACTS_BUCKET="pnkln-task-artifacts"

# Vertex AI Workbench
INSTANCE_NAME="pnkln-multi-agent"
MACHINE_TYPE="n1-standard-8"  # 8 vCPU, 30GB RAM for multi-agent + Rust compilation
DISK_SIZE="200"  # GB - Rust toolchain + cargo cache

# Service Account
SA_NAME="pnkln-agent-orchestrator"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=0

    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
        missing=1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq not found. Install: apt-get install jq / brew install jq"
        missing=1
    fi

    if [ $missing -eq 1 ]; then
        exit 1
    fi

    log_success "All prerequisites installed"
}

prompt_if_empty() {
    local var_name=$1
    local prompt_text=$2
    local current_value="${!var_name}"

    if [ -z "$current_value" ]; then
        read -p "$prompt_text: " input_value
        eval "$var_name=\"$input_value\""
    fi
}

validate_gcp_project() {
    log_info "Validating GCP project: $PROJECT_ID"

    if ! gcloud projects describe "$PROJECT_ID" &> /dev/null; then
        log_error "Project $PROJECT_ID not found or you lack access"
        exit 1
    fi

    gcloud config set project "$PROJECT_ID"
    log_success "Project validated: $PROJECT_ID"
}

enable_apis() {
    log_info "Enabling required GCP APIs..."

    local apis=(
        "compute.googleapis.com"
        "notebooks.googleapis.com"
        "aiplatform.googleapis.com"
        "storage.googleapis.com"
        "iam.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log_info "  Enabling $api..."
        gcloud services enable "$api" --project="$PROJECT_ID" 2>/dev/null || true
    done

    log_success "APIs enabled"
}

create_gcs_buckets() {
    log_info "Creating GCS buckets..."

    local buckets=("$AGENT_MAIL_BUCKET" "$GOVERNANCE_BUCKET" "$ARTIFACTS_BUCKET")

    for bucket in "${buckets[@]}"; do
        if gsutil ls -b "gs://$bucket" &> /dev/null; then
            log_warn "Bucket gs://$bucket already exists"
        else
            log_info "  Creating gs://$bucket..."
            gsutil mb -p "$PROJECT_ID" -l "$REGION" "gs://$bucket"

            # Set lifecycle for Agent Mail (delete after 90 days)
            if [ "$bucket" == "$AGENT_MAIL_BUCKET" ]; then
                cat > /tmp/lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF
                gsutil lifecycle set /tmp/lifecycle.json "gs://$bucket"
                rm /tmp/lifecycle.json
            fi

            log_success "  Created gs://$bucket"
        fi
    done
}

create_service_account() {
    log_info "Creating service account: $SA_NAME"

    if gcloud iam service-accounts describe "$SA_EMAIL" --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Service account $SA_EMAIL already exists"
    else
        gcloud iam service-accounts create "$SA_NAME" \
            --display-name="PNKLN Agent Orchestrator" \
            --project="$PROJECT_ID"
        log_success "Service account created"
    fi

    log_info "Granting IAM roles..."

    local roles=(
        "roles/storage.objectAdmin"
        "roles/aiplatform.user"
        "roles/notebooks.runner"
    )

    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$SA_EMAIL" \
            --role="$role" \
            --condition=None \
            > /dev/null 2>&1 || true
    done

    # Grant specific bucket permissions
    for bucket in "$AGENT_MAIL_BUCKET" "$GOVERNANCE_BUCKET" "$ARTIFACTS_BUCKET"; do
        gsutil iam ch "serviceAccount:$SA_EMAIL:objectAdmin" "gs://$bucket" 2>/dev/null || true
    done

    log_success "IAM roles configured"
}

create_workbench_instance() {
    log_info "Creating Vertex AI Workbench instance: $INSTANCE_NAME"

    # Check if instance exists
    if gcloud notebooks instances describe "$INSTANCE_NAME" \
        --location="$ZONE" \
        --project="$PROJECT_ID" &> /dev/null; then
        log_warn "Instance $INSTANCE_NAME already exists"
        return
    fi

    log_info "  Provisioning (this takes ~5 minutes)..."

    gcloud notebooks instances create "$INSTANCE_NAME" \
        --location="$ZONE" \
        --machine-type="$MACHINE_TYPE" \
        --boot-disk-size="$DISK_SIZE" \
        --boot-disk-type="PD_SSD" \
        --service-account="$SA_EMAIL" \
        --install-gpu-driver \
        --project="$PROJECT_ID" \
        --metadata="proxy-mode=service_account,terraform=true" \
        --async

    log_info "  Waiting for instance to be ACTIVE..."

    local max_wait=600  # 10 minutes
    local elapsed=0

    while [ $elapsed -lt $max_wait ]; do
        local state=$(gcloud notebooks instances describe "$INSTANCE_NAME" \
            --location="$ZONE" \
            --project="$PROJECT_ID" \
            --format="value(state)" 2>/dev/null || echo "PROVISIONING")

        if [ "$state" == "ACTIVE" ]; then
            log_success "Instance is ACTIVE"
            return
        fi

        echo -n "."
        sleep 10
        elapsed=$((elapsed + 10))
    done

    log_error "Instance failed to become ACTIVE within ${max_wait}s"
    exit 1
}

upload_supporting_docs() {
    log_info "Uploading supporting documents to GCS..."

    local docs_dir="/tmp/pnkln_docs"
    mkdir -p "$docs_dir"

    # Create AGENTS.md
    cat > "$docs_dir/AGENTS.md" <<'EOF'
# PNKLN Multi-Agent Registry

## Active Agents

### WhiteCastle
- **Role**: Backend/API Development (Rust)
- **Specialization**: Async patterns, memory safety, performance optimization
- **Risk Tolerance**: RA-2 (auto-approve standard development)
- **Contact**: Agent Mail (WhiteCastle)

### BrownSnow
- **Role**: DevOps/Infrastructure
- **Specialization**: Cloud automation, CI/CD, hardware coordination
- **Risk Tolerance**: RA-2 (requires peer review for infrastructure changes)
- **Contact**: Agent Mail (BrownSnow)

### OrangeCreek
- **Role**: Frontend/UX
- **Specialization**: Bevy UI integration, accessibility, performance
- **Risk Tolerance**: RA-1 (UI changes low-risk)
- **Contact**: Agent Mail (OrangeCreek)

## Communication Protocol

All agents must:
1. Check Agent Mail on startup
2. Send introduction to `cor_orchestrator`
3. Coordinate task distribution via Agent Mail threads
4. Update PLAN.md inline with progress
5. Run governance validation before task completion

## Escalation Path

RA-1/RA-2 → Self-approve with peer notification
RA-3 → Require 2-agent peer review
RA-4 → Human approval (Erik) required via Agent Mail to `human_approver`
EOF

    # Create AIYOUJR_DOCTRINE.md
    cat > "$docs_dir/AIYOUJR_DOCTRINE.md" <<'EOF'
# AiYouJR Governance Doctrine

## Purpose / Reasons / Brakes (PRB) Framework

Every agent operates under three constraints:

### Purpose (P)
*What you exist to accomplish*

Defines the agent's primary objective and success criteria.

### Reasons (R)
*Why your actions are justified*

Explicit justifications for decisions. All significant actions must have documented reasons.

### Brakes (B)
*What you must never do*

Non-negotiable constraints. Brake violations trigger immediate work stoppage and governance escalation.

## ATP 5-19 Risk Stratification

Based on U.S. Army Techniques Publication 5-19 (Risk Management):

### RA-1: Extremely Low Risk
- **Examples**: Documentation updates, simple refactors, UI polish
- **Coverage**: 95%+ test coverage
- **Approval**: Auto-approve with peer notification
- **Human Gate**: No

### RA-2: Low Risk
- **Examples**: New features, API endpoints, standard development
- **Coverage**: 98%+ test coverage
- **Approval**: Auto-approve with 1 peer review
- **Human Gate**: No

### RA-3: Medium Risk
- **Examples**: Data schemas, auth flows, performance-critical paths
- **Coverage**: 98%+ test coverage
- **Approval**: Requires 2-agent peer review
- **Human Gate**: No

### RA-4: High Risk
- **Examples**: Production deployments, security, compliance, infrastructure
- **Coverage**: 99%+ test coverage
- **Approval**: Requires 3-agent peer review + human approval
- **Human Gate**: Yes (Erik)

## Judge #6: Code Validation

All code completions must pass Judge #6 validation:

1. **Security**: No vulnerabilities (SQL injection, XSS, auth bypass)
2. **Coverage**: Meets RA-level threshold (95-99%)
3. **Edge Cases**: Critical paths have defensive checks
4. **Documentation**: Functions have clear docstrings
5. **Performance**: No anti-patterns (N+1 queries, blocking I/O)

Judge #6 uses Gemini 2.0 Flash for automated analysis.

## Brake Activation Protocol

If an agent detects a brake violation:

1. **STOP** work on the task immediately
2. Call `governance.enforce_brake()` to log violation
3. Send Agent Mail to `cor_orchestrator` with details
4. Wait for human intervention before resuming

Brake violations are logged to `gs://pnkln-aiyoujr-logs/brakes/` for audit trail.

## Context Management

At 80% context utilization:

1. Create summary of work completed
2. Save to GCS artifacts bucket
3. Send summary via Agent Mail to `cor_orchestrator`
4. Reset context and resume from last checkpoint

This prevents context exhaustion and maintains continuity.
EOF

    # Create PLAN_TEMPLATE.md (Bevy integration specific)
    cat > "$docs_dir/PLAN_TO_INTEGRATE_BEVY_ENGINE.md" <<'EOF'
# Bevy Engine Integration Plan

## Objective
Integrate Bevy game engine with rust_scriptbots for visual rendering and UI components.

## Prerequisites
- [x] Rust toolchain installed (rustc 1.75+, cargo)
- [x] Bevy dependencies (see Cargo.toml)
- [ ] GPU driver validation on Vertex AI Workbench
- [ ] Agent Mail system initialized

## Task Breakdown

### RA-2: Core Integration
**Owner**: WhiteCastle
**Status**: Not Started
**Progress**: 0%

Tasks:
- [ ] Add Bevy to Cargo.toml with feature flags
- [ ] Create `bevy_integration` module structure
- [ ] Implement basic window + render loop
- [ ] Wire scriptbots events → Bevy ECS
- [ ] Write integration tests (target: 98% coverage)

**Checkpoints**:
- 25%: Cargo.toml updated, module scaffolding
- 50%: Basic window renders, ECS initialized
- 75%: Event pipeline connected
- 100%: Tests pass, Judge #6 validation

---

### RA-1: UI Components
**Owner**: OrangeCreek
**Status**: Not Started
**Progress**: 0%

Tasks:
- [ ] Design Bevy UI hierarchy (egui plugin)
- [ ] Implement control panel for scriptbot execution
- [ ] Add visual feedback for agent actions
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Performance profiling (target: 60 FPS)

**Checkpoints**:
- 25%: UI mockups approved
- 50%: Control panel functional
- 75%: Visual feedback implemented
- 100%: Accessibility + performance validated

---

### RA-2: CI/CD Pipeline
**Owner**: BrownSnow
**Status**: Not Started
**Progress**: 0%

Tasks:
- [ ] Update GitHub Actions for Bevy build
- [ ] Add GPU driver checks to CI
- [ ] Configure cargo-tarpaulin for coverage
- [ ] Set up artifact storage for builds
- [ ] Document deployment process

**Checkpoints**:
- 25%: GitHub Actions updated
- 50%: GPU validation working
- 75%: Coverage reporting automated
- 100%: Full pipeline operational

---

## Dependencies

```
bevy_integration ← bevy_ui ← ci_cd_pipeline
```

Critical path: Core Integration must complete before UI Components.

## Risk Assessment

- **RA-2** (Core Integration): GPU dependencies might not work on Vertex
  - *Mitigation*: Validate GPU driver on instance provisioning

- **RA-2** (CI/CD): Bevy compilation time may exceed CI limits
  - *Mitigation*: Use sccache for cargo caching

## Success Criteria

- [ ] All tests pass with 98%+ coverage
- [ ] Bevy window renders on Vertex AI Workbench
- [ ] Agent Mail coordination logged throughout
- [ ] Judge #6 validates all code completions
- [ ] No brake violations

## Timeline

- **Day 1**: Environment setup + Core Integration (0-50%)
- **Day 2**: Core Integration (50-100%) + UI Components start
- **Day 3**: UI Components + CI/CD Pipeline
- **Day 4**: Integration testing + Judge #6 validation
- **Day 5**: Buffer for brake resolutions / refactoring

## Agent Coordination

All agents:
1. Read this plan on startup
2. Assess task risks via `governance.assess_task_risk()`
3. Coordinate via Agent Mail thread: "Bevy Integration Coordination"
4. Update progress inline in this document
5. Send checkpoint notifications at 25/50/75/100%

**Thread starter**: WhiteCastle initiates coordination after agent introductions.
EOF

    # Upload to artifacts bucket
    log_info "  Uploading to gs://$ARTIFACTS_BUCKET/docs/"
    gsutil -m cp "$docs_dir/"*.md "gs://$ARTIFACTS_BUCKET/docs/"

    log_success "Supporting documents uploaded"

    rm -rf "$docs_dir"
}

generate_startup_script() {
    log_info "Generating instance startup script..."

    cat > /tmp/startup.sh <<'STARTUP_EOF'
#!/bin/bash
# PNKLN Vertex AI Workbench - Instance Initialization

set -euo pipefail

JUPYTER_HOME="/home/jupyter"
RUST_SCRIPTBOTS_DIR="$JUPYTER_HOME/rust_scriptbots"
NOTEBOOKS_DIR="$JUPYTER_HOME/notebooks"

echo "[INFO] Installing Rust toolchain..."
if ! command -v rustc &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

rustc --version
cargo --version

echo "[INFO] Installing Rust tools..."
cargo install cargo-tarpaulin --locked  # Coverage
cargo install sccache --locked           # Build cache
cargo install cargo-watch --locked       # Auto-rebuild

echo "[INFO] Configuring cargo to use sccache..."
export RUSTC_WRAPPER=sccache
echo 'export RUSTC_WRAPPER=sccache' >> "$HOME/.bashrc"

echo "[INFO] Installing Python dependencies..."
pip install -q pyautogen google-cloud-storage google-cloud-aiplatform vertexai

echo "[INFO] Creating project directories..."
mkdir -p "$NOTEBOOKS_DIR"
mkdir -p "$RUST_SCRIPTBOTS_DIR"

echo "[INFO] Downloading supporting documents from GCS..."
gsutil -m cp "gs://pnkln-task-artifacts/docs/*.md" "$JUPYTER_HOME/" || true

echo "[INFO] Cloning rust_scriptbots repository..."
if [ ! -d "$RUST_SCRIPTBOTS_DIR/.git" ]; then
    # This will be set during deployment if REPO_URL is provided
    # git clone "$REPO_URL" "$RUST_SCRIPTBOTS_DIR"
    echo "[WARN] REPO_URL not set - skipping git clone"
    echo "[WARN] Manually clone your repo or upload to instance"
fi

echo "[INFO] Downloading COR_MULTI_AGENT_TEMPLATE.ipynb..."
gsutil cp "gs://pnkln-task-artifacts/notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb" "$NOTEBOOKS_DIR/" || true

echo "[INFO] Setting permissions..."
chown -R jupyter:jupyter "$JUPYTER_HOME"

echo "[SUCCESS] Initialization complete!"
STARTUP_EOF

    # Upload startup script to artifacts bucket
    gsutil cp /tmp/startup.sh "gs://$ARTIFACTS_BUCKET/scripts/startup.sh"
    rm /tmp/startup.sh

    log_success "Startup script generated"
}

display_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "  PNKLN CORE STACK™ - DEPLOYMENT COMPLETE"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Project:           $PROJECT_ID"
    echo "Region:            $REGION"
    echo "Zone:              $ZONE"
    echo ""
    echo "GCS Buckets:"
    echo "  • gs://$AGENT_MAIL_BUCKET       (Agent Mail / NS)"
    echo "  • gs://$GOVERNANCE_BUCKET     (AiYouJR Logs)"
    echo "  • gs://$ARTIFACTS_BUCKET   (Task Artifacts)"
    echo ""
    echo "Service Account:   $SA_EMAIL"
    echo ""
    echo "Workbench Instance:"
    echo "  • Name:          $INSTANCE_NAME"
    echo "  • Zone:          $ZONE"
    echo "  • Machine:       $MACHINE_TYPE"
    echo "  • Disk:          ${DISK_SIZE}GB SSD"
    echo ""
    echo "Next Steps:"
    echo "  1. Open Workbench UI:"
    echo "     https://console.cloud.google.com/vertex-ai/workbench/list/instances?project=$PROJECT_ID"
    echo ""
    echo "  2. Click 'OPEN JUPYTERLAB' on $INSTANCE_NAME"
    echo ""
    echo "  3. Upload COR_MULTI_AGENT_TEMPLATE.ipynb to ~/notebooks/"
    echo "     (Or run: gsutil cp gs://$ARTIFACTS_BUCKET/notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb ~/notebooks/)"
    echo ""
    echo "  4. Edit Cell 2: Set PROJECT_ID = \"$PROJECT_ID\""
    echo ""
    echo "  5. Clone rust_scriptbots:"
    echo "     cd /home/jupyter"
    echo "     git clone <YOUR_REPO_URL> rust_scriptbots"
    echo ""
    echo "  6. Run Cells 1-9 to initialize agents"
    echo ""
    echo "  7. Execute Cell 10 to start coordination"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════════════╗"
    echo "║  PNKLN CORE STACK™ - VERTEX AI WORKBENCH DEPLOYMENT                      ║"
    echo "║  Bootstrap from $0K → Multi-Agent Coordination                            ║"
    echo "╚═══════════════════════════════════════════════════════════════════════════╝"
    echo ""

    check_prerequisites

    # Prompt for missing configuration
    prompt_if_empty "PROJECT_ID" "Enter GCP Project ID"
    prompt_if_empty "REPO_URL" "Enter rust_scriptbots Git URL (or press Enter to skip)"

    # Update SA email after PROJECT_ID is set
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

    validate_gcp_project
    enable_apis
    create_gcs_buckets
    create_service_account
    upload_supporting_docs
    generate_startup_script

    # Upload notebook template
    log_info "Uploading COR_MULTI_AGENT_TEMPLATE.ipynb..."
    if [ -f "./COR_MULTI_AGENT_TEMPLATE.ipynb" ]; then
        gsutil cp ./COR_MULTI_AGENT_TEMPLATE.ipynb "gs://$ARTIFACTS_BUCKET/notebooks/"
        log_success "Notebook uploaded"
    else
        log_warn "COR_MULTI_AGENT_TEMPLATE.ipynb not found in current directory"
        log_warn "Upload manually after instance is ready"
    fi

    create_workbench_instance

    display_summary
}

# Trap errors
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Execute
main "$@"
