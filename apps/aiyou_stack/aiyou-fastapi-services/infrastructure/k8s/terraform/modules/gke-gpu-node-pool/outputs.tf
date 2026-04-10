# Outputs for GKE GPU Node Pool Module

output "node_pool_name" {
  description = "Name of the node pool"
  value       = google_container_node_pool.gpu_pool.name
}

output "node_pool_id" {
  description = "ID of the node pool"
  value       = google_container_node_pool.gpu_pool.id
}
