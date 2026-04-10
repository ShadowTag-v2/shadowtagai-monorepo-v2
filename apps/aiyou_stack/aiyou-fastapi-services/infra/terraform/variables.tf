variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "deployment_region" {
  description = "Region to deploy resources"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "n-autoresearch/Kosmos/BioAgentss-server"
}

variable "repository_name" {
  description = "Name of the GitHub repository (e.g., owner/repo)"
  type        = string
  default     = "ShadowTag-v2/aiyou-fastapi-services"
}
