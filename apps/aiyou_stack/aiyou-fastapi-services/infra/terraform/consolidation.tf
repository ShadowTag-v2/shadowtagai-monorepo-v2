
# ==============================================================================
# 🏟️ MASSIVE CONSOLIDATION INFRASTRUCTURE
# ==============================================================================
# Components:
# 1. Google Managed Service for Apache Kafka (The Nervous System)
# 2. BigQuery Dataset (Velocity Lake)
# 3. Service Accounts (Identity)
# ==============================================================================

# 1. SERVICE ACCOUNT
resource "google_service_account" "consolidation_sa" {
  account_id   = "consolidation-sa"
  display_name = "Consolidation Pipeline SA"
  description  = "Identity for Dataflow and Kafka operations"
}

resource "google_project_iam_member" "consolidation_sa_kafka" {
  project = var.project_id
  role    = "roles/managedkafka.client"
  member  = "serviceAccount:${google_service_account.consolidation_sa.email}"
}

resource "google_project_iam_member" "consolidation_sa_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.consolidation_sa.email}"
}

resource "google_project_iam_member" "consolidation_sa_dataflow" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.consolidation_sa.email}"
}

# Kafka Cluster Removed by User Request (Scale-to-Zero Protocol)
# resource "google_managed_kafka_cluster" "omega_cluster" {
#   ... (deleted)
# }
# resource "google_managed_kafka_topic" "events" { ... }
# resource "google_managed_kafka_topic" "verdicts" { ... }

# 3. BIGQUERY VELOCITY LAKE
resource "google_bigquery_dataset" "velocity_lake" {
  dataset_id                  = "velocity_lake"
  friendly_name               = "Velocity Lake"
  description                 = "Grand Central Station for all ShadowTag events"
  location                    = "US"
  default_table_expiration_ms = null # Permanent storage
}

# 4. FIRESTORE ENTERPRISE (The Hot Cortex)
resource "google_firestore_database" "shadowtag_engine" {
  project     = var.project_id
  name        = "shadowtag-engine"
  location_id = "us-central1"
  type        = "FIRESTORE_NATIVE"
  
  # Enabling the new Pipeline Operations engine
  # Note: Enterprise edition is required for the advanced query engine optimizations
  # and predictable cost model.
  delete_protection_state = "DELETE_PROTECTION_ENABLED"
}

resource "google_project_iam_member" "consolidation_sa_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.consolidation_sa.email}"
}

resource "google_bigquery_table" "events_v1" {
  dataset_id = google_bigquery_dataset.velocity_lake.dataset_id
  table_id   = "events_v1"

  schema = <<EOF
[
  {
    "name": "event_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "source",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "payload",
    "type": "JSON",
    "mode": "NULLABLE"
  },
  {
    "name": "risk_score",
    "type": "FLOAT",
    "mode": "NULLABLE"
  }
]
EOF
}

# 5. SOVEREIGN LAKE (Iceberg on GCS)
resource "google_storage_bucket" "iceberg_lake" {
  name          = "velocity-lake-iceberg-${var.project_id}"
  location      = "US"
  force_destroy = false
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
}

resource "google_project_iam_member" "consolidation_sa_gcs" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.consolidation_sa.email}"
}

# 6. GROUNDING (Vertex AI Search / Discovery Engine)
# Defines the Data Store that indexes the data for Agents.
resource "google_discovery_engine_data_store" "shadowtag_knowledge" {
  location      = "global"
  data_store_id = "shadowtag-knowledge-v1"
  display_name  = "ShadowTag Sovereign Knowledge"
  industry_vertical = "GENERIC"
  content_config    = "CONTENT_REQUIRED"
  solution_types    = ["SOLUTION_TYPE_SEARCH"]
  
  # Note: Actual schema mapping / linking to GCS/BQ usually happens via API or Console 
  # for the initial sync, or via a special resource link. 
  # We establish the container here.
}

# Grant Vertex AI Agents permission to query this store
resource "google_project_iam_member" "vertex_agent_search" {
  project = var.project_id
  role    = "roles/discoveryengine.editor" # Simplified for MVP
  member  = "serviceAccount:${google_service_account.consolidation_sa.email}"
}

# 7. TRANSFORMATION (Dataform)

# Ensure Dataform Service Identity exists (Fixes "Service account does not exist" error)
resource "google_project_service_identity" "dataform_sa" {
  provider = google-beta
  service  = "dataform.googleapis.com"
  project  = var.project_id
}

resource "google_dataform_repository" "transformation_repo" {
  provider = google-beta
  name     = "shadowtag-transformations"
  region   = "us-central1"
  
  git_remote_settings {
    url = "https://github.com/ShadowTag-v2/aiyou-fastapi-services.git"
    default_branch = "main"
    authentication_token_secret_version = google_secret_manager_secret_version.github_token_version.id
  }
}

# STRICT ACT-AS ENFORCEMENT
# Allow the Dataform Service Agent to impersonate the Consolidation SA
resource "google_service_account_iam_member" "dataform_sa_impersonation" {
  service_account_id = google_service_account.consolidation_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_project_service_identity.dataform_sa.email}"
}

# SECRET MANAGER FOR GITHUB TOKEN (Required for Dataform)
resource "google_secret_manager_secret" "github_token" {
  secret_id = "dataform-github-token"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "github_token_version" {
  secret      = google_secret_manager_secret.github_token.id
  secret_data = "placeholder-token-must-be-updated-manually" 
  # Note: In production, this data should not be in TF state.
  # User must update this secret version via Console or CLI with valid GH PAT.
}

# Grant Dataform SA access to the secret
resource "google_secret_manager_secret_iam_member" "dataform_secret_access" {
  secret_id = google_secret_manager_secret.github_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_project_service_identity.dataform_sa.email}"
}
