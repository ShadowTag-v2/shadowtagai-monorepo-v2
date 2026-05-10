# Ingestion Workflow Validation Checklist

Use this checklist to validate the ingestion workflow fix before and after deployment.

---

## Pre-Deployment Validation

### 1. Repository: ShadowTag-v2-fastapi-services

- [ ] **Workflow file exists**

  ```bash
  ls -la .github/workflows/ingest.yml
  ```

  Expected: File exists with read permissions

- [ ] **Workflow syntax is valid**

  ```bash
  ./scripts/verify-workflow.sh
  ```

  Expected: "All checks passed! Workflow is ready for deployment."

- [ ] **URL format is correct**
  - [ ] Does NOT contain `/refs/heads/`
  - [ ] Follows format: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`

  ```bash
  grep -n "raw.githubusercontent.com" .github/workflows/ingest.yml
  ```

- [ ] **Environment variables are defined**
  - [ ] `POLICY_REPO` is set
  - [ ] `POLICY_BRANCH` is set
  - [ ] `POLICY_FILE_PATH` is set

- [ ] **Retry logic is present**

  ```bash
  grep -c "MAX_RETRIES\|--retry" .github/workflows/ingest.yml
  ```

  Expected: Greater than 0

- [ ] **File validation is present**

  ```bash
  grep -c "if \[ -f.*\]" .github/workflows/ingest.yml
  ```

  Expected: Greater than 0

- [ ] **Debug output is present**
  ```bash
  grep -c 'echo.*URL' .github/workflows/ingest.yml
  ```
  Expected: Greater than 0

---

## Post-Deployment Validation (ShadowTag-v2-fastapi-services)

### 2. GitHub Actions Execution

- [ ] **Workflow is visible in Actions tab**
  - Visit: https://github.com/ehanc69/ShadowTag-v2-fastapi-services/actions
  - Verify "Ingestion (hourly)" workflow appears

- [ ] **Manual trigger works**
  - [ ] Click "Run workflow"
  - [ ] Workflow starts successfully
  - [ ] No immediate errors

- [ ] **Workflow executes successfully**
  - [ ] All steps complete with green checkmarks
  - [ ] No "curl: (22)" errors in logs
  - [ ] No "404" errors in logs

- [ ] **Download step succeeds**
  - [ ] "Successfully downloaded policy configuration" message appears
  - [ ] File size is logged (> 0 bytes)
  - [ ] Line count is logged (> 0 lines)
  - [ ] First 20 lines preview is shown

- [ ] **File validation passes**
  - [ ] "Policy file validated (non-empty)" message appears
  - [ ] No "Downloaded file is empty" errors

- [ ] **Artifacts are uploaded**
  - [ ] `policy-config` artifact appears in workflow run
  - [ ] Artifact can be downloaded
  - [ ] Artifact contains `strict_policy.yml`
  - [ ] Downloaded file is valid YAML

- [ ] **Workflow summary is generated**
  - [ ] Summary section appears in workflow run
  - [ ] Shows success status
  - [ ] Lists repository, branch, and file path

---

## MLOps Repository Validation

### 3. Pre-Deployment (mlops)

- [ ] **Fix script runs successfully**

  ```bash
  cd /home/user/ShadowTag-v2-fastapi-services
  ./scripts/apply-fix-to-mlops.sh
  ```

  Expected: No errors, creates branch and commits

- [ ] **Branch is created**

  ```bash
  cd ../mlops
  git branch | grep fix-ingestion-curl-404
  ```

  Expected: Branch exists

- [ ] **Workflow file is updated**

  ```bash
  cat .github/workflows/ingest.yml | grep -c "refs/heads"
  ```

  Expected: 0 (no occurrences)

- [ ] **Backup was created** (if previous workflow existed)

  ```bash
  ls -la .github/workflows/ingest.yml.backup
  ```

- [ ] **Verification passes**
  ```bash
  cd ../ShadowTag-v2-fastapi-services
  ./scripts/verify-workflow.sh ../mlops
  ```
  Expected: All checks passed

### 4. Post-Deployment (mlops)

- [ ] **Branch is pushed**

  ```bash
  cd ../mlops
  git branch -r | grep fix-ingestion-curl-404
  ```

- [ ] **Pull request is created**
  - Visit: https://github.com/ehanc69/mlops/pulls
  - PR exists with title "Fix ingestion workflow curl 404 error"

- [ ] **PR checks pass**
  - No merge conflicts
  - All status checks green
  - No review comments blocking merge

- [ ] **PR is merged**
  - Merged to main/default branch
  - Branch can be deleted

- [ ] **Workflow runs successfully on main**
  - First run after merge completes successfully
  - No 404 errors
  - File downloads correctly

---

## Scheduled Execution Validation

### 5. Hourly Schedule

- [ ] **Cron expression is correct**

  ```yaml
  schedule:
    - cron: "0 * * * *"
  ```

  This runs at minute 0 of every hour

- [ ] **First scheduled run executes**
  - Wait for the top of the hour
  - Verify workflow runs automatically
  - No manual trigger needed

- [ ] **Subsequent runs execute**
  - Check after 2-3 scheduled runs
  - All runs complete successfully
  - No pattern of failures

---

## Error Handling Validation

### 6. Retry Logic

- [ ] **Network failure handling**
  - Temporarily block network (if testing)
  - Verify retry attempts occur
  - Verify exponential backoff (2s, 4s, 8s, 16s)

- [ ] **Maximum retries respected**
  - After 4 failed attempts, workflow fails
  - Error message is clear and helpful

### 7. Invalid URL Handling

Test with temporarily modified URLs:

- [ ] **Invalid repository**

  ```yaml
  POLICY_REPO: ehanc69/nonexistent-repo
  ```

  Expected: Clear 404 error with troubleshooting guidance

- [ ] **Invalid branch**

  ```yaml
  POLICY_BRANCH: nonexistent-branch
  ```

  Expected: Clear error message

- [ ] **Invalid file path**

  ```yaml
  POLICY_FILE_PATH: path/to/nonexistent/file.yml
  ```

  Expected: Clear error message

- [ ] **URL with refs/heads (regression test)**
  ```yaml
  # Manually construct broken URL
  POLICY_URL="...//refs/heads/main/..."
  ```
  Expected: Should fail with 404, but with helpful error message

---

## Performance Validation

### 8. Execution Time

- [ ] **Workflow completes in reasonable time**
  - Expected: < 5 minutes for download step
  - Expected: < 10 minutes total workflow time

- [ ] **No timeout errors**
  - curl commands complete within timeout
  - No "timeout" status in workflow runs

### 9. Resource Usage

- [ ] **Artifacts are reasonable size**
  - policy-config artifact < 10 MB
  - No unnecessarily large files

- [ ] **Workflow history is maintained**
  - Successful runs: kept for 3 runs (per config)
  - Failed runs: kept for 1 run (per config)

---

## Security Validation

### 10. Secrets and Credentials

- [ ] **No secrets in logs**
  - Review workflow logs
  - No API keys or tokens visible
  - URLs don't contain sensitive parameters

- [ ] **Token usage is correct**
  - `${{ github.token }}` used where needed
  - Scopes are appropriate (read-only for downloads)

### 11. URL Safety

- [ ] **URLs use HTTPS**
  - All URLs start with `https://`
  - No HTTP (insecure) URLs

- [ ] **No URL injection possible**
  - Variables are properly quoted
  - No user input in URL construction

---

## Documentation Validation

### 12. Documentation Quality

- [ ] **WORKFLOW_FIX.md is accurate**
  - Describes the problem correctly
  - Solution matches implementation
  - Examples are valid

- [ ] **DEPLOYMENT_GUIDE.md is complete**
  - All steps are clear
  - Commands are copy-paste ready
  - Links work correctly

- [ ] **VALIDATION_CHECKLIST.md is usable**
  - Checklist items are actionable
  - Commands work as expected
  - Expected results are clear

### 13. Code Comments

- [ ] **Workflow has clear comments**
  - Each major section is commented
  - Complex logic is explained
  - URLs are documented

---

## Monitoring and Alerts

### 14. Notification Setup

- [ ] **Email notifications work**
  - Failure notifications are received
  - Success notifications can be enabled (if desired)

- [ ] **Status badge is accurate**
  - Badge shows current workflow status
  - Updates after each run

### 15. Logging Quality

- [ ] **Logs are searchable**
  - Can search for "404" to find errors
  - Can search for "Successfully downloaded" to verify success

- [ ] **Log grouping works**
  - `::group::` sections collapse properly
  - Makes logs easier to read

---

## Regression Prevention

### 16. Version Control

- [ ] **Workflow is in version control**
  - File is tracked by git
  - Changes are committed
  - History is preserved

- [ ] **Changes are documented**
  - Commit messages are clear
  - PR descriptions explain changes
  - Documentation is updated

### 17. Review Process

- [ ] **Changes are peer-reviewed** (if applicable)
  - At least one approval
  - No unaddressed comments

- [ ] **Tests pass before merge**
  - Manual test run successful
  - No known issues

---

## Final Sign-Off

### 18. Deployment Complete

Date: ******\_\_\_\_******

Validated by: ******\_\_\_\_******

- [ ] **All pre-deployment checks passed**
- [ ] **All post-deployment checks passed**
- [ ] **No outstanding issues**
- [ ] **Documentation is complete**
- [ ] **Monitoring is in place**

**Status:**

- [ ] ✅ APPROVED - Ready for production
- [ ] ⚠️ APPROVED WITH NOTES - See comments below
- [ ] ❌ NOT APPROVED - Issues must be resolved

**Notes:**

```
[Add any notes, issues, or follow-up items here]



```

---

## Appendix: Quick Test Commands

### Test URL Manually

```bash
curl -fsSL "https://raw.githubusercontent.com/ehanc69/ShadowTag-v2-policy/main/policy/config/strict_policy.yml" | head -20
```

### Verify No refs/heads

```bash
grep -r "refs/heads" .github/workflows/ || echo "✓ No refs/heads found"
```

### Test with Verbose Output

```bash
curl -v "https://raw.githubusercontent.com/ehanc69/ShadowTag-v2-policy/main/policy/config/strict_policy.yml"
```

### Validate YAML Syntax

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ingest.yml'))" && echo "✓ Valid YAML"
```

### Check Workflow Status

```bash
gh run list --workflow=ingest.yml --limit 5
```

### Watch Live Execution

```bash
gh run watch
```

---

**Checklist Version:** 1.0.0
**Last Updated:** 2025-11-18
**Applies to:** Ingestion Workflow Fix
