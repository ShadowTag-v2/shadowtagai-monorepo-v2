# Ingestion Workflow Fix Scripts

This directory contains automated scripts to help deploy and verify the ingestion workflow curl 404 fix.

## Available Scripts

### 1. `apply-fix-to-mlops.sh`

**Purpose:** Automatically applies the ingestion workflow fix to the mlops repository.

**Usage:**
```bash
# Clone mlops to default location (../mlops)
./scripts/apply-fix-to-mlops.sh

# Or specify custom path
./scripts/apply-fix-to-mlops.sh /path/to/mlops
```

**What it does:**
- Clones or uses existing mlops repository
- Creates a new fix branch
- Backs up existing workflow file
- Copies the fixed workflow from shadowtag_v4-fastapi-services
- Commits the changes
- Provides instructions for pushing and creating a PR

**Output:**
- Creates branch: `claude/fix-ingestion-curl-404-YYYYMMDD-HHMMSS`
- Commits changes with descriptive message
- Shows next steps for completion

---

### 2. `verify-workflow.sh`

**Purpose:** Verifies that a workflow file is correctly configured and tests URLs.

**Usage:**
```bash
# Verify current repository
./scripts/verify-workflow.sh

# Verify another repository
./scripts/verify-workflow.sh /path/to/repo

# Verify mlops repository
./scripts/verify-workflow.sh ../mlops
```

**What it checks:**
- ✅ Workflow file exists
- ✅ URL format is correct (no `refs/heads/`)
- ✅ URL is accessible via curl
- ✅ Downloaded file is non-empty
- ✅ YAML syntax is valid
- ✅ Retry logic is present
- ✅ File validation is present
- ✅ Debug output is present

**Exit codes:**
- `0` - All checks passed
- `1` - One or more checks failed

---

## Quick Start Guide

### For First-Time Setup

1. **Verify the current repository's workflow:**
   ```bash
   cd /home/user/shadowtag_v4-fastapi-services
   ./scripts/verify-workflow.sh
   ```

2. **Apply fix to mlops repository:**
   ```bash
   ./scripts/apply-fix-to-mlops.sh
   ```

3. **Follow the on-screen instructions to:**
   - Push the branch
   - Create a pull request
   - Review and merge

4. **Verify the fix in mlops:**
   ```bash
   ./scripts/verify-workflow.sh ../mlops
   ```

### For Ongoing Maintenance

**Check workflow health regularly:**
```bash
# Verify shadowtag_v4-fastapi-services
./scripts/verify-workflow.sh

# Verify mlops
./scripts/verify-workflow.sh ../mlops
```

---

## Prerequisites

### Required Tools

- `bash` (version 4.0+)
- `git`
- `curl`

### Optional Tools (for enhanced features)

- `yq` - For YAML validation
- `python3` - Alternative YAML validation
- `gh` - GitHub CLI for easier PR management

### Install Optional Tools

**yq (YAML processor):**
```bash
# Ubuntu/Debian
sudo apt-get install yq

# Or download binary
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
```

**GitHub CLI:**
```bash
# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

---

## Troubleshooting

### Script Won't Execute

**Error:** `Permission denied`

**Solution:**
```bash
chmod +x scripts/apply-fix-to-mlops.sh
chmod +x scripts/verify-workflow.sh
```

### mlops Repository Not Found

**Error:** `Repository not found`

**Solution:**
```bash
# Ensure git credentials are configured
git config --global user.name "Your Name"
git config --global user.email "redacted@shadowtag-v4.local"

# Clone manually first
git clone https://github.com/ehanc69/mlops.git ../mlops
./scripts/apply-fix-to-mlops.sh ../mlops
```

### Verification Fails

**Error:** `curl: (22) The requested URL returned error: 404`

**This means the URL is still incorrect!**

Check:
1. URL does NOT contain `/refs/heads/`
2. Repository, branch, and file path are correct
3. File exists in the target repository

**Debug:**
```bash
# Test URL manually
curl -I "https://raw.githubusercontent.com/ehanc69/shadowtag_v4-policy/main/policy/config/strict_policy.yml"
```

### YAML Validation Fails

**Error:** `YAML syntax errors detected`

**Solution:**
```bash
# Check YAML syntax manually
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ingest.yml'))"

# Or use yq
yq eval '.' .github/workflows/ingest.yml
```

---

## Examples

### Example 1: First-Time Fix Application

```bash
$ cd /home/user/shadowtag_v4-fastapi-services
$ ./scripts/apply-fix-to-mlops.sh

============================================================================
Applying Ingestion Workflow Fix to MLOps Repository
============================================================================

✓ Source repository verified: shadowtag_v4-fastapi-services

📥 Cloning mlops repository to: ../mlops
✓ Repository cloned successfully

============================================================================
Creating Fix Branch in MLOps Repository
============================================================================

🌿 Creating branch: claude/fix-ingestion-curl-404-20251118-101500
✓ Branch created successfully

============================================================================
Copying Fixed Workflow File
============================================================================

📄 Copying fixed workflow from shadowtag_v4-fastapi-services...
✓ Workflow file copied successfully

...

✓ Changes committed successfully

============================================================================
Next Steps
============================================================================

1. Review the changes:
   cd ../mlops
   git diff main...claude/fix-ingestion-curl-404-20251118-101500

2. Push the branch:
   git push -u origin claude/fix-ingestion-curl-404-20251118-101500

3. Create a pull request on GitHub
```

### Example 2: Workflow Verification

```bash
$ ./scripts/verify-workflow.sh

============================================================================
Ingestion Workflow Verification
============================================================================

✓ Workflow file found: .github/workflows/ingest.yml

============================================================================
Extracting Configuration from Workflow
============================================================================

Policy Repository: ehanc69/shadowtag_v4-policy
Policy Branch: main
Policy File Path: policy/config/strict_policy.yml

============================================================================
URL Validation
============================================================================

Constructed URL:
  https://raw.githubusercontent.com/ehanc69/shadowtag_v4-policy/main/policy/config/strict_policy.yml

✓ URL format is correct (no refs/heads/)
✓ URL structure matches expected format

============================================================================
Testing URL with curl
============================================================================

Attempting to download from URL...

✓ Download successful!

File Details:
  Size: 1234 bytes
  Lines: 45

First 10 lines of downloaded file:
----------------------------------------
# Strict Policy Configuration
version: 1.0
...
----------------------------------------

✓ File validation passed (non-empty)

============================================================================
Verification Summary
============================================================================

✅ Workflow file exists and is readable
✅ URL format is correct (no refs/heads/)
✅ URL is accessible and returns valid content
✅ Downloaded file is non-empty

🎉 All checks passed! Workflow is ready for deployment.
```

---

## Script Architecture

### apply-fix-to-mlops.sh

```
1. Validate environment
   ├─ Check we're in shadowtag_v4-fastapi-services
   └─ Verify source workflow exists

2. Prepare mlops repository
   ├─ Clone (if needed) or use existing
   ├─ Fetch latest changes
   └─ Create new fix branch

3. Apply fix
   ├─ Backup existing workflow (if present)
   ├─ Copy fixed workflow
   └─ Search for additional issues

4. Commit changes
   ├─ Stage modified files
   └─ Create descriptive commit

5. Provide next steps
   ├─ Show push command
   ├─ Show PR creation URL
   └─ Show verification steps
```

### verify-workflow.sh

```
1. Locate workflow file
   └─ Check .github/workflows/ingest.yml exists

2. Extract configuration
   ├─ Parse POLICY_REPO
   ├─ Parse POLICY_BRANCH
   └─ Parse POLICY_FILE_PATH

3. Validate URL
   ├─ Check for refs/heads (should be absent)
   ├─ Verify URL structure
   └─ Construct full URL

4. Test download
   ├─ curl with retry logic
   ├─ Check HTTP response
   └─ Validate file contents

5. Check best practices
   ├─ Retry logic present?
   ├─ File validation present?
   └─ Debug output present?

6. Report results
   ├─ Success summary
   └─ Or detailed error messages
```

---

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

### GitHub Actions Example

```yaml
name: Verify Workflow Configuration

on:
  pull_request:
    paths:
      - '.github/workflows/ingest.yml'

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Verify workflow
        run: |
          chmod +x scripts/verify-workflow.sh
          ./scripts/verify-workflow.sh
```

---

## Contributing

When adding new scripts to this directory:

1. **Make scripts executable:**
   ```bash
   chmod +x scripts/new-script.sh
   ```

2. **Add documentation:**
   - Update this README
   - Add usage examples
   - Document prerequisites

3. **Follow conventions:**
   - Use bash for shell scripts
   - Include error handling (`set -e`)
   - Add descriptive comments
   - Use meaningful variable names

4. **Test thoroughly:**
   - Test on fresh clone
   - Test with missing dependencies
   - Test error conditions

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the main documentation:
   - `docs/WORKFLOW_FIX.md` - Detailed fix explanation
   - `docs/DEPLOYMENT_GUIDE.md` - Deployment procedures
   - `docs/VALIDATION_CHECKLIST.md` - Validation steps

3. Run scripts with verbose output:
   ```bash
   bash -x ./scripts/verify-workflow.sh
   ```

---

**Last Updated:** 2025-11-18
**Version:** 1.0.0
**Maintained by:** PNKLN Core Stack™ Team
