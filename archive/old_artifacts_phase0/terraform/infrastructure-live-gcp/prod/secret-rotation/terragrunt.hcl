# Secret Rotation Automation — Cloud Scheduler + Secret Manager
# Item 21: Automated secret rotation via Cloud Scheduler

include "root" {
  path = find_in_parent_folders("terragrunt.hcl")
}

terraform {
  source = "../../../../infrastructure-catalog-gcp-cloud-run//cloud-scheduler"
}

inputs = {
  jobs = [
    {
      name             = "secret-rotation-check"
      description      = "Check for secrets approaching expiry and send alerts"
      schedule         = "0 9 * * 1"  # Every Monday at 9am
      time_zone        = "America/New_York"
      attempt_deadline = "300s"
      region           = "us-central1"

      http_target = {
        uri         = "https://counselconduit-767252945109.us-central1.run.app/admin/secret-rotation-check"
        http_method = "POST"
        body        = "{\"check_type\": \"expiry_warning\", \"threshold_days\": 30}"
        headers     = { "Content-Type" = "application/json" }

        oidc_token = {
          service_account_email = "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
          audience              = "https://counselconduit-767252945109.us-central1.run.app"
        }
      }
    },
    {
      name             = "stripe-key-rotation-reminder"
      description      = "Monthly reminder to rotate Stripe API keys"
      schedule         = "0 10 1 * *"  # 1st of each month
      time_zone        = "America/New_York"
      attempt_deadline = "60s"
      region           = "us-central1"

      http_target = {
        uri         = "https://counselconduit-767252945109.us-central1.run.app/admin/rotation-reminder"
        http_method = "POST"
        body        = "{\"secret_name\": \"stripe-secret-key\", \"action\": \"remind\"}"
        headers     = { "Content-Type" = "application/json" }

        oidc_token = {
          service_account_email = "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com"
          audience              = "https://counselconduit-767252945109.us-central1.run.app"
        }
      }
    }
  ]
}
