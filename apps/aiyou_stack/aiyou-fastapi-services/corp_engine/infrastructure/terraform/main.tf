# ShadowTagAI Corp Engine - Terraform IaC
# =========================================
# Dedicated GKE cluster for enterprise SaaS platform

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "shadowtagai-terraform-state"
    prefix = "corp-engine"
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "acquired-jet-478701-b3"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (prod, staging, dev)"
  type        = string
  default     = "prod"
}

# Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "sqladmin.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "corp_engine_vpc" {
  name                    = "corp-engine-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "corp_engine_subnet" {
  name          = "corp-engine-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/20"
  region        = var.region
  network       = google_compute_network.corp_engine_vpc.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.2.0.0/20"
  }
}

# GKE Cluster - Dedicated for Corp Engine
resource "google_container_cluster" "corp_engine" {
  provider = google-beta
  name     = "corp-engine-cluster-${var.environment}"
  location = var.region

  # Autopilot mode for serverless Kubernetes
  enable_autopilot = true

  network    = google_compute_network.corp_engine_vpc.name
  subnetwork = google_compute_subnetwork.corp_engine_subnet.name

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Private cluster
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Release channel
  release_channel {
    channel = "REGULAR"
  }

  # Addons
  addons_config {
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
  }

  depends_on = [google_project_service.apis]
}

# Cloud SQL - Multi-tenant PostgreSQL
resource "google_sql_database_instance" "corp_engine_db" {
  name             = "corp-engine-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-custom-4-16384"  # 4 vCPU, 16GB RAM
    availability_type = "REGIONAL"

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.corp_engine_vpc.id
    }

    database_flags {
      name  = "max_connections"
      value = "500"
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
  }

  deletion_protection = true

  depends_on = [google_project_service.apis]
}

resource "google_sql_database" "corp_engine" {
  name     = "corp_engine"
  instance = google_sql_database_instance.corp_engine_db.name
}

resource "google_sql_user" "corp_engine_user" {
  name     = "corp_engine_app"
  instance = google_sql_database_instance.corp_engine_db.name
  password = "CHANGE_ME_IN_SECRETS"  # Use Secret Manager in production
}

# Pub/Sub - Event-driven architecture
resource "google_pubsub_topic" "intel_updates" {
  name = "corp-engine-intel-updates-${var.environment}"
}

resource "google_pubsub_topic" "config_changes" {
  name = "corp-engine-config-changes-${var.environment}"
}

resource "google_pubsub_topic" "auto_port_events" {
  name = "corp-engine-auto-port-${var.environment}"
}

resource "google_pubsub_subscription" "intel_processor" {
  name  = "intel-processor-${var.environment}"
  topic = google_pubsub_topic.intel_updates.name

  ack_deadline_seconds = 60

  push_config {
    push_endpoint = "https://corp-engine-${var.environment}.${var.region}.run.app/pubsub/intel"
  }
}

# Artifact Registry
resource "google_artifact_registry_repository" "corp_engine" {
  location      = var.region
  repository_id = "corp-engine-${var.environment}"
  format        = "DOCKER"
}

# Cloud Run - Serverless API
resource "google_cloud_run_service" "corp_engine_api" {
  name     = "corp-engine-api-${var.environment}"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/corp-engine-${var.environment}/api:latest"

        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_url.secret_id
              key  = "latest"
            }
          }
        }
      }

      service_account_name = google_service_account.corp_engine.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"      = "1"
        "autoscaling.knative.dev/maxScale"      = "100"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.corp_engine_db.connection_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.apis]
}

# IAM - Service Account
resource "google_service_account" "corp_engine" {
  account_id   = "corp-engine-${var.environment}"
  display_name = "Corp Engine Service Account"
}

resource "google_project_iam_member" "corp_engine_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/secretmanager.secretAccessor",
    "roles/run.invoker",
  ])
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.corp_engine.email}"
}

# Secrets
resource "google_secret_manager_secret" "db_url" {
  secret_id = "corp-engine-db-url-${var.environment}"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "corp-engine-gemini-key-${var.environment}"

  replication {
    auto {}
  }
}

# Outputs
output "gke_cluster_name" {
  value = google_container_cluster.corp_engine.name
}

output "gke_cluster_endpoint" {
  value     = google_container_cluster.corp_engine.endpoint
  sensitive = true
}

output "cloud_sql_connection" {
  value = google_sql_database_instance.corp_engine_db.connection_name
}

output "cloud_run_url" {
  value = google_cloud_run_service.corp_engine_api.status[0].url
}

output "artifact_registry" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.corp_engine.repository_id}"
}
