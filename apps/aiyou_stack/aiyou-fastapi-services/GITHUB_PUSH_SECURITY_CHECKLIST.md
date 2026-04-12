# GitHub Push Security Checklist

## Pre-Push Security Audit

### 1. Secret Detection

Run these commands before ANY push:

```bash
# Find hardcoded API keys
grep -rn "API_KEY\|api_key\|apikey" --include="*.py" --include="*.sh" --include="*.js" --include="*.ts" | grep -v ".env" | grep -v "os.environ" | grep -v "process.env"

# Find potential secrets
grep -rn "secret\|password\|token\|credential" --include="*.py" --include="*.sh" --include="*.js" --include="*.ts" | grep -v ".env" | grep -v "os.environ" | grep -v "process.env" | grep -v ".example"

# Find private keys
find . -name "*.pem" -o -name "*.key" -o -name "id_rsa*" -o -name "*.p12" -o -name "*.pfx" 2>/dev/null

# Find .env files that shouldn't be committed
find . -name ".env" -o -name ".env.local" -o -name ".env.production" 2>/dev/null
```

### 2. Verify .gitignore

Ensure these patterns are in `.gitignore`:

```gitignore
# Secrets
.env
.env.*
!.env.example
*.pem
*.key
id_rsa*
*.p12
*.pfx
credentials.json
service-account*.json

# Generated
__pycache__/
*.pyc
node_modules/
dist/
build/
.pytest_cache/
.venv/
venv/

# IDE
.idea/
.vscode/settings.json
*.swp

# OS
.DS_Store
Thumbs.db
```

### 3. Sensitive Files Requiring Review

| File | Issue | Required Action |
|------|-------|-----------------|
| `agents/autoresearch.py` | XAI_API_KEY, GEMINI_API_KEY, ANTHROPIC_API_KEY | Verify uses `os.environ.get()` |
| `agents/autoresearch2.py` | Multiple API key references | Verify uses `os.environ.get()` |
| `agents/cloudcode_client.py` | GOOGLE_API_KEY | Verify uses `os.environ.get()` |
| `agents/gemini_executor.py` | GEMINI_API_KEY | Verify uses `os.environ.get()` |
| `agents/swarm_boss.py` | GEMINI_API_KEY | Verify uses `os.environ.get()` |
| `agents/jura_protocol.py` | GEMINI_API_KEY | Verify uses `os.environ.get()` |
| `agents/llm_chorus.py` | Multiple LLM API keys | Verify uses `os.environ.get()` |
| `api/swarm_endpoint.py` | Auth API keys | Verify uses `os.environ.get()` |
| `api/n-autoresearch/Kosmos/BioAgents_api.py` | Auth API keys | Verify uses `os.environ.get()` |
| `api/enterprise_compliance_api.py` | Auth API keys | Verify uses `os.environ.get()` |
| `terraform/secrets.tf` | GCP Secret Manager | Never commit actual secret values |
| `setup_stripe.sh` | Stripe API key | Parameterize or use .env |
| `scripts/*.sh` | Project IDs | Parameterize with variables |

### 4. Files to NEVER Commit

- [ ] `.env` (use `.env.example` instead)
- [ ] `credentials.json` (GCP service account)
- [ ] `service-account-*.json`
- [ ] Any `*.pem` or `*.key` files
- [ ] `terraform.tfstate` (use remote backend)
- [ ] `terraform.tfstate.backup`

### 5. Pre-Commit Hooks

Install pre-commit to automate checks:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials
      - id: check-added-large-files

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

### 6. Per-Repository Checklist

Before pushing to each proposed repo:

#### shadowtag_v4-agent-swarm

- [ ] Verified all API keys use `os.environ.get()`
- [ ] Created `.env.example` with placeholder values
- [ ] Documented required environment variables in README
- [ ] Added API key validation on startup

#### shadowtag_v4-governance-engine

- [ ] Verified JURA protocol secret handling
- [ ] Added audit logging for sensitive operations
- [ ] Documented risk band thresholds

#### shadowtag_v4-infrastructure

- [ ] Parameterized all GCP project IDs
- [ ] Verified terraform/secrets.tf has no actual values
- [ ] Configured Terraform remote state backend
- [ ] Added state locking configuration

#### shadowtag_v4-pinkln-reasoning

- [ ] Added input validation for prompts
- [ ] Documented prompt injection protections

#### shadowtag_v4-media-edge

- [ ] Verified no secrets in Rust code
- [ ] Documented CDN authentication requirements

#### shadowtag_v4-corp-engine

- [ ] Created `.env.example` for Stripe credentials
- [ ] Added audit logging for financial operations
- [ ] Reviewed legal documents for PII

#### shadowtag_v4-dev-tools

- [ ] Documented required environment variables
- [ ] Added validation for external tool dependencies

## Post-Push Verification

After pushing, verify:

1. **GitHub Secret Scanning**: Check if GitHub detected any secrets
2. **Branch Protection**: Ensure main branch requires PR reviews
3. **CI/CD Secrets**: Use GitHub Secrets for CI/CD, not hardcoded values

## Emergency: Secret Leaked

If a secret was accidentally committed:

1. **Immediately rotate the secret** (generate new API key)
2. **Remove from history**: Use `git filter-branch` or BFG Repo-Cleaner
3. **Force push** (requires admin approval)
4. **Audit access logs** for the compromised secret

```bash
# Using BFG Repo-Cleaner (faster than filter-branch)
bfg --delete-files .env
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force
```

---

*Last updated: 2025-11-29*
*Generated by GitHub Script Discovery Agent*
