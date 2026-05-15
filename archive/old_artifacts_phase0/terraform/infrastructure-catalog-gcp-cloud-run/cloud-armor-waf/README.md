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
| [google_compute_security_policy.waf](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_security_policy) | resource |

## Inputs

| Name | Description | Type | Default | Required |
| ---- | ----------- | ---- | ------- | :------: |
| <a name="input_admin_path_prefix"></a> [admin\_path\_prefix](#input\_admin\_path\_prefix) | Path prefix for admin rate limiting. | `string` | `"/admin"` | no |
| <a name="input_admin_rate_limit_rpm"></a> [admin\_rate\_limit\_rpm](#input\_admin\_rate\_limit\_rpm) | Admin endpoint rate limit: requests per minute per IP. | `number` | `20` | no |
| <a name="input_enable_sqli"></a> [enable\_sqli](#input\_enable\_sqli) | Enable SQL injection protection rule. | `bool` | `true` | no |
| <a name="input_enable_xss"></a> [enable\_xss](#input\_enable\_xss) | Enable XSS protection rule. | `bool` | `true` | no |
| <a name="input_project_id"></a> [project\_id](#input\_project\_id) | GCP project ID. | `string` | n/a | yes |
| <a name="input_rate_limit_rpm"></a> [rate\_limit\_rpm](#input\_rate\_limit\_rpm) | Rate limit: requests per minute per IP. | `number` | `100` | no |
| <a name="input_service_name"></a> [service\_name](#input\_service\_name) | Service name for policy naming. | `string` | n/a | yes |

## Outputs

| Name | Description |
| ---- | ----------- |
| <a name="output_policy"></a> [policy](#output\_policy) | The Cloud Armor security policy resource. |
| <a name="output_policy_name"></a> [policy\_name](#output\_policy\_name) | Security policy name. |
| <a name="output_policy_self_link"></a> [policy\_self\_link](#output\_policy\_self\_link) | Security policy self\_link for backend service attachment. |
