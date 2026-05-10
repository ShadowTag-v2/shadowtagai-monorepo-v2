# Eventarc Trigger for Vision Refinery (vLLM)
# Triggers when a file is finalized in the input bucket.

resource "google_eventarc_trigger" "vllm_doc_processor" {
  name     = "vllm-doc-processor-trigger"
  location = var.region

  # Capture GCS Object Finalize events (File Uploads)
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }

  # Filter by specific bucket
  matching_criteria {
    attribute = "bucket"
    value     = "shadowtag-input-docs" # Placeholder bucket name
  }

  destination {
    cloud_run_service {
      service = "vllm-doc-parser"
      region  = var.region
    }
  }

  service_account = google_service_account.cloud_run_invoker.email
}

# Service Account for Eventarc to invoke Cloud Run
resource "google_service_account" "cloud_run_invoker" {
  account_id   = "eventarc-invoker"
  display_name = "Eventarc Cloud Run Invoker"
}

resource "google_project_iam_binding" "eventarc_invoker_binding" {
  project = var.project_id
  role    = "roles/run.invoker"
  members = ["serviceAccount:${google_service_account.cloud_run_invoker.email}"]
}
