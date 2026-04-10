# ═══════════════════════════════════════════════════════════════
# AIYOU PLATFORM - GKE BASE CLUSTER
# ═══════════════════════════════════════════════════════════════
# Purpose: Core GKE cluster with networking, security, and monitoring
# Latency-optimized for NS mesh (<100μs routing), Judge (<90ms), Cor layers
# ═══════════════════════════════════════════════════════════════

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
    bucket = "aiyou-terraform-state"
    prefix = "base-platform"
  }
}

# ═══════════════════════════════════════════════════════════════
# VARIABLES
# ═══════════════════════════════════════════════════════════════

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "aiyou-platform"
}

variable "gke_version" {
  description = "GKE version (use 'latest' for auto)"
  type        = string
  default     = "1.29"
}

variable "network_name" {
  description = "VPC network name"
  type        = string
  default     = "aiyou-vpc"
}

variable "subnet_cidr" {
  description = "Subnet CIDR for GKE nodes"
  type        = string
  default     = "10.0.0.0/20"
}

variable "pods_cidr" {
  description = "Secondary IP range for pods"
  type        = string
  default     = "10.4.0.0/14"
}

variable "services_cidr" {
  description = "Secondary IP range for services"
  type        = string
  default     = "10.8.0.0/20"
}

# ═══════════════════════════════════════════════════════════════
# DATA SOURCES (FROM BOOTSTRAP)
# ═══════════════════════════════════════════════════════════════

data "terraform_remote_state" "bootstrap" {
  backend = "gcs"
  config = {
    bucket = "aiyou-terraform-state"
    prefix = "bootstrap"
  }
}

# ═══════════════════════════════════════════════════════════════
# VPC NETWORK
# ═══════════════════════════════════════════════════════════════

resource "google_compute_network" "vpc" {
  name                    = "${var.network_name}-${var.environment}"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "gke_subnet" {
  name          = "gke-subnet-${var.environment}"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
  project       = var.project_id

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

# ═══════════════════════════════════════════════════════════════
# CLOUD ROUTER & NAT (for private nodes)
# ═══════════════════════════════════════════════════════════════

resource "google_compute_router" "nat_router" {
  name    = "nat-router-${var.environment}"
  region  = var.region
  network = google_compute_network.vpc.id
  project = var.project_id
}

resource "google_compute_router_nat" "nat_gateway" {
  name   = "nat-gateway-${var.environment}"
  router = google_compute_router.nat_router.name
  region = var.region

  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ═══════════════════════════════════════════════════════════════
# FIREWALL RULES
# ═══════════════════════════════════════════════════════════════

# Allow internal communication between pods/services
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-${var.environment}"
  network = google_compute_network.vpc.name
  project = var.project_id

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

  source_ranges = [
    var.subnet_cidr,
    var.pods_cidr,
    var.services_cidr,
  ]
}

# Allow health checks from GCP load balancers
resource "google_compute_firewall" "allow_health_checks" {
  name    = "allow-health-checks-${var.environment}"
  network = google_compute_network.vpc.name
  project = var.project_id

  allow {
    protocol = "tcp"
  }

  source_ranges = [
    "35.191.0.0/16",  # GCP health check ranges
    "130.211.0.0/22",
  ]

  target_tags = ["gke-node"]
}

# ═══════════════════════════════════════════════════════════════
# GKE CLUSTER
# ═══════════════════════════════════════════════════════════════

resource "google_container_cluster" "primary" {
  provider = google-beta

  name     = "${var.cluster_name}-${var.environment}"
  location = var.region
  project  = var.project_id

  # Regional cluster (multi-zonal) for HA
  node_locations = [
    "${var.region}-a",
    "${var.region}-b",
    "${var.region}-c",
  ]

  # Remove default node pool (we'll create custom pools)
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.gke_subnet.name

  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Master authorized networks (adjust for your IP ranges)
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks (adjust in production)"
    }
  }

  # Workload Identity (for Vertex AI integration)
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Release channel (regular = balanced stability/features)
  release_channel {
    channel = "REGULAR"
  }

  # Logging and monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]

    managed_prometheus {
      enabled = true
    }
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    network_policy_config {
      disabled = false
    }

    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    gcp_filestore_csi_driver_config {
      enabled = true
    }
  }

  # Network policy
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED" # Uses Calico
  }

  # Security: Enable Shielded Nodes
  enable_shielded_nodes = true

  # Security: Application-layer secrets encryption
  database_encryption {
    state    = "ENCRYPTED"
    key_name = data.terraform_remote_state.bootstrap.outputs.gke_secrets_key_id
  }

  # Maintenance window (Sunday 4am UTC)
  maintenance_policy {
    daily_maintenance_window {
      start_time = "04:00"
    }
  }

  # Binary Authorization (optional, for image security)
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
  }

  # Cost optimization: Enable cluster autoscaling
  cluster_autoscaling {
    enabled = true

    resource_limits {
      resource_type = "cpu"
      minimum       = 4
      maximum       = 200
    }

    resource_limits {
      resource_type = "memory"
      minimum       = 16
      maximum       = 800
    }

    auto_provisioning_defaults {
      service_account = data.terraform_remote_state.bootstrap.outputs.gke_nodes_sa_email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]

      management {
        auto_repair  = true
        auto_upgrade = true
      }

      shielded_instance_config {
        enable_secure_boot          = true
        enable_integrity_monitoring = true
      }
    }
  }

  lifecycle {
    ignore_changes = [
      node_pool,
      initial_node_count,
    ]
  }
}

# ═══════════════════════════════════════════════════════════════
# OUTPUTS
# ═══════════════════════════════════════════════════════════════

output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "vpc_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "subnet_name" {
  description = "GKE subnet name"
  value       = google_compute_subnetwork.gke_subnet.name
}

output "workload_identity_pool" {
  description = "Workload Identity pool for Vertex AI"
  value       = "${var.project_id}.svc.id.goog"
}
