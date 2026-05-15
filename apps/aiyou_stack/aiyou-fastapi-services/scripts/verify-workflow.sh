#!/bin/bash
set -e

##############################################################################
# Verify Ingestion Workflow Configuration
#
# This script verifies that the ingestion workflow is correctly configured
# and tests the curl commands locally before deploying.
#
# Usage:
#   ./scripts/verify-workflow.sh [repository-path]
#
# If no path is provided, it will verify the current repository.
##############################################################################

REPO_PATH="${1:-.}"
WORKFLOW_FILE="$REPO_PATH/.github/workflows/ingest.yml"

echo "============================================================================"
echo "Ingestion Workflow Verification"
echo "============================================================================"
echo ""

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "❌ Error: Workflow file not found: $WORKFLOW_FILE"
    exit 1
fi

echo "✓ Workflow file found: $WORKFLOW_FILE"
echo ""

# Extract environment variables from workflow
echo "============================================================================"
echo "Extracting Configuration from Workflow"
echo "============================================================================"
echo ""

POLICY_REPO=$(grep "POLICY_REPO:" "$WORKFLOW_FILE" | awk '{print $2}' | head -1)
POLICY_BRANCH=$(grep "POLICY_BRANCH:" "$WORKFLOW_FILE" | awk '{print $2}' | head -1)
POLICY_FILE_PATH=$(grep "POLICY_FILE_PATH:" "$WORKFLOW_FILE" | awk '{print $2}' | head -1)

echo "Policy Repository: $POLICY_REPO"
echo "Policy Branch: $POLICY_BRANCH"
echo "Policy File Path: $POLICY_FILE_PATH"
echo ""

if [ -z "$POLICY_REPO" ] || [ -z "$POLICY_BRANCH" ] || [ -z "$POLICY_FILE_PATH" ]; then
    echo "⚠️  Warning: Could not extract all configuration variables from workflow"
    echo "   This may be expected if the workflow uses a different format"
    echo ""
fi

# Construct the URL
POLICY_URL="https://raw.githubusercontent.com/$POLICY_REPO/$POLICY_BRANCH/$POLICY_FILE_PATH"

echo "============================================================================"
echo "URL Validation"
echo "============================================================================"
echo ""

echo "Constructed URL:"
echo "  $POLICY_URL"
echo ""

# Check for common mistakes
HAS_REFS_HEADS=$(echo "$POLICY_URL" | grep -c "refs/heads" || true)
if [ "$HAS_REFS_HEADS" -gt 0 ]; then
    echo "❌ ERROR: URL contains 'refs/heads/' which will cause 404 errors!"
    echo ""
    echo "Current URL:"
    echo "  $POLICY_URL"
    echo ""
    echo "Should be:"
    FIXED_URL=$(echo "$POLICY_URL" | sed 's|/refs/heads/|/|')
    echo "  $FIXED_URL"
    echo ""
    exit 1
else
    echo "✓ URL format is correct (no refs/heads/)"
fi

# Check URL structure
if [[ "$POLICY_URL" =~ ^https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/.+ ]]; then
    echo "✓ URL structure matches expected format"
else
    echo "⚠️  Warning: URL structure may be incorrect"
    echo "   Expected: https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
fi

echo ""

# Test the URL with curl
echo "============================================================================"
echo "Testing URL with curl"
echo "============================================================================"
echo ""

echo "Attempting to download from URL..."
echo ""

TEMP_FILE=$(mktemp)
trap "rm -f $TEMP_FILE" EXIT

if curl -fsSL \
    --max-time 30 \
    --connect-timeout 10 \
    -H "Accept: application/vnd.github.v3.raw" \
    -o "$TEMP_FILE" \
    "$POLICY_URL" 2>&1; then

    echo "✓ Download successful!"
    echo ""

    # Validate the downloaded file
    if [ -f "$TEMP_FILE" ] && [ -s "$TEMP_FILE" ]; then
        FILE_SIZE=$(wc -c < "$TEMP_FILE")
        LINE_COUNT=$(wc -l < "$TEMP_FILE")

        echo "File Details:"
        echo "  Size: $FILE_SIZE bytes"
        echo "  Lines: $LINE_COUNT"
        echo ""

        echo "First 10 lines of downloaded file:"
        echo "----------------------------------------"
        head -n 10 "$TEMP_FILE"
        echo "----------------------------------------"
        echo ""

        echo "✓ File validation passed (non-empty)"
    else
        echo "❌ Downloaded file is empty or missing"
        exit 1
    fi
else
    EXIT_CODE=$?
    echo ""
    echo "❌ Download failed with exit code: $EXIT_CODE"
    echo ""

    if [ $EXIT_CODE -eq 22 ]; then
        echo "Exit code 22 indicates HTTP error (likely 404)"
        echo ""
        echo "Troubleshooting steps:"
        echo "  1. Verify the repository exists: https://github.com/$POLICY_REPO"
        echo "  2. Verify the branch exists: $POLICY_BRANCH"
        echo "  3. Verify the file path is correct: $POLICY_FILE_PATH"
        echo "  4. Check if the repository is private (requires authentication)"
        echo ""
        echo "Try accessing the file directly in your browser:"
        WEB_URL="https://github.com/$POLICY_REPO/blob/$POLICY_BRANCH/$POLICY_FILE_PATH"
        echo "  $WEB_URL"
    fi
    echo ""
    exit 1
fi

echo ""

# Check workflow syntax
echo "============================================================================"
echo "Checking Workflow Syntax"
echo "============================================================================"
echo ""

# Check if yq or python yaml validator is available
if command -v yq &> /dev/null; then
    echo "Validating YAML syntax with yq..."
    if yq eval '.' "$WORKFLOW_FILE" > /dev/null 2>&1; then
        echo "✓ YAML syntax is valid"
    else
        echo "❌ YAML syntax errors detected"
        exit 1
    fi
elif command -v python3 &> /dev/null; then
    echo "Validating YAML syntax with Python..."
    if python3 -c "import yaml; yaml.safe_load(open('$WORKFLOW_FILE'))" 2>&1; then
        echo "✓ YAML syntax is valid"
    else
        echo "❌ YAML syntax errors detected"
        exit 1
    fi
else
    echo "⚠️  No YAML validator found (yq or python3 not available)"
    echo "   Skipping syntax validation"
fi

echo ""

# Check for retry logic
echo "============================================================================"
echo "Checking for Best Practices"
echo "============================================================================"
echo ""

HAS_RETRY=$(grep -c "\-\-retry" "$WORKFLOW_FILE" || true)
HAS_MAX_RETRIES=$(grep -c "MAX_RETRIES" "$WORKFLOW_FILE" || true)
HAS_VALIDATION=$(grep -c "if \[ -f" "$WORKFLOW_FILE" || true)
HAS_DEBUG=$(grep -c "echo.*URL" "$WORKFLOW_FILE" || true)

if [ "$HAS_RETRY" -gt 0 ] || [ "$HAS_MAX_RETRIES" -gt 0 ]; then
    echo "✓ Retry logic found in workflow"
else
    echo "⚠️  No retry logic detected"
fi

if [ "$HAS_VALIDATION" -gt 0 ]; then
    echo "✓ File validation found in workflow"
else
    echo "⚠️  No file validation detected"
fi

if [ "$HAS_DEBUG" -gt 0 ]; then
    echo "✓ Debug output found in workflow"
else
    echo "⚠️  No debug output detected"
fi

echo ""

# Final summary
echo "============================================================================"
echo "Verification Summary"
echo "============================================================================"
echo ""

echo "✅ Workflow file exists and is readable"
echo "✅ URL format is correct (no refs/heads/)"
echo "✅ URL is accessible and returns valid content"
echo "✅ Downloaded file is non-empty"
echo ""

if [ "$HAS_RETRY" -gt 0 ] && [ "$HAS_VALIDATION" -gt 0 ] && [ "$HAS_DEBUG" -gt 0 ]; then
    echo "🎉 All checks passed! Workflow is ready for deployment."
    echo ""
    echo "Recommended next steps:"
    echo "  1. Commit and push the workflow file"
    echo "  2. Create a pull request if needed"
    echo "  3. Test the workflow in GitHub Actions"
else
    echo "⚠️  Workflow is functional but could be improved:"
    [ "$HAS_RETRY" -eq 0 ] && echo "  - Add retry logic for network failures"
    [ "$HAS_VALIDATION" -eq 0 ] && echo "  - Add file validation after download"
    [ "$HAS_DEBUG" -eq 0 ] && echo "  - Add debug output for troubleshooting"
fi

echo ""
echo "============================================================================"
