terraform { required_providers { google = { source = "hashicorp/google", version = "~> 5.0" } } }
provider "google" { project = "shadowtag-omega-v2"; region = "us-central1" }
resource "google_billing_budget" "budget" {
  billing_account = "011219-FBD1F1-F5AB42"
  display_name    = "Antigravity-Safety-Net"
  budget_filter { projects = ["projects/shadowtag-omega-v2"] }
  amount { specified_amount { currency_code = "USD"; units = "100" } } # Hard Stop
  threshold_rules { threshold_percent = 0.5 }
  threshold_rules { threshold_percent = 0.9 }
}
