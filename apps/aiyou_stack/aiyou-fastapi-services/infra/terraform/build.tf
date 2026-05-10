resource "google_cloudbuild_trigger" "manual_trigger" {
  name        = "${var.service_name}-trigger"
  description = "Trigger for ${var.service_name} on main branch"

  github {
    owner = split("/", var.repository_name)[0]
    name  = split("/", var.repository_name)[1]
    push {
      branch = "^main$"
    }
  }

  substitutions = {
    _SERVICE_NAME = var.service_name
    _DEPLOY_REGION = var.deployment_region
  }

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "gcr.io/${var.project_id}/${var.service_name}:$COMMIT_SHA", "-t", "gcr.io/${var.project_id}/${var.service_name}:latest", "."]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${var.project_id}/${var.service_name}:$COMMIT_SHA"]
    }

    step {
        name = "gcr.io/cloud-builders/docker"
        args = ["push", "gcr.io/${var.project_id}/${var.service_name}:latest"]
    }

    step {
      name = "gcr.io/google.com/cloudsdktool/cloud-sdk"
      entrypoint = "gcloud"
      args = [
        "run", "deploy", var.service_name,
        "--image", "gcr.io/${var.project_id}/${var.service_name}:$COMMIT_SHA",
        "--region", var.deployment_region,
        "--project", var.project_id
      ]
    }

    images = ["gcr.io/${var.project_id}/${var.service_name}:$COMMIT_SHA", "gcr.io/${var.project_id}/${var.service_name}:latest"]
  }
}
