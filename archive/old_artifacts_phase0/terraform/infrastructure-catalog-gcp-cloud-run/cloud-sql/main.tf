# Cloud SQL Module — Future Use
# For potential Supabase replacement or compliance ledger needs
# Status: PLANNED — not yet in use per architecture doctrine (Firestore is canonical)

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region."
}

variable "instance_name" {
  type        = string
  description = "Cloud SQL instance name."
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,96}$", var.instance_name))
    error_message = "Instance name must be lowercase, 3-97 chars."
  }
}

variable "database_version" {
  type        = string
  default     = "POSTGRES_16"
  description = "Database version (POSTGRES_16, POSTGRES_15, MYSQL_8_0)."
  validation {
    condition     = can(regex("^(POSTGRES_1[4-7]|MYSQL_8_0)$", var.database_version))
    error_message = "Must be POSTGRES_14-17 or MYSQL_8_0."
  }
}

variable "tier" {
  type        = string
  default     = "db-f1-micro"
  description = "Machine type tier."
  validation {
    condition     = can(regex("^db-", var.tier))
    error_message = "Tier must start with 'db-' (e.g. db-f1-micro, db-custom-2-8192)."
  }
}

variable "disk_size_gb" {
  type        = number
  default     = 10
  description = "Storage size in GB."
  validation {
    condition     = var.disk_size_gb >= 10 && var.disk_size_gb <= 30720
    error_message = "Disk size must be between 10 GB and 30 TB."
  }
}

variable "availability_type" {
  type        = string
  default     = "ZONAL"
  description = "ZONAL or REGIONAL (HA)."
}

variable "databases" {
  type        = list(string)
  default     = ["default"]
  description = "List of databases to create."
}

variable "deletion_protection" {
  type        = bool
  default     = true
  description = "Prevent accidental deletion."
}

resource "google_sql_database_instance" "main" {
  project             = var.project_id
  name                = var.instance_name
  database_version    = var.database_version
  region              = var.region
  deletion_protection = var.deletion_protection

  settings {
    tier              = var.tier
    disk_size         = var.disk_size_gb
    availability_type = var.availability_type

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
      backup_retention_settings {
        retained_backups = 14
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = "projects/${var.project_id}/global/networks/default"
      ssl_mode        = "ENCRYPTED_ONLY"  # CKV_GCP_6: Require SSL for all connections
    }

    maintenance_window {
      day          = 7  # Sunday
      hour         = 4  # 4am UTC
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = false
    }

    # Checkov CKV_GCP_109: log levels ERROR or lower
    # Checkov CKV_GCP_111: log SQL statements
    # Checkov CKV_GCP_54: log_lock_waits
    database_flags {
      name  = "log_min_messages"
      value = "error"
    }
    database_flags {
      name  = "log_min_error_statement"  # CKV_GCP_109
      value = "error"
    }
    database_flags {
      name  = "log_statement"
      value = "all"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    # CKV_GCP_51: log_checkpoints
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    # CKV_GCP_53: log_disconnections
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    # CKV_GCP_110: pgAudit
    database_flags {
      name  = "cloudsql.enable_pgaudit"
      value = "on"
    }
    database_flags {
      name  = "pgaudit.log"
      value = "all"
    }
  }

  lifecycle {
    prevent_destroy = true
  }
}

resource "google_sql_database" "databases" {
  for_each = toset(var.databases)
  project  = var.project_id
  name     = each.value
  instance = google_sql_database_instance.main.name
}

output "instance" {
  value       = google_sql_database_instance.main
  description = "The Cloud SQL instance resource."
  sensitive   = true
}

output "connection_name" {
  value       = google_sql_database_instance.main.connection_name
  description = "Connection name for Cloud SQL proxy."
}

output "private_ip" {
  value       = google_sql_database_instance.main.private_ip_address
  description = "Private IP address."
}
