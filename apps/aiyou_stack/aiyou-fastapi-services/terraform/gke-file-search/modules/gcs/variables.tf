# ============================================================================
# GCS MODULE VARIABLES
# ============================================================================

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCS bucket region"
  type        = string
}

variable "verticals" {
  description = "Map of verticals with regulatory requirements"
  type = map(object({
    regulations = list(string)
    description = string
  }))
}

variable "bucket_prefix" {
  description = "Prefix for bucket names"
  type        = string
}

variable "enable_versioning" {
  description = "Enable bucket versioning"
  type        = bool
  default     = true
}

variable "lifecycle_rules" {
  description = "Lifecycle rules for buckets"
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
}

variable "labels" {
  description = "Resource labels"
  type        = map(string)
  default     = {}
}
