# Prod environment — CounselConduit Cloud Run Service
# Inherits from root terragrunt.hcl

include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../infrastructure-catalog-gcp-cloud-run//cloud-run-service"
}

inputs = {
  service_name  = "counselconduit"
  image         = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:latest"
  min_instances = 1
  max_instances = 10
  cpu           = "1000m"
  memory        = "512Mi"
  port          = 8080
  environment   = "prod"

  env_vars = {
    ENVIRONMENT    = "production"
    LOG_LEVEL      = "INFO"
    PROJECT_ID     = "shadowtag-omega-v4"
    FIRESTORE_DB   = "(default)"
  }

  secret_env_vars = {
    STRIPE_SECRET_KEY = "stripe-secret-key"
    STITCH_API_KEY    = "stitch-api-key"
  }
}
