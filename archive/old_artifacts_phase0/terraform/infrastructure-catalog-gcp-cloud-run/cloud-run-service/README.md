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
| [google_cloud_run_v2_service.main](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloud_run_v2_service) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_concurrency"></a> [concurrency](#input\_concurrency) | Max concurrent requests per instance (80-250 typical). | `number` | `100` | no |
| <a name="input_cpu"></a> [cpu](#input\_cpu) | CPU allocation (e.g. 1000m, 2000m). | `string` | `"1000m"` | no |
| <a name="input_env"></a> [env](#input\_env) | Environment label (prod, staging, dev). | `string` | `"prod"` | no |
| <a name="input_env_vars"></a> [env\_vars](#input\_env\_vars) | Plain-text environment variables. | `map(string)` | `{}` | no |
| <a name="input_health_check_path"></a> [health\_check\_path](#input\_health\_check\_path) | Health check endpoint path. | `string` | `"/health"` | no |
| <a name="input_image"></a> [image](#input\_image) | Container image URI (e.g. us-central1-docker.pkg.dev/project/repo/image:tag). | `string` | n/a | yes |
| <a name="input_ingress"></a> [ingress](#input\_ingress) | Ingress traffic filter. | `string` | `"INGRESS_TRAFFIC_ALL"` | no |
| <a name="input_max_instances"></a> [max\_instances](#input\_max\_instances) | Maximum number of instances. | `number` | `10` | no |
| <a name="input_memory"></a> [memory](#input\_memory) | Memory allocation (e.g. 256Mi, 512Mi, 1Gi). | `string` | `"512Mi"` | no |
| <a name="input_min_instances"></a> [min\_instances](#input\_min\_instances) | Minimum number of instances (0 = scale to zero). | `number` | `0` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP region for the Cloud Run service. | `string` | `"us-central1"` | no |
| <a name="input_secret_env_vars"></a> [secret\_env\_vars](#input\_secret\_env\_vars) | Secret Manager references as name:version (e.g. stripe-key:latest). | `map(string)` | `{}` | no |
| <a name="input_service_account"></a> [service\_account](#input\_service\_account) | Service account email. Empty = default compute SA. | `string` | `""` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Name of the Cloud Run service. | `string` | n/a | yes |
| <a name="input_startup_cpu_boost"></a> [startup\_cpu\_boost](#input\_startup\_cpu\_boost) | Enable startup CPU boost for faster cold starts. | `bool` | `true` | no |
| <a name="input_trace_sample_rate"></a> [trace\_sample\_rate](#input\_trace\_sample\_rate) | OTEL trace sampling rate (0.0-1.0). | `string` | `"0.1"` | no |
| <a name="input_vpc_connector"></a> [vpc\_connector](#input\_vpc\_connector) | VPC connector name for private networking. | `string` | `""` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_latest_revision"></a> [latest\_revision](#output\_latest\_revision) | Latest ready revision name. |
| <a name="output_service"></a> [service](#output\_service) | The Cloud Run v2 service resource. |
| <a name="output_service_name"></a> [service\_name](#output\_service\_name) | Cloud Run service name. |
| <a name="output_uri"></a> [uri](#output\_uri) | The URL of the Cloud Run service. |
