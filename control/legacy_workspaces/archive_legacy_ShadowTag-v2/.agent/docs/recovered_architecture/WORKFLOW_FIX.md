# Ingestion Workflow Curl 404 Fix

## Issue Summary

The ingestion workflow was failing with a `curl: (22) The requested URL returned error: 404` error because of an incorrect GitHub raw URL format.

## Root Cause

**Incorrect URL Format (causes 404):**

```

https://raw.githubusercontent.com/ehanc69/aiyou-policy/refs/heads/main/policy/config/strict_policy.yml

```

**Correct URL Format:**

```

https://raw.githubusercontent.com/ehanc69/aiyou-policy/main/policy/config/strict_policy.yml

```

### The Problem

The incorrect URL included `/refs/heads/` in the path, which is part of Git's internal reference structure but NOT part of the GitHub raw content URL format.

## GitHub Raw URL Structure

The correct format for accessing raw files from GitHub repositories is:

```

https://raw.githubusercontent.com/{owner}/{repo}/{branch-or-commit}/{file-path}

```

### Examples

✅ **Correct:**


- `https://raw.githubusercontent.com/ehanc69/aiyou-policy/main/policy/config/strict_policy.yml`


- `https://raw.githubusercontent.com/ehanc69/aiyou-policy/v1.0.0/policy/config/strict_policy.yml`


- `https://raw.githubusercontent.com/ehanc69/aiyou-policy/abc123def456/policy/config/strict_policy.yml`

❌ **Incorrect:**


- `https://raw.githubusercontent.com/ehanc69/aiyou-policy/refs/heads/main/policy/config/strict_policy.yml`


- `https://raw.githubusercontent.com/ehanc69/aiyou-policy/refs/tags/v1.0.0/policy/config/strict_policy.yml`


- `https://github.com/ehanc69/aiyou-policy/blob/main/policy/config/strict_policy.yml` (not raw URL)

## Fix Implemented

### 1. Created New Workflow

Created `.github/workflows/ingest.yml` with:



- ✅ Correct raw URL format


- ✅ Exponential backoff retry logic (4 retries: 2s, 4s, 8s, 16s)


- ✅ Detailed debugging output with URL logging


- ✅ File validation (checks if downloaded file is non-empty)


- ✅ Comprehensive error messages


- ✅ Workflow summary in GitHub Actions UI

### 2. Key Features

**Retry Logic:**

```yaml

# Retry up to 4 times with exponential backoff

MAX_RETRIES=4
RETRY_DELAY=2  # Initial delay: 2s, then 4s, 8s, 16s

```

**URL Construction:**

```yaml

# Environment variables for easy configuration

POLICY_REPO: ehanc69/aiyou-policy
POLICY_BRANCH: main
POLICY_FILE_PATH: policy/config/strict_policy.yml

# Correct URL format

POLICY_URL="https://raw.githubusercontent.com/${POLICY_REPO}/${POLICY_BRANCH}/${POLICY_FILE_PATH}"

```

**Robust Curl Command:**

```bash
curl -fsSL \
  --retry 3 \
  --retry-delay 2 \
  --retry-max-time 60 \
  --max-time 30 \
  --connect-timeout 10 \
  -H "Accept: application/vnd.github.v3.raw" \
  -o "${TARGET_FILE}" \
  "${POLICY_URL}"

```

### 3. Error Handling

The workflow provides detailed error messages if the download fails:

```

Please verify:


  1. The repository 'ehanc69/aiyou-policy' exists and is accessible


  2. The branch 'main' exists


  3. The file path 'policy/config/strict_policy.yml' is correct


  4. The URL format is: https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}


  5. NOT: https://raw.githubusercontent.com/{owner}/{repo}/refs/heads/{branch}/{path}

```

## Testing

### Manual Testing

To test the workflow manually:

```bash

# Test the curl command locally

curl -fsSL \
  https://raw.githubusercontent.com/ehanc69/aiyou-policy/main/policy/config/strict_policy.yml

# Test with verbose output

curl -v \
  https://raw.githubusercontent.com/ehanc69/aiyou-policy/main/policy/config/strict_policy.yml

```

### GitHub Actions Testing



1. Navigate to **Actions** tab in GitHub


2. Select **Ingestion (hourly)** workflow


3. Click **Run workflow** > **Run workflow**


4. Monitor the execution and check for successful download

## Migration Guide

If you have existing workflows using the incorrect URL format:

### Before (Broken):

```yaml


- name: Download policy
  run: |
    curl -fsSL -o policy/config/strict_policy.yml \
      https://raw.githubusercontent.com/ehanc69/aiyou-policy/refs/heads/main/policy/config/strict_policy.yml

```

### After (Fixed):

```yaml


- name: Download policy
  env:
    POLICY_URL: https://raw.githubusercontent.com/ehanc69/aiyou-policy/main/policy/config/strict_policy.yml
  run: |
    echo "Downloading from: ${POLICY_URL}"

    curl -fsSL \
      --retry 3 \
      --retry-delay 2 \
      -o policy/config/strict_policy.yml \
      "${POLICY_URL}"

    # Validate download
    if [ ! -s policy/config/strict_policy.yml ]; then
      echo "Error: Downloaded file is empty or missing"
      exit 1
    fi

```

## Best Practices

### 1. Always Use Raw URLs for Direct Downloads

When downloading files directly with `curl`, use the raw URL format:


- ✅ `https://raw.githubusercontent.com/...`


- ❌ `https://github.com/.../blob/...`

### 2. Add Debugging Output

Always log the URL being used:

```bash
echo "Downloading from: ${URL}"

```

### 3. Implement Retry Logic

Network requests can fail transiently:

```bash
curl --retry 3 --retry-delay 2 "${URL}"

```

### 4. Validate Downloaded Files

Check if the file exists and is non-empty:

```bash
if [ ! -s "${FILE_PATH}" ]; then
  echo "Error: File is empty or missing"
  exit 1
fi

```

### 5. Use Environment Variables

Make URLs configurable:

```yaml
env:
  REPO: owner/repo
  BRANCH: main
  FILE_PATH: path/to/file.yml

```

### 6. Prefer GitHub Actions

For files in the same repository, use `actions/checkout`:

```yaml


- uses: actions/checkout@v4
  with:
    repository: ehanc69/aiyou-policy
    ref: main
    path: policy

```

### 7. Use Release Assets API

For release assets, use the GitHub API:

```bash
gh release download v1.0.0 --pattern '*.yml' --repo ehanc69/aiyou-policy

```

## Alternative Solutions

### Option 1: Use actions/checkout

Instead of `curl`, checkout the entire repository:

```yaml


- name: Checkout policy repository
  uses: actions/checkout@v4
  with:
    repository: ehanc69/aiyou-policy
    ref: main
    path: policy-repo



- name: Copy policy file
  run: |
    cp policy-repo/policy/config/strict_policy.yml policy/config/

```

**Pros:**


- No URL construction needed


- Handles authentication automatically


- More reliable for large files

**Cons:**


- Downloads entire repository (slower)


- Uses more disk space

### Option 2: Use GitHub CLI

Use `gh` to download specific files:

```yaml


- name: Download policy file
  env:
    GH_TOKEN: ${{ github.token }}
  run: |
    gh api \
      -H "Accept: application/vnd.github.v3.raw" \
      /repos/ehanc69/aiyou-policy/contents/policy/config/strict_policy.yml?ref=main \
      > policy/config/strict_policy.yml

```

**Pros:**


- Handles authentication


- More robust error handling


- Can access private repositories

**Cons:**


- Requires GitHub CLI


- More complex syntax

## Verification

To verify the fix is working:



1. **Check workflow runs:**
   ```bash
   # View recent workflow runs
   gh run list --workflow=ingest.yml

   # View logs of latest run
   gh run view --log
   ```



2. **Check for artifacts:**


   - Navigate to Actions > Workflow run


   - Download the `policy-config` artifact


   - Verify it contains `strict_policy.yml`



3. **Monitor for 404 errors:**


   - Check workflow logs for "404" or "curl: (22)"


   - Verify "Successfully downloaded policy configuration" message

## Related Issues

This fix addresses:


- `curl: (22) The requested URL returned error: 404`


- `Process completed with exit code 22`


- GitHub Actions workflow failures in ingestion pipeline

## References



- [GitHub Raw Content URLs](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files)


- [GitHub Actions: actions/checkout](https://github.com/actions/checkout)


- [Curl Retry Options](https://curl.se/docs/manpage.html#--retry)


- [GitHub API: Get repository content](https://docs.github.com/en/rest/repos/contents)

## Version History



- **2025-11-18**: Initial fix - Created workflow with correct URL format and retry logic


- **Commit**: `claude/fix-ingestion-curl-404-0114azLCQoL9g4a2wpcf5joA`

---

**Status**: ✅ Fixed
**Last Updated**: 2025-11-18
**Author**: Claude (via Claude Agent SDK)
