# CounselConduit production Cloud Run service

terraform {
  source = "../../../../infrastructure-catalog-gcp-cloud-run//cloud-run-service"
}

include "root" {
  path = find_in_parent_folders()
}

include "envcommon" {
  path   = "${dirname(find_in_parent_folders())}/_envcommon/cloud-run.hcl"
  expose = true
}

inputs = {
  service_name      = "counselconduit"
  image             = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:latest"
  min_instances     = 1
  max_instances     = 10
  cpu               = "1000m"
  memory            = "512Mi"
  concurrency       = 100
  startup_cpu_boost = true
  env               = "prod"
  trace_sample_rate = "0.1"

  env_vars = {
    APP_ENV       = "production"
    CLOUD_RUN_URL = "https://counselconduit-767252945109.us-central1.run.app"
  }

  secret_env_vars = {
    STRIPE_SECRET_KEY = "stripe-secret-key:latest"
  }

  service_account = "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
}
