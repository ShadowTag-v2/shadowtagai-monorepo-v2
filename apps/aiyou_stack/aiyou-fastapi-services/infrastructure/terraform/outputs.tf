# PNKLN Core Stack™ - Terraform Outputs
# AI Operating Posture Framework Implementation

# Cluster Information
output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.pnkln_gke.name
}

output "cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.pnkln_gke.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.pnkln_gke.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "cluster_location" {
  description = "GKE cluster location"
  value       = google_container_cluster.pnkln_gke.location
}

# Network Information
output "vpc_name" {
  description = "Name of the VPC"
  value       = google_compute_network.pnkln_vpc.name
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = google_compute_network.pnkln_vpc.id
}

output "subnet_name" {
  description = "Name of the GKE subnet"
  value       = google_compute_subnetwork.gke_subnet.name
}

output "subnet_cidr" {
  description = "CIDR range of the GKE subnet"
  value       = google_compute_subnetwork.gke_subnet.ip_cidr_range
}

output "pods_cidr" {
  description = "CIDR range for pods"
  value       = google_compute_subnetwork.gke_subnet.secondary_ip_range[0].ip_cidr_range
}

output "services_cidr" {
  description = "CIDR range for services"
  value       = google_compute_subnetwork.gke_subnet.secondary_ip_range[1].ip_cidr_range
}

# Node Pool Information
output "system_node_pool_name" {
  description = "Name of the system node pool"
  value       = google_container_node_pool.system_pool.name
}

output "judge_gpu_pool_name" {
  description = "Name of the judge GPU node pool"
  value       = google_container_node_pool.judge_gpu_pool.name
}

output "llm_routing_pool_name" {
  description = "Name of the LLM routing node pool"
  value       = google_container_node_pool.llm_routing_pool.name
}

# Service Account Information
output "gke_node_service_account_email" {
  description = "Email of the GKE node service account"
  value       = google_service_account.gke_node_sa.email
}

# Storage Information
output "artifact_registry_repository" {
  description = "Full name of the Artifact Registry repository"
  value       = google_artifact_registry_repository.pnkln_repo.name
}

output "artifact_registry_url" {
  description = "URL of the Artifact Registry repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_id}"
}

output "model_weights_bucket_name" {
  description = "Name of the model weights GCS bucket"
  value       = google_storage_bucket.model_weights.name
}

output "model_weights_bucket_url" {
  description = "URL of the model weights GCS bucket"
  value       = google_storage_bucket.model_weights.url
}

output "logs_bucket_name" {
  description = "Name of the logs GCS bucket"
  value       = google_storage_bucket.logs.name
}

# kubectl Command
output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.pnkln_gke.name} --region=${var.region} --project=${var.project_id}"
}

# Summary
output "deployment_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    cluster_name    = google_container_cluster.pnkln_gke.name
    cluster_region  = var.region
    node_pools      = {
      system        = "n2-standard-4 (${var.system_node_count} nodes)"
      judge_gpu     = "g2-standard-16 with ${var.judge_gpu_count}x L4 GPUs (${var.judge_gpu_min_nodes}-${var.judge_gpu_max_nodes} nodes)"
      llm_routing   = "n2-standard-32 (${var.llm_routing_min_nodes}-${var.llm_routing_max_nodes} nodes)"
    }
    network         = {
      vpc           = google_compute_network.pnkln_vpc.name
      subnet        = google_compute_subnetwork.gke_subnet.name
      pods_range    = google_compute_subnetwork.gke_subnet.secondary_ip_range[0].ip_cidr_range
      services_range = google_compute_subnetwork.gke_subnet.secondary_ip_range[1].ip_cidr_range
    }
    storage         = {
      artifact_registry = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_id}"
      model_weights     = google_storage_bucket.model_weights.name
      logs              = google_storage_bucket.logs.name
    }
  }
}
