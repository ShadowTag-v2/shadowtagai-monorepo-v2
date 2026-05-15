# ============================================================================
# VARIABLES - GKE + FILE SEARCH INTEGRATION
# ============================================================================

# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

variable "project_id" {
  description = "GCP project ID for Pnkln Core Stack"
  type        = string
  default     = "pnkln-core-gke"
}

variable "region" {
  description = "GCP region for deployment (recommend us-central1 for Hypercomputer)"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

# ============================================================================
# GKE CLUSTER CONFIGURATION
# ============================================================================

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "pnkln-core-cluster"
}

variable "network_name" {
  description = "VPC network name for GKE cluster"
  type        = string
  default     = "pnkln-vpc"
}

variable "subnetwork_name" {
  description = "Subnetwork name for GKE cluster"
  type        = string
  default     = "pnkln-gke-subnet"
}

variable "node_pool_config" {
  description = "GKE node pool configuration"
  type = object({
    machine_type   = string
    min_nodes      = number
    max_nodes      = number
    disk_size_gb   = number
    disk_type      = string
    preemptible    = bool
    spot           = bool
  })

  default = {
    machine_type   = "n2-standard-8"
    min_nodes      = 3
    max_nodes      = 10
    disk_size_gb   = 100
    disk_type      = "pd-ssd"
    preemptible    = false
    spot           = false
  }
}

# ============================================================================
# VERTEX AI / FILE SEARCH CONFIGURATION
# ============================================================================

variable "rag_chunk_size" {
  description = "RAG corpus chunk size (optimal for policy docs)"
  type        = number
  default     = 512
}

variable "rag_chunk_overlap" {
  description = "RAG corpus chunk overlap"
  type        = number
  default     = 100
}

variable "enable_file_search" {
  description = "Enable Vertex AI File Search API"
  type        = bool
  default     = true
}

# ============================================================================
# GCS BUCKET CONFIGURATION
# ============================================================================

variable "bucket_prefix" {
  description = "Prefix for GCS policy corpus buckets"
  type        = string
  default     = "pnkln-policy-corpus"
}

variable "enable_bucket_versioning" {
  description = "Enable versioning for policy corpus buckets"
  type        = bool
  default     = true
}

variable "bucket_lifecycle_rules" {
  description = "Lifecycle rules for GCS buckets"
  type = list(object({
    action = object({
      type          = string
      storage_class = optional(string)
    })
    condition = object({
      age                   = optional(number)
      num_newer_versions    = optional(number)
      with_state            = optional(string)
    })
  }))

  default = [
    {
      action = {
        type = "Delete"
      }
      condition = {
        num_newer_versions = 5
        with_state        = "ARCHIVED"
      }
    }
  ]
}

# ============================================================================
# WORKLOAD IDENTITY CONFIGURATION
# ============================================================================

variable "workload_identity_namespace" {
  description = "Kubernetes namespace for Workload Identity"
  type        = string
  default     = "pnkln-core"
}

variable "kubernetes_sa_name" {
  description = "Kubernetes service account name"
  type        = string
  default     = "pnkln-file-search-sa"
}

# ============================================================================
# PERFORMANCE & MONITORING
# ============================================================================

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring for GKE cluster"
  type        = bool
  default     = true
}

variable "enable_logging" {
  description = "Enable Cloud Logging for GKE cluster"
  type        = bool
  default     = true
}

variable "latency_sla" {
  description = "Latency SLA thresholds (ms)"
  type = object({
    judge_p99           = number
    file_search_p99     = number
    total_acceptable    = number
  })

  default = {
    judge_p99           = 90
    file_search_p99     = 1000
    total_acceptable    = 850
  }
}

# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

variable "enable_binary_authorization" {
  description = "Enable Binary Authorization for GKE"
  type        = bool
  default     = true
}

variable "enable_shielded_nodes" {
  description = "Enable Shielded GKE Nodes"
  type        = bool
  default     = true
}

variable "enable_pod_security_policy" {
  description = "Enable Pod Security Policy"
  type        = bool
  default     = true
}

# ============================================================================
# COST OPTIMIZATION
# ============================================================================

variable "enable_autopilot" {
  description = "Use GKE Autopilot mode (simplified, cost-optimized)"
  type        = bool
  default     = false
}

variable "enable_cluster_autoscaling" {
  description = "Enable cluster-level autoscaling"
  type        = bool
  default     = true
}

variable "budget_alert_threshold" {
  description = "Budget alert threshold (USD per month)"
  type        = number
  default     = 5000
}
