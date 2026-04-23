---
name: GitHub App Short-Lived Token Push
description: >
  Pushes all git changes to https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git
  using ephemeral GitHub App installation tokens (60-minute TTL) instead of PATs or SSH keys.
  Uses peter-murray/workflow-application-token-action@v4 for CI/CD and scripts/auth_github_app.py
  for local agent pushes. Zero long-lived credentials in the pipeline.
---

# GitHub App Short-Lived Token Push

## TL;DR

Push to `https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git` using a
**1-hour ephemeral installation token** generated from the GitHub App PEM key.
Never use PATs, never use `gh auth login`, never embed long-lived credentials.

## Why GitHub Apps Over PATs

| Feature | PAT (Classic) | PAT (Fine-Grained) | GitHub App Token |
|---------|---------------|---------------------|------------------|
| TTL | Indefinite or configurable | Configurable | **60 minutes (automatic)** |
| Scope | User-wide | Repo-scoped | **Installation-scoped** |
| Identity | Tied to user | Tied to user | **Bot identity** |
| CI/CD safe | ❌ Stale creds | ⚠️ Rotation needed | **✅ Generated at runtime** |
| Downstream triggers | ❌ `GITHUB_TOKEN` blocks | ❌ Same | **✅ Triggers downstream workflows** |
| Rotation | Manual | Manual | **Automatic per-request** |

## Canonical Credentials

```yaml
GitHub App: antigravity-shadowtag-manager
App ID: 3018200
Client ID: Iv23ctYqrxPQIt2ir8gY
Installation ID: 114307210  # ShadowTag-v2 org
PEM Location: 5-tier fallback chain (see below)
Repo: https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git
SSH: git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git
```

## PEM Fallback Chain (Priority Order)

1. **GCP Secret Manager**: `github-app-shadowtag-v2-pem` in project `shadowtag-omega-v4`
2. **`keys/`**: `${REPO_ROOT}/keys/shadowtag-manager.pem`
3. **`~/Downloads/`**: `antigravity-shadowtag-manager.2026-03-17.private-key.pem`
4. **`~/.ssh/`**: Same filename
5. **`$SHADOWTAG_PEM`**: Environment variable pointing to PEM file

## Local Push (Agent / Developer)

### Quick Push
```bash
# Generate token + set HTTPS remote + push main
python scripts/auth_github_app.py --push
```

### Step-by-Step
```bash
# 1. Generate and cache token (1hr TTL, cached at /tmp/gh_token_shadowtag.txt)
python scripts/auth_github_app.py --refresh

# 2. Token is automatically injected into git remote URL via _update_remote_url()
# 3. Push normally
git push origin main
```

### Export Token
```bash
# Export GITHUB_TOKEN for other tools
source <(python scripts/auth_github_app.py --export)
```

## CI/CD Pipeline (GitHub Actions)

### Workflow: Token Generation + Push

Uses `peter-murray/workflow-application-token-action@v4` to generate a scoped
installation token at runtime. Token is **never stored** — it exists only for
the duration of the workflow job and expires after 60 minutes.

```yaml
name: Secure Push with GitHub App Token
on:
  workflow_dispatch:
  push:
    branches: [main]

jobs:
  secure-push:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Generate Short-Lived Token
        id: get_token
        uses: peter-murray/workflow-application-token-action@v4
        with:
          application_id: ${{ secrets.GH_APP_ID }}
          application_private_key: ${{ secrets.GH_APP_PRIVATE_KEY }}
          organization: ShadowTag-v2
          permissions: "contents:write,pull_requests:write"
          revoke_token: true  # Auto-revoke after job completes

      - name: Checkout with App Token
        uses: actions/checkout@v4
        with:
          token: ${{ steps.get_token.outputs.token }}

      - name: Push Changes
        run: |
          git config user.name "antigravity-shadowtag-manager[bot]"
          git config user.email "3018200+antigravity-shadowtag-manager[bot]@users.noreply.github.com"
          git push origin main
        env:
          GITHUB_TOKEN: ${{ steps.get_token.outputs.token }}
```

### Required GitHub Secrets

Set these in `Settings → Secrets and variables → Actions` for the ShadowTag-v2 org
or the Monorepo-Uphillsnowball repo:

| Secret | Value |
|--------|-------|
| `GH_APP_ID` | `3018200` |
| `GH_APP_PRIVATE_KEY` | Contents of the `.pem` file (raw PEM, not base64) |

### Token Revocation

Setting `revoke_token: true` in the action ensures the installation token is
**immediately invalidated** after the job completes. This is a defense-in-depth
measure — even if logs are compromised, the token is already dead.

## GitHub App Permissions (as-configured)

The following permissions are set on the `antigravity-shadowtag-manager` app:

### Repository Permissions
| Permission | Access | Purpose |
|-----------|--------|---------|
| Actions | Read & Write | Trigger/manage workflows |
| Contents | Read & Write | Push code, create releases |
| Pull Requests | Read & Write | Create/merge PRs |
| Commit Statuses | Read & Write | Set CI status checks |
| Code Scanning Alerts | Read & Write | Security scan results |
| Workflows | Read & Write | Modify workflow files |
| Events | Read Only | Webhook event monitoring |

### Organization Permissions
| Permission | Access | Purpose |
|-----------|--------|---------|
| Secrets | Read Only | Access org-level secrets in pipelines |

## Prohibited Actions (ABSOLUTE)

- ❌ **`gh auth login`** — Creates stale OAuth tokens. BANNED.
- ❌ **Personal Access Tokens (PATs)** — User-tied, over-privileged. BANNED.
- ❌ **Deploy Keys** — Static SSH keys. Use GitHub Apps instead.
- ❌ **macOS Keychain GitHub entries** — Stale credential source. Keep purged.
- ❌ **`.env` files with tokens** — Secrets Manager only.
- ❌ **Hardcoded tokens in workflow files** — Use `${{ secrets.* }}` only.

## How JWT Authentication Works

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│  PEM Key    │────▶│  JWT (10min) │────▶│  Installation  │
│  (static)   │     │  RS256 signed │     │  Token (60min) │
└─────────────┘     └──────────────┘     └────────────────┘
                         │                       │
                    POST /app/installations      │
                    /{id}/access_tokens           │
                         │                       ▼
                         │              git push (HTTPS)
                         │              x-access-token:{token}
                         │              @github.com/...
                         ▼
                    api.github.com
```

1. **PEM → JWT**: `auth_github_app.py` signs a 10-minute JWT using the PEM private key
2. **JWT → Installation Token**: POST to GitHub API creates a 60-minute scoped token
3. **Token → Git Push**: HTTPS remote URL is rewritten with `x-access-token:{token}@github.com/`
4. **Token Expires**: After 60 minutes (or revoked immediately in CI via `revoke_token: true`)

## Reference Implementations

| Repo | Purpose |
|------|---------|
| `peter-murray/workflow-application-token-action@v4` | GitHub Action for CI/CD token generation |
| `OctopusDeploy/login` | Similar pattern for Octopus Server auth |
| `scripts/auth_github_app.py` | Local Python JWT generator with 5-tier PEM fallback |

## Atlassian / JIRA Integration Note

If connecting to JIRA Cloud via this GitHub App:
1. Homepage URL can be `https://github.com/ShadowTag-v2`
2. **Uncheck** the "Active" webhook checkbox unless connecting to JIRA/third-party tools
3. Generate a separate private key for JIRA integration (key rotation isolation)
4. Store PEM in org secrets with `secrets:read-only` permission

## Troubleshooting

### "Resource not accessible by integration"
→ The GitHub App is not installed on the target repo. Go to Settings → GitHub Apps → Configure.

### "Bad credentials"
→ PEM key mismatch or JWT expired. Run `python scripts/auth_github_app.py --refresh`.

### "SSH Permission denied (publickey)"
→ SSH key not loaded. This skill uses **HTTPS with token**, not SSH. Run:
```bash
python scripts/auth_github_app.py --push
```

### Token cache stale
→ Delete cache and regenerate:
```bash
rm -f /tmp/gh_token_shadowtag.txt /tmp/gh_token_shadowtag_exp.txt
python scripts/auth_github_app.py --refresh
```
