variable "project_id" {
  type        = string
  description = "The GCP project ID"
}

variable "region" {
  type        = string
  description = "The GCP region"
  default     = "us-central1"
}

variable "instance_name" {
  type        = string
  description = "The name of the Redis instance"
  default     = "counselconduit-redis"
}

variable "tier" {
  type        = string
  description = "The service tier of the instance (BASIC or STANDARD_HA)"
  default     = "BASIC"
}

variable "memory_size_gb" {
  type        = number
  description = "Redis memory size in GiB"
  default     = 1
}

variable "vpc_network_id" {
  type        = string
  description = "The ID of the VPC network to attach to"
}
