# Shared Cloud Run configuration for all environments
# Include this in per-service terragrunt.hcl files

locals {
  # Default values shared across all Cloud Run services
  default_cpu               = "1000m"
  default_memory            = "512Mi"
  default_concurrency       = 100
  default_startup_cpu_boost = true
  default_health_check_path = "/health"
  default_trace_sample_rate = "0.1"
}
