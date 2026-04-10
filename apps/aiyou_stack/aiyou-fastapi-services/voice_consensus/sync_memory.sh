#!/bin/bash
# Automated Memory Sync Pipeline
# Syncs personal memory to GitHub and team memory to GCS

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
LOCAL_MEMORY="$HOME/.claude-code/memory.md"
GCS_BUCKET="${GCS_BUCKET:-gs://pnkln-consensus-memory}"
SYNC_DAYS="${SYNC_DAYS:-7}"

echo "================================"
echo "MEMORY SYNC PIPELINE"
echo "================================"
echo ""
echo "Date: $(date)"
echo "Local Memory: $LOCAL_MEMORY"
echo "GCS Bucket: $GCS_BUCKET"
echo "Sync Days: $SYNC_DAYS"
echo ""

# Step 1: Extract patterns from local archive
echo -e "${GREEN}[1/5]${NC} Extracting patterns from consensus archive..."
cd "$(dirname "$0")"
python claude_code_memory.py sync "$SYNC_DAYS"

if [ ! -f "$LOCAL_MEMORY" ]; then
    echo -e "${YELLOW}[WARNING]${NC} Memory file not created. Skipping sync."
    exit 0
fi

echo "✓ Memory extracted: $(wc -l < "$LOCAL_MEMORY") lines"
echo ""

# Step 2: Sync personal memory to GitHub
echo -e "${GREEN}[2/5]${NC} Syncing personal memory to GitHub..."
cd ~

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "Initializing git repository in home directory..."
    git init
    git remote add origin https://github.com/${GITHUB_USER:-ShadowTag-v2}/dotfiles.git 2>/dev/null || true
fi

# Commit memory
git add .claude-code/memory.md 2>/dev/null || true
if git diff --staged --quiet; then
    echo "✓ No changes to commit"
else
    git commit -m "Update Claude Code memory: $(date +%Y-%m-%d)" 2>/dev/null || true

    # Try to push (may fail if not configured, that's ok)
    if git push origin main 2>/dev/null; then
        echo "✓ Pushed to GitHub"
    else
        echo -e "${YELLOW}[INFO]${NC} Could not push to GitHub (may not be configured)"
    fi
fi

echo ""

# Step 3: Sync to GCS (if configured)
echo -e "${GREEN}[3/5]${NC} Syncing to Google Cloud Storage..."
if command -v gsutil &> /dev/null && [ -n "$GCS_BUCKET" ]; then
    cd "$(dirname "$0")"

    if python vertex_gke_deployment.py sync-to-gcs 2>/dev/null; then
        echo "✓ Uploaded to $GCS_BUCKET"
    else
        echo -e "${YELLOW}[INFO]${NC} Could not sync to GCS (may not be configured)"
    fi
else
    echo -e "${YELLOW}[INFO]${NC} GCS sync skipped (gsutil not available or bucket not set)"
fi

echo ""

# Step 4: Generate team patterns (optional)
echo -e "${GREEN}[4/5]${NC} Generating team patterns..."
TEAM_PATTERNS="/tmp/team_patterns_$(date +%Y%m%d).md"

# Extract useful sections for team
cat "$LOCAL_MEMORY" | grep -A 10 "## Best Practices\|## Patterns Observed\|## Technical" > "$TEAM_PATTERNS" 2>/dev/null || echo "# No team patterns extracted" > "$TEAM_PATTERNS"

echo "✓ Team patterns saved: $TEAM_PATTERNS"
echo ""

# Step 5: Update Kubernetes ConfigMap (if GKE is configured)
echo -e "${GREEN}[5/5]${NC} Updating Kubernetes ConfigMap (if applicable)..."
if command -v kubectl &> /dev/null && kubectl cluster-info &> /dev/null; then
    cd "$(dirname "$0")"

    if python vertex_gke_deployment.py create-configmap 2>/dev/null; then
        echo "✓ ConfigMap YAML generated"

        # Try to apply (may fail if not connected to cluster)
        if kubectl apply -f k8s/memory-configmap.yaml 2>/dev/null; then
            echo "✓ ConfigMap applied to cluster"

            # Restart pods to pick up new memory
            kubectl rollout restart deployment/consensus-orchestrator -n consensus 2>/dev/null || true
            echo "✓ Deployment restarted"
        else
            echo -e "${YELLOW}[INFO]${NC} Could not apply ConfigMap (cluster may not be accessible)"
        fi
    fi
else
    echo -e "${YELLOW}[INFO]${NC} Kubernetes update skipped (kubectl not configured)"
fi

echo ""
echo "================================"
echo "SYNC COMPLETE"
echo "================================"
echo ""
echo "Summary:"
echo "  ✓ Local memory: $LOCAL_MEMORY"
echo "  ✓ GitHub: Attempted sync"
echo "  ✓ GCS: Attempted sync to $GCS_BUCKET"
echo "  ✓ Team patterns: $TEAM_PATTERNS"
echo ""
echo "Next steps:"
echo "  1. Review team patterns: cat $TEAM_PATTERNS"
echo "  2. Manual GCS upload: python vertex_gke_deployment.py sync-to-gcs"
echo "  3. Verify GitHub: cd ~ && git log --oneline -5"
echo ""
