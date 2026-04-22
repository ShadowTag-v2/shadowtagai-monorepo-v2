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
| [google_monitoring_dashboard.cost_dashboard](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_dashboard) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_service_names"></a> [service\_names](#input\_service\_names) | Cloud Run service names to monitor. | `list(string)` | <pre>[<br/>  "counselconduit"<br/>]</pre> | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_dashboard_id"></a> [dashboard\_id](#output\_dashboard\_id) | Monitoring dashboard resource ID. |
