output "pipeline_name"  { value = google_clouddeploy_delivery_pipeline.pipeline.name }
output "target_name"    { value = google_clouddeploy_target.run_target.name }
output "rollout_url" {
  value = "https://console.cloud.google.com/deploy/delivery-pipelines/${var.region}/${google_clouddeploy_delivery_pipeline.pipeline.name}?project=${var.project_id}"
}
