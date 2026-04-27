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
| [google_cloud_scheduler_job.jobs](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_scheduler_job) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_jobs"></a> [jobs](#input\_jobs) | Map of Cloud Scheduler jobs to create. | <pre>map(object({<br/>    description = string<br/>    schedule    = string<br/>    time_zone   = optional(string, "America/Los_Angeles")<br/>    uri         = string<br/>    http_method = optional(string, "POST")<br/>    body        = optional(string, "")<br/>    headers     = optional(map(string), {})<br/>    oidc_sa     = optional(string, "")<br/>    oidc_audience = optional(string, "")<br/>    retry_count = optional(number, 1)<br/>    paused      = optional(bool, false)<br/>  }))</pre> | n/a | yes |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP region. | `string` | `"us-central1"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_job_names"></a> [job\_names](#output\_job\_names) | Map of created Cloud Scheduler job names. |
| <a name="output_job_schedules"></a> [job\_schedules](#output\_job\_schedules) | Map of job schedules. |
