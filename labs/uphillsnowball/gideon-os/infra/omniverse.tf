# infra/omniverse.tf
# ============================================================================
# FedRAMP Sovereign Infrastructure
# ============================================================================
# Block 13 of the Ex Toto Omni-Compile (Gideon OS Architecture)
# 100% Serverless. Assured Workloads. Cloud Tasks. AlloyDB Omni.
# ============================================================================

provider "google" {
  project = "shadowtag-fedramp"
  region  = "us-central1"
}

variable "tenant_id" {
  default = "master-tenant"
}

# 1. FEDRAMP ASSURED WORKLOADS
resource "google_assured_workloads_workload" "fedramp_high" {
  compliance_regime = "FEDRAMP_HIGH"
  display_name      = "gideon-os-sovereign-enclave"
  location          = "us-central1"
  billing_account   = "billing-account-id"
}

# 2. THE PROSECUTOR VAULT (Ice Lake WORM Storage)
resource "google_storage_bucket" "sovereign_vault" {
  name     = "gideon-sovereign-evidence-vault"
  location = "US"
  retention_policy {
    retention_period = 220752000
    is_locked        = true
  }
}

# 3. CLOUD TASKS (Coordinator XML Queue)
resource "google_cloud_tasks_queue" "ultraplan_queue" {
  name     = "ultraplan-queue"
  location = "us-central1"
}

# 4. GIDEON OS KERNEL (Cloud Run Source-Based Deploy)
resource "google_cloud_run_v2_service" "gideon_kernel" {
  name     = "gideon-kernel"
  location = "us-central1"
  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    containers {
      image = "us-central1-docker.pkg.dev/shadowtag/repo/kernel:latest"
      ports {
        container_port = 8080
      }
    }
    timeout = "300s"
  }
}
