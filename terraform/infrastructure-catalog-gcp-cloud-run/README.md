# Infrastructure Catalog — GCP Cloud Run

Production-grade, reusable Terraform modules for GCP Cloud Run and related services.

## Module Catalog

| Module | Description | Status |
|--------|-------------|--------|
| [`cloud-run-service`](./cloud-run-service/) | Gen2 Cloud Run with OTEL, health probes, secrets | ✅ Ready |
| [`cloud-run-vpc-connector`](./cloud-run-vpc-connector/) | Serverless VPC Access connector | ✅ Ready |
| [`cloud-run-iam`](./cloud-run-iam/) | Flexible for_each role bindings | ✅ Ready |
| [`cloud-run-secrets`](./cloud-run-secrets/) | Secret Manager accessor grants | ✅ Ready |
| [`cloud-armor-waf`](./cloud-armor-waf/) | WAF with XSS, SQLi, rate limiting | ✅ Ready |
| [`cloud-deploy-canary-pipeline`](./cloud-deploy-canary-pipeline/) | Progressive 25→50→75→100% rollout | ✅ Ready |
| [`monitoring-alerts`](./monitoring-alerts/) | Uptime checks + Firestore spike alerts | ✅ Ready |
| [`firestore-backup-verify`](./firestore-backup-verify/) | Scheduled exports + failure alerts | ✅ Ready |
| [`github-wif`](./github-wif/) | Workload Identity Federation for GitHub Actions | ✅ Ready |
| [`cloud-sql`](./cloud-sql/) | PostgreSQL with PITR, query insights | 📋 Future |

## Usage

Each module is consumed via Terragrunt in `infrastructure-live-gcp/`:

```hcl
terraform {
  source = "../../../../infrastructure-catalog-gcp-cloud-run//cloud-run-service"
}

inputs = {
  service_name = "my-service"
  image        = "gcr.io/my-project/my-image:latest"
  min_instances = 1
}
```

## Provider Requirements

```hcl
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    google      = { source = "hashicorp/google",      version = "~> 6.0" }
    google-beta = { source = "hashicorp/google-beta",  version = "~> 6.0" }
  }
}
```

## Testing

```bash
cd cloud-run-service
terraform test  # Runs tests/basic.tftest.hcl
```

## Standards

All modules follow these conventions:
- **Variables**: typed, described, validated with `validation {}` blocks
- **Outputs**: full resource + convenience fields (name, ID, URI)
- **Labels**: `managed_by`, `environment`, `service`
- **Lifecycle**: `prevent_destroy` on stateful resources
- **Security**: no inline secrets, Secret Manager references only
- **Docs**: README.md with usage example and input table

## Related

- [Playbook](../PLAYBOOK.md) — operational runbook
- [State Migration Plan](../STATE_MIGRATION_PLAN.md) — import strategy
- [Cost Projection](../COST_PROJECTION.md) — monthly cost analysis
- [Terragrunt Live](../infrastructure-live-gcp/) — environment configs
- [Pulumi Alternative](../infrastructure-pulumi/) — TypeScript IaC
