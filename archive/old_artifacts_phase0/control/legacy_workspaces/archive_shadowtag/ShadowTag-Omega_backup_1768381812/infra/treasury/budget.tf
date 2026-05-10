resource "google_billing_budget" "budget" {
  billing_account = "011219-FBD1F1-F5AB42"; display_name = "Antigravity-Safety-Net"
  amount { specified_amount { currency_code = "USD"; units = "100" } }
  threshold_rules { threshold_percent = 0.5 }
}
