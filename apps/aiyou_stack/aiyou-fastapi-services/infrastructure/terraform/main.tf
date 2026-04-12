# Pnkln Judge #6 GKE Infrastructure
# Production-ready deployment on Google Cloud Platform

terraform {
  required_version = ">= 1.5.0"

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
    bucket = "pnkln-terraform-state"
    prefix = "judge-6/gke"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Local variables
locals {
  cluster_name = "judge-6-inference"
  network_name = "${local.cluster_name}-network"
  subnet_name  = "${local.cluster_name}-subnet"

  labels = {
    environment = var.environment
    application = "judge-6"
    managed_by  = "terraform"
    owner       = "pnkln"
  }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "container.googleapis.com",          # GKE
    "compute.googleapis.com",            # Compute Engine
    "aiplatform.googleapis.com",         # Vertex AI
    "documentai.googleapis.com",         # Document AI
    "storage.googleapis.com",            # Cloud Storage
    "monitoring.googleapis.com",         # Cloud Monitoring
    "logging.googleapis.com",            # Cloud Logging
    "cloudtrace.googleapis.com",         # Cloud Trace
    "redis.googleapis.com",              # Memorystore
    "pubsub.googleapis.com",             # Pub/Sub
    "secretmanager.googleapis.com",      # Secret Manager
    "binaryauthorization.googleapis.com" # Binary Authorization
  ])

  service            = each.key
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "gke_network" {
  name                    = local.network_name
  auto_create_subnetworks = false

  depends_on = [google_project_service.required_apis]
}

# Subnet for GKE cluster
resource "google_compute_subnetwork" "gke_subnet" {
  name          = local.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.gke_network.id

  # Secondary IP ranges for pods and services
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }

  private_ip_google_access = true
}

# Cloud NAT for egress traffic from private cluster
resource "google_compute_router" "router" {
  name    = "${local.cluster_name}-router"
  region  = var.region
  network = google_compute_network.gke_network.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "${local.cluster_name}-nat"
  router                            = google_compute_router.router.name
  region                            = var.region
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# GKE Autopilot Cluster
resource "google_container_cluster" "judge_6_cluster" {
  provider = google-beta

  name     = local.cluster_name
  location = var.region

  # Autopilot mode - Google manages nodes
  enable_autopilot = true

  # Network configuration
  network    = google_compute_network.gke_network.name
  subnetwork = google_compute_subnetwork.gke_subnet.name

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false  # Allow public endpoint for kubectl access
    master_ipv4_cidr_block = var.master_cidr

    master_global_access_config {
      enabled = true
    }
  }

  # Workload Identity for secure GCP authentication
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Binary Authorization for container image validation
  binary_authorization {
    evaluation_mode = var.environment == "production" ? "PROJECT_SINGLETON_POLICY_ENFORCE" : "DISABLED"
  }

  # Release channel for automatic upgrades
  release_channel {
    channel = var.release_channel  # REGULAR recommended for production
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"  # 3 AM local time
    }
  }

  # Monitoring and logging
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]

    managed_prometheus {
      enabled = true
    }
  }

  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  # Security features
  security_posture_config {
    mode               = var.environment == "production" ? "ENTERPRISE" : "BASIC"
    vulnerability_mode = var.environment == "production" ? "VULNERABILITY_ENTERPRISE" : "VULNERABILITY_BASIC"
  }

  # Addons
  addons_config {
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    gcs_fuse_csi_driver_config {
      enabled = true  # For Cloud Storage FUSE model weights
    }
  }

  # Resource labels
  resource_labels = local.labels

  depends_on = [
    google_project_service.required_apis,
    google_compute_subnetwork.gke_subnet
  ]
}

# Service Account for GKE workloads
resource "google_service_account" "judge_6_sa" {
  account_id   = "judge-6-workload-sa"
  display_name = "Judge #6 Workload Service Account"
  description  = "Service account for Judge #6 inference workloads"
}

# IAM bindings for service account
resource "google_project_iam_member" "judge_6_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.judge_6_sa.email}"
}

resource "google_project_iam_member" "judge_6_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.judge_6_sa.email}"
}

resource "google_project_iam_member" "judge_6_document_ai" {
  project = var.project_id
  role    = "roles/documentai.apiUser"
  member  = "serviceAccount:${google_service_account.judge_6_sa.email}"
}

resource "google_project_iam_member" "judge_6_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.judge_6_sa.email}"
}

resource "google_project_iam_member" "judge_6_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.judge_6_sa.email}"
}

resource "google_project_iam_member" "judge_6_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.judge_6_sa.email}"
}

# Workload Identity binding
resource "google_service_account_iam_binding" "judge_6_workload_identity" {
  service_account_id = google_service_account.judge_6_sa.name
  role              = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[${var.k8s_namespace}/judge-6-sa]"
  ]
}

# Cloud Storage bucket for model weights
resource "google_storage_bucket" "model_weights" {
  name          = "${var.project_id}-judge-6-models"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }

  labels = local.labels
}

# Cloud Storage bucket for compliance documents
resource "google_storage_bucket" "compliance_docs" {
  name          = "${var.project_id}-compliance-docs"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 2555  # 7 years for regulatory compliance
    }
    action {
      type          = "SetStorageClass"
      storage_class = "ARCHIVE"
    }
  }

  labels = local.labels
}

# Pub/Sub topic for Document AI results
resource "google_pubsub_topic" "document_processing" {
  name = "judge-6-document-processing"

  labels = local.labels
}

resource "google_pubsub_subscription" "langgraph_consumer" {
  name  = "langgraph-consumer"
  topic = google_pubsub_topic.document_processing.name

  ack_deadline_seconds = 600  # 10 minutes for long-running workflows

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  labels = local.labels
}

resource "google_pubsub_topic" "dead_letter" {
  name = "judge-6-dead-letter"

  labels = local.labels
}

# Memorystore Redis for LangGraph state
resource "google_redis_instance" "langgraph_state" {
  name           = "langgraph-state"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = 4
  region         = var.region

  redis_version = "REDIS_7_0"

  authorized_network = google_compute_network.gke_network.id

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  labels = local.labels

  depends_on = [google_project_service.required_apis]
}

# Firestore for durable state
resource "google_firestore_database" "judge_6_state" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.required_apis]
}

# Document AI Processor
resource "google_document_ai_processor" "ocr_processor" {
  location     = var.document_ai_location
  display_name = "Judge #6 OCR Processor"
  type         = "OCR_PROCESSOR"

  depends_on = [google_project_service.required_apis]
}

resource "google_document_ai_processor" "form_parser" {
  location     = var.document_ai_location
  display_name = "Judge #6 Form Parser"
  type         = "FORM_PARSER_PROCESSOR"

  depends_on = [google_project_service.required_apis]
}

# Outputs
output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.judge_6_cluster.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.judge_6_cluster.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.judge_6_cluster.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "service_account_email" {
  description = "Service account email for workloads"
  value       = google_service_account.judge_6_sa.email
}

output "model_weights_bucket" {
  description = "Cloud Storage bucket for model weights"
  value       = google_storage_bucket.model_weights.name
}

output "compliance_docs_bucket" {
  description = "Cloud Storage bucket for compliance documents"
  value       = google_storage_bucket.compliance_docs.name
}

output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.langgraph_state.host
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.langgraph_state.port
}

output "ocr_processor_id" {
  description = "Document AI OCR processor ID"
  value       = google_document_ai_processor.ocr_processor.id
}

output "form_parser_processor_id" {
  description = "Document AI Form Parser processor ID"
  value       = google_document_ai_processor.form_parser.id
}

output "pubsub_topic" {
  description = "Pub/Sub topic for document processing"
  value       = google_pubsub_topic.document_processing.name
}
