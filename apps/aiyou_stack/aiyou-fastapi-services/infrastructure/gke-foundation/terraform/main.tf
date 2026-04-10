provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {}
variable "region" { default = "us-central1" }

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "pnkln-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "pnkln-subnet"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.0.0.0/16"
}

# GKE Cluster (Standard Mode for Judge Isolation)
resource "google_container_cluster" "primary" {
  name     = "pnkln-foundation" # Renamed to bypass locked 'pnkln-cluster'
  location = var.region
  
  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1
  
  # CRITICAL: Force the default pool to use HDD to avoid SSD Quota limits during creation
  node_config {
    disk_type = "pd-standard"
    machine_type = "e2-medium"
  }

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  deletion_protection = false # Allow Terraform to replace cluster if needed
}

# 1. System Node Pool (Control Plane / Monitoring)
resource "google_container_node_pool" "system_pool" {
  name       = "system-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    machine_type = "e2-standard-4"
    disk_type    = "pd-standard" # Bypass SSD Quota
    labels = {
      pool = "system"
    }
  }
}

# 2. Judge Node Pool (Isolated Enforcement)
resource "google_container_node_pool" "judge_pool" {
  name       = "judge-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 2

  node_config {
    machine_type = "n2-standard-4"
    disk_type    = "pd-standard" # Bypass SSD Quota
    taint {
      key    = "components"
      value  = "judge"
      effect = "NO_SCHEDULE"
    }
    labels = {
      pool = "judge"
      component = "enforcement"
    }
  }
}

# 3. GPU Node Pool (A3/H100 or L4 for inference)
resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  initial_node_count = 0
  
  autoscaling {
    min_node_count = 0
    max_node_count = 10
  }

  node_config {
    machine_type = "g2-standard-4" # L4 GPU for cost-effective inference
    disk_type    = "pd-standard" # Bypass SSD Quota
    guest_accelerator {
      type  = "nvidia-l4"
      count = 1
    }
    labels = {
      pool = "gpu"
      accelerator = "l4"
    }
    taint {
      key    = "accelerator"
      value  = "gpu"
      effect = "NO_SCHEDULE"
    }
  }
}
