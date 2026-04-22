## Requirements

No requirements.

## Providers

| Name | Version |
| ---- | ------- |
| <a name="provider_google"></a> [google](#provider\_google) | n/a |

## Modules

No modules.

## Resources

| Name | Type |
| ---- | ---- |
| [google_cloud_run_v2_service_iam_member.custom](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service_iam_member) | resource |
| [google_cloud_run_v2_service_iam_member.invokers](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service_iam_member) | resource |
| [google_cloud_run_v2_service_iam_member.public](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service_iam_member) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_custom_bindings"></a> [custom\_bindings](#input\_custom\_bindings) | Additional custom IAM bindings. Key is arbitrary label. | <pre>map(object({<br/>    role    = string<br/>    members = list(string)<br/>  }))</pre> | `{}` | no |
| <a name="input_invokers"></a> [invokers](#input\_invokers) | List of members to grant roles/run.invoker (e.g. 'serviceAccount:sa@proj.iam.gserviceaccount.com'). | `list(string)` | `[]` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_public_access"></a> [public\_access](#input\_public\_access) | If true, grants allUsers the invoker role (public access). | `bool` | `false` | no |
| <a name="input_region"></a> [region](#input\_region) | GCP region. | `string` | `"us-central1"` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Cloud Run service name to bind IAM to. | `string` | n/a | yes |

## Outputs

No outputs.
