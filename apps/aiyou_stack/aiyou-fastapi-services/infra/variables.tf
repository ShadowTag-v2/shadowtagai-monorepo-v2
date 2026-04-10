# Core project configuration
variable "project_id" {
  description = "GCP project ID for PNKLN deployment"
  type        = string
}

variable "region" {
  description = "GCP region for resources (us-central1 recommended for GPU availability)"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Primary GCP zone for zonal resources"
  type        = string
  default     = "us-central1-a"
}

# Cluster configuration
variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "pnkln-gke-cluster"
}

variable "cluster_type" {
  description = "GKE cluster type: autopilot or standard"
  type        = string
  default     = "standard"
  validation {
    condition     = contains(["autopilot", "standard"], var.cluster_type)
    error_message = "cluster_type must be either 'autopilot' or 'standard'"
  }
}

variable "network_name" {
  description = "VPC network name"
  type        = string
  default     = "pnkln-network"
}

# GPU node pool configuration
variable "gpu_node_pools" {
  description = "GPU node pool configurations for inference workloads"
  type = map(object({
    machine_type       = string
    gpu_type          = string
    gpu_count         = number
    min_node_count    = number
    max_node_count    = number
    disk_size_gb      = number
    disk_type         = string
    preemptible       = bool
    spot              = bool
  }))
  default = {
    # L4 GPU pool - Cost optimized for inference (Judge #6 workload)
    "l4-inference" = {
      machine_type    = "g2-standard-4"
      gpu_type        = "nvidia-l4"
      gpu_count       = 1
      min_node_count  = 0
      max_node_count  = 3
      disk_size_gb    = 100
      disk_type       = "pd-balanced"
      preemptible     = false
      spot            = true  # Enable spot VMs for cost savings
    }
    # H100 GPU pool - High performance for production (scales to zero)
    "h100-production" = {
      machine_type    = "a3-highgpu-1g"
      gpu_type        = "nvidia-h100-80gb"
      gpu_count       = 1
      min_node_count  = 0
      max_node_count  = 2
      disk_size_gb    = 200
      disk_type       = "pd-balanced"
      preemptible     = false
      spot            = false
    }
  }
}

# CPU node pool for non-GPU workloads
variable "cpu_node_pool" {
  description = "CPU node pool configuration for control plane and non-GPU services"
  type = object({
    machine_type    = string
    min_node_count  = number
    max_node_count  = number
    disk_size_gb    = number
  })
  default = {
    machine_type    = "n2-standard-4"
    min_node_count  = 1
    max_node_count  = 5
    disk_size_gb    = 50
  }
}

# Network configuration
variable "pod_cidr" {
  description = "CIDR range for pods"
  type        = string
  default     = "10.4.0.0/14"
}

variable "service_cidr" {
  description = "CIDR range for services"
  type        = string
  default     = "10.8.0.0/20"
}

variable "master_cidr" {
  description = "CIDR range for GKE master nodes (private cluster)"
  type        = string
  default     = "172.16.0.0/28"
}

# Storage configuration
variable "model_bucket_name" {
  description = "GCS bucket name for model storage (must be globally unique)"
  type        = string
}

# Cost optimization
variable "enable_autoscaling" {
  description = "Enable cluster autoscaling for cost optimization"
  type        = bool
  default     = true
}

variable "enable_workload_identity" {
  description = "Enable workload identity for secure GCS access"
  type        = bool
  default     = true
}

# Monitoring and observability
variable "enable_managed_prometheus" {
  description = "Enable Google Cloud Managed Service for Prometheus"
  type        = bool
  default     = true
}

variable "enable_cloud_logging" {
  description = "Enable Cloud Logging for cluster"
  type        = bool
  default     = true
}

variable "enable_cloud_monitoring" {
  description = "Enable Cloud Monitoring for cluster"
  type        = bool
  default     = true
}

# Security
variable "enable_private_nodes" {
  description = "Enable private IP addresses for nodes"
  type        = bool
  default     = true
}

variable "enable_private_endpoint" {
  description = "Enable private endpoint for GKE master"
  type        = bool
  default     = false  # Set to true for production
}

variable "master_authorized_networks" {
  description = "CIDR blocks that can access the GKE master endpoint"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = [
    {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks (replace with Vertex AI Workbench IPs)"
    }
  ]
}

# Labels for cost tracking
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    environment = "production"
    managed-by  = "terraform"
    project     = "pnkln"
    cost-center = "ai-inference"
  }
}
