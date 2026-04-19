# CI/CD Workflows — Monorepo-Uphillsnowball

> **Note**: All workflows require GitHub Actions minutes. On the free plan,
> private repos get 2,000 min/month. Runs show `startup_failure` when exhausted.

## Hardening Standards

All workflows enforce:

- **`timeout-minutes`**: Every job has a timeout (5–45m by workflow type)
- **`concurrency`**: Every workflow has `cancel-in-progress: true` to avoid stacking runs
- **`paths` / `paths-ignore`**: Scoped triggers to avoid unnecessary runs on docs-only changes

---

## Workflow Catalog

### Security

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Bandit SAST + Lighthouse | `security-and-lighthouse.yml` | Push/PR `**.py` | SAST scan + performance budget |
| CodeQL Analysis | `codeql-analysis.yml` | Push/PR/Schedule | GitHub native code scanning |
| Security Audit | `security-audit.yml` | Push/PR | Dependency vulnerability audit |
| Firestore Rules Validation | `firestore-rules-validate.yml` | PR `*.rules` | Checks for overly permissive rules |
| Dependency Review | `dependency-review.yml` | PR | License + vulnerability check on deps |

### Quality

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Quality Gate | `quality-gate.yml` | PR `control/pnkln/**` | Ruff + Vulture + pytest |
| Code Quality Gate | `code-quality-gate.yml` | Push/PR `**.py` | Ruff lint/format + Vulture dead code |
| Backend CI | `backend-ci.yml` | Push/PR | uv + ruff + basedpyright |
| Pnkln Governance CI | `pnkln-governance.yml` | Push/PR | Governance checks |
| Code Quality | `code-quality.yml` | Push/PR | Additional quality checks |

### Deployment

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Deploy | `deploy.yml` | Push main + tags | Docker build + Firebase Hosting |
| CD | `cd.yml` | Push main | CD to production |
| Firebase Deploy | `firebase-deploy.yml` | Push main | Firebase-specific deploy |
| Deploy Autoresearch | `deploy-autoresearch.yml` | Push/dispatch | Autoresearch service deploy |
| Deploy Lead Router | `deploy_lead_router.yml` | Push | Lead router service deploy |
| Docker | `docker.yml` | Push/PR | Docker image builds |
| OpenTofu | `opentofu.yml` | PR/Push `infra/**` | Infrastructure plan/apply |

### Testing

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Smoke | `smoke.yml` | Push/PR | File existence + basic test run |
| Endpoint Smoke | `endpoint-smoke.yml` | After deploy / 30min | Live endpoint health checks |
| Coverage | `coverage.yml` | Push/PR | Test coverage reporting |
| Offline Eval | `offline-eval.yml` | PR `tools/eval/**` / daily | Eval pipeline + promotion gate |

### Code Review

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| GCA PR Review | `gca-pr-review.yml` | PR | Gemini-powered 4-agent code review |

### Automation

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Auto Approve | `auto-approve.yml` | PR | Auto-approve Dependabot PRs |
| Conditional Automerge | `conditional-automerge.yml` | PR | Merge when checks pass |
| Dependabot Automerge | `dependabot-automerge.yml` | PR | Auto-merge patch/minor bumps |
| CI Notify | `ci-notify.yml` | Workflow failure | Webhook notification on CI failure |
| Daily Sync | `daily_sync.yml` | Schedule | Daily sync tasks |

### Monitoring

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| PageSpeed Monitor | `pagespeed-monitor.yml` | Push/Schedule | PageSpeed Insights tracking |
| Lighthouse CI | `lighthouse-ci.yml` | Push/PR | Lighthouse performance budget |
| WebPageTest CI | `webpagetest-ci.yml` | Push/PR | WebPageTest benchmarks |

### Governance

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Branch Protection | `branch-protection.yml` | PR | Branch protection verification |
| Make Check PR | `make-check-pr.yml` | PR | Makefile-based PR checks |
| Judge6 YOLO Gate | `judge6_yolo_gate.yml` | PR | Judge #6 policy gate |
| Omega Sync CI | `omega-sync-ci.yml` | Push/PR | Omega sync verification |
| Safety Evidence | `safety-evidence.yml` | Push/PR | Safety evidence collection |

### Special Purpose

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Veo Demo Generator | `veo-demo-generator.yml` | Dispatch | Veo 3.1 video demo generation |
| Gemini Ingestion CI | `gemini-ingestion-ci.yml` | Push/PR | Gemini knowledge ingestion |
| Release | `release.yml` | Push tags | Release automation |
| Antigravity CI | `antigravity_ci.yml` | Push/PR | Antigravity toolchain CI |
| Python 3.14 CI | `python-3.14-ci.yml` | Push/PR | Python 3.14 compatibility |
| Playwright API Limits | `playwright_api_limits.yml` | Push/PR | API rate limit testing |
| Ingest | `ingest.yml` | Dispatch | Data ingestion pipeline |

---

## Secrets Required

| Secret | Used By | Purpose |
|--------|---------|---------|
| `GITHUB_TOKEN` | Most workflows | Auto-provided by GitHub |
| `GEMINI_API_KEY` | GCA review, ingestion | Gemini API access |
| `GH_APP_ID` | GCA review | GitHub App ID (3018200) |
| `GH_APP_PEM` | GCA review | GitHub App private key |
| `FIREBASE_TOKEN` | Firebase deploy | Firebase CLI auth |
| `FIREBASE_SERVICE_ACCOUNT` | Firebase deploy | SA JSON key |
| `DOCKER_USERNAME` | Docker build/push | Docker Hub auth |
| `DOCKER_PASSWORD` | Docker build/push | Docker Hub auth |
| `ANTHROPIC_API_KEY` | Claude workflows | Claude API access |
| `AUTO_APPROVE_PAT` | Auto-approve | PAT for PR approval |
| `CI_NOTIFICATION_WEBHOOK` | CI notify | Slack/Discord webhook URL |

## WIF (Workload Identity Federation)

Deploy workflows use keyless auth via WIF:
- **Pool**: `github-pool` (project 767252945109)
- **Provider**: `github-provider`
- **CI SA**: `github-actions@shadowtag-omega-v4.iam.gserviceaccount.com`
- **Deploy SA**: `github-deployer@shadowtag-omega-v4.iam.gserviceaccount.com`

## Troubleshooting

### `startup_failure` on all runs
GitHub Actions minutes exhausted. Check billing at:
Settings → Billing → Actions

### YAML validation
```bash
python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"
```

### Duplicate detection
```bash
for f in .github/workflows/*.yml; do
  echo "$f: $(grep -c 'concurrency:' $f) concurrency, $(grep -c 'timeout-minutes:' $f) timeout"
done
```
