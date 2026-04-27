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
| [google_clouddeploy_delivery_pipeline.canary](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/clouddeploy_delivery_pipeline) | resource |
| [google_clouddeploy_target.prod](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/clouddeploy_target) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_canary_percentages"></a> [canary\_percentages](#input\_canary\_percentages) | Progressive canary percentages before full rollout. | `list(number)` | <pre>[<br/>  25,<br/>  50,<br/>  75<br/>]</pre> | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP region. | `string` | `"us-central1"` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Cloud Run service name. | `string` | n/a | yes |
| <a name="input_verify"></a> [verify](#input\_verify) | Enable canary verification at each stage. | `bool` | `true` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_pipeline_name"></a> [pipeline\_name](#output\_pipeline\_name) | Cloud Deploy pipeline name. |
| <a name="output_target_name"></a> [target\_name](#output\_target\_name) | Cloud Deploy target name. |
