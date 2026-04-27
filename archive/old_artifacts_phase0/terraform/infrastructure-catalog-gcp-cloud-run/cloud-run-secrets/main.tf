# Cloud Run Secrets Module
# Grants Secret Manager accessor role to Cloud Run service accounts

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "service_account_email" {
  type        = string
  description = "Service account email that needs secret access."
}

variable "secret_ids" {
  type        = list(string)
  description = "List of Secret Manager secret IDs to grant access to."
  validation {
    condition     = length(var.secret_ids) > 0
    error_message = "At least one secret ID must be provided."
  }
}

# Grant secretAccessor on each secret
resource "google_secret_manager_secret_iam_member" "accessor" {
  for_each  = toset(var.secret_ids)
  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}

output "granted_secrets" {
  value       = [for s in var.secret_ids : s]
  description = "List of secret IDs with accessor grants."
}
