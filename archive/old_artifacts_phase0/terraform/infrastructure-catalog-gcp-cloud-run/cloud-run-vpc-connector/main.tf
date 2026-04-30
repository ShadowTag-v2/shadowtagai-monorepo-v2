# Cloud Run VPC Connector Module
# Provisions a Serverless VPC Access connector for private networking

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region."
}

variable "name" {
  type        = string
  description = "VPC connector name."
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,24}$", var.name))
    error_message = "Name must be lowercase, 3-25 chars."
  }
}

variable "network" {
  type        = string
  default     = "default"
  description = "VPC network name or self_link."
}

variable "ip_cidr_range" {
  type        = string
  default     = "10.8.0.0/28"
  description = "CIDR range for the connector (must be /28 unused range)."
  validation {
    condition     = can(cidrhost(var.ip_cidr_range, 0))
    error_message = "Must be a valid CIDR range."
  }
}

variable "min_throughput" {
  type        = number
  default     = 200
  description = "Min throughput in Mbps (200-1000)."
}

variable "max_throughput" {
  type        = number
  default     = 300
  description = "Max throughput in Mbps (200-1000)."
}

resource "google_vpc_access_connector" "main" {
  project       = var.project_id
  region        = var.region
  name          = var.name
  network       = var.network
  ip_cidr_range = var.ip_cidr_range
  min_throughput = var.min_throughput
  max_throughput = var.max_throughput
}

output "connector" {
  value       = google_vpc_access_connector.main
  description = "The VPC Access connector resource."
}

output "connector_id" {
  value       = google_vpc_access_connector.main.id
  description = "The connector ID for use in Cloud Run."
}

output "connector_name" {
  value       = google_vpc_access_connector.main.name
  description = "The connector name."
}
