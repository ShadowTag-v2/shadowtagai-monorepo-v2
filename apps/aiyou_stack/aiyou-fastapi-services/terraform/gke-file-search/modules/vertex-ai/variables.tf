# ============================================================================
# VERTEX AI MODULE VARIABLES
# ============================================================================

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Vertex AI"
  type        = string
}

variable "verticals" {
  description = "Map of verticals with regulatory requirements"
  type = map(object({
    regulations = list(string)
    description = string
  }))
}

variable "chunk_size" {
  description = "RAG corpus chunk size"
  type        = number
  default     = 512
}

variable "chunk_overlap" {
  description = "RAG corpus chunk overlap"
  type        = number
  default     = 100
}

variable "config_bucket" {
  description = "GCS bucket for configuration files"
  type        = string
}

variable "create_workbench_instance" {
  description = "Create Vertex AI Workbench instance"
  type        = bool
  default     = false
}

variable "workbench_machine_type" {
  description = "Machine type for Workbench instance"
  type        = string
  default     = "n1-standard-4"
}

variable "alert_email" {
  description = "Email for monitoring alerts"
  type        = string
  default     = "alerts@pnkln.com"
}
