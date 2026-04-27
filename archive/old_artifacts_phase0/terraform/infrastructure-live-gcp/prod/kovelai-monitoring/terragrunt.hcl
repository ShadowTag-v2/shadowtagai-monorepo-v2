# Item 8: KovelAI Terragrunt config — prod
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../infrastructure-catalog-gcp-cloud-run//monitoring-alerts"
}

inputs = {
  service_name      = "kovelai"
  project_id        = "shadowtag-omega-v4"
  uptime_check_host = "kovelai.web.app"
  uptime_check_path = "/"
  admin_email       = "founder@shadowtagai.com"

  enable_uptime_check    = true
  enable_firestore_alert = false  # KovelAI is static hosting, no Firestore writes
}
