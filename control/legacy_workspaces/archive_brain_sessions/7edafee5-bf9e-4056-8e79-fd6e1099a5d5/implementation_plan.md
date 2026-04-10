# Stateful Push Resumption & Secret Sanitation Plan

Based on the GitHub Push Protection trigger and the sheer volume of the 23GB monorepo, restarting the push script from scratch loses the previous 13 pushed batches. We need a targeted approach to strip secrets and resume exactly where the upload left off.

## Proposed Changes

### 1. Secret Sanitation (`scripts/sanitize_secrets.sh`)
Instead of manually deleting secrets (which breaks third-party SDKs like `google-cloud-java`), we will use `gitleaks` to globally identify any file containing a secret, and dynamically append those file paths to `.gitignore`. Since these are all test tokens inside `/reference` or `/vendor` directories, ignoring them entirely from the Git history is the safest route without breaking local compilation.

```bash
# 1. Run gitleaks across the workspace
gitleaks detect --no-git -f json -r secrets_report.json

# 2. Extract file paths via jq and append to .gitignore
jq -r '.[].File' secrets_report.json | sort | uniq >> .gitignore
```

### 2. Stateful Chunk Pusher (`scripts/resume_chunked_push.py`)
I will refactor the chunking script so that it **no longer destroys the `.git` directory on execution**.

1. By persisting `.git`, the chunker automatically retains the fact that Batches 1-13 are already pushed to `origin/main`.
2. The script will simply call `git ls-files --others --exclude-standard`, which will strictly return only files that *have not yet been pushed*.
3. It will then batch those remaining files into 90MB commits (Batch 14, 15, 16...) and resume sequential pushing until the payload is 0.

## User Review Required
> [!IMPORTANT]
> Ignoring the secret-bearing files via `.gitignore` means those specific demo files (like `google-cloud-java` test protos and `dev.integrations.yaml`) will not be uploaded to GitHub. They will remain locally on your machine. This is standard practice for test keys, but please confirm this is acceptable before I execute the sanitation.

## Verification Plan

### Automated Verification
* The `gitleaks` script will output the exact number of files it appends to `.gitignore`.
* We will dry-run the Git status to ensure the flagged `dev.integrations.yaml` is now correctly listed as ignored.
* The `resume_chunked_push.py` script will be executed, and we will monitor the output to ensure it successfully starts at Batch 14 and pushes without triggering GitHub Push Protection blocks.
