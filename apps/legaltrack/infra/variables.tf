variable "project_id" {
  type        = string
  description = "The GCP Project ID."
  default     = "shadowtag-omega-v4" 
}

variable "region" {
  type        = string
  description = "The default GCP region for serverless deployment."
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "The deployment environment (e.g. dev, prod, staging)."
  default     = "prod"
}
