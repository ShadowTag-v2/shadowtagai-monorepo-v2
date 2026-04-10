# ============================================================================
# IAM MODULE VARIABLES
# ============================================================================

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
}

variable "gke_service_account" {
  description = "GKE service account email"
  type        = string
}

variable "workload_identity_namespace" {
  description = "Kubernetes namespace for Workload Identity"
  type        = string
}

variable "kubernetes_sa_name" {
  description = "Kubernetes service account name"
  type        = string
}

variable "corpus_buckets" {
  description = "List of corpus bucket names"
  type        = map(string)
}
