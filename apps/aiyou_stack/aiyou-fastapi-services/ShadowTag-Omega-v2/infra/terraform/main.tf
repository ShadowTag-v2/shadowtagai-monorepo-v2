provider "google" { project = "shadowtag-omega-v2"; region = "us-central1" }
resource "google_workstations_workstation_cluster" "c" { workstation_cluster_id="antigravity-v2"; location="us-central1" }
resource "google_storage_bucket" "l" { name="shadowtag-omega-v2-lake"; location="US" }
resource "google_project_service" "s" { for_each=toset(["firestore.googleapis.com","workstations.googleapis.com"]); service=each.key }
