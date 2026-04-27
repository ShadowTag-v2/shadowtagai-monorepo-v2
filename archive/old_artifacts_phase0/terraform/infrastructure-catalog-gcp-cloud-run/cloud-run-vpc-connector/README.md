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
| [google_vpc_access_connector.main](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/vpc_access_connector) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_ip_cidr_range"></a> [ip\_cidr\_range](#input\_ip\_cidr\_range) | CIDR range for the connector (must be /28 unused range). | `string` | `"10.8.0.0/28"` | no |
| <a name="input_max_throughput"></a> [max\_throughput](#input\_max\_throughput) | Max throughput in Mbps (200-1000). | `number` | `300` | no |
| <a name="input_min_throughput"></a> [min\_throughput](#input\_min\_throughput) | Min throughput in Mbps (200-1000). | `number` | `200` | no |
| <a name="input_name"></a> [name](#input\_name) | VPC connector name. | `string` | n/a | yes |
| <a name="input_network"></a> [network](#input\_network) | VPC network name or self\_link. | `string` | `"default"` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | GCP region. | `string` | `"us-central1"` | no |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_connector"></a> [connector](#output\_connector) | The VPC Access connector resource. |
| <a name="output_connector_id"></a> [connector\_id](#output\_connector\_id) | The connector ID for use in Cloud Run. |
| <a name="output_connector_name"></a> [connector\_name](#output\_connector\_name) | The connector name. |
