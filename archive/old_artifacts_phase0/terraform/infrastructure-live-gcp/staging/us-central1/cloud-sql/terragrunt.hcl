# Staging CounselConduit — Separate Terragrunt config for staging CloudSQL
# Item 9: Add Cloud SQL module to staging Terragrunt config

include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../../infrastructure-catalog-gcp-cloud-run//cloud-sql"
}

inputs = {
  instance_name           = "counselconduit-staging-db"
  database_version        = "POSTGRES_16"
  tier                    = "db-f1-micro"
  region                  = "us-central1"
  availability_type       = "ZONAL"
  disk_size_gb            = 10
  disk_autoresize         = false
  deletion_protection     = false
  environment             = "staging"

  database_name           = "counselconduit_staging"
  database_user           = "cc_staging_user"

  # Backup — minimal for staging
  backup_enabled          = true
  backup_start_time       = "04:00"
  point_in_time_recovery  = false

  # Network
  ipv4_enabled            = false
  private_network         = "projects/shadowtag-omega-v4/global/networks/default"

  # Flags
  database_flags = {
    "log_min_duration_statement" = "1000"
    "max_connections"            = "50"
  }
}
