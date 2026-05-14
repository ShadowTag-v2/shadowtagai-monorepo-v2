variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region for the Cloud Run service."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Name of the Cloud Run v2 service."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,48}[a-z0-9]$", var.service_name))
    error_message = "service_name must be lowercase alphanumeric + hyphens, 3-50 chars."
  }
}

variable "image" {
  description = "Full container image reference (e.g. us-docker.pkg.dev/project/repo/app:tag)."
  type        = string
}

variable "min_instances" {
  description = "Minimum number of warm instances (set >=1 for user-facing services)."
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances."
  type        = number
  default     = 10
}

variable "concurrency" {
  description = "Max concurrent requests per instance."
  type        = number
  default     = 80
}

variable "cpu" {
  description = "CPU limit per instance (e.g. '1', '2')."
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit per instance (e.g. '512Mi', '2Gi')."
  type        = string
  default     = "512Mi"
}

variable "startup_cpu_boost" {
  description = "Enable extra CPU during cold starts."
  type        = bool
  default     = true
}

variable "service_account_email" {
  description = "Service account email for the Cloud Run identity (least-privilege)."
  type        = string
  default     = null
}

variable "vpc_connector_id" {
  description = "VPC Access Connector ID for private networking. Null = public egress."
  type        = string
  default     = null
}

variable "vpc_egress" {
  description = "Egress policy when VPC connector is set."
  type        = string
  default     = "PRIVATE_RANGES_ONLY"
  validation {
    condition     = contains(["ALL_TRAFFIC", "PRIVATE_RANGES_ONLY"], var.vpc_egress)
    error_message = "vpc_egress must be ALL_TRAFFIC or PRIVATE_RANGES_ONLY."
  }
}

variable "cloud_sql_instances" {
  description = "List of Cloud SQL connection names (project:region:instance)."
  type        = list(string)
  default     = []
}

variable "env_vars" {
  description = "Static environment variables injected at runtime."
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secret Manager references injected as env vars."
  type = list(object({
    env_var_name = string
    secret_id    = string
    version      = optional(string, "latest")
  }))
  default = []
}

variable "traffic" {
  description = "Traffic split configuration. Supports canary deployments."
  type = list(object({
    percent         = number
    latest_revision = optional(bool, true)
    revision        = optional(string, null)
  }))
  default = [{ percent = 100, latest_revision = true }]
}

variable "allow_unauthenticated" {
  description = "Allow public unauthenticated invocations."
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Prevent accidental service deletion."
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels applied to the service."
  type        = map(string)
  default     = {}
}

variable "environment" {
  description = "Deployment environment name for labels and observability."
  type        = string
  default     = "prod"
}
