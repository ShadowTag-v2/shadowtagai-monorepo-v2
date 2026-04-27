# Item 12: Staging Terragrunt stack
# Deploys staging versions of prod services with reduced resources

locals {
  environment = "staging"
}

unit "counselconduit" {
  source = "../../../infrastructure-catalog-gcp-cloud-run//cloud-run-service"

  inputs = {
    service_name  = "counselconduit-staging"
    image         = "us-central1-docker.pkg.dev/shadowtag-omega-v4/counselconduit/api:staging"
    min_instances = 0
    max_instances = 3
    cpu           = "1000m"
    memory        = "256Mi"
    port          = 8080
    environment   = local.environment
  }
}

unit "monitoring" {
  source = "../../../infrastructure-catalog-gcp-cloud-run//monitoring-alerts"

  inputs = {
    service_name      = "counselconduit-staging"
    project_id        = "shadowtag-omega-v4"
    uptime_check_host = "counselconduit-staging-767252945109.us-central1.run.app"
    uptime_check_path = "/health"
    admin_email       = "founder@shadowtagai.com"

    enable_uptime_check    = true
    enable_firestore_alert = false
  }
}
