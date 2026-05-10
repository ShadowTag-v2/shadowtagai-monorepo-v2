resource "google_project_service" "apis" {
  for_each = toset(["firestore.googleapis.com","workstations.googleapis.com","bigquery.googleapis.com"])
  service = each.key; disable_on_destroy=false
}
