# Complete Deployment Guide for Ingestion Workflow Fix

## Overview

This guide provides step-by-step instructions for deploying the ingestion workflow curl 404 fix to all repositories.

## Quick Reference

| Repository | Status | Action Required |
|------------|--------|-----------------|
| `ehanc69/pnkln-stack-fastapi-services` | ✅ **Fixed & Merged** | Test the workflow |
| `ehanc69/mlops` | ⚠️ **Needs Fix** | Apply fix using script |

---

## Part 1: Verify Fix in pnkln-stack-fastapi-services

### Step 1: Verify the Workflow Locally

```bash
# Navigate to the repository
cd /home/user/pnkln-stack-fastapi-services

# Run the verification script
chmod +x scripts/verify-workflow.sh
./scripts/verify-workflow.sh
```

**Expected Output:**
```
✅ Workflow file exists and is readable
✅ URL format is correct (no refs/heads/)
✅ URL is accessible and returns valid content
✅ Downloaded file is non-empty
🎉 All checks passed! Workflow is ready for deployment.
```

### Step 2: Test the Workflow in GitHub Actions

#### Option A: Manual Trigger
1. Go to https://github.com/ehanc69/pnkln-stack-fastapi-services/actions
2. Select **Ingestion (hourly)** workflow
3. Click **Run workflow**
4. Select branch: `main`
5. Click **Run workflow** button
6. Monitor the execution

#### Option B: Wait for Scheduled Run
- The workflow runs hourly (at minute 0 of every hour)
- Check the Actions tab after the next hour

### Step 3: Validate Success

Look for these indicators in the workflow logs:

✅ **Success Indicators:**
```
✓ Successfully downloaded policy configuration
✓ Policy file validated (non-empty)
File size: XXX bytes
Lines: XXX
```

❌ **Failure Indicators:**
```
curl: (22) The requested URL returned error: 404
Process completed with exit code 22
```

---

## Part 2: Apply Fix to mlops Repository

### Option A: Automated Script (Recommended)

```bash
# Navigate to pnkln-stack-fastapi-services repository
cd /home/user/pnkln-stack-fastapi-services

# Make the script executable
chmod +x scripts/apply-fix-to-mlops.sh

# Run the script (will clone mlops to ../mlops if not present)
./scripts/apply-fix-to-mlops.sh

# Or specify a custom path
./scripts/apply-fix-to-mlops.sh /path/to/mlops
```

The script will:
1. Clone or use existing mlops repository
2. Create a new fix branch
3. Copy the fixed workflow file
4. Create a backup of the old workflow
5. Commit the changes
6. Provide next steps for pushing and creating a PR

**Follow the output instructions to complete deployment.**

### Option B: Manual Process

If you prefer to apply the fix manually:

#### Step 1: Clone/Navigate to mlops Repository

```bash
# Clone if you don't have it
git clone https://github.com/ehanc69/mlops.git
cd mlops

# Or navigate to existing clone
cd /path/to/mlops
```

#### Step 2: Create a Fix Branch

```bash
# Create and checkout a new branch
git checkout -b claude/fix-ingestion-curl-404
```

#### Step 3: Backup Existing Workflow (if it exists)

```bash
# Check if workflow exists
if [ -f .github/workflows/ingest.yml ]; then
    cp .github/workflows/ingest.yml .github/workflows/ingest.yml.backup
    echo "Backup created: .github/workflows/ingest.yml.backup"
fi
```

#### Step 4: Copy Fixed Workflow

```bash
# Copy from pnkln-stack-fastapi-services repository
cp /home/user/pnkln-stack-fastapi-services/.github/workflows/ingest.yml \
   .github/workflows/ingest.yml
```

**Or manually edit the existing workflow:**

Find this line (around line 29):
```yaml
https://raw.githubusercontent.com/ehanc69/pnkln-stack-policy/refs/heads/main/policy/config/strict_policy.yml
```

Change to:
```yaml
https://raw.githubusercontent.com/ehanc69/pnkln-stack-policy/main/policy/config/strict_policy.yml
```

#### Step 5: Verify the Fix

```bash
# Run verification script
/home/user/pnkln-stack-fastapi-services/scripts/verify-workflow.sh .
```

#### Step 6: Commit Changes

```bash
git add .github/workflows/ingest.yml

git commit -m "Fix ingestion workflow curl 404 error with correct GitHub raw URL format

- Updated URL format to remove refs/heads/
- Added retry logic and error handling
- Applied fix from pnkln-stack-fastapi-services repository"
```

#### Step 7: Push and Create PR

```bash
# Push the branch
git push -u origin claude/fix-ingestion-curl-404

# The output will provide a URL to create a PR
```

#### Step 8: Create Pull Request

1. Click the PR creation URL from the git push output
2. Or go to: https://github.com/ehanc69/mlops/pulls
3. Click **New pull request**
4. Select your fix branch
5. Add title: "Fix ingestion workflow curl 404 error"
6. Add description referencing this fix
7. Click **Create pull request**

#### Step 9: Review and Merge

1. Review the changes in the PR
2. Ensure all checks pass
3. Merge the PR

---

## Part 3: Post-Deployment Verification

### For Each Repository

After merging the fix, verify it's working:

#### 1. Trigger the Workflow

```bash
# Using GitHub CLI
gh workflow run ingest.yml --repo ehanc69/mlops

# Or via web UI
# Go to Actions → Ingestion (hourly) → Run workflow
```

#### 2. Monitor the Execution

```bash
# Watch the latest run
gh run watch --repo ehanc69/mlops

# Or view in browser
# https://github.com/ehanc69/mlops/actions
```

#### 3. Check the Logs

Look for:
- ✅ No `curl: (22)` errors
- ✅ `Successfully downloaded policy configuration`
- ✅ File size and line count displayed
- ✅ Policy file contents preview

#### 4. Download Artifacts

```bash
# List recent runs
gh run list --workflow=ingest.yml --repo ehanc69/mlops --limit 5

# Download artifact from specific run
gh run download <RUN_ID> --repo ehanc69/mlops --name policy-config
```

Verify the `strict_policy.yml` file was downloaded correctly.

---

## Part 4: Testing Matrix

### Test Scenarios

Test the workflow under different conditions:

| Scenario | Test Method | Expected Result |
|----------|-------------|-----------------|
| **Scheduled Run** | Wait for hourly cron | ✅ Runs automatically |
| **Manual Trigger** | Actions UI → Run workflow | ✅ Runs on-demand |
| **Network Failure** | Simulate by blocking connection | ✅ Retries with backoff |
| **Invalid URL** | Temporarily change to bad URL | ✅ Clear error message |
| **Missing File** | Temporarily change to non-existent file | ✅ 404 with helpful guidance |

### Simulate Network Failure (Optional)

To test retry logic:

```yaml
# Temporarily add to workflow for testing
- name: Test retry logic
  run: |
    # This will fail and trigger retries
    curl --retry 3 --retry-delay 2 \
      https://raw.githubusercontent.com/invalid/repo/main/file.yml || true
```

---

## Part 5: Rollback Procedures

If the fix causes issues, you can quickly rollback.

### Rollback via GitHub UI

1. Go to the repository
2. Navigate to: `.github/workflows/ingest.yml`
3. Click **History**
4. Find the previous working version
5. Click the commit hash
6. Click **View file**
7. Click **Edit** → Copy contents
8. Navigate back to current file
9. Click **Edit** → Paste old contents
10. Commit directly to main (if urgent)

### Rollback via Git

```bash
# Revert the fix commit
git revert <COMMIT_HASH>
git push origin main

# Or restore from backup (if you created one)
git checkout <PREVIOUS_COMMIT> -- .github/workflows/ingest.yml
git commit -m "Rollback workflow to previous version"
git push origin main
```

---

## Part 6: Monitoring and Alerts

### Set Up Monitoring

#### GitHub Actions Notifications

1. Go to repository **Settings**
2. Click **Notifications**
3. Enable **Actions** notifications
4. Choose notification method (email, Slack, etc.)

#### Monitor via GitHub CLI

```bash
# Check workflow status
gh run list --workflow=ingest.yml --limit 10

# View failed runs only
gh run list --workflow=ingest.yml --status=failure

# Get detailed view
gh run view <RUN_ID> --log-failed
```

#### Set Up Status Checks

Create a status badge in your README:

```markdown
[![Ingestion Workflow](https://github.com/ehanc69/mlops/actions/workflows/ingest.yml/badge.svg)](https://github.com/ehanc69/mlops/actions/workflows/ingest.yml)
```

---

## Part 7: Troubleshooting

### Common Issues and Solutions

#### Issue: "curl: (22) The requested URL returned error: 404"

**Diagnosis:**
```bash
# Check the URL in the workflow logs
# Look for: "Policy URL: https://..."
```

**Solution:**
1. Verify URL does NOT contain `/refs/heads/`
2. Correct format: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`
3. Test URL manually: `curl -I <URL>`

#### Issue: "Downloaded file is empty or missing"

**Diagnosis:**
```bash
# Check workflow logs for file size
# Look for: "File size: 0 bytes"
```

**Solution:**
1. Verify the file exists in the target repository
2. Check file path is correct (case-sensitive)
3. Ensure branch name is correct

#### Issue: "Permission denied" or 403 errors

**Diagnosis:**
Repository is private and requires authentication.

**Solution:**
```yaml
# Add authentication to curl command
- name: Download policy
  env:
    GH_TOKEN: ${{ github.token }}
  run: |
    curl -H "Authorization: token ${GH_TOKEN}" \
      -fsSL -o file.yml \
      "https://raw.githubusercontent.com/owner/repo/branch/file.yml"
```

#### Issue: Workflow doesn't run on schedule

**Diagnosis:**
Check cron expression and repository settings.

**Solution:**
1. Verify cron expression: https://crontab.guru/
2. Ensure Actions are enabled in repository settings
3. Check if workflow file is in the default branch
4. Workflows in new repositories may have a delay (first run)

---

## Part 8: Best Practices

### 1. Always Test Locally First

```bash
# Before deploying, test the URL
POLICY_URL="https://raw.githubusercontent.com/ehanc69/pnkln-stack-policy/main/policy/config/strict_policy.yml"

curl -fsSL "$POLICY_URL" | head -20
```

### 2. Use Environment Variables

```yaml
env:
  POLICY_REPO: ehanc69/pnkln-stack-policy
  POLICY_BRANCH: main
  POLICY_FILE_PATH: policy/config/strict_policy.yml
```

### 3. Add Comprehensive Logging

```yaml
- name: Download file
  run: |
    echo "::group::Download Configuration"
    echo "URL: ${URL}"
    echo "Target: ${TARGET_FILE}"
    echo "::endgroup::"
```

### 4. Implement Retry Logic

```bash
MAX_RETRIES=4
RETRY_DELAY=2

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if curl -fsSL "${URL}"; then
    break
  fi
  sleep $RETRY_DELAY
  RETRY_DELAY=$((RETRY_DELAY * 2))
done
```

### 5. Validate Downloads

```bash
if [ ! -s "${FILE_PATH}" ]; then
  echo "Error: Downloaded file is empty"
  exit 1
fi
```

---

## Part 9: Success Criteria

The deployment is successful when:

- [ ] ✅ Workflow runs without curl 404 errors
- [ ] ✅ Policy file downloads successfully
- [ ] ✅ File validation passes (non-empty)
- [ ] ✅ Workflow completes in expected time
- [ ] ✅ Artifacts are uploaded correctly
- [ ] ✅ No error notifications received
- [ ] ✅ Scheduled runs execute on time
- [ ] ✅ Manual triggers work as expected

---

## Part 10: Maintenance

### Regular Checks

Perform these checks monthly:

```bash
# Check workflow success rate
gh run list --workflow=ingest.yml --limit 30 --json conclusion \
  | jq '[.[] | .conclusion] | group_by(.) | map({conclusion: .[0], count: length})'

# Check for 404 errors in recent runs
gh run list --workflow=ingest.yml --limit 10 \
  | while read id status; do
      gh run view $id --log | grep -i "404\|curl.*22" || true
    done
```

### Update Checklist

When updating the workflow:

1. [ ] Update in development branch first
2. [ ] Run verification script
3. [ ] Test manually via Actions UI
4. [ ] Monitor first scheduled run
5. [ ] Update documentation if needed
6. [ ] Apply to other repositories if successful

---

## Quick Command Reference

```bash
# Verify workflow configuration
./scripts/verify-workflow.sh

# Apply fix to mlops repository
./scripts/apply-fix-to-mlops.sh

# Test URL manually
curl -fsSL "https://raw.githubusercontent.com/ehanc69/pnkln-stack-policy/main/policy/config/strict_policy.yml"

# Trigger workflow manually
gh workflow run ingest.yml --repo ehanc69/mlops

# Watch workflow execution
gh run watch --repo ehanc69/mlops

# View workflow logs
gh run view --log --repo ehanc69/mlops

# List recent runs
gh run list --workflow=ingest.yml --limit 10
```

---

## Support

If you encounter issues not covered in this guide:

1. Check the workflow logs in GitHub Actions
2. Review `docs/WORKFLOW_FIX.md` for detailed fix explanation
3. Run the verification script for automated diagnostics
4. Check GitHub Actions status: https://www.githubstatus.com/

---

**Last Updated:** 2025-11-18
**Version:** 1.0.0
**Repository:** ehanc69/pnkln-stack-fastapi-services
