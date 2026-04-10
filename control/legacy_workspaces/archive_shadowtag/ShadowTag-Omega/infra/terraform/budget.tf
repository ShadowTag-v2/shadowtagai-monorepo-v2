resource "google_billing_budget" "safety" {
  billing_account = "011219-FBD1F1-F5AB42"; display_name = "Antigravity-Safety-Net"
  amount { specified_amount { currency_code = "USD"; units = "100" } }
}
