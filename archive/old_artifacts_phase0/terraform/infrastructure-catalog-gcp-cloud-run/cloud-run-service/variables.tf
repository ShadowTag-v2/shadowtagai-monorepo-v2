variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region for the Cloud Run service."
}

variable "service_name" {
  type        = string
  description = "Name of the Cloud Run service."
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,62}$", var.service_name))
    error_message = "Service name must be lowercase, start with a letter, 3-63 chars."
  }
}

variable "image" {
  type        = string
  description = "Container image URI (e.g. us-central1-docker.pkg.dev/project/repo/image:tag)."
}

variable "min_instances" {
  type        = number
  default     = 0
  description = "Minimum number of instances (0 = scale to zero)."
  validation {
    condition     = var.min_instances >= 0 && var.min_instances <= 100
    error_message = "min_instances must be 0-100."
  }
}

variable "max_instances" {
  type        = number
  default     = 10
  description = "Maximum number of instances."
  validation {
    condition     = var.max_instances >= 1 && var.max_instances <= 1000
    error_message = "max_instances must be 1-1000."
  }
}

variable "cpu" {
  type        = string
  default     = "1000m"
  description = "CPU allocation (e.g. 1000m, 2000m)."
}

variable "memory" {
  type        = string
  default     = "512Mi"
  description = "Memory allocation (e.g. 256Mi, 512Mi, 1Gi)."
}

variable "concurrency" {
  type        = number
  default     = 100
  description = "Max concurrent requests per instance (80-250 typical)."
}

variable "startup_cpu_boost" {
  type        = bool
  default     = true
  description = "Enable startup CPU boost for faster cold starts."
}

variable "env" {
  type        = string
  default     = "prod"
  description = "Environment label (prod, staging, dev)."
}

variable "env_vars" {
  type        = map(string)
  default     = {}
  description = "Plain-text environment variables."
}

variable "secret_env_vars" {
  type        = map(string)
  default     = {}
  description = "Secret Manager references as name:version (e.g. stripe-key:latest)."
}

variable "service_account" {
  type        = string
  default     = ""
  description = "Service account email. Empty = default compute SA."
}

variable "vpc_connector" {
  type        = string
  default     = ""
  description = "VPC connector name for private networking."
}

variable "trace_sample_rate" {
  type        = string
  default     = "0.1"
  description = "OTEL trace sampling rate (0.0-1.0)."
}

variable "health_check_path" {
  type        = string
  default     = "/health"
  description = "Health check endpoint path."
}

variable "ingress" {
  type        = string
  default     = "INGRESS_TRAFFIC_ALL"
  description = "Ingress traffic filter."
  validation {
    condition     = contains(["INGRESS_TRAFFIC_ALL", "INGRESS_TRAFFIC_INTERNAL_ONLY", "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"], var.ingress)
    error_message = "Invalid ingress setting."
  }
}
