terraform {
  required_version = ">= 1.5.0"
}

# Source the GitHub Actions Runners from the Terraform Registry
module "gh_actions_runners" {
  source  = "terraform-google-modules/github-actions-runners/google"
  version = "~> 4.0"

  project_id = "shadowtag-omega-v4"
  region     = "us-central1"
  zone       = "us-central1-a"

  # Link context to our designated GitHub App
  github_app_id = "3018200"

  # Network config defaults inside the module
  network = "default"
  subnet  = "default"

  machine_type = "e2-medium"

  # Deploy 2 active runners bound to UphillSnowball
  target_size = 2
}
