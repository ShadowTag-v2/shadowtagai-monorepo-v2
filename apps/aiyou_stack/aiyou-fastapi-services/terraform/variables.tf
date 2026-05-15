# Variables for PNKLN Core Stack GKE Inference Infrastructure

variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "pnkln-core-stack"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "pnkln-inference-prod"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}
