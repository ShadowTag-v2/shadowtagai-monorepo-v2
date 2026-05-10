# Artifact Registry for container images

resource "google_artifact_registry_repository" "shadowtagai" {
  location      = var.region
  repository_id = "shadowtagai"
  description   = "shadowtagai orchestrator container images"
  format        = "DOCKER"
  project       = var.project_id

  docker_config {
    immutable_tags = false
  }

  cleanup_policies {
    id     = "keep-recent-versions"
    action = "KEEP"

    most_recent_versions {
      keep_count = 10
    }
  }

  cleanup_policies {
    id     = "delete-old-untagged"
    action = "DELETE"

    condition {
      tag_state  = "UNTAGGED"
      older_than = "2592000s" # 30 days
    }
  }

  depends_on = [google_project_service.required_apis]
}

# IAM binding for Cloud Build to push images
resource "google_artifact_registry_repository_iam_member" "cloudbuild_writer" {
  project    = var.project_id
  location   = google_artifact_registry_repository.shadowtagai.location
  repository = google_artifact_registry_repository.shadowtagai.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

output "artifact_registry_url" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.shadowtagai.repository_id}"
  description = "Artifact Registry repository URL"
}
