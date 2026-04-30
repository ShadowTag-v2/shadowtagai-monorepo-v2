# Sovereign Infra TF

> Gideon OS Block 13 — Infrastructure as Code (OpenTofu)

## Purpose

Defines the entire Gideon OS cloud infrastructure as code using OpenTofu. Ensures zero-drift between declared infrastructure and actual GCP state.

## Infrastructure

| Resource | Count | Details |
|----------|-------|---------|
| Cloud Run Services | 2 | counselconduit prod + staging |
| Firestore DBs | 1 | (default) with PITR enabled |
| GCP Secrets | 19 | Rotated quarterly |
| Cloud Scheduler | 5 | Daemon cron triggers |
| Alert Policies | 8 | Latency, error rate, uptime |
| Cloud Armor | 4 | WAF rate limiting + geo blocks |

## Usage

```bash
tofu plan -var-file=environments/prod/terraform.tfvars
tofu apply -var-file=environments/prod/terraform.tfvars
tofu plan -detailed-exitcode  # drift detection
```

## Status

🟢 Active — 0 drift verified.
