# ═══════════════════════════════════════════════════════════════
# AIYOU PLATFORM - GKE NODE POOLS
# ═══════════════════════════════════════════════════════════════
# Purpose: Specialized node pools for latency-optimized workloads
# - Judge Pool: <90ms inference (medical decision validation)
# - LLM-GPU Pool: Gemini/vLLM GPU inference
# - Cor Pool: Coordination layer (medium latency)
# - NS-Mesh Pool: Neural Signal routing (<100μs latency)
# - ShadowTag Pool: Watermark embedding/validation
# - TensorLake Pool: Document processing (async)
# ═══════════════════════════════════════════════════════════════

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "aiyou-terraform-state"
    prefix = "node-pools"
  }
}

# ═══════════════════════════════════════════════════════════════
# DATA SOURCES
# ═══════════════════════════════════════════════════════════════

data "terraform_remote_state" "bootstrap" {
  backend = "gcs"
  config = {
    bucket = "aiyou-terraform-state"
    prefix = "bootstrap"
  }
}

data "terraform_remote_state" "base_platform" {
  backend = "gcs"
  config = {
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
  description = "Environment"
  type        = string
}

# ═══════════════════════════════════════════════════════════════
# NODE POOL 1: JUDGE (Medical Decision Validation)
# Latency Budget: <90ms (P95)
# ═══════════════════════════════════════════════════════════════

resource "google_container_node_pool" "judge" {
  name     = "judge-pool-${var.environment}"
  location = var.region
  cluster  = data.terraform_remote_state.base_platform.outputs.cluster_name
  project  = var.project_id

  # Autoscaling based on workload
  autoscaling {
    min_node_count = 2
    max_node_count = 10
  }

  # Node configuration
  node_config {
    machine_type = "n2-standard-8" # 8 vCPU, 32GB RAM

    labels = {
      workload     = "judge"
      latency      = "critical-90ms"
      pool_name    = "judge"
      environment  = var.environment
    }

    tags = ["gke-node", "judge-node"]

    # Taints to ensure only Judge workloads run here
    taint {
      key    = "workload"
      value  = "judge"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 100
    disk_type    = "pd-ssd" # SSD for low-latency I/O

    service_account = data.terraform_remote_state.bootstrap.outputs.gke_nodes_sa_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Workload Identity for Vertex AI access
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ═══════════════════════════════════════════════════════════════
# NODE POOL 2: LLM-GPU (Gemini Video, vLLM)
# GPU-accelerated inference for video analysis
# ═══════════════════════════════════════════════════════════════

resource "google_container_node_pool" "llm_gpu" {
  name     = "llm-gpu-pool-${var.environment}"
  location = var.region
  cluster  = data.terraform_remote_state.base_platform.outputs.cluster_name
  project  = var.project_id

  autoscaling {
    min_node_count = 1
    max_node_count = 5
  }

  node_config {
    machine_type = "n1-standard-8" # Compatible with T4 GPU

    # NVIDIA Tesla T4 GPU
    guest_accelerator {
      type  = "nvidia-tesla-t4"
      count = 1

      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }
    }

    labels = {
      workload    = "llm-gpu"
      gpu_type    = "t4"
      pool_name   = "llm-gpu"
      environment = var.environment
    }

    tags = ["gke-node", "gpu-node"]

    taint {
      key    = "workload"
      value  = "llm-gpu"
      effect = "NO_SCHEDULE"
    }

    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 200
    disk_type    = "pd-ssd"

    service_account = data.terraform_remote_state.bootstrap.outputs.gke_nodes_sa_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ═══════════════════════════════════════════════════════════════
# NODE POOL 3: COR (Coordination Layer)
# Medium latency, orchestration workloads
# ═══════════════════════════════════════════════════════════════

resource "google_container_node_pool" "cor" {
  name     = "cor-pool-${var.environment}"
  location = var.region
  cluster  = data.terraform_remote_state.base_platform.outputs.cluster_name
  project  = var.project_id

  autoscaling {
    min_node_count = 2
    max_node_count = 8
  }

  node_config {
    machine_type = "n2-standard-4" # 4 vCPU, 16GB RAM

    labels = {
      workload    = "cor"
      latency     = "medium"
      pool_name   = "cor"
      environment = var.environment
    }

    tags = ["gke-node", "cor-node"]

    taint {
      key    = "workload"
      value  = "cor"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 100
    disk_type    = "pd-balanced"

    service_account = data.terraform_remote_state.bootstrap.outputs.gke_nodes_sa_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ═══════════════════════════════════════════════════════════════
# NODE POOL 4: NS-MESH (Neural Signal Routing)
# Ultra-low latency: <100μs (P99)
# ═══════════════════════════════════════════════════════════════

resource "google_container_node_pool" "ns_mesh" {
  name     = "ns-mesh-pool-${var.environment}"
  location = var.region
  cluster  = data.terraform_remote_state.base_platform.outputs.cluster_name
  project  = var.project_id

  autoscaling {
    min_node_count = 3  # Higher minimum for latency SLA
    max_node_count = 12
  }

  node_config {
    machine_type = "n2-highcpu-8" # 8 vCPU, 8GB RAM (CPU-optimized)

    labels = {
      workload    = "ns-mesh"
      latency     = "ultra-low-100us"
      pool_name   = "ns-mesh"
      environment = var.environment
    }

    tags = ["gke-node", "ns-mesh-node"]

    taint {
      key    = "workload"
      value  = "ns-mesh"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 50
    disk_type    = "pd-ssd" # SSD critical for latency

    service_account = data.terraform_remote_state.bootstrap.outputs.ns_mesh_router_sa_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ═══════════════════════════════════════════════════════════════
# NODE POOL 5: SHADOWTAG (Watermark Embedding/Validation)
# CPU-intensive watermark operations
# ═══════════════════════════════════════════════════════════════

resource "google_container_node_pool" "shadowtag" {
  name     = "shadowtag-pool-${var.environment}"
  location = var.region
  cluster  = data.terraform_remote_state.base_platform.outputs.cluster_name
  project  = var.project_id

  autoscaling {
    min_node_count = 2
    max_node_count = 8
  }

  node_config {
    machine_type = "c2-standard-8" # 8 vCPU, 32GB RAM (compute-optimized)

    labels = {
      workload    = "shadowtag"
      latency     = "medium"
      pool_name   = "shadowtag"
      environment = var.environment
    }

    tags = ["gke-node", "shadowtag-node"]

    taint {
      key    = "workload"
      value  = "shadowtag"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 100
    disk_type    = "pd-ssd"

    service_account = data.terraform_remote_state.bootstrap.outputs.gke_nodes_sa_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ═══════════════════════════════════════════════════════════════
# NODE POOL 6: TENSORLAKE (Document Processing)
# Async workload, cost-optimized with preemptible nodes
# ═══════════════════════════════════════════════════════════════

resource "google_container_node_pool" "tensorlake" {
  name     = "tensorlake-pool-${var.environment}"
  location = var.region
  cluster  = data.terraform_remote_state.base_platform.outputs.cluster_name
  project  = var.project_id

  autoscaling {
    min_node_count = 3
    max_node_count = 20
  }

  node_config {
    machine_type = "n1-standard-8" # 8 vCPU, 30GB RAM
    preemptible  = true            # 70% cost savings (safe for async queue)
    spot         = false

    labels = {
      workload    = "tensorlake"
      latency     = "async"
      pool_name   = "tensorlake"
      environment = var.environment
      preemptible = "true"
    }

    tags = ["gke-node", "tensorlake-node"]

    taint {
      key    = "workload"
      value  = "tensorlake"
      effect = "NO_SCHEDULE"
    }

    disk_size_gb = 150
    disk_type    = "pd-balanced" # Balanced cost/performance

    service_account = data.terraform_remote_state.bootstrap.outputs.tensorlake_worker_sa_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# ═══════════════════════════════════════════════════════════════
# OUTPUTS
# ═══════════════════════════════════════════════════════════════

output "judge_pool_name" {
  value = google_container_node_pool.judge.name
}

output "llm_gpu_pool_name" {
  value = google_container_node_pool.llm_gpu.name
}

output "cor_pool_name" {
  value = google_container_node_pool.cor.name
}

output "ns_mesh_pool_name" {
  value = google_container_node_pool.ns_mesh.name
}

output "shadowtag_pool_name" {
  value = google_container_node_pool.shadowtag.name
}

output "tensorlake_pool_name" {
  value = google_container_node_pool.tensorlake.name
}
