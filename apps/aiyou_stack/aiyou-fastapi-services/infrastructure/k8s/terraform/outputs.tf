# Outputs for YouAi GKE GPU Infrastructure

output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = module.gke_cluster.cluster_name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = module.gke_cluster.cluster_endpoint
  sensitive   = true
}

output "cluster_location" {
  description = "GKE cluster location"
  value       = module.gke_cluster.cluster_location
}

output "gpu_node_pools" {
  description = "GPU node pool names"
  value       = { for k, v in module.gpu_node_pools : k => v.node_pool_name }
}

output "models_bucket" {
  description = "GCS bucket for models"
  value       = google_storage_bucket.models.name
}

output "checkpoints_bucket" {
  description = "GCS bucket for checkpoints"
  value       = google_storage_bucket.checkpoints.name
}

output "training_service_account" {
  description = "Training service account email"
  value       = google_service_account.training_sa.email
}

output "inference_service_account" {
  description = "Inference service account email"
  value       = google_service_account.inference_sa.email
}

output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${module.gke_cluster.cluster_name} --region ${var.region} --project ${var.project_id}"
}
