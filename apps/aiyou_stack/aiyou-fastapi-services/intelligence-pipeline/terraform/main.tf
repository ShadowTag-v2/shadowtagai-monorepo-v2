# PNKLN Intelligence Pipeline - Terraform Infrastructure
# GKE-Native Deployment | ATP 5-19 RA-1 Compliant
# Cost: $370/month | ROI: 3.3× in 18 months

terraform {
  required_version = ">= 1.6"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Remote state storage (recommended for production)
  # backend "gcs" {
  #   bucket = "pnkln-terraform-state"
  #   prefix = "intelligence-pipeline"
  # }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Provider Configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable Required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "cloudscheduler.googleapis.com",
    "iam.googleapis.com",
  ])

  service            = each.value
  disable_on_destroy = false
}

# GCS Bucket for Intelligence Data
resource "google_storage_bucket" "intelligence_bucket" {
  name     = "${var.project_id}-pnkln-intelligence"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  labels = {
    component   = "intelligence-pipeline"
    environment = var.environment
    cost-center = "engineering"
  }

  depends_on = [google_project_service.required_apis]
}

# BigQuery Dataset
resource "google_bigquery_dataset" "intelligence_dataset" {
  dataset_id  = "pnkln_intelligence"
  description = "Intelligence pipeline data - ATP 5-19 RA-1 compliant"
  location    = "US"

  default_table_expiration_ms = null  # No auto-expiration

  labels = {
    component   = "intelligence-pipeline"
    environment = var.environment
    atp-5-19    = "ra-1"
  }

  depends_on = [google_project_service.required_apis]
}

# BigQuery Table for Intelligence Items
resource "google_bigquery_table" "intelligence_items" {
  dataset_id = google_bigquery_dataset.intelligence_dataset.dataset_id
  table_id   = "intelligence_items"

  time_partitioning {
    type  = "DAY"
    field = "published_date"
  }

  schema = jsonencode([
    {
      name        = "id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique intelligence item ID"
    },
    {
      name        = "source"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Intelligence source type"
    },
    {
      name        = "title"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Item title"
    },
    {
      name        = "url"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Source URL"
    },
    {
      name        = "content"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Item content"
    },
    {
      name        = "published_date"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Publication date"
    },
    {
      name        = "ingested_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Ingestion timestamp"
    },
    {
      name        = "jr_score"
      type        = "FLOAT64"
      mode        = "REQUIRED"
      description = "JR Engine relevance score (0.0-1.0)"
    },
    {
      name        = "jr_reasoning"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "JR scoring reasoning"
    },
    {
      name        = "tier"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Tier classification (tier_1, tier_2, tier_3)"
    },
    {
      name        = "tier_reasoning"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Tier classification reasoning"
    },
    {
      name        = "cor_synthesis"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Cor Brain executive synthesis"
    },
    {
      name        = "action_items"
      type        = "STRING"
      mode        = "REPEATED"
      description = "Action items"
    },
    {
      name        = "metadata"
      type        = "JSON"
      mode        = "NULLABLE"
      description = "Additional metadata"
    }
  ])

  labels = {
    component = "intelligence-pipeline"
  }
}

# Service Account for Intelligence Pipeline
resource "google_service_account" "intelligence_pipeline" {
  account_id   = "intelligence-pipeline"
  display_name = "Intelligence Pipeline Service Account"
  description  = "Service account for PNKLN Intelligence Pipeline - ATP 5-19 RA-1"
}

# IAM Bindings for Service Account
resource "google_project_iam_member" "intelligence_pipeline_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.intelligence_pipeline.email}"
}

resource "google_project_iam_member" "intelligence_pipeline_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.intelligence_pipeline.email}"
}

# Workload Identity Binding (for GKE)
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.intelligence_pipeline.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[intelligence-pipeline/intelligence-runner]"
}

# Outputs
output "bucket_name" {
  description = "GCS bucket name"
  value       = google_storage_bucket.intelligence_bucket.name
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.intelligence_dataset.dataset_id
}

output "bigquery_table" {
  description = "BigQuery table ID"
  value       = google_bigquery_table.intelligence_items.table_id
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.intelligence_pipeline.email
}

output "deployment_commands" {
  description = "Next steps for deployment"
  value = <<-EOT
    # 1. Annotate Kubernetes Service Account with Workload Identity
    kubectl annotate serviceaccount intelligence-runner \
      --namespace intelligence-pipeline \
      iam.gke.io/gcp-service-account=${google_service_account.intelligence_pipeline.email}

    # 2. Build and push Docker image
    gcloud builds submit --tag gcr.io/${var.project_id}/intelligence-pipeline:latest

    # 3. Apply Kubernetes manifests
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/serviceaccount.yaml
    kubectl apply -f k8s/cronjob.yaml

    # 4. Create secrets
    kubectl create secret generic api-keys \
      --from-literal=ANTHROPIC_API_KEY="your-key" \
      --from-literal=PROJECT_ID="${var.project_id}" \
      --from-literal=BIGQUERY_DATASET="${google_bigquery_dataset.intelligence_dataset.dataset_id}" \
      --from-literal=GCS_BUCKET="${google_storage_bucket.intelligence_bucket.name}" \
      --namespace intelligence-pipeline
  EOT
}
