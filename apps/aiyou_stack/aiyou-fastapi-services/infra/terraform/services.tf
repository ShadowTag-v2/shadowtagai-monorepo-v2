
resource "google_project_service" "required_apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "dataflow.googleapis.com",
    # "managedkafka.googleapis.com", # Removed by User Request
    "firestore.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "discoveryengine.googleapis.com",
    "aiplatform.googleapis.com",
    "dataform.googleapis.com",
    # User Requested APIs
    "developerconnect.googleapis.com",
    "containeranalysis.googleapis.com",
    "iam.googleapis.com",
    "compute.googleapis.com",
    "workstations.googleapis.com"
  ])

  service            = each.key
  disable_on_destroy = false
}
