# Cluster outputs
output "cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "cluster_location" {
  description = "GKE cluster location"
  value       = google_container_cluster.primary.location
}

# Network outputs
output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "subnet_name" {
  description = "GKE subnet name"
  value       = google_compute_subnetwork.gke_subnet.name
}

# Storage outputs
output "model_bucket_name" {
  description = "GCS bucket name for model storage"
  value       = google_storage_bucket.models.name
}

output "model_bucket_url" {
  description = "GCS bucket URL for model storage"
  value       = google_storage_bucket.models.url
}

# Service account outputs
output "workload_service_account_email" {
  description = "Email of the workload identity service account"
  value       = google_service_account.gke_workload.email
}

# Kubectl configuration command
output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.primary.name} --region ${var.region} --project ${var.project_id}"
}

# Node pool information
output "gpu_node_pools" {
  description = "GPU node pool names and configurations"
  value = {
    for k, v in google_container_node_pool.gpu_pools : k => {
      name         = v.name
      machine_type = v.node_config[0].machine_type
      gpu_type     = v.node_config[0].guest_accelerator[0].type
      gpu_count    = v.node_config[0].guest_accelerator[0].count
      min_nodes    = v.autoscaling[0].min_node_count
      max_nodes    = v.autoscaling[0].max_node_count
    }
  }
}

output "cpu_node_pool" {
  description = "CPU node pool information"
  value = {
    name         = google_container_node_pool.cpu_pool.name
    machine_type = google_container_node_pool.cpu_pool.node_config[0].machine_type
    min_nodes    = google_container_node_pool.cpu_pool.autoscaling[0].min_node_count
    max_nodes    = google_container_node_pool.cpu_pool.autoscaling[0].max_node_count
  }
}

# Secret Manager outputs
output "secret_manager_secret_name" {
  description = "Secret Manager secret name for API keys"
  value       = google_secret_manager_secret.api_keys.secret_id
}

# Cost estimation helper
output "estimated_monthly_cost_notes" {
  description = "Notes on cost optimization features enabled"
  value = <<-EOT
  Cost Optimization Features Enabled:
  - GPU node pools scale to zero when idle
  - Spot VMs enabled for L4 inference pool
  - GCS FUSE for efficient model loading (no image bloat)
  - Cluster autoscaling enabled
  - Managed Prometheus for cost-effective monitoring

  Estimated costs (when running):
  - L4 GPU (g2-standard-4 spot): ~$0.40/hr per node
  - H100 GPU (a3-highgpu-1g on-demand): ~$2.50/hr per node
  - CPU pool (n2-standard-4): ~$0.19/hr per node
  - GCS storage: ~$0.020/GB/month
  - Network egress: varies by usage

  Target: <$65K/mo = ~2,167 GPU hours/mo (H100) when at max capacity
  With scale-to-zero: Actual costs scale with actual usage
  EOT
}
