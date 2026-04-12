# YouAi GPU Infrastructure on GKE
# Terraform Configuration - Main Entry Point
# Version: 1.0
# Date: 2025-11-17

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
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "gcs" {
    bucket = "youai-terraform-state"
    prefix = "gke-gpu-cluster"
  }
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Get GKE cluster credentials for Kubernetes provider
data "google_client_config" "default" {}

data "google_container_cluster" "primary" {
  name     = module.gke_cluster.cluster_name
  location = var.region
  depends_on = [module.gke_cluster]
}

provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(data.google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = "https://${data.google_container_cluster.primary.endpoint}"
    token                  = data.google_client_config.default.access_token
    cluster_ca_certificate = base64decode(data.google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
  }
}

# Local Variables
locals {
  cluster_name = "${var.project_name}-${var.environment}-gpu"

  common_labels = {
    environment = var.environment
    managed_by  = "terraform"
    project     = var.project_name
    team        = "platform-engineering"
  }

  gpu_node_pools = {
    inference_l4 = {
      name               = "inference-l4-pool"
      machine_type       = "g2-standard-4"
      accelerator_type   = "nvidia-l4"
      accelerator_count  = 1
      disk_size_gb       = 200
      disk_type          = "pd-balanced"
      min_nodes          = 0
      max_nodes          = 20
      initial_nodes      = 0
      preemptible        = false
      workload_label     = "inference"
    }

    finetune_a100_2g = {
      name               = "finetune-a100-2g-pool"
      machine_type       = "a2-highgpu-2g"
      accelerator_type   = "nvidia-tesla-a100"
      accelerator_count  = 2
      disk_size_gb       = 500
      disk_type          = "pd-ssd"
      min_nodes          = 0
      max_nodes          = 10
      initial_nodes      = 0
      preemptible        = false
      workload_label     = "fine-tuning"
    }

    training_a100_8g = {
      name               = "training-a100-8g-pool"
      machine_type       = "a2-ultragpu-8g"
      accelerator_type   = "nvidia-a100-80gb"
      accelerator_count  = 8
      disk_size_gb       = 1000
      disk_type          = "pd-ssd"
      min_nodes          = 0
      max_nodes          = 4
      initial_nodes      = 0
      preemptible        = false
      workload_label     = "training"
    }

    spot_a100 = {
      name               = "spot-a100-pool"
      machine_type       = "a2-highgpu-1g"
      accelerator_type   = "nvidia-tesla-a100"
      accelerator_count  = 1
      disk_size_gb       = 200
      disk_type          = "pd-balanced"
      min_nodes          = 0
      max_nodes          = 10
      initial_nodes      = 0
      preemptible        = true
      workload_label     = "batch"
    }

    multi_agent_a100 = {
      name               = "multi-agent-a100-pool"
      machine_type       = "a2-highgpu-4g"
      accelerator_type   = "nvidia-tesla-a100"
      accelerator_count  = 4
      disk_size_gb       = 500
      disk_type          = "pd-ssd"
      min_nodes          = 0
      max_nodes          = 8
      initial_nodes      = 0
      preemptible        = false
      workload_label     = "multi-agent"
    }
  }
}

# VPC Network
module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 7.0"

  project_id   = var.project_id
  network_name = "${var.project_name}-vpc"
  routing_mode = "REGIONAL"

  subnets = [
    {
      subnet_name           = "${var.project_name}-gpu-subnet"
      subnet_ip             = "10.0.0.0/20"
      subnet_region         = var.region
      subnet_private_access = true
      subnet_flow_logs      = true
    }
  ]

  secondary_ranges = {
    "${var.project_name}-gpu-subnet" = [
      {
        range_name    = "pods"
        ip_cidr_range = "10.16.0.0/14"
      },
      {
        range_name    = "services"
        ip_cidr_range = "10.20.0.0/20"
      }
    ]
  }
}

# Cloud NAT (for private cluster egress)
resource "google_compute_router" "router" {
  name    = "${var.project_name}-router"
  region  = var.region
  network = module.vpc.network_name
  project = var.project_id
}

resource "google_compute_router_nat" "nat" {
  name   = "${var.project_name}-nat"
  router = google_compute_router.router.name
  region = var.region

  nat_ip_allocate_option = "AUTO_ONLY"

  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# GKE Cluster with GPU Support
module "gke_cluster" {
  source = "./modules/gke-gpu-cluster"

  project_id       = var.project_id
  region           = var.region
  cluster_name     = local.cluster_name
  network          = module.vpc.network_name
  subnetwork       = module.vpc.subnets_names[0]
  pods_range_name  = "pods"
  services_range_name = "services"

  master_ipv4_cidr_block = "172.16.0.0/28"
  master_authorized_networks = var.master_authorized_networks

  labels = local.common_labels
}

# GPU Node Pools
module "gpu_node_pools" {
  source = "./modules/gke-gpu-node-pool"

  for_each = local.gpu_node_pools

  project_id    = var.project_id
  cluster_name  = module.gke_cluster.cluster_name
  location      = var.region

  pool_name         = each.value.name
  machine_type      = each.value.machine_type
  accelerator_type  = each.value.accelerator_type
  accelerator_count = each.value.accelerator_count
  disk_size_gb      = each.value.disk_size_gb
  disk_type         = each.value.disk_type

  min_node_count = each.value.min_nodes
  max_node_count = each.value.max_nodes
  initial_node_count = each.value.initial_nodes

  preemptible = each.value.preemptible

  node_labels = merge(
    local.common_labels,
    {
      workload = each.value.workload_label
      gpu      = split("-", each.value.accelerator_type)[1]
      pool     = each.value.name
    }
  )

  node_taints = each.value.preemptible ? [
    {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    },
    {
      key    = "cloud.google.com/gke-spot"
      value  = "true"
      effect = "NO_SCHEDULE"
    }
  ] : [
    {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  ]

  depends_on = [module.gke_cluster]
}

# NVIDIA GPU Operator (via Helm)
resource "helm_release" "gpu_operator" {
  name             = "gpu-operator"
  repository       = "https://helm.ngc.nvidia.com/nvidia"
  chart            = "gpu-operator"
  namespace        = "gpu-operator"
  create_namespace = true
  version          = "v23.9.0"

  values = [
    yamlencode({
      driver = {
        enabled = false  # GKE pre-installs drivers
      }
      toolkit = {
        enabled = true
      }
      dcgm = {
        enabled = true
      }
      dcgmExporter = {
        enabled = true
        serviceMonitor = {
          enabled = var.enable_prometheus
        }
      }
      devicePlugin = {
        enabled = true
      }
      mig = {
        strategy = "single"
      }
      operator = {
        defaultRuntime = "containerd"
      }
      gfd = {
        enabled = true
      }
    })
  ]

  depends_on = [module.gke_cluster, module.gpu_node_pools]
}

# Kubernetes Namespaces
resource "kubernetes_namespace" "ml_training" {
  metadata {
    name = "ml-training"
    labels = merge(
      local.common_labels,
      {
        purpose = "machine-learning-training"
      }
    )
  }

  depends_on = [module.gke_cluster]
}

resource "kubernetes_namespace" "production" {
  metadata {
    name = "production"
    labels = merge(
      local.common_labels,
      {
        purpose = "production-inference"
      }
    )
  }

  depends_on = [module.gke_cluster]
}

resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
    labels = merge(
      local.common_labels,
      {
        purpose = "observability"
      }
    )
  }

  depends_on = [module.gke_cluster]
}

# Google Cloud Storage Bucket for Models
resource "google_storage_bucket" "models" {
  name          = "${var.project_id}-models"
  location      = var.region
  project       = var.project_id
  force_destroy = false

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  labels = local.common_labels
}

resource "google_storage_bucket" "checkpoints" {
  name          = "${var.project_id}-checkpoints"
  location      = var.region
  project       = var.project_id
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = local.common_labels
}

# Service Accounts for Workload Identity
resource "google_service_account" "training_sa" {
  account_id   = "gke-training-sa"
  display_name = "GKE Training Service Account"
  project      = var.project_id
}

resource "google_service_account" "inference_sa" {
  account_id   = "gke-inference-sa"
  display_name = "GKE Inference Service Account"
  project      = var.project_id
}

# IAM Bindings
resource "google_project_iam_member" "training_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.training_sa.email}"
}

resource "google_project_iam_member" "inference_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.inference_sa.email}"
}

# Workload Identity Binding
resource "google_service_account_iam_member" "training_workload_identity" {
  service_account_id = google_service_account.training_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[ml-training/training-sa]"
}

resource "google_service_account_iam_member" "inference_workload_identity" {
  service_account_id = google_service_account.inference_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[production/inference-sa]"
}

# Kubernetes Service Accounts
resource "kubernetes_service_account" "training_sa" {
  metadata {
    name      = "training-sa"
    namespace = kubernetes_namespace.ml_training.metadata[0].name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.training_sa.email
    }
  }
}

resource "kubernetes_service_account" "inference_sa" {
  metadata {
    name      = "inference-sa"
    namespace = kubernetes_namespace.production.metadata[0].name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.inference_sa.email
    }
  }
}

# Budget Alert
resource "google_billing_budget" "gpu_budget" {
  count = var.budget_amount > 0 ? 1 : 0

  billing_account = var.billing_account_id
  display_name    = "GPU Compute Budget"

  budget_filter {
    projects = ["projects/${data.google_project.project.number}"]
    labels = {
      environment = var.environment
    }
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = tostring(var.budget_amount)
    }
  }

  threshold_rules {
    threshold_percent = 0.5
  }

  threshold_rules {
    threshold_percent = 0.8
  }

  threshold_rules {
    threshold_percent = 1.0
  }

  all_updates_rule {
    monitoring_notification_channels = var.budget_notification_channels
    disable_default_iam_recipients   = false
  }
}

data "google_project" "project" {
  project_id = var.project_id
}
