## Requirements

No requirements.

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_google"></a> [google](#provider\_google) | 7.29.0 |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [google_iam_workload_identity_pool.github](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iam_workload_identity_pool) | resource |
| [google_iam_workload_identity_pool_provider.github](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/iam_workload_identity_pool_provider) | resource |
| [google_project_iam_member.github_actions_roles](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/project_iam_member) | resource |
| [google_service_account.github_actions](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account) | resource |
| [google_service_account_iam_member.sa_level_roles](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |
| [google_service_account_iam_member.wif_binding](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/service_account_iam_member) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_github_org"></a> [github\_org](#input\_github\_org) | GitHub organization name. | `string` | `"ShadowTag-v2"` | no |
| <a name="input_github_repo"></a> [github\_repo](#input\_github\_repo) | GitHub repository name. | `string` | `"Monorepo-Uphillsnowball"` | no |
| <a name="input_pool_id"></a> [pool\_id](#input\_pool\_id) | Workload Identity Pool ID. | `string` | `"github-actions-pool"` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_project_number"></a> [project\_number](#input\_project\_number) | GCP project number. | `string` | n/a | yes |
| <a name="input_provider_id"></a> [provider\_id](#input\_provider\_id) | Workload Identity Provider ID. | `string` | `"github-actions-provider"` | no |
| <a name="input_roles"></a> [roles](#input\_roles) | IAM roles to grant the GitHub Actions service account. | `list(string)` | <pre>[<br/>  "roles/run.admin",<br/>  "roles/iam.serviceAccountUser",<br/>  "roles/artifactregistry.writer",<br/>  "roles/clouddeploy.operator",<br/>  "roles/monitoring.viewer"<br/>]</pre> | no |
| <a name="input_service_account_id"></a> [service\_account\_id](#input\_service\_account\_id) | Service account for GitHub Actions. | `string` | `"github-actions-sa"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_service_account_email"></a> [service\_account\_email](#output\_service\_account\_email) | GitHub Actions SA email — use as WIF\_SA secret in GitHub. |
| <a name="output_workload_identity_provider"></a> [workload\_identity\_provider](#output\_workload\_identity\_provider) | Full WIF provider resource name — use as WIF\_PROVIDER secret in GitHub. |
