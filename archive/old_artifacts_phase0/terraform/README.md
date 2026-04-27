# Infrastructure as Code — Top-Level README

# 🏗️ Terraform & IaC

Infrastructure as Code for the ShadowTag monorepo. Three pillars:

## Directory Structure

```
terraform/
├── infrastructure-catalog-gcp-cloud-run/  # Reusable modules (10 modules)
│   ├── cloud-run-service/                 # Cloud Run v2 service
│   ├── iam-baseline/                      # Least-privilege IAM
│   ├── artifact-registry/                 # Container registry
│   ├── monitoring-alerts/                 # SLO alerts + uptime
│   ├── firestore-backup-verify/           # Backup + verification
│   ├── cloud-sql/                         # PostgreSQL (planned)
│   ├── github-wif/                        # Workload Identity Federation
│   ├── cloud-scheduler/                   # Cron jobs
│   ├── cost-dashboard/                    # Cost monitoring
│   └── secret-manager/                    # Secret Manager
├── infrastructure-live-gcp/               # Terragrunt environments
│   ├── terragrunt.hcl                     # Root config (GCS state, provider)
│   ├── prod/                              # Production stacks
│   │   ├── counselconduit/
│   │   ├── kovelai-monitoring/
│   │   └── github-wif/
│   └── staging/                           # Staging stacks
├── infrastructure-pulumi/                 # Pulumi experiments (R&D)
├── Makefile                               # Common operations
├── CODEOWNERS                             # Review ownership
└── .pre-commit-config.yaml                # Checkov + format hooks
```

## Quick Start

```bash
# Validate all modules
make validate

# Run security scan
make checkov

# Plan production changes
make plan

# Format all files
make fmt
```

## Tools Required

| Tool | Version | Purpose |
|------|---------|---------|
| OpenTofu | ≥1.9.0 | Terraform-compatible IaC runtime |
| Terragrunt | ≥1.0.0 | DRY configuration + remote state |
| Checkov | ≥3.2.0 | Security policy scanning |
| gcloud | latest | GCP CLI for auth + bucket mgmt |

## State Management

State is stored in GCS bucket `shadowtag-omega-v4-tfstate` with:
- Versioning enabled (rollback on corrupt state)
- Uniform bucket-level access (no ACLs)
- Public access prevention enforced

## Security

- All modules pass Checkov scans
- WIF eliminates long-lived service account keys
- Pre-commit hooks block unscanned code
- CODEOWNERS require review for security-sensitive modules
