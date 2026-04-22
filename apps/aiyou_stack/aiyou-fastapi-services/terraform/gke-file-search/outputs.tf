# ============================================================================
# OUTPUTS - GKE + FILE SEARCH INTEGRATION
# ============================================================================

# ============================================================================
# GKE CLUSTER OUTPUTS
# ============================================================================

output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = module.gke.cluster_name
}

output "cluster_endpoint" {
  description = "Endpoint for GKE cluster API server"
  value       = module.gke.cluster_endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "CA certificate for GKE cluster"
  value       = module.gke.cluster_ca_certificate
  sensitive   = true
}

output "cluster_location" {
  description = "Location of the GKE cluster"
  value       = var.region
}

# ============================================================================
# VERTEX AI / FILE SEARCH OUTPUTS
# ============================================================================

output "vertex_ai_region" {
  description = "Region for Vertex AI services"
  value       = var.region
}

output "vertex_ai_apis_enabled" {
  description = "List of enabled Vertex AI APIs"
  value = [
    "aiplatform.googleapis.com",
    "generativelanguage.googleapis.com",
    "ml.googleapis.com"
  ]
}

output "file_search_endpoint" {
  description = "Vertex AI File Search API endpoint"
  value       = "https://${var.region}-aiplatform.googleapis.com"
}

# ============================================================================
# GCS CORPUS BUCKETS
# ============================================================================

output "policy_corpus_buckets" {
  description = "Map of vertical names to GCS bucket names"
  value       = module.gcs.bucket_names
}

output "corpus_bucket_urls" {
  description = "GCS bucket URLs for policy corpus upload"
  value = {
    for vertical, bucket in module.gcs.bucket_names :
    vertical => "gs://${bucket}"
  }
}

output "total_verticals" {
  description = "Total number of configured verticals"
  value       = length(local.verticals)
}

# ============================================================================
# IAM & SERVICE ACCOUNTS
# ============================================================================

output "gke_service_account" {
  description = "Service account email for GKE workloads"
  value       = module.gke.service_account_email
}

output "workload_identity_binding" {
  description = "Workload Identity configuration for Kubernetes"
  value = {
    namespace                  = var.workload_identity_namespace
    kubernetes_service_account = var.kubernetes_sa_name
    gcp_service_account       = module.gke.service_account_email
    annotation                = "iam.gke.io/gcp-service-account=${module.gke.service_account_email}"
  }
}

output "iam_roles_granted" {
  description = "IAM roles granted to GKE service account"
  value = [
    "roles/aiplatform.user",
    "roles/storage.objectViewer",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter"
  ]
}

# ============================================================================
# KUBECTL CONFIGURATION
# ============================================================================

output "kubectl_config_command" {
  description = "Command to configure kubectl for this cluster"
  value       = "gcloud container clusters get-credentials ${module.gke.cluster_name} --region ${var.region} --project ${var.project_id}"
}

# ============================================================================
# DEPLOYMENT SCRIPTS
# ============================================================================

output "corpus_initialization_command" {
  description = "Command to initialize RAG corpora for all verticals"
  value       = "./scripts/setup_file_search.sh --project ${var.project_id} --region ${var.region}"
}

output "workload_deployment_manifest" {
  description = "Kubernetes manifest snippet for Workload Identity"
  value = yamlencode({
    apiVersion = "v1"
    kind       = "ServiceAccount"
    metadata = {
      name      = var.kubernetes_sa_name
      namespace = var.workload_identity_namespace
      annotations = {
        "iam.gke.io/gcp-service-account" = module.gke.service_account_email
      }
    }
  })
}

# ============================================================================
# MONITORING & ALERTING
# ============================================================================

output "monitoring_dashboard_url" {
  description = "URL for Cloud Monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom?project=${var.project_id}"
}

output "latency_sla_config" {
  description = "Configured latency SLA thresholds"
  value       = var.latency_sla
}

# ============================================================================
# COST ESTIMATION
# ============================================================================

output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (USD)"
  value = {
    gke_cluster       = "~$200-500 (3-10 nodes, n2-standard-8)"
    vertex_ai_calls   = "~$100-300 (based on query volume)"
    gcs_storage       = "~$50-100 (10GB corpus across 30 verticals)"
    networking        = "~$50-150 (egress, load balancing)"
    total_estimated   = "~$400-1050/month"
    budget_alert      = var.budget_alert_threshold
  }
}

# ============================================================================
# QUICKSTART GUIDE
# ============================================================================

output "quickstart_guide" {
  description = "Quick deployment guide"
  value = <<-EOT

  ═══════════════════════════════════════════════════════════════
  PNKLN CORE STACK - GKE + FILE SEARCH INTEGRATION
  ═══════════════════════════════════════════════════════════════

  ✅ Infrastructure deployed successfully!

  NEXT STEPS:

  1. Configure kubectl:
     ${output.kubectl_config_command.value}

  2. Initialize RAG corpora:
     ${output.corpus_initialization_command.value}

  3. Deploy Kubernetes workloads with Workload Identity:
     Apply this ServiceAccount manifest to your cluster:

     ${indent(3, output.workload_deployment_manifest.value)}

  4. Upload policy documents to corpus buckets:
     Example for defense vertical:
     gsutil cp itar_regulations.pdf ${module.gcs.bucket_urls["defense"]}/

  5. Monitor latency SLAs:
     - Judge 6 p99: ≤${var.latency_sla.judge_p99}ms
     - File Search p99: ≤${var.latency_sla.file_search_p99}ms
     - Total acceptable: ≤${var.latency_sla.total_acceptable}ms

  RESOURCES:
  - Monitoring Dashboard: ${output.monitoring_dashboard_url.value}
  - Vertex AI Console: https://console.cloud.google.com/vertex-ai
  - GCS Buckets: ${length(module.gcs.bucket_names)} verticals configured

  ═══════════════════════════════════════════════════════════════
  EOT
}
