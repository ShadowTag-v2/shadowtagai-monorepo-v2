# Cloud Run IAM Module
# Flexible for_each role bindings for Cloud Run services

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region."
}

variable "service_name" {
  type        = string
  description = "Cloud Run service name to bind IAM to."
}

variable "public_access" {
  type        = bool
  default     = false
  description = "If true, grants allUsers the invoker role (public access)."
}

variable "invokers" {
  type        = list(string)
  default     = []
  description = "List of members to grant roles/run.invoker (e.g. 'serviceAccount:sa@proj.iam.gserviceaccount.com')."
}

variable "custom_bindings" {
  type = map(object({
    role    = string
    members = list(string)
  }))
  default     = {}
  description = "Additional custom IAM bindings. Key is arbitrary label."
}

# Public access binding
resource "google_cloud_run_v2_service_iam_member" "public" {
  count    = var.public_access ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Named invoker bindings
resource "google_cloud_run_v2_service_iam_member" "invokers" {
  for_each = toset(var.invokers)
  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = "roles/run.invoker"
  member   = each.value
}

# Custom role bindings
resource "google_cloud_run_v2_service_iam_member" "custom" {
  for_each = { for pair in flatten([
    for key, binding in var.custom_bindings : [
      for member in binding.members : {
        key    = "${key}-${member}"
        role   = binding.role
        member = member
      }
    ]
  ]) : pair.key => pair }

  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = each.value.role
  member   = each.value.member
}
