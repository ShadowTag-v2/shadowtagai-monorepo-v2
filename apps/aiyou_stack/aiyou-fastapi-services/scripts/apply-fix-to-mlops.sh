#!/bin/bash
set -e

##############################################################################
# Apply Ingestion Workflow Fix to MLOps Repository
#
# This script helps apply the curl 404 fix to the mlops repository.
# It can be run from the ShadowTag-v2-fastapi-services repository.
#
# Usage:
#   ./scripts/apply-fix-to-mlops.sh [mlops-repo-path]
#
# If no path is provided, it will clone the mlops repo to ../mlops
##############################################################################

MLOPS_REPO_URL="https://github.com/ehanc69/mlops.git"
MLOPS_REPO_PATH="${1:-../mlops}"
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "============================================================================"
echo "Applying Ingestion Workflow Fix to MLOps Repository"
echo "============================================================================"
echo ""

# Check if we're in the right repository
if [ ! -f "$PROJECT_ROOT/.github/workflows/ingest.yml" ]; then
    echo "❌ Error: This script must be run from the ShadowTag-v2-fastapi-services repository"
    echo "   Expected to find: .github/workflows/ingest.yml"
    exit 1
fi

echo "✓ Source repository verified: ShadowTag-v2-fastapi-services"
echo ""

# Clone or use existing mlops repository
if [ ! -d "$MLOPS_REPO_PATH" ]; then
    echo "📥 Cloning mlops repository to: $MLOPS_REPO_PATH"
    git clone "$MLOPS_REPO_URL" "$MLOPS_REPO_PATH"
    echo "✓ Repository cloned successfully"
else
    echo "✓ Using existing mlops repository at: $MLOPS_REPO_PATH"
    echo ""
    echo "📥 Fetching latest changes..."
    cd "$MLOPS_REPO_PATH"
    git fetch origin
    cd "$CURRENT_DIR"
fi

echo ""
echo "============================================================================"
echo "Creating Fix Branch in MLOps Repository"
echo "============================================================================"
echo ""

cd "$MLOPS_REPO_PATH"

# Create a new branch for the fix
BRANCH_NAME="claude/fix-ingestion-curl-404-$(date +%Y%m%d-%H%M%S)"
echo "🌿 Creating branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

echo "✓ Branch created successfully"
echo ""

# Check if .github/workflows directory exists
if [ ! -d ".github/workflows" ]; then
    echo "📁 Creating .github/workflows directory..."
    mkdir -p .github/workflows
fi

# Copy the fixed workflow file
echo "============================================================================"
echo "Copying Fixed Workflow File"
echo "============================================================================"
echo ""

SOURCE_WORKFLOW="$PROJECT_ROOT/.github/workflows/ingest.yml"
TARGET_WORKFLOW=".github/workflows/ingest.yml"

if [ -f "$TARGET_WORKFLOW" ]; then
    echo "⚠️  Existing workflow file found: $TARGET_WORKFLOW"
    echo "📋 Creating backup: ${TARGET_WORKFLOW}.backup"
    cp "$TARGET_WORKFLOW" "${TARGET_WORKFLOW}.backup"
fi

echo "📄 Copying fixed workflow from ShadowTag-v2-fastapi-services..."
cp "$SOURCE_WORKFLOW" "$TARGET_WORKFLOW"

echo "✓ Workflow file copied successfully"
echo ""

# Show the key differences
echo "============================================================================"
echo "Key Changes in the Fixed Workflow"
echo "============================================================================"
echo ""
echo "✅ Correct URL format (without refs/heads/):"
echo "   https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
echo ""
echo "✅ Added retry logic with exponential backoff (2s, 4s, 8s, 16s)"
echo "✅ Added file validation (non-empty check)"
echo "✅ Added comprehensive error messages"
echo "✅ Added debugging output"
echo ""

# Check if there are any other files that might need updating
echo "============================================================================"
echo "Searching for Other Files with Incorrect URLs"
echo "============================================================================"
echo ""

echo "🔍 Searching for 'refs/heads' in workflow files..."
if grep -r "refs/heads" .github/workflows/ 2>/dev/null; then
    echo ""
    echo "⚠️  Found additional occurrences of 'refs/heads' in workflow files"
    echo "   These may need manual review and fixing"
else
    echo "✓ No other occurrences of 'refs/heads' found in workflow files"
fi

echo ""
echo "🔍 Searching for raw.githubusercontent.com URLs..."
RAW_URL_COUNT=$(grep -r "raw.githubusercontent.com" . --include="*.yml" --include="*.yaml" 2>/dev/null | wc -l)
echo "   Found $RAW_URL_COUNT occurrence(s) of raw.githubusercontent.com URLs"

echo ""

# Stage and commit the changes
echo "============================================================================"
echo "Committing Changes"
echo "============================================================================"
echo ""

git add .github/workflows/ingest.yml

if git diff --staged --quiet; then
    echo "⚠️  No changes to commit (workflow file may be identical)"
else
    echo "📝 Creating commit..."
    git commit -m "$(cat <<'EOF'
Fix ingestion workflow curl 404 error with correct GitHub raw URL format

Problem:
- Workflow was using incorrect GitHub raw URL format with 'refs/heads/'
- Caused curl to return HTTP 404 error (exit code 22)
- Format: https://raw.githubusercontent.com/owner/repo/refs/heads/main/path
  (INCORRECT)

Solution:
- Updated .github/workflows/ingest.yml with correct URL format
- Correct format: https://raw.githubusercontent.com/owner/repo/main/path
- Added exponential backoff retry logic (4 retries: 2s, 4s, 8s, 16s)
- Implemented comprehensive error handling and debugging
- Added file validation to ensure downloads are non-empty

Key improvements:
- Proper GitHub raw URL construction (no refs/heads/)
- Retry logic for network failures
- Detailed error messages with troubleshooting guidance
- File validation after download
- Workflow summary for GitHub Actions UI

Files changed:
- .github/workflows/ingest.yml: Fixed ingestion workflow

Resolves: curl 404 error in ingestion workflow
Applied from: ehanc69/ShadowTag-v2-fastapi-services fix
EOF
)"

    echo "✓ Changes committed successfully"
fi

echo ""
echo "============================================================================"
echo "Next Steps"
echo "============================================================================"
echo ""
echo "The fix has been applied to the mlops repository!"
echo ""
echo "Branch: $BRANCH_NAME"
echo "Location: $MLOPS_REPO_PATH"
echo ""
echo "To complete the deployment:"
echo ""
echo "1. Review the changes:"
echo "   cd $MLOPS_REPO_PATH"
echo "   git diff main...$BRANCH_NAME"
echo ""
echo "2. Push the branch:"
echo "   git push -u origin $BRANCH_NAME"
echo ""
echo "3. Create a pull request on GitHub:"
echo "   https://github.com/ehanc69/mlops/compare/$BRANCH_NAME"
echo ""
echo "4. After merging, test the workflow:"
echo "   - Go to Actions → Ingestion (hourly) → Run workflow"
echo "   - Monitor for successful completion"
echo ""
echo "============================================================================"

cd "$CURRENT_DIR"
