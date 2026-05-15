# Variables for YouAi GKE GPU Infrastructure

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "youai"
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "master_authorized_networks" {
  description = "List of CIDR blocks that can access the GKE master"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = [
    {
      cidr_block   = "10.0.0.0/8"
      display_name = "Internal Network"
    }
  ]
}

variable "enable_prometheus" {
  description = "Enable Prometheus ServiceMonitor for DCGM metrics"
  type        = bool
  default     = true
}

variable "billing_account_id" {
  description = "GCP Billing Account ID for budget alerts"
  type        = string
  default     = ""
}

variable "budget_amount" {
  description = "Monthly budget amount in USD (0 to disable)"
  type        = number
  default     = 50000
}

variable "budget_notification_channels" {
  description = "List of notification channel IDs for budget alerts"
  type        = list(string)
  default     = []
}
