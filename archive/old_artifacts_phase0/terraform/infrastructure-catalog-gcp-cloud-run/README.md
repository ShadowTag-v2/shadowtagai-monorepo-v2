# Infrastructure Catalog — Module Catalog README
# Generated: 2026-04-21

# 🏗️ Infrastructure Catalog (GCP Cloud Run)

Reusable, Checkov-compliant OpenTofu/Terraform modules for the ShadowTag monorepo.

## Module Index

| Module | Purpose | Status |
|--------|---------|--------|
| [cloud-run-service](./cloud-run-service/) | Cloud Run v2 service with IAM, domain, scaling | ✅ Active |
| [iam-baseline](./iam-baseline/) | Least-privilege SA + custom roles | ✅ Active |
| [artifact-registry](./artifact-registry/) | Container image registry | ✅ Active |
| [monitoring-alerts](./monitoring-alerts/) | Uptime checks, SLO alerts, notification channels | ✅ Active |
| [firestore-backup-verify](./firestore-backup-verify/) | Scheduled Firestore exports + failure alerts | ✅ Active |
| [cloud-sql](./cloud-sql/) | Cloud SQL PostgreSQL (future compliance ledger) | 📋 Planned |
| [github-wif](./github-wif/) | Workload Identity Federation for GitHub Actions | ✅ Active |
| [cloud-scheduler](./cloud-scheduler/) | Cron-triggered Cloud Run jobs | ✅ Active |
| [cost-dashboard](./cost-dashboard/) | Cloud Monitoring cost & resource dashboard | ✅ Active |
| [secret-manager](./secret-manager/) | Secret Manager with IAM bindings | ✅ Active |

## Usage

Modules are consumed via Terragrunt in `infrastructure-live-gcp/`:

```hcl
# infrastructure-live-gcp/prod/counselconduit/terragrunt.hcl
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../infrastructure-catalog-gcp-cloud-run//cloud-run-service"
}

inputs = {
  service_name  = "counselconduit"
  image         = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:latest"
  min_instances = 1
  max_instances = 10
}
```

## Security

All modules pass Checkov scans. Run locally:

```bash
make checkov    # Scan all modules
make validate   # Terraform validate
make fmt        # Format check
```

## Environments

| Environment | Path | State Bucket |
|-------------|------|-------------|
| Production | `infrastructure-live-gcp/prod/` | `shadowtag-omega-v4-tfstate` |
| Staging | `infrastructure-live-gcp/staging/` | `shadowtag-omega-v4-tfstate` |

## CI/CD

`.github/workflows/terraform-ci.yml` runs on every PR touching `terraform/`:
1. **Validate** — `tofu fmt` + `tofu validate` on all modules
2. **Security** — Checkov scan with SARIF output
3. **Plan** — Terragrunt plan via WIF (posted as PR comment)
