# Terraform Reference Repos (shallow clones)

Cloned with `git clone --depth 1` for local study. Not committed to monorepo.
Status: `reference_only` in `fold_in_checklist.yaml`.

## GoogleCloudPlatform
| Repo | Local Path | Primary Use |
|---|---|---|
| terraformer | googlecloudplatform/terraformer | Reverse-TF existing infra |
| microservices-demo | googlecloudplatform/microservices-demo | GKE service mesh patterns |
| gcp-hardening-toolkit | googlecloudplatform/gcp-hardening-toolkit | IAM least-priv + hardening |
| cloud-foundation-fabric | googlecloudplatform/cloud-foundation-fabric | Official GCP modules (Cloud Run v2 source) |
| terraform-google-vertex-ai | googlecloudplatform/terraform-google-vertex-ai | Vertex AI infra patterns |
| genai-factory | googlecloudplatform/genai-factory | GenAI GCP patterns |
| magic-modules | googlecloudplatform/magic-modules | Provider source + GCP resource specs |
| click-to-deploy-solutions | googlecloudplatform/click-to-deploy-solutions | Quickstart blueprints |

## Gruntwork
| Repo | Local Path | Primary Use |
|---|---|---|
| terragrunt-infrastructure-catalog-example | gruntwork/terragrunt-infrastructure-catalog-example | Catalog pattern (used in infrastructure-catalog-gcp-cloud-run) |
| terragrunt-infrastructure-live-example | gruntwork/terragrunt-infrastructure-live-example | Live repo pattern |
| terragrunt-infrastructure-live-stacks-example | gruntwork/terragrunt-infrastructure-live-stacks-example | Stacks pattern (2026) |
| runbooks-infrastructure-live-example | gruntwork/runbooks-infrastructure-live-example | Runbook integration |
| terragrunt | gruntwork/terragrunt | Terragrunt source + docs |
| pipelines-workflows | gruntwork/pipelines-workflows | CI/CD pipeline patterns |

## HashiCorp
| Repo | Local Path | Primary Use |
|---|---|---|
| terraform | hashicorp/terraform | Core TF source + provider API reference |

## Community
| Repo | Local Path | Primary Use |
|---|---|---|
| devops-exercises | community/devops-exercises | IaC patterns + exercises |
| 90DaysOfDevOps | community/90DaysOfDevOps | Terraform day-by-day learning |
| terraform-zero-to-hero | community/terraform-zero-to-hero | Structured TF curriculum |

## How to refresh
```bash
cd reference_architectures/terraform
for d in googlecloudplatform gruntwork hashicorp community; do
  for repo in $d/*/; do
    echo "Updating $repo..."
    git -C "$repo" fetch --depth 1 origin HEAD && git -C "$repo" reset --hard FETCH_HEAD
  done
done
```
