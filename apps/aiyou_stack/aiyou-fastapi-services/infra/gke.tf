# VPC Network
resource "google_compute_network" "pnkln_vpc" {
  name                    = var.network_name
  auto_create_subnetworks = false
  project                 = var.project_id
}

# Subnet with secondary ranges for GKE
resource "google_compute_subnetwork" "pnkln_subnet" {
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.pnkln_vpc.id
  project       = var.project_id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr_range
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr_range
  }

  private_ip_google_access = true
}

# Cloud Router for NAT
resource "google_compute_router" "pnkln_router" {
  name    = "${var.network_name}-router"
  region  = var.region
  network = google_compute_network.pnkln_vpc.id
  project = var.project_id
}

# Cloud NAT for private cluster internet access
resource "google_compute_router_nat" "pnkln_nat" {
  name                               = "${var.network_name}-nat"
  router                             = google_compute_router.pnkln_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  project                            = var.project_id

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# GKE Cluster
resource "google_container_cluster" "pnkln_cluster" {
  name     = var.cluster_name
  location = var.zone
  project  = var.project_id

  # We manage node pools separately
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.pnkln_vpc.name
  subnetwork = google_compute_subnetwork.pnkln_subnet.name

  # IP allocation policy for VPC-native cluster
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  # Workload Identity for secure service authentication
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = var.enable_private_endpoint
    master_ipv4_cidr_block  = var.master_ipv4_cidr_block
  }

  # Master authorized networks - configure based on your needs
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"  # SECURITY: Restrict this in production
      display_name = "All networks (temporary)"
    }
  }

  # Release channel for automatic upgrades
  release_channel {
    channel = "REGULAR"
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"  # 3 AM UTC
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
    gce_persistent_disk_csi_driver_config {
      enabled = true
    }
    gcs_fuse_csi_driver_config {
      enabled = true  # For model loading from Cloud Storage
    }
  }

  # Network policy
  network_policy {
    enabled  = true
    provider = "PROVIDER_UNSPECIFIED"
  }

  # Binary authorization
  binary_authorization {
    evaluation_mode = "PROJECT_SINGLETON_POLICY_ENFORCE"
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

  # Resource labels
  resource_labels = merge(var.labels, {
    cluster = var.cluster_name
    env     = var.environment
  })

  # Security configurations
  enable_shielded_nodes = true

  # Enable autopilot features
  cluster_autoscaling {
    enabled = true
    autoscaling_profile = "OPTIMIZE_UTILIZATION"  # More aggressive scale-down

    resource_limits {
      resource_type = "cpu"
      minimum       = 1
      maximum       = 100
    }

    resource_limits {
      resource_type = "memory"
      minimum       = 4
      maximum       = 400
    }
  }

  depends_on = [
    google_compute_subnetwork.pnkln_subnet
  ]
}

# CPU Node Pool for lightweight services
resource "google_container_node_pool" "cpu_pool" {
  name       = "cpu-pool"
  location   = var.zone
  cluster    = google_container_cluster.pnkln_cluster.name
  project    = var.project_id

  # Autoscaling configuration
  autoscaling {
    min_node_count = var.cpu_node_pool_config.min_nodes
    max_node_count = var.cpu_node_pool_config.max_nodes
  }

  # Node configuration
  node_config {
    machine_type = var.cpu_node_pool_config.machine_type
    disk_size_gb = var.cpu_node_pool_config.disk_size_gb
    disk_type    = "pd-standard"

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Labels
    labels = merge(var.labels, {
      pool_type = "cpu"
      workload  = "general"
    })

    # Taints - none for CPU pool
    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# GPU Node Pool for inference workloads
resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  location   = var.zone
  cluster    = google_container_cluster.pnkln_cluster.name
  project    = var.project_id

  # Autoscaling configuration - scale to zero for cost optimization
  autoscaling {
    min_node_count = var.gpu_node_pool_config.min_nodes
    max_node_count = var.gpu_node_pool_config.max_nodes
  }

  # Node configuration
  node_config {
    machine_type = var.gpu_node_pool_config.machine_type
    disk_size_gb = var.gpu_node_pool_config.disk_size_gb
    disk_type    = var.gpu_node_pool_config.disk_type

    # GPU configuration
    guest_accelerator {
      type  = var.gpu_node_pool_config.gpu_type
      count = var.gpu_node_pool_config.gpu_count
      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }
    }

    # OAuth scopes
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Labels
    labels = merge(var.labels, {
      pool_type = "gpu"
      workload  = "inference"
      gpu_type  = var.gpu_node_pool_config.gpu_type
    })

    # Taints to ensure only GPU workloads land here
    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
