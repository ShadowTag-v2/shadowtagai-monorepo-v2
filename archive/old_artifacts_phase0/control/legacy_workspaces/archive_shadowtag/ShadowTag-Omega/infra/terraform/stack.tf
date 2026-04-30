resource "google_workstations_workstation_cluster" "c" { provider=google; workstation_cluster_id="antigravity"; location="us-central1" }
resource "google_storage_bucket" "l" { name="acquired-jet-velocity-lake"; location="US" }
resource "google_project_service" "s" { for_each=toset(["firestore.googleapis.com","workstations.googleapis.com","bigquery.googleapis.com"]); service=each.key }
