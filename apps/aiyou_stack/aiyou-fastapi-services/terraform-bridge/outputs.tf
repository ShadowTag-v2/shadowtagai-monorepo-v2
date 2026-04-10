output "bridge_url" {
  description = "The HTTP URL of the Bridge Server"
  value       = google_cloud_run_v2_service.bridge_server.uri
}

output "repo_url" {
  description = "Push your bridge images here"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.bridge_repo.name}"
}

output "ssh_command" {
  description = "Command to SSH into the Workstation"
  value       = "gcloud workstations ssh brave-agent-workstation --region=${var.region} --cluster=agent-cluster --config=agent-config"
}
