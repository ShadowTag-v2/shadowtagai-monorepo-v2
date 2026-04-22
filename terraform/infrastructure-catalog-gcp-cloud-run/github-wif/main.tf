# Workload Identity Federation for GitHub Actions
# Eliminates the need for long-lived service account keys
# See: https://cloud.google.com/iam/docs/workload-identity-federation

variable "project_id" {
  type        = string
  description = "GCP project ID."
}

variable "project_number" {
  type        = string
  description = "GCP project number."
}

variable "github_org" {
  type        = string
  default     = "ShadowTag-v2"
  description = "GitHub organization name."
}

variable "github_repo" {
  type        = string
  default     = "Monorepo-Uphillsnowball"
  description = "GitHub repository name."
}

variable "pool_id" {
  type        = string
  default     = "github-actions-pool"
  description = "Workload Identity Pool ID."
}

variable "provider_id" {
  type        = string
  default     = "github-actions-provider"
  description = "Workload Identity Provider ID."
}

variable "service_account_id" {
  type        = string
  default     = "github-actions-sa"
  description = "Service account for GitHub Actions."
}

variable "roles" {
  type = list(string)
  default = [
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.writer",
    "roles/clouddeploy.operator",
    "roles/monitoring.viewer",
  ]
  description = "IAM roles to grant the GitHub Actions service account."
}

# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github" {
  project                   = var.project_id
  workload_identity_pool_id = var.pool_id
  display_name              = "GitHub Actions Pool"
  description               = "WIF pool for GitHub Actions CI/CD"
}

# OIDC Provider
resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = var.provider_id
  display_name                       = "GitHub Actions OIDC"

  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.actor"            = "assertion.actor"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }

  attribute_condition = "assertion.repository_owner == '${var.github_org}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Service Account for GitHub Actions
resource "google_service_account" "github_actions" {
  project      = var.project_id
  account_id   = var.service_account_id
  display_name = "GitHub Actions Service Account"
  description  = "Used by GitHub Actions via WIF — no long-lived keys"
}

# Bind WIF pool to service account
resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/projects/${var.project_number}/locations/global/workloadIdentityPools/${var.pool_id}/attribute.repository/${var.github_org}/${var.github_repo}"
}

# Grant IAM roles
resource "google_project_iam_member" "github_actions_roles" {
  for_each = toset(var.roles)
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.github_actions.email}"
}

output "workload_identity_provider" {
  value       = google_iam_workload_identity_pool_provider.github.name
  description = "Full WIF provider resource name — use as WIF_PROVIDER secret in GitHub."
}

output "service_account_email" {
  value       = google_service_account.github_actions.email
  description = "GitHub Actions SA email — use as WIF_SA secret in GitHub."
}
