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
| [google_monitoring_alert_policy.firestore_spike](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_alert_policy) | resource |
| [google_monitoring_alert_policy.uptime_failure](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_alert_policy) | resource |
| [google_monitoring_notification_channel.email](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_notification_channel) | resource |
| [google_monitoring_uptime_check_config.health](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_uptime_check_config) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_admin_email"></a> [admin\_email](#input\_admin\_email) | Admin email for alert notifications. | `string` | `"admin@shadowtagai.com"` | no |
| <a name="input_enable_firestore_alert"></a> [enable\_firestore\_alert](#input\_enable\_firestore\_alert) | Enable Firestore write spike alert. | `bool` | `true` | no |
| <a name="input_enable_uptime_check"></a> [enable\_uptime\_check](#input\_enable\_uptime\_check) | Enable HTTPS uptime check. | `bool` | `true` | no |
| <a name="input_firestore_write_threshold"></a> [firestore\_write\_threshold](#input\_firestore\_write\_threshold) | Firestore writes/min threshold for alerting. | `number` | `50000` | no |
| <a name="input_health_check_path"></a> [health\_check\_path](#input\_health\_check\_path) | Health check endpoint path. | `string` | `"/health"` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_service_host"></a> [service\_host](#input\_service\_host) | Hostname for uptime checks (e.g. counselconduit-767252945109.us-central1.run.app). | `string` | n/a | yes |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Service name for alert naming. | `string` | n/a | yes |
| <a name="input_uptime_check_period"></a> [uptime\_check\_period](#input\_uptime\_check\_period) | Uptime check interval. | `string` | `"60s"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_notification_channel"></a> [notification\_channel](#output\_notification\_channel) | The email notification channel. |
| <a name="output_notification_channel_name"></a> [notification\_channel\_name](#output\_notification\_channel\_name) | Notification channel resource name for use in other modules. |
