# CounselConduit staging Cloud Run service

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
  service_name      = "counselconduit-staging"
  image             = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:staging"
  min_instances     = 0
  max_instances     = 3
  cpu               = "1000m"
  memory            = "512Mi"
  concurrency       = 100
  startup_cpu_boost = true
  env               = "staging"
  trace_sample_rate = "1.0"

  env_vars = {
    APP_ENV = "staging"
  }

  service_account = "counselconduit-staging-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
}
