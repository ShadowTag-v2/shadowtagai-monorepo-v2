# PNKLN Core Stack - GKE Inference Infrastructure
# Aligned with Google Cloud accelerated-platforms reference architecture
# Last updated: 2025-11-08

terraform {
  required_version = ">= 1.8.0"

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
    bucket = "pnkln-core-stack-terraform-state"
    prefix = "gke-inference/prod"
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

# ============================================================================
# NETWORKING
# ============================================================================

resource "google_compute_network" "pnkln_vpc" {
  name                    = "pnkln-inference-vpc"
  auto_create_subnetworks = false
  mtu                     = 8896  # Jumbo frames for model transfer
  routing_mode            = "GLOBAL"
}

resource "google_compute_subnetwork" "gke_subnet" {
  name                     = "gke-inference-subnet"
  network                  = google_compute_network.pnkln_vpc.id
  ip_cidr_range           = "10.0.0.0/20"
  region                  = var.region
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"  # 262k pod IPs
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"  # 4k service IPs
  }

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Cloud Router for NAT
resource "google_compute_router" "nat_router" {
  name    = "pnkln-nat-router"
  region  = var.region
  network = google_compute_network.pnkln_vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "pnkln-nat-gateway"
  router                             = google_compute_router.nat_router.name
  region                             = var.region
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "pnkln-allow-internal"
  network = google_compute_network.pnkln_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/8"]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "pnkln-allow-health-checks"
  network = google_compute_network.pnkln_vpc.name

  allow {
    protocol = "tcp"
  }

  source_ranges = [
    "35.191.0.0/16",  # GCP health checks
    "130.211.0.0/22"  # GCP health checks
  ]
}

# ============================================================================
# GKE CLUSTER (Standard Mode)
# ============================================================================

resource "google_container_cluster" "pnkln_gke" {
  provider = google-beta

  name     = var.cluster_name
  location = var.region

  # Remove default node pool (will create custom pools)
  remove_default_node_pool = true
  initial_node_count       = 1

  # GKE release channel
  release_channel {
    channel = "RAPID"  # Latest inference optimizations
  }

  # Network configuration
  network    = google_compute_network.pnkln_vpc.name
  subnetwork = google_compute_subnetwork.gke_subnet.name

  # IP allocation
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block = "172.16.0.0/28"

    master_global_access_config {
      enabled = true
    }
  }

  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"  # Restrict in production
      display_name = "All networks"
    }
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Binary Authorization
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  # Gateway API (Required for Inference Gateway)
  gateway_api_config {
    channel = "CHANNEL_STANDARD"
  }

  # Add-ons
  addons_config {
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    gcs_fuse_csi_driver_config {
      enabled = true  # Critical for model weight streaming
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    http_load_balancing {
      disabled = false
    }

    gke_backup_agent_config {
      enabled = true
    }
  }

  # Node auto-provisioning
  cluster_autoscaling {
    enabled = true

    autoscaling_profile = "OPTIMIZE_UTILIZATION"  # vs BALANCED

    auto_provisioning_defaults {
      service_account = google_service_account.gke_node_sa.email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]

      shielded_instance_config {
        enable_secure_boot          = true
        enable_integrity_monitoring = true
      }

      management {
        auto_upgrade = true
        auto_repair  = true
      }
    }

    # Resource limits
    resource_limits {
      resource_type = "cpu"
      minimum       = 4
      maximum       = 1000
    }

    resource_limits {
      resource_type = "memory"
      minimum       = 16
      maximum       = 4000
    }

    resource_limits {
      resource_type = "nvidia-l4"
      minimum       = 0
      maximum       = 32
    }

    resource_limits {
      resource_type = "nvidia-a100-40gb"
      minimum       = 0
      maximum       = 16
    }
  }

  # Monitoring configuration
  monitoring_config {
    enable_components = [
      "SYSTEM_COMPONENTS",
      "APISERVER",
      "SCHEDULER",
      "CONTROLLER_MANAGER"
    ]

    managed_prometheus {
      enabled = true
    }

    advanced_datapath_observability_config {
      enable_metrics = true
      enable_relay   = true
    }
  }

  # Logging configuration
  logging_config {
    enable_components = [
      "SYSTEM_COMPONENTS",
      "WORKLOADS",
      "APISERVER",
      "SCHEDULER",
      "CONTROLLER_MANAGER"
    ]
  }

  # Resource usage export
  resource_usage_export_config {
    enable_network_egress_metering = true

    bigquery_destination {
      dataset_id = google_bigquery_dataset.gke_usage.dataset_id
    }
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"  # 3 AM UTC
    }
  }

  # Cost management
  cost_management_config {
    enabled = true
  }

  # Security hardening
  enable_shielded_nodes = true

  # Network policy
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # DNS config
  dns_config {
    cluster_dns        = "CLOUD_DNS"
    cluster_dns_scope  = "CLUSTER_SCOPE"
    cluster_dns_domain = "cluster.local"
  }
}

# ============================================================================
# NODE POOLS
# ============================================================================

# System node pool (lightweight workloads)
resource "google_container_node_pool" "system_pool" {
  name       = "system-pool"
  location   = var.region
  cluster    = google_container_cluster.pnkln_gke.name
  node_count = 1

  autoscaling {
    min_node_count = 1
    max_node_count = 5
  }

  node_config {
    machine_type = "n2-standard-4"
    disk_size_gb = 100
    disk_type    = "pd-balanced"

    service_account = google_service_account.gke_node_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Image streaming
    gcfs_config {
      enabled = true
    }

    # gVNIC for better networking
    gvnic {
      enabled = true
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }

    labels = {
      workload = "system"
      tier     = "control-plane"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}

# Judge 6 GPU pool (L4 GPUs for enforcement)
resource "google_container_node_pool" "judge_gpu_pool" {
  name     = "judge-l4-pool"
  location = var.region
  cluster  = google_container_cluster.pnkln_gke.name

  autoscaling {
    min_node_count       = 0
    max_node_count       = 8
    location_policy      = "BALANCED"
    total_min_node_count = 0
    total_max_node_count = 16
  }

  node_config {
    machine_type = "g2-standard-16"  # 4 vCPU, 16GB RAM, 1x L4
    spot         = true  # 60-91% discount

    guest_accelerator {
      type  = "nvidia-l4"
      count = 1

      gpu_driver_installation_config {
        gpu_driver_version = "LATEST"
      }

      # GPU time-sharing for better utilization
      gpu_sharing_config {
        gpu_sharing_strategy       = "TIME_SHARING"
        max_shared_clients_per_gpu = 4
      }
    }

    service_account = google_service_account.gke_node_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    gcfs_config {
      enabled = true
    }

    gvnic {
      enabled = true
    }

    # Fast local SSDs for model caching
    local_nvme_ssd_block_config {
      local_ssd_count = 1
    }

    labels = {
      workload            = "judge-enforcement"
      tier                = "inference"
      "compute-class-pool" = "gpu-l4-spot"
    }

    taint {
      key    = "nvidia.com/gpu"
      value  = "true"
      effect = "NO_SCHEDULE"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}

# LLM Prefill pool (optimized for parallel processing)
resource "google_container_node_pool" "llm_prefill_pool" {
  name     = "llm-prefill-l4-pool"
  location = var.region
  cluster  = google_container_cluster.pnkln_gke.name

  autoscaling {
    min_node_count       = 0
    max_node_count       = 10
    location_policy      = "BALANCED"
    total_min_node_count = 0
    total_max_node_count = 20
  }

  node_config {
    machine_type = "g2-standard-24"  # 12 vCPU, 96GB RAM, 2x L4
    spot         = true

    guest_accelerator {
      type  = "nvidia-l4"
      count = 2

      gpu_driver_installation_config {
        gpu_driver_version = "LATEST"
      }
    }

    service_account = google_service_account.gke_node_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    gcfs_config {
      enabled = true
    }

    gvnic {
      enabled = true
    }

    labels = {
      workload            = "llm-prefill"
      tier                = "inference"
      "compute-class-pool" = "gpu-l4-spot"
    }

    taint {
      key    = "workload"
      value  = "prefill"
      effect = "NO_SCHEDULE"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}

# LLM Decode pool (optimized for generation)
resource "google_container_node_pool" "llm_decode_pool" {
  name     = "llm-decode-l4-pool"
  location = var.region
  cluster  = google_container_cluster.pnkln_gke.name

  autoscaling {
    min_node_count       = 1
    max_node_count       = 20
    location_policy      = "BALANCED"
    total_min_node_count = 1
    total_max_node_count = 40
  }

  node_config {
    machine_type = "g2-standard-16"  # 4 vCPU, 16GB RAM, 1x L4
    spot         = true

    guest_accelerator {
      type  = "nvidia-l4"
      count = 1

      gpu_driver_installation_config {
        gpu_driver_version = "LATEST"
      }
    }

    service_account = google_service_account.gke_node_sa.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    gcfs_config {
      enabled = true
    }

    gvnic {
      enabled = true
    }

    labels = {
      workload            = "llm-decode"
      tier                = "inference"
      "compute-class-pool" = "gpu-l4-spot"
    }

    taint {
      key    = "workload"
      value  = "decode"
      effect = "NO_SCHEDULE"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }
}

# ============================================================================
# SERVICE ACCOUNTS & IAM
# ============================================================================

resource "google_service_account" "gke_node_sa" {
  account_id   = "gke-inference-node-sa"
  display_name = "GKE Inference Node Service Account"
  description  = "Service account for GKE inference node pools"
}

resource "google_project_iam_member" "gke_node_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/storage.objectViewer",
    "roles/artifactregistry.reader",
    "roles/aiplatform.user",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

# Workload Identity for Judge 6
resource "google_service_account" "Claude_Code_6_sa" {
  account_id   = "Claude_Code_6-workload-sa"
  display_name = "Judge 6 Workload Service Account"
}

resource "google_service_account_iam_binding" "Claude_Code_6_workload_identity" {
  service_account_id = google_service_account.Claude_Code_6_sa.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[aiyoujr-governance/Claude_Code_6]"
  ]
}

# Workload Identity for LLM Router
resource "google_service_account" "llm_router_sa" {
  account_id   = "llm-router-workload-sa"
  display_name = "LLM Router Workload Service Account"
}

resource "google_service_account_iam_binding" "llm_router_workload_identity" {
  service_account_id = google_service_account.llm_router_sa.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[cognitive-stack-v5/llm-router]"
  ]
}

resource "google_project_iam_member" "llm_router_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.llm_router_sa.email}"
}

# Workload Identity for Gemini Ingestion Layer
resource "google_service_account" "gemini_ingestion_sa" {
  account_id   = "gemini-ingestion-workload-sa"
  display_name = "Gemini Ingestion Layer Workload Service Account"
  description  = "Service account for nightly intelligence collection pipeline"
}

resource "google_service_account_iam_binding" "gemini_ingestion_workload_identity" {
  service_account_id = google_service_account.gemini_ingestion_sa.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[gemini-ingestion/gemini-ingestion-sa]"
  ]
}

resource "google_project_iam_member" "gemini_ingestion_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/storage.objectViewer",
    "roles/storage.objectCreator",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gemini_ingestion_sa.email}"
}

# ============================================================================
# ARTIFACT REGISTRY
# ============================================================================

resource "google_artifact_registry_repository" "pnkln_repo" {
  location      = var.region
  repository_id = "pnkln-inference"
  description   = "Container images for PNKLN inference workloads"
  format        = "DOCKER"

  docker_config {
    immutable_tags = false
  }

  cleanup_policies {
    id     = "keep-latest-50"
    action = "DELETE"

    condition {
      tag_state    = "UNTAGGED"
      older_than   = "2592000s"  # 30 days
    }
  }
}

# ============================================================================
# CLOUD STORAGE
# ============================================================================

resource "google_storage_bucket" "model_weights" {
  name          = "${var.project_id}-model-weights"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
      with_state = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 30
      matches_storage_class = ["STANDARD"]
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

resource "google_storage_bucket_iam_member" "model_weights_reader" {
  bucket = google_storage_bucket.model_weights.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.gke_node_sa.email}"
}

# ============================================================================
# BIGQUERY FOR COST TRACKING
# ============================================================================

resource "google_bigquery_dataset" "gke_usage" {
  dataset_id                 = "gke_inference_usage"
  location                   = var.region
  default_table_expiration_ms = 7776000000  # 90 days

  labels = {
    environment = "production"
    team        = "ml-infrastructure"
  }
}

# ============================================================================
# GLOBAL IP FOR INFERENCE GATEWAY
# ============================================================================

resource "google_compute_global_address" "inference_gateway_ip" {
  name = "inference-gateway-ip"
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.pnkln_gke.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.pnkln_gke.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.pnkln_gke.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "region" {
  description = "GCP region"
  value       = var.region
}

output "inference_gateway_ip" {
  description = "Global IP for Inference Gateway"
  value       = google_compute_global_address.inference_gateway_ip.address
}

output "artifact_registry_url" {
  description = "Artifact Registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.pnkln_repo.repository_id}"
}

output "model_weights_bucket" {
  description = "GCS bucket for model weights"
  value       = google_storage_bucket.model_weights.name
}

output "gke_node_sa_email" {
  description = "GKE node service account email"
  value       = google_service_account.gke_node_sa.email
}

output "Claude_Code_6_sa_email" {
  description = "Judge 6 workload identity service account"
  value       = google_service_account.Claude_Code_6_sa.email
}

output "llm_router_sa_email" {
  description = "LLM Router workload identity service account"
  value       = google_service_account.llm_router_sa.email
}

output "gemini_ingestion_sa_email" {
  description = "Gemini Ingestion Layer workload identity service account"
  value       = google_service_account.gemini_ingestion_sa.email
}
