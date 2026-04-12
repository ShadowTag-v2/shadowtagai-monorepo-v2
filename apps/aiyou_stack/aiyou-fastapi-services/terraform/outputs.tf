# Terraform Outputs for PNKLN GKE Inference Deployment

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "gke_cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_location" {
  description = "Location of the GKE cluster"
  value       = google_container_cluster.primary.location
}

output "gke_cluster_endpoint" {
  description = "Endpoint for GKE cluster API"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "gke_cluster_ca_certificate" {
  description = "CA certificate for GKE cluster"
  value       = base64decode(google_container_cluster.primary.master_auth[0].cluster_ca_certificate)
  sensitive   = true
}

output "vpc_network_name" {
  description = "Name of the VPC network"
  value       = google_compute_network.vpc.name
}

output "vpc_network_id" {
  description = "ID of the VPC network"
  value       = google_compute_network.vpc.id
}

output "subnet_name" {
  description = "Name of the subnet"
  value       = google_compute_subnetwork.subnet.name
}

output "subnet_cidr" {
  description = "CIDR range of the subnet"
  value       = google_compute_subnetwork.subnet.ip_cidr_range
}

output "pods_cidr" {
  description = "CIDR range for pods"
  value       = var.pods_cidr
}

output "services_cidr" {
  description = "CIDR range for services"
  value       = var.services_cidr
}

output "node_pools" {
  description = "Node pool names and configurations"
  value = {
    system = {
      name         = google_container_node_pool.system.name
      machine_type = var.system_node_pool_machine_type
      min_nodes    = var.system_node_pool_min_nodes
      max_nodes    = var.system_node_pool_max_nodes
    }
    governance = {
      name         = google_container_node_pool.governance.name
      machine_type = var.governance_node_pool_machine_type
      min_nodes    = var.governance_node_pool_min_nodes
      max_nodes    = var.governance_node_pool_max_nodes
    }
    inference_l4 = {
      name         = google_container_node_pool.inference_l4.name
      machine_type = var.inference_l4_machine_type
      gpu_type     = "nvidia-l4"
      gpu_count    = 2
      min_nodes    = var.inference_l4_min_nodes
      max_nodes    = var.inference_l4_max_nodes
    }
    cognitive = {
      name         = google_container_node_pool.cognitive.name
      machine_type = var.cognitive_node_pool_machine_type
      min_nodes    = var.cognitive_node_pool_min_nodes
      max_nodes    = var.cognitive_node_pool_max_nodes
    }
    shadowtag = {
      name         = google_container_node_pool.shadowtag.name
      machine_type = var.shadowtag_node_pool_machine_type
      min_nodes    = var.shadowtag_node_pool_min_nodes
      max_nodes    = var.shadowtag_node_pool_max_nodes
    }
  }
}

output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.primary.name} --region ${var.region} --project ${var.project_id}"
}

output "workload_identity_pool" {
  description = "Workload Identity pool for service accounts"
  value       = "${var.project_id}.svc.id.goog"
}

output "monthly_budget_usd" {
  description = "Monthly budget threshold"
  value       = var.monthly_budget_usd
}
