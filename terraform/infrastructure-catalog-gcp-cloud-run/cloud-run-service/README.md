# Cloud Run Service Module

Production-grade Cloud Run Gen2 module with health probes, secrets, canary traffic, and OTEL.

## Usage

```hcl
module "counselconduit" {
  source = "../infrastructure-catalog-gcp-cloud-run//cloud-run-service"

  project_id        = "shadowtag-omega-v4"
  region            = "us-central1"
  service_name      = "counselconduit"
  image             = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:v3.3.2"
  min_instances     = 1
  max_instances     = 10
  cpu               = "1000m"
  memory            = "512Mi"
  concurrency       = 100
  startup_cpu_boost = true
  env               = "prod"

  env_vars = {
    APP_ENV = "production"
  }

  secret_env_vars = {
    STRIPE_SECRET_KEY = "stripe-secret-key:latest"
  }
}
```

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| project_id | string | — | GCP project ID |
| region | string | `us-central1` | GCP region |
| service_name | string | — | Cloud Run service name |
| image | string | — | Container image URI |
| min_instances | number | `0` | Min instance count |
| max_instances | number | `10` | Max instance count |
| cpu | string | `1000m` | CPU allocation |
| memory | string | `512Mi` | Memory allocation |
| concurrency | number | `100` | Max concurrent requests |
| startup_cpu_boost | bool | `true` | Enable startup CPU boost |
| env | string | `prod` | Environment label |
| env_vars | map(string) | `{}` | Environment variables |
| secret_env_vars | map(string) | `{}` | Secret Manager refs (`name:version`) |
| service_account | string | `""` | Custom SA email |
| vpc_connector | string | `""` | VPC connector name |
| trace_sample_rate | string | `"0.1"` | OTEL trace sampling rate |
