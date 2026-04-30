# Item 10: Wire WIF into prod Terragrunt stack
include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../infrastructure-catalog-gcp-cloud-run//github-wif"
}

inputs = {
  project_id     = "shadowtag-omega-v4"
  project_number = "767252945109"
  github_org     = "ShadowTag-v2"
  github_repo    = "Monorepo-Uphillsnowball"

  roles = [
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.writer",
    "roles/clouddeploy.operator",
    "roles/monitoring.viewer",
    "roles/firebasehosting.admin",
  ]
}
