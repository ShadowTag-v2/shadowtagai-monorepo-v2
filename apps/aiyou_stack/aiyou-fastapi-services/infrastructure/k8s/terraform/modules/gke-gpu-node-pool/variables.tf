# Variables for GKE GPU Node Pool Module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
}

variable "location" {
  description = "Location (region or zone) of the cluster"
  type        = string
}

variable "pool_name" {
  description = "Name of the node pool"
  type        = string
}

variable "machine_type" {
  description = "Machine type for nodes"
  type        = string
}

variable "accelerator_type" {
  description = "GPU accelerator type (e.g., nvidia-tesla-a100)"
  type        = string
}

variable "accelerator_count" {
  description = "Number of GPUs per node"
  type        = number
}

variable "disk_size_gb" {
  description = "Disk size in GB"
  type        = number
  default     = 100
}

variable "disk_type" {
  description = "Disk type (pd-standard, pd-balanced, pd-ssd)"
  type        = string
  default     = "pd-balanced"
}

variable "min_node_count" {
  description = "Minimum number of nodes"
  type        = number
  default     = 0
}

variable "max_node_count" {
  description = "Maximum number of nodes"
  type        = number
  default     = 10
}

variable "initial_node_count" {
  description = "Initial number of nodes (will be managed by autoscaler)"
  type        = number
  default     = 0
}

variable "preemptible" {
  description = "Use spot VMs (preemptible)"
  type        = bool
  default     = false
}

variable "node_labels" {
  description = "Labels to apply to nodes"
  type        = map(string)
  default     = {}
}

variable "node_taints" {
  description = "Taints to apply to nodes"
  type = list(object({
    key    = string
    value  = string
    effect = string
  }))
  default = []
}

variable "gpu_sharing_strategy" {
  description = "GPU sharing strategy (TIME_SHARING or MPS)"
  type        = string
  default     = "TIME_SHARING"
}

variable "max_shared_clients_per_gpu" {
  description = "Max shared clients per GPU (for time-sharing)"
  type        = number
  default     = 2
}

variable "enable_compact_placement" {
  description = "Enable compact placement policy for better multi-GPU performance"
  type        = bool
  default     = false
}
