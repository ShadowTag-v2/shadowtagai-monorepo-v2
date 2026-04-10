# Terraform variables for shadowtagai orchestrator

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "anthropic_vertex_project_id" {
  description = "Anthropic Vertex AI Project ID"
  type        = string
  sensitive   = true
}
