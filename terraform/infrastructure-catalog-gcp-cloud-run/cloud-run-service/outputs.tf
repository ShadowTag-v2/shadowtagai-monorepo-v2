output "service" {
  value       = google_cloud_run_v2_service.main
  description = "The Cloud Run v2 service resource."
}

output "service_name" {
  value       = google_cloud_run_v2_service.main.name
  description = "Cloud Run service name."
}

output "uri" {
  value       = google_cloud_run_v2_service.main.uri
  description = "The URL of the Cloud Run service."
}

output "latest_revision" {
  value       = google_cloud_run_v2_service.main.latest_ready_revision
  description = "Latest ready revision name."
}
