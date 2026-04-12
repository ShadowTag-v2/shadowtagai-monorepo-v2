# ============================================================================
# GKE MODULE - PNKLN CORE CLUSTER
# ============================================================================

resource "google_container_cluster" "primary" {
  provider = google-beta

  name     = var.cluster_name
  location = var.region

  # Network configuration
  network    = var.network_name
  subnetwork = var.subnetwork_name

  # Remove default node pool (we'll create custom ones)
  remove_default_node_pool = true
  initial_node_count       = 1

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Release channel for automatic updates
  release_channel {
    channel = "REGULAR"
  }

  # Addons configuration
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
    gcp_filestore_csi_driver_config {
      enabled = true
    }
  }

  # Network policy
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }

  # Monitoring & Logging
  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
    managed_prometheus {
      enabled = true
    }
  }

  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  # Security settings
  binary_authorization {
    evaluation_mode = var.enable_binary_authorization ? "PROJECT_SINGLETON_POLICY_ENFORCE" : "DISABLED"
  }

  # Enable Shielded Nodes
  enable_shielded_nodes = var.enable_shielded_nodes

  # Resource labels
  resource_labels = var.labels
}

# ============================================================================
# NODE POOL - OPTIMIZED FOR JUDGE #6 + FILE SEARCH WORKLOADS
# ============================================================================

resource "google_container_node_pool" "primary_nodes" {
  provider = google-beta

  name       = "${var.cluster_name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name

  # Autoscaling configuration
  autoscaling {
    min_node_count = var.node_pool_config.min_nodes
    max_node_count = var.node_pool_config.max_nodes
  }

  # Node management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Node configuration
  node_config {
    machine_type = var.node_pool_config.machine_type
    disk_size_gb = var.node_pool_config.disk_size_gb
    disk_type    = var.node_pool_config.disk_type

    # Use spot/preemptible instances if configured
    preemptible = var.node_pool_config.preemptible
    spot        = var.node_pool_config.spot

    # OAuth scopes for GCP services
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Shielded instance config
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Service account
    service_account = google_service_account.gke_sa.email

    # Labels
    labels = merge(
      var.labels,
      {
        workload = "pnkln-core"
        component = "judge-file-search"
      }
    )

    # Taints for dedicated workloads (if needed)
    # taint {
    #   key    = "workload"
    #   value  = "pnkln-core"
    #   effect = "NO_SCHEDULE"
    # }

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  # Network configuration
  network_config {
    enable_private_nodes = false  # Set to true for production
  }
}

# ============================================================================
# SERVICE ACCOUNT FOR GKE NODES
# ============================================================================

resource "google_service_account" "gke_sa" {
  account_id   = "${var.cluster_name}-sa"
  display_name = "Service Account for ${var.cluster_name} GKE nodes"
  project      = var.project_id
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "gke_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  value = google_container_cluster.primary.endpoint
}

output "cluster_ca_certificate" {
  value = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
}

output "service_account_email" {
  value = google_service_account.gke_sa.email
}
