# AGNT_OS Terraform / OpenTofu Playbook

This playbook eliminates the 10 common mistakes highlighted in Branko Petric's Feb 2026 thread.

## Core Rules

- Remote state only (GCS)
- Modules over god-modules
- Validation blocks everywhere
- Mandatory plan review in PRs
- Post-apply drift check
- No `--auto-approve` in production
- Strict tagging policy
- Pre-commit + lint on every commit

## Recommended Stack (2026)

- **OpenTofu + Terragrunt** — for ops teams
- **Pulumi** — for developer teams
- Run both side-by-side during migration

## Crossplane Comparison (2026)

| Criteria                    | **Pulumi**                              | **Crossplane**                              | Winner      |
|----------------------------|-----------------------------------------|---------------------------------------------|-------------|
| **Learning Curve**         | Medium (if you know programming)        | Steep (Kubernetes CRDs + composition)       | Pulumi      |
| **Cloud Run Support**      | Excellent + easy canary                 | Good (via Composition + XRDs)               | Pulumi      |
| **Composability**          | Components (TypeScript/Python)          | Compositions + XRDs                         | Tie         |
| **GitOps Native**          | Good (with Pulumi Kubernetes Operator)  | **Excellent** (native Kubernetes)           | Crossplane  |
| **Observability**          | Built-in AlertPolicies + OTEL           | Requires extra setup                        | Pulumi      |
| **Team Fit**               | Software engineers + platform teams     | Platform engineering / K8s-heavy teams      | Depends     |

**Recommendation**: Use **Pulumi** for Cloud Run + canary + observability. Use **Crossplane** if you're heavily invested in Kubernetes control planes.

## Canary Deployment Strategy

### OpenTofu / Terragrunt

- Use `cloud-deploy-canary-pipeline` module
- Trigger via GitHub Actions `repository_dispatch`
- Progressive 25% → 50% → 75% → 100% with verification gate

### Pulumi

- Use `CloudDeployCanaryPipeline` component
- Same GitHub Actions dispatch pattern
- Native TypeScript control over percentages and verification

## Key Repos (Side-by-Side)

| Repo | Purpose | IaC Tool |
|------|---------|----------|
| `infrastructure-catalog-gcp-cloud-run` | Reusable Cloud Run modules | OpenTofu |
| `infrastructure-live-gcp` | Live Terragrunt configuration | Terragrunt |
| `infrastructure-pulumi` | Pulumi TypeScript monorepo | Pulumi |

## X Search Insights (May 2026)

- Pulumi is frequently praised for developer experience and real code
- Crossplane is popular in Kubernetes-native platform teams
- Cloud Run canary deployments are commonly done via **Cloud Deploy** (both OpenTofu and Pulumi integrate well)
- Many teams run **Pulumi + Cloud Deploy** together for progressive delivery
