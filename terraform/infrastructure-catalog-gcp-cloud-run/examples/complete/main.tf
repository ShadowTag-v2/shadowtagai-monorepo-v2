module "vpc_connector" {
  source     = "../../modules/cloud-run-vpc-connector"
  project_id = var.project_id
  region     = var.region
  name       = "private-run-connector"
  subnet_name = "default"
}

module "secrets" {
  source                = "../../modules/cloud-run-secrets"
  project_id            = var.project_id
  service_account_email = var.service_account_email
  secret_ids            = ["db-password", "api-key"]
}

module "service" {
  source     = "../../modules/cloud-run-service"
  project_id = var.project_id
  region     = var.region

  service_name          = "my-api"
  image                 = "us-central1-docker.pkg.dev/${var.project_id}/my-repo/api:latest"
  service_account_email = var.service_account_email

  min_instances = 1
  max_instances = 20
  concurrency   = 100
  cpu           = "2"
  memory        = "1Gi"

  vpc_connector_id = module.vpc_connector.id
  vpc_egress       = "PRIVATE_RANGES_ONLY"

  cloud_sql_instances = ["${var.project_id}:${var.region}:my-db"]

  env_vars = { ENVIRONMENT = "prod" }
  secrets = [
    { env_var_name = "DB_PASS", secret_id = "db-password" },
    { env_var_name = "API_KEY", secret_id = "api-key" },
  ]

  traffic = [
    { percent = 90, latest_revision = true },
    { percent = 10, revision = "my-api-00042-abc" },
  ]
}

module "canary" {
  source                 = "../../modules/cloud-deploy-canary-pipeline"
  project_id             = var.project_id
  region                 = var.region
  name                   = "my-api"
  cloud_run_service_name = module.service.name
  percentages            = [25, 50, 75]
  verify                 = true
}

variable "project_id"            { type = string }
variable "region"                { type = string; default = "us-central1" }
variable "service_account_email" { type = string }

output "url"        { value = module.service.url }
output "rollout_url" { value = module.canary.rollout_url }
