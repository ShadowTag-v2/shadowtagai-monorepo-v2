# GKE GPU Cluster Module
# Creates a GKE cluster optimized for GPU workloads

resource "google_container_cluster" "primary" {
  provider = google-beta

  name     = var.cluster_name
  location = var.region
  project  = var.project_id

  # Regional cluster with min 1 node per zone (system pool)
  initial_node_count       = 1
  remove_default_node_pool = true

  # Network configuration
  network    = var.network
  subnetwork = var.subnetwork

  # IP allocation policy (required for private clusters)
  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = var.enable_private_endpoint
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
  }

  # Master authorized networks (who can access the control plane)
  dynamic "master_authorized_networks_config" {
    for_each = length(var.master_authorized_networks) > 0 ? [1] : []
    content {
      dynamic "cidr_blocks" {
        for_each = var.master_authorized_networks
        content {
          cidr_block   = cidr_blocks.value.cidr_block
          display_name = cidr_blocks.value.display_name
        }
      }
    }
  }

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    gcp_filestore_csi_driver_config {
      enabled = true
    }
  }

  # Release channel
  release_channel {
    channel = var.release_channel
  }

  # Enable auto-upgrade and auto-repair
  maintenance_policy {
    recurring_window {
      start_time = "2025-01-01T00:00:00Z"
      end_time   = "2025-01-01T04:00:00Z"
      recurrence = "FREQ=WEEKLY;BYDAY=SU"
    }
  }

  # Cluster autoscaling
  cluster_autoscaling {
    enabled = true

    autoscaling_profile = "OPTIMIZE_UTILIZATION"

    resource_limits {
      resource_type = "cpu"
      minimum       = 4
      maximum       = 1000
    }

    resource_limits {
      resource_type = "memory"
      minimum       = 16
      maximum       = 10000
    }

    auto_provisioning_defaults {
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

  # Vertical Pod Autoscaling
  vertical_pod_autoscaling {
    enabled = true
  }

  # Enable Binary Authorization
  binary_authorization {
    evaluation_mode = var.enable_binary_authorization ? "PROJECT_SINGLETON_POLICY_ENFORCE" : "DISABLED"
  }

  # Enable Shielded Nodes
  enable_shielded_nodes = true

  # Logging and Monitoring
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]

    managed_prometheus {
      enabled = var.enable_managed_prometheus
    }
  }

  # Resource labels
  resource_labels = var.labels

  # Datapath provider (use ADVANCED_DATAPATH for better performance)
  datapath_provider = "ADVANCED_DATAPATH"

  # Enable intranode visibility (useful for debugging)
  enable_intranode_visibility = true

  # Network policy
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"  # Will use Calico
  }

  # Pod security policy (deprecated but kept for reference)
  # Use PSS instead via admission controller

  # Cost management
  resource_usage_export_config {
    enable_network_egress_metering = true

    bigquery_destination {
      dataset_id = var.cost_export_dataset_id != "" ? var.cost_export_dataset_id : null
    }
  }

  lifecycle {
    ignore_changes = [
      node_pool,
      initial_node_count,
    ]
  }
}

# System Node Pool (for cluster add-ons)
resource "google_container_node_pool" "system" {
  name     = "system-pool"
  location = var.region
  cluster  = google_container_cluster.primary.name
  project  = var.project_id

  initial_node_count = 1

  autoscaling {
    min_node_count = 1
    max_node_count = 3
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 100
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = merge(
      var.labels,
      {
        pool = "system"
      }
    )

    taint {
      key    = "CriticalAddonsOnly"
      value  = "true"
      effect = "NO_SCHEDULE"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}
