# 10_wif.tf
# Save in terraform-stack/

# 1. The Pool (The Container for External Identities)
resource "google_iam_workload_identity_pool" "github_pool" {
  workload_identity_pool_id = "github-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Identity pool for GitHub Actions"
  disabled                  = false
}

# 2. The Provider (The Trust Configuration)
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"
  description                        = "OIDC provider for GitHub Actions"
  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# 3. The Binding (Granting the "Brain" Role to the Repo)
# REPLACE 'YOUR_GITHUB_USER/YOUR_REPO_NAME' below!
resource "google_service_account_iam_member" "wif_binding" {
  service_account_id = google_service_account.brain_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/YOUR_GITHUB_USER/YOUR_REPO_NAME"
}

output "wif_provider_name" {
  value = google_iam_workload_identity_pool_provider.github_provider.name
}
output "service_account_email" {
  value = google_service_account.brain_sa.email
}
