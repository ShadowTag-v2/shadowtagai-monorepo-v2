# Terraform Reference Architectures — Manifest

> **Purpose**: Read-only shallow clones for pattern extraction, module design, and CI/CD reference.
> **Source**: `Cor. Comprehensive Terraform Workflow` skill + user `/pickle` thread.
> **Cloned**: 2026-04-21, `--depth 1`

## Google Cloud Platform (8 repos)

| Repo | Purpose |
|------|---------|
| `cloud-foundation-fabric` | GCP module gold standard — production-grade Terraform modules |
| `gcp-hardening-toolkit` | Security hardening patterns for GCP infrastructure |
| `microservices-demo` | GKE/Cloud Run microservice deployment patterns |
| `terraformer` | Import existing GCP infra into Terraform state |
| `terraform-google-vertex-ai` | Vertex AI Terraform modules (GenAI infra) |
| `genai-factory` | GenAI application factory patterns |
| `magic-modules` | Google provider auto-generation (understand provider internals) |
| `click-to-deploy-solutions` | Ready-to-deploy GCP solutions (marketplace patterns) |

## Gruntwork (6 repos)

| Repo | Purpose |
|------|---------|
| `terragrunt` | DRY wrapper for Terraform — core tool reference |
| `terragrunt-infrastructure-catalog-example` | Reusable module catalog pattern |
| `terragrunt-infrastructure-live-example` | Live environment configuration pattern |
| `terragrunt-infrastructure-live-stacks-example` | Stacks-based multi-env pattern (newest) |
| `runbooks-infrastructure-live-example` | Operational runbook patterns |
| `pipelines-workflows` | CI/CD pipeline + workflow automation patterns |

## HashiCorp (1 repo)

| Repo | Purpose |
|------|---------|
| `terraform` | Core Terraform source — understand internals, `terraform test` patterns |

## Community (3 repos)

| Repo | Purpose |
|------|---------|
| `devops-exercises` | DevOps/Terraform interview Q&A, concept reference |
| `90DaysOfDevOps` | Comprehensive DevOps learning reference |
| `terraform-zero-to-hero` | Beginner-to-advanced Terraform patterns |

## Usage Rules

1. **Read-only** — never modify source in these repos.
2. **Pattern extraction** — copy patterns into `terraform/infrastructure-catalog-gcp-cloud-run/`.
3. **Not committed** — `.gitignore` excludes all source. Only this MANIFEST is tracked.
4. **Refresh** — `git -C <repo> pull --depth 1` to update any repo.
