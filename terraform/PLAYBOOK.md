# Cor. Comprehensive Terraform Workflow Playbook
## Refactoring Inherited Codebases — 2026 Edition

> Based on @brankopetric00's Feb 22 2026 thread + community replies.
> Refined and extended for the Antigravity / Shadowtag-v2 monorepo.

---

## Phase 0: Preparation (1–2 hours)

1. Clone repo, run `tofu init` + `tofu plan` to establish baseline.
2. Install pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.95.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terragrunt_fmt
      - id: terragrunt_validate
```

3. Add Checkov / tfsec for policy-as-code scanning.

---

## Phase 1: State Management (Fixes #1, #2, #7)

**Goal:** Never store state locally or in Git again.

1. Choose remote backend: GCS (GCP), S3 + DynamoDB (AWS), or Terraform Cloud.
2. Migrate state: `tofu init -migrate-state`
3. Split monolithic state into workspaces per environment + per module (`network/`, `compute/`, `data/`).
4. Enable state locking.
5. Drift detection: run `tofu plan` in CI nightly, alert on changes.
6. **After every `apply`**, immediately run `tofu plan` again to catch partial failures.

---

## Phase 2: Code Organization & Modularity (Fixes #3, #4)

**Standard project layout:**

```
├── modules/
│   ├── vpc/
│   ├── cloud-run-service/
│   └── cloud-sql/
├── environments/
│   ├── dev/
│   ├── staging/
│   └── prod/
├── variables.tf
├── terraform.tfvars     # NEVER commit secrets
└── versions.tf
```

**Validation blocks on every variable:**

```hcl
variable "instance_type" {
  type = string
  validation {
    condition     = can(regex("^t[2-4]", var.instance_type))
    error_message = "Instance type must be t2/t3/t4 family."
  }
}
```

---

## Phase 3: Versioning & Reproducibility (Fix #5)

```hcl
# versions.tf
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
```

Pin provider versions. Commit `terraform.lock.hcl` to Git.

---

## Phase 4: Tagging Strategy (Fix #8)

```hcl
provider "google" {
  default_tags {
    tags = {
      Environment = var.env
      ManagedBy   = "opentofu"
      Repo        = "https://github.com/ShadowTag-v2/Monorepo-Uphillsnowball"
      Owner       = "platform-team"
    }
  }
}
```

---

## Phase 5: CI/CD Pipeline (Fix #9) — Mandatory

```yaml
# .github/workflows/terraform.yml
name: OpenTofu CI/CD
on: [push, pull_request]
jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: opentofu/setup-opentofu@v1
        with: { tofu_version: 1.9.0 }
      - run: tofu init
      - run: tofu validate
      - run: tofu fmt -check
      - run: tofu plan -out=plan.tfplan
        if: github.ref == 'refs/heads/main'
      - run: tofu apply "plan.tfplan"
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**NEVER** run `tofu apply` locally on production branches.

---

## Phase 6: Operational Safety (Fixes #6, #10)

1. Block merges without plan approval in PRs.
2. **Never** use `--auto-approve` in CI (especially prod).
3. Pre-commit + lint on every commit.
4. Post-apply plan check — fail pipeline if output != "No changes".
5. Use Atlantis / Terraform Cloud run tasks for locking + approval.

---

## Phase 7: Continuous Improvement & Governance

- Weekly Terraform health dashboard (state file count, drift count, module reuse %).
- Quarterly refactor sprint dedicated to these fixes.
- Enforce via policy-as-code (Checkov, OPA, Sentinel).
- Document in README + runbooks.

---

## IaC Tools Decision Matrix (2026)

| Tool         | License    | Best For                              | Recommendation               |
|---|---|---|---|
| **OpenTofu** | MPL 2.0    | Terraform drop-in, no vendor lock     | ✅ Default for this monorepo |
| **Terraform**| BSL        | Existing HCL teams, Registry modules | OK if already invested        |
| **Terragrunt**| Apache 2.0 | DRY at scale (100+ accounts/envs)   | ✅ Add on top of OpenTofu     |
| **Pulumi**   | Apache 2.0 | Dev-heavy teams wanting real code    | Use for complex logic         |
| **Crossplane**| CNCF       | K8s-native platform engineering      | If K8s-first                 |

---

## Expected Outcomes After 4–6 Weeks

- [ ] Zero local state files
- [ ] State files < 1 MB each
- [ ] 90%+ of resources in modules
- [ ] All plans reviewed + approved
- [ ] Zero `--auto-approve` in prod
- [ ] Full audit trail and tagging
- [ ] New team onboards in < 1 day

---

## Repo Structure (this monorepo)

```
terraform/
├── PLAYBOOK.md                              ← This file
├── infrastructure-catalog-gcp-cloud-run/    ← Reusable OpenTofu modules
│   └── modules/
│       ├── cloud-run-service/               ← Gen2, VPC, probes, traffic split
│       ├── cloud-run-vpc-connector/         ← Private networking
│       ├── cloud-run-iam/                   ← Flexible role bindings
│       ├── cloud-run-secrets/               ← Secret Manager integration
│       └── cloud-deploy-canary-pipeline/    ← Progressive delivery
├── infrastructure-live-gcp/                 ← Terragrunt live configs (GCS backend)
│   ├── root.hcl
│   ├── non-prod/
│   └── prod/
└── infrastructure-pulumi/                   ← Pulumi TypeScript monorepo
    ├── packages/gcp-cloud-run/src/          ← Reusable components
    └── stacks/dev|prod/                     ← Stack entrypoints
```

Reference repos: `reference_architectures/terraform/`
