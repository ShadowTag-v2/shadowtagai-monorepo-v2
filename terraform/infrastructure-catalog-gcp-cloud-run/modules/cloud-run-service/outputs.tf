output "service" {
  description = "Full google_cloud_run_v2_service resource object."
  value       = google_cloud_run_v2_service.service
}

output "url" {
  description = "Service URL."
  value       = google_cloud_run_v2_service.service.uri
}

output "name" {
  description = "Service name."
  value       = google_cloud_run_v2_service.service.name
}

output "id" {
  description = "Service resource ID."
  value       = google_cloud_run_v2_service.service.id
}

output "latest_revision" {
  description = "Most recently deployed revision name."
  value       = google_cloud_run_v2_service.service.latest_ready_revision
}
