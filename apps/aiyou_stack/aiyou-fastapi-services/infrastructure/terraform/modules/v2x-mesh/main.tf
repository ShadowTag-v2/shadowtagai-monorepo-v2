# V2X Mesh GKE Infrastructure Module

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
  default     = "aiyou-v2x-cluster"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# V2X Edge Node Pool (GPU-enabled for edge reasoning)
resource "google_container_node_pool" "v2x_edge" {
  name       = "v2x-edge-pool"
  cluster    = var.cluster_name
  location   = var.region

  # Auto-scaling configuration
  autoscaling {
    min_node_count = 3
    max_node_count = 20
    location_policy = "BALANCED"
  }

  # Node configuration
  node_config {
    machine_type = "n1-standard-8"  # 8 vCPU, 30GB RAM

    # GPU acceleration for edge reasoning
    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1
      gpu_driver_installation_config {
        gpu_driver_version = "LATEST"
      }
    }

    disk_size_gb = 100
    disk_type    = "pd-ssd"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    # Labels
    labels = {
      workload-type = "v2x-edge"
      environment   = var.environment
      gpu-enabled   = "true"
    }

    # Taints to ensure only V2X workloads run here
    taint {
      key    = "v2x-edge"
      value  = "true"
      effect = "NO_SCHEDULE"
    }

    # Metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Networking
    tags = ["v2x-edge", "gpu-enabled"]
  }

  # Upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
    strategy        = "SURGE"
  }

  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# V2X Mesh API Load Balancer
resource "google_compute_global_address" "v2x_mesh_ip" {
  name         = "v2x-mesh-gateway-ip"
  ip_version   = "IPV4"
  address_type = "EXTERNAL"
}

# Cloud Armor Security Policy
resource "google_compute_security_policy" "v2x_mesh_policy" {
  name        = "v2x-mesh-security-policy"
  description = "Security policy for V2X mesh gateway"

  # Rate limiting
  rule {
    action   = "rate_based_ban"
    priority = 100
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      ban_duration_sec = 600
      rate_limit_threshold {
        count        = 1000
        interval_sec = 60
      }
    }
  }

  # DDoS protection
  rule {
    action   = "deny(403)"
    priority = 200
    match {
      expr {
        expression = "origin.region_code == 'XX'"  # Block specific regions if needed
      }
    }
  }

  # Default rule
  rule {
    action   = "allow"
    priority = 2147483647
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}

# Redis instance for mesh state
resource "google_redis_instance" "v2x_mesh_cache" {
  name               = "v2x-mesh-cache"
  tier               = "STANDARD_HA"
  memory_size_gb     = 10
  region             = var.region
  redis_version      = "REDIS_7_0"
  display_name       = "V2X Mesh State Cache"
  reserved_ip_range  = "10.1.0.0/29"

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }

  labels = {
    environment = var.environment
    service     = "v2x-mesh"
  }
}

# Cloud Storage bucket for audit logs
resource "google_storage_bucket" "v2x_audit_logs" {
  name          = "${var.project_id}-v2x-audit-logs"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90  # Days
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365  # Days
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  labels = {
    environment = var.environment
    service     = "v2x-mesh"
    data-type   = "audit-logs"
  }
}

# IAM Service Account for V2X Mesh
resource "google_service_account" "v2x_mesh_sa" {
  account_id   = "v2x-mesh-service"
  display_name = "V2X Mesh Service Account"
  description  = "Service account for V2X mesh operations"
}

# IAM bindings
resource "google_project_iam_member" "v2x_mesh_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.v2x_mesh_sa.email}"
}

resource "google_project_iam_member" "v2x_mesh_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.v2x_mesh_sa.email}"
}

resource "google_storage_bucket_iam_member" "v2x_audit_writer" {
  bucket = google_storage_bucket.v2x_audit_logs.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.v2x_mesh_sa.email}"
}

# Cloud Monitoring Alert Policies
resource "google_monitoring_alert_policy" "v2x_high_latency" {
  display_name = "V2X Mesh - High Latency Alert"
  combiner     = "OR"

  conditions {
    display_name = "Mesh message latency > 90ms"

    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND resource.labels.namespace_name=\"v2x-mesh\" AND metric.type=\"custom.googleapis.com/v2x/message_latency_ms\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 90

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = []  # Add notification channels as needed

  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "v2x_message_drop_rate" {
  display_name = "V2X Mesh - High Message Drop Rate"
  combiner     = "OR"

  conditions {
    display_name = "Message drop rate > 5%"

    condition_threshold {
      filter          = "resource.type=\"k8s_container\" AND resource.labels.namespace_name=\"v2x-mesh\" AND metric.type=\"custom.googleapis.com/v2x/message_drop_rate\""
      duration        = "120s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = []

  alert_strategy {
    auto_close = "1800s"
  }
}

# Outputs
output "v2x_edge_node_pool_name" {
  description = "Name of the V2X edge node pool"
  value       = google_container_node_pool.v2x_edge.name
}

output "v2x_mesh_gateway_ip" {
  description = "External IP address for V2X mesh gateway"
  value       = google_compute_global_address.v2x_mesh_ip.address
}

output "v2x_redis_host" {
  description = "Redis instance host for mesh state"
  value       = google_redis_instance.v2x_mesh_cache.host
}

output "v2x_audit_bucket" {
  description = "GCS bucket for audit logs"
  value       = google_storage_bucket.v2x_audit_logs.name
}

output "v2x_service_account_email" {
  description = "Service account email for V2X mesh"
  value       = google_service_account.v2x_mesh_sa.email
}
