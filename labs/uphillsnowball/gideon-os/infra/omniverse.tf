# infra/omniverse.tf
# FedRAMP Sovereign Infrastructure — 100% Serverless
# Assured Workloads, Cloud Tasks, TimescaleDB, Sovereign Evidence Vault.
#
# WARNING: Do NOT terraform apply without STATE B (Clutch) approval.
# This modifies billable GCP infrastructure.

provider "google" {
  project = "shadowtag-omega-v4"
  region  = "us-central1"
}

variable "tenant_id" {
  default     = "master-tenant"
  description = "Tenant identifier for multi-tenant isolation."
}

# 1. FEDRAMP ASSURED WORKLOADS
resource "google_assured_workloads_workload" "fedramp_high" {
  compliance_regime = "FEDRAMP_HIGH"
  display_name      = "gideon-os-sovereign-enclave"
  location          = "us-central1"
  billing_account   = var.billing_account
}

variable "billing_account" {
  description = "GCP billing account ID. Must be set in terraform.tfvars."
  type        = string
  sensitive   = true
}

# 2. THE PROSECUTOR VAULT (Ice Lake WORM Storage)
resource "google_storage_bucket" "sovereign_vault" {
  name     = "gideon-sovereign-evidence-vault-${var.tenant_id}"
  location = "US"

  retention_policy {
    retention_period = 220752000 # 7 years in seconds
    is_locked        = true
  }

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true
}

# 3. TIMESCALEDB (Midas 10x Hot Path)
resource "google_sql_database_instance" "timescale_db" {
  name             = "timescaledb-${var.tenant_id}"
  database_version = "POSTGRES_15"
  region           = "us-central1"

  settings {
    tier = "db-custom-4-16384"

    database_flags {
      name  = "shared_preload_libraries"
      value = "timescaledb"
    }

    backup_configuration {
      enabled = true
    }
  }

  deletion_protection = true
}

# 4. CLOUD TASKS QUEUES (BullMQ Incineration)
resource "google_cloud_tasks_queue" "omega_swarm" {
  name     = "omega-swarm-queue"
  location = "us-central1"

  rate_limits {
    max_dispatches_per_second = 500
    max_concurrent_dispatches = 100
  }

  retry_config {
    max_attempts = 5
  }
}

resource "google_cloud_tasks_queue" "worker_queue" {
  name     = "worker-queue"
  location = "us-central1"

  rate_limits {
    max_dispatches_per_second = 100
    max_concurrent_dispatches = 50
  }

  retry_config {
    max_attempts = 3
  }
}

# 5. GIDEON OS KERNEL (Cloud Run Gen2 with Confidential Compute)
resource "google_cloud_run_v2_service" "gideon_kernel" {
  name     = "gideon-kernel"
  location = "us-central1"

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    containers {
      image = "us-central1-docker.pkg.dev/shadowtag-omega-v4/repo/kernel:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "4"
          memory = "8Gi"
        }
      }
    }

    timeout = "300s" # 5-Minute Crucible Timeout

    scaling {
      min_instance_count = 0
      max_instance_count = 100
    }
  }
}
