# Terraform IaC Playbook — ShadowTag Omega v4

> **Generated from**: `Cor. Comprehensive Terraform Workflow` skill (v100%)
> **Stack**: OpenTofu 1.11.5 / Terragrunt 1.0 / Pulumi 3.150
> **Target**: GCP Cloud Run Gen2 (serverless)

## Quick Start

```bash
# 1. Install tools
brew install opentofu tflint pre-commit checkov
pip install pre-commit-terraform

# 2. Init pre-commit
pre-commit install

# 3. Plan (never apply locally in prod)
cd infrastructure-live-gcp/prod/us-central1/counselconduit
terragrunt plan
```

## Architecture

```
terraform/
├── infrastructure-catalog-gcp-cloud-run/   ← reusable modules (versioned)
├── infrastructure-live-gcp/                ← Terragrunt live configs (per-env)
├── infrastructure-pulumi/                  ← TypeScript alternative
├── monitoring.tf                           ← existing Cloud Monitoring alerts
├── runners.tf                              ← GitHub Actions runners
└── PLAYBOOK.md                             ← this file
```

## Module Catalog

| Module | Status | Purpose |
|--------|--------|---------|
| `cloud-run-service` | 📋 Planned | Gen2, probes, secrets, canary traffic |
| `cloud-run-vpc-connector` | 📋 Planned | Private networking |
| `cloud-run-iam` | 📋 Planned | Flexible role bindings |
| `cloud-run-secrets` | 📋 Planned | Secret Manager accessor grants |
| `cloud-armor-waf` | ✅ Created | XSS/SQLi/rate limiting (`infra/cloud-armor/main.tf`) |
| `cloud-deploy-canary-pipeline` | 📋 Planned | Progressive 25→50→75→100% |
| `monitoring-alerts` | ⚠️ Partial | `monitoring.tf` exists, needs modularization |

## Environments

| Env | State Bucket | Min Instances |
|-----|-------------|---------------|
| prod | `shadowtag-omega-v4-tfstate/counselconduit/prod` | 1 |
| staging | `shadowtag-omega-v4-tfstate/counselconduit/staging` | 0 |

## CI/CD

| Workflow | Trigger | Action |
|----------|---------|--------|
| `tofu-ci.yml` | PR | fmt + validate + plan |
| `tofu-apply.yml` | merge to main | apply + post-apply drift check |
| `drift-detection.yml` | nightly 6am UTC | plan -detailed-exitcode |
| `checkov.yml` | PR | policy-as-code scan |

## Runbooks

- **State recovery**: `terraform init -reconfigure` → `terraform import`
- **Module upgrade**: bump version in `terragrunt.hcl` → PR → plan review → apply
- **Drift remediation**: review nightly drift alert → `terragrunt apply` or manual fix
- **Emergency rollback**: `gcloud run services update-traffic --to-revisions=PREVIOUS=100`

## References

- Skill: `skills/terraform-comprehensive-workflow/SKILL.md`
- Reference repos: `reference_architectures/terraform/MANIFEST.md`
- Cloud Armor: `infra/cloud-armor/main.tf`
