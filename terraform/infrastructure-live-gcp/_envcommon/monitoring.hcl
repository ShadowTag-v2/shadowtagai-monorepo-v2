# Shared monitoring configuration
# Include this in per-service terragrunt.hcl files for monitoring overlays

locals {
  # Default values shared across all monitoring alerts
  default_admin_email            = "admin@shadowtagai.com"
  default_uptime_check_period    = "60s"
  default_firestore_threshold    = 50000
  default_enable_uptime_check    = true
  default_enable_firestore_alert = true
}
