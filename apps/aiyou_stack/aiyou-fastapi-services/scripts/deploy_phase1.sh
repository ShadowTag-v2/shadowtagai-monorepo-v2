#!/bin/bash
#
# One-Click Phase 1 Deployment Script
# Deploys complete PNKLN Core Stack Phase 1 (Ingestion + Orchestrator)
#
# Prerequisites:
#   - GKE cluster created (run setup_gke_cluster.sh first)
#   - Secrets configured (run configure_secrets.sh first)
#   - Training data ready in datasets/merged/
#
# Usage: ./scripts/deploy_phase1.sh [--skip-training] [--dry-run]
#

set -e

# Parse arguments
SKIP_TRAINING=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-training)
            SKIP_TRAINING=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-training] [--dry-run]"
            exit 1
            ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██████╗ ███╗   ██╗██╗  ██╗██╗     ███╗   ██╗                     ║
║   ██╔══██╗████╗  ██║██║ ██╔╝██║     ████╗  ██║                     ║
║   ██████╔╝██╔██╗ ██║█████╔╝ ██║     ██╔██╗ ██║                     ║
║   ██╔═══╝ ██║╚██╗██║██╔═██╗ ██║     ██║╚██╗██║                     ║
║   ██║     ██║ ╚████║██║  ██╗███████╗██║ ╚████║                     ║
║   ╚═╝     ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝                     ║
║                                                                      ║
║              CORE STACK™ - PHASE 1 DEPLOYMENT                       ║
║       Integrated Intelligence Pipeline + AI Orchestrator            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}▸ DRY RUN MODE - No changes will be made${NC}\n"
fi

if [ "$SKIP_TRAINING" = true ]; then
    echo -e "${YELLOW}▸ SKIPPING TRAINING - Using pre-trained model${NC}\n"
fi

# Function to run command or show in dry-run
run_cmd() {
    local cmd=$1
    local description=$2

    echo -e "${CYAN}▸ $description${NC}"

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}  [DRY-RUN] Would execute: $cmd${NC}"
    else
        if eval "$cmd"; then
            echo -e "${GREEN}  ✓ Success${NC}\n"
        else
            echo -e "${RED}  ✗ Failed${NC}\n"
            return 1
        fi
    fi
}

# Pre-flight checks
echo -e "${BOLD}${CYAN}═══ PRE-FLIGHT CHECKS ═══${NC}\n"

echo -e "${CYAN}Checking kubectl access...${NC}"
if kubectl cluster-info &>/dev/null; then
    echo -e "${GREEN}✓ kubectl configured${NC}\n"
else
    echo -e "${RED}✗ kubectl not configured or cluster not accessible${NC}"
    echo "Run: ./scripts/setup_gke_cluster.sh first"
    exit 1
fi

echo -e "${CYAN}Checking namespaces...${NC}"
for ns in ingestion orchestrator storage; do
    if kubectl get namespace "$ns" &>/dev/null; then
        echo -e "${GREEN}✓ Namespace $ns exists${NC}"
    else
        echo -e "${RED}✗ Namespace $ns missing${NC}"
        echo "Run: ./scripts/setup_gke_cluster.sh first"
        exit 1
    fi
done
echo

echo -e "${CYAN}Checking secrets...${NC}"
for secret in postgres-secret:storage crawler-secrets:ingestion llm-secrets:orchestrator; do
    name="${secret%%:*}"
    ns="${secret##*:}"
    if kubectl get secret "$name" -n "$ns" &>/dev/null; then
        echo -e "${GREEN}✓ Secret $name exists in $ns${NC}"
    else
        echo -e "${YELLOW}⚠ Secret $name missing in $ns${NC}"
        echo "  Run: ./scripts/configure_secrets.sh"
    fi
done
echo

echo -e "${GREEN}✓ Pre-flight checks complete${NC}\n"

# Deployment Timeline
echo -e "${BOLD}${CYAN}═══ DEPLOYMENT TIMELINE ═══${NC}\n"
echo "Phase 1 deployment consists of 3 major stages:"
echo ""
echo "  1. Storage Layer (PostgreSQL)         ~5 minutes"
echo "  2. Ingestion Layer (GKE CronJob)      ~10 minutes"
if [ "$SKIP_TRAINING" = false ]; then
echo "  3. Model Training (Vertex AI)         ~2-4 hours"
echo "  4. Orchestrator Layer (API Service)   ~10 minutes"
else
echo "  3. Orchestrator Layer (API Service)   ~10 minutes"
fi
echo ""
echo "  Total estimated time: $([ "$SKIP_TRAINING" = false ] && echo "3-5 hours" || echo "25-30 minutes")"
echo ""

if [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}Press ENTER to continue or Ctrl+C to cancel...${NC}"
    read
fi
echo

# ============================================================================
# STAGE 1: STORAGE LAYER
# ============================================================================

echo -e "${BOLD}${CYAN}═══ STAGE 1: STORAGE LAYER ═══${NC}\n"

if [ -f "k8s/storage/postgresql.yaml" ]; then
    run_cmd "kubectl apply -f k8s/storage/postgresql.yaml" "Deploying PostgreSQL"

    if [ "$DRY_RUN" = false ]; then
        echo -e "${CYAN}Waiting for PostgreSQL to be ready (max 5 minutes)...${NC}"
        kubectl wait --for=condition=ready pod -l app=postgres -n storage --timeout=300s
        echo -e "${GREEN}✓ PostgreSQL is ready${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ k8s/storage/postgresql.yaml not found, skipping${NC}\n"
fi

# Initialize database schema
if [ -f "db/schema.sql" ] && [ "$DRY_RUN" = false ]; then
    echo -e "${CYAN}▸ Initializing database schema${NC}"

    POD_NAME=$(kubectl get pod -n storage -l app=postgres -o jsonpath="{.items[0].metadata.name}")

    if [ -n "$POD_NAME" ]; then
        kubectl cp db/schema.sql storage/"$POD_NAME":/tmp/schema.sql
        kubectl exec -n storage "$POD_NAME" -- psql -U "$DB_USER" -d pnkln_intelligence -f /tmp/schema.sql
        echo -e "${GREEN}✓ Database schema initialized${NC}\n"
    else
        echo -e "${YELLOW}⚠ PostgreSQL pod not found, schema initialization skipped${NC}\n"
    fi
fi

# ============================================================================
# STAGE 2: INGESTION LAYER
# ============================================================================

echo -e "${BOLD}${CYAN}═══ STAGE 2: INGESTION LAYER ═══${NC}\n"

if [ -d "k8s/ingestion" ]; then
    run_cmd "kubectl apply -f k8s/ingestion/" "Deploying ingestion CronJob and ConfigMap"

    echo -e "${CYAN}▸ Triggering test ingestion run${NC}"
    if [ "$DRY_RUN" = false ]; then
        kubectl create job --from=cronjob/ingestion-crawler test-ingestion-$(date +%s) -n ingestion
        echo -e "${GREEN}✓ Test job created${NC}"
        echo -e "${YELLOW}  Note: Ingestion takes ~45 minutes. Check logs with:${NC}"
        echo -e "${YELLOW}  kubectl logs -f job/test-ingestion-XXX -n ingestion${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ k8s/ingestion/ directory not found, skipping${NC}\n"
fi

# ============================================================================
# STAGE 3: MODEL TRAINING (Optional)
# ============================================================================

if [ "$SKIP_TRAINING" = false ]; then
    echo -e "${BOLD}${CYAN}═══ STAGE 3: MODEL TRAINING ═══${NC}\n"

    if [ -f "training/vertex_ai_pipeline.py" ]; then
        # Check if datasets exist
        if [ -f "datasets/merged/single_turn_examples.jsonl" ]; then
            echo -e "${CYAN}▸ Submitting Vertex AI training job${NC}"

            if [ "$DRY_RUN" = false ]; then
                python training/vertex_ai_pipeline.py \
                    --single_turn_data=datasets/merged/single_turn_examples.jsonl \
                    --multi_turn_data=datasets/merged/multi_turn_trajectories.jsonl \
                    --model_name=gemini-codeact-v1 \
                    --num_epochs=3 \
                    --auto_deploy=true

                echo -e "${GREEN}✓ Training job submitted${NC}"
                echo -e "${YELLOW}  Note: Training takes 2-4 hours. Monitor with:${NC}"
                echo -e "${YELLOW}  gcloud ai custom-jobs stream-logs \$JOB_ID${NC}\n"
            else
                echo -e "${YELLOW}  [DRY-RUN] Would submit training job${NC}\n"
            fi
        else
            echo -e "${YELLOW}⚠ Training dataset not found${NC}"
            echo -e "${YELLOW}  Run: python training/dataset_generator.py first${NC}\n"
        fi
    else
        echo -e "${YELLOW}⚠ training/vertex_ai_pipeline.py not found, skipping${NC}\n"
    fi
fi

# ============================================================================
# STAGE 4: ORCHESTRATOR LAYER
# ============================================================================

echo -e "${BOLD}${CYAN}═══ STAGE 4: ORCHESTRATOR LAYER ═══${NC}\n"

if [ "$SKIP_TRAINING" = false ] && [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}⚠ Waiting for training to complete before deploying orchestrator${NC}"
    echo -e "${YELLOW}  This deployment will pause here. Resume after training completes.${NC}\n"

    echo -e "${YELLOW}Press ENTER when training is complete, or Ctrl+C to exit...${NC}"
    read
fi

# Build and push orchestrator image
if [ -d "orchestrator" ] && [ -f "orchestrator/Dockerfile" ]; then
    PROJECT_ID=$(gcloud config get-value project)
    IMAGE="gcr.io/$PROJECT_ID/codeact-orchestrator:latest"

    run_cmd "docker build -t $IMAGE orchestrator/" "Building orchestrator Docker image"

    if [ "$DRY_RUN" = false ]; then
        echo -e "${CYAN}▸ Pushing image to GCR${NC}"
        docker push "$IMAGE"
        echo -e "${GREEN}✓ Image pushed${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ orchestrator/ directory not found, skipping image build${NC}\n"
fi

# Deploy orchestrator
if [ -f "k8s/orchestrator/deployment.yaml" ]; then
    run_cmd "kubectl apply -f k8s/orchestrator/deployment.yaml" "Deploying orchestrator service"

    if [ "$DRY_RUN" = false ]; then
        echo -e "${CYAN}Waiting for orchestrator to be ready (max 3 minutes)...${NC}"
        kubectl wait --for=condition=ready pod -l app=codeact-orchestrator -n orchestrator --timeout=180s
        echo -e "${GREEN}✓ Orchestrator is ready${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ k8s/orchestrator/deployment.yaml not found, skipping${NC}\n"
fi

# ============================================================================
# STAGE 5: BRIEFING GENERATOR
# ============================================================================

echo -e "${BOLD}${CYAN}═══ STAGE 5: BRIEFING GENERATOR ═══${NC}\n"

if [ -f "k8s/briefing/cronjob.yaml" ]; then
    run_cmd "kubectl apply -f k8s/briefing/cronjob.yaml" "Deploying AM Briefing CronJob"

    echo -e "${CYAN}▸ Triggering test briefing generation${NC}"
    if [ "$DRY_RUN" = false ]; then
        kubectl create job --from=cronjob/am-briefing-generator test-briefing-$(date +%s) -n orchestrator
        echo -e "${GREEN}✓ Test job created${NC}\n"

        echo -e "${YELLOW}  Check briefing output with:${NC}"
        echo -e "${YELLOW}  kubectl logs -f job/test-briefing-XXX -n orchestrator${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ k8s/briefing/cronjob.yaml not found, skipping${NC}\n"
fi

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================

echo -e "${BOLD}${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║                 ✓ PHASE 1 DEPLOYMENT COMPLETE                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

if [ "$DRY_RUN" = false ]; then
    echo -e "${CYAN}Deployment Summary:${NC}\n"

    echo -e "${GREEN}Storage Layer:${NC}"
    kubectl get pods -n storage

    echo -e "\n${GREEN}Ingestion Layer:${NC}"
    kubectl get cronjobs -n ingestion
    kubectl get jobs -n ingestion | head -5

    echo -e "\n${GREEN}Orchestrator Layer:${NC}"
    kubectl get deployments -n orchestrator
    kubectl get pods -n orchestrator

    echo -e "\n${GREEN}Briefing Generator:${NC}"
    kubectl get cronjobs -n orchestrator

    echo -e "\n${CYAN}Scheduled Jobs:${NC}"
    echo "  • Ingestion: Daily at 2:00 AM (nightly data collection)"
    echo "  • Briefing:  Daily at 6:00 AM (morning intelligence summary)"

    echo -e "\n${CYAN}Useful Commands:${NC}"
    echo "  • View ingestion logs:    kubectl logs -f -l app=ingestion-crawler -n ingestion"
    echo "  • View orchestrator logs: kubectl logs -f -l app=codeact-orchestrator -n orchestrator"
    echo "  • Check database:         kubectl exec -it postgres-0 -n storage -- psql -U \$DB_USER -d pnkln_intelligence"
    echo "  • Manual ingestion:       kubectl create job --from=cronjob/ingestion-crawler manual-$(date +%s) -n ingestion"
    echo "  • Manual briefing:        kubectl create job --from=cronjob/am-briefing-generator manual-$(date +%s) -n orchestrator"

    echo -e "\n${CYAN}Next Steps:${NC}"
    echo "  1. Monitor first ingestion run (wait ~45 min)"
    echo "  2. Verify data in PostgreSQL"
    echo "  3. Test orchestrator API"
    echo "  4. Review first AM Briefing (next morning at 6 AM)"
    echo "  5. Proceed to Phase 2 validation"

    echo -e "\n${GREEN}For detailed Phase 1 checklist, see: PHASE1_CHECKLIST.md${NC}\n"
else
    echo -e "${YELLOW}DRY RUN COMPLETE - No changes were made${NC}"
    echo -e "${YELLOW}Run without --dry-run to perform actual deployment${NC}\n"
fi
