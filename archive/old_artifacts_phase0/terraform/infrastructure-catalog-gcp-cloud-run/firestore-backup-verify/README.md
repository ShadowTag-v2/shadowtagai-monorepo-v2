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
| [google_cloud_scheduler_job.firestore_backup](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_scheduler_job) | resource |
| [google_monitoring_alert_policy.backup_failure](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/monitoring_alert_policy) | resource |
| [google_storage_bucket.firestore_backups](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_admin_email"></a> [admin\_email](#input\_admin\_email) | Alert notification email. | `string` | `"admin@shadowtagai.com"` | no |
| <a name="input_backup_bucket"></a> [backup\_bucket](#input\_backup\_bucket) | GCS bucket for Firestore exports. Defaults to {project}-firestore-backups. | `string` | `""` | no |
| <a name="input_database_id"></a> [database\_id](#input\_database\_id) | Firestore database ID. | `string` | `"(default)"` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_schedule"></a> [schedule](#input\_schedule) | Cron schedule for backup (default: 3am UTC daily). | `string` | `"0 3 * * *"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_backup_bucket"></a> [backup\_bucket](#output\_backup\_bucket) | GCS bucket storing Firestore backups. |
| <a name="output_scheduler_job"></a> [scheduler\_job](#output\_scheduler\_job) | Cloud Scheduler job name for backups. |
