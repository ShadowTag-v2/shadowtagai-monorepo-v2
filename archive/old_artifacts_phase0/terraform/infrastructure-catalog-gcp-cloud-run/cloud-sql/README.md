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
| [google_sql_database.databases](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database) | resource |
| [google_sql_database_instance.main](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/sql_database_instance) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_availability_type"></a> [availability\_type](#input\_availability\_type) | ZONAL or REGIONAL (HA). | `string` | `"ZONAL"` | no |
| <a name="input_database_version"></a> [database\_version](#input\_database\_version) | Database version (POSTGRES\_16, POSTGRES\_15, MYSQL\_8\_0). | `string` | `"POSTGRES_16"` | no |
| <a name="input_databases"></a> [databases](#input\_databases) | List of databases to create. | `list(string)` | <pre>[<br/>  "default"<br/>]</pre> | no |
| <a name="input_deletion_protection"></a> [deletion\_protection](#input\_deletion\_protection) | Prevent accidental deletion. | `bool` | `true` | no |
| <a name="input_disk_size_gb"></a> [disk\_size\_gb](#input\_disk\_size\_gb) | Storage size in GB. | `number` | `10` | no |
| <a name="input_instance_name"></a> [instance\_name](#input\_instance\_name) | Cloud SQL instance name. | `string` | n/a | yes |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP region. | `string` | `"us-central1"` | no |
| <a name="input_tier"></a> [tier](#input\_tier) | Machine type tier. | `string` | `"db-f1-micro"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_connection_name"></a> [connection\_name](#output\_connection\_name) | Connection name for Cloud SQL proxy. |
| <a name="output_instance"></a> [instance](#output\_instance) | The Cloud SQL instance resource. |
| <a name="output_private_ip"></a> [private\_ip](#output\_private\_ip) | Private IP address. |
