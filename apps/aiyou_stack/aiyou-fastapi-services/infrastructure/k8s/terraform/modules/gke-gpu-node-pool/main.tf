# GKE GPU Node Pool Module
# Creates GPU-enabled node pools

resource "google_container_node_pool" "gpu_pool" {
  provider = google-beta

  name     = var.pool_name
  location = var.location
  cluster  = var.cluster_name
  project  = var.project_id

  initial_node_count = var.initial_node_count

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    machine_type = var.machine_type
    disk_size_gb = var.disk_size_gb
    disk_type    = var.disk_type

    # GPU accelerator
    guest_accelerator {
      type  = var.accelerator_type
      count = var.accelerator_count

      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }

      gpu_sharing_config {
        gpu_sharing_strategy       = var.gpu_sharing_strategy
        max_shared_clients_per_gpu = var.max_shared_clients_per_gpu
      }
    }

    # Spot/Preemptible configuration
    spot        = var.preemptible
    preemptible = false  # Use spot instead

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    labels = var.node_labels

    # Taints for GPU nodes
    dynamic "taint" {
      for_each = var.node_taints
      content {
        key    = taint.value.key
        value  = taint.value.value
        effect = taint.value.effect
      }
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    metadata = {
      disable-legacy-endpoints = "true"
      google-logging-enabled   = "true"
      google-monitoring-enabled = "true"
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Enable gVNIC for better performance
    gvnic {
      enabled = true
    }

    # Placement policy for compact placement (better for multi-GPU jobs)
    dynamic "advanced_machine_features" {
      for_each = var.enable_compact_placement ? [1] : []
      content {
        threads_per_core = 2
      }
    }
  }

  # Placement policy
  dynamic "placement_policy" {
    for_each = var.enable_compact_placement ? [1] : []
    content {
      type = "COMPACT"
    }
  }

  lifecycle {
    ignore_changes = [
      initial_node_count,
    ]
  }
}
