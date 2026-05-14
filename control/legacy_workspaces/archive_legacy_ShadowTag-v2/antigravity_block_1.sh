#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
REPO_NAME="ShadowTag-Omega"
BUCKET_NAME="acquired-jet-velocity-lake"

echo ">>> 🦍 BLOCK 1/5: FOUNDATION & INFRASTRUCTURE..."

# 1. SCAFFOLDING (The Vacuum)
if [ -d "$REPO_NAME" ]; then echo "⚠️  Backing up..."; mv "$REPO_NAME" "${REPO_NAME}_backup_$(date +%s)"; fi
mkdir -p $REPO_NAME/{apps,libs,infra,tools,scripts,commercial,Docs,.vscode,.agent,.quibbler}
cd $REPO_NAME

# Package Structure
mkdir -p libs/aiyou/{agents,proxies,governance,provenance,superpowers}
mkdir -p libs/arsenal/{shadowtag_core,tegu_vision,gaas_flight,flying_monkeys,gemini_ingest,safety_net}
mkdir -p libs/pnkln/compression/src/compression
find libs -type d -exec touch {}/__init__.py \;

# Subdirectories
mkdir -p apps/{flyingmonkeys-server,wealth-os,aiyou-video,composer-dags,billing-service}
mkdir -p infra/{velocity-lake,treasury,workstations}
mkdir -p commercial/{sales,legal,strategy,hr,dashboard}
mkdir -p .agent/{rules,context}
mkdir -p tools/mcp_servers

# 2. CONFIGURATION
cat <<TOML > pyproject.toml
[project]
name = "shadowtag-omega"
version = "2026.01.14"
requires-python = ">=3.11"
dependencies = [
    "fastapi", "uvicorn", "google-cloud-aiplatform", "google-auth", "google-generativeai",
    "colorama", "requests", "rich", "apache-airflow", "pydantic", "pandas", "ast-grep-cli",
    "torch", "transformers", "llmlingua", "zstandard", "google-genai"
]
[tool.uv.workspace]
members = ["apps/*", "libs/*"]
[tool.ruff]
line-length = 88
TOML

# 3. INFRASTRUCTURE (Velocity Lake + SMT)
cat <<TF > infra/velocity-lake/main.tf
terraform { required_providers { google = { source = "hashicorp/google", version = "~> 5.0" } } }
provider "google" { project = "$PROJECT_ID"; region = "$REGION" }

resource "google_storage_bucket" "lake" { name = "$BUCKET_NAME"; location = "US"; uniform_bucket_level_access = true }
resource "google_bigquery_connection" "conn" { connection_id = "velocity-conn"; location = "US"; cloud_resource {} }
resource "google_storage_bucket_iam_member" "iam" { bucket = google_storage_bucket.lake.name; role = "roles/storage.objectViewer"; member = "serviceAccount:\${google_bigquery_connection.conn.cloud_resource[0].service_account_id}" }

resource "google_bigquery_dataset" "ds" { dataset_id = "velocity_dataset"; location = "US" }
resource "google_bigquery_table" "tbl" {
  dataset_id = google_bigquery_dataset.ds.dataset_id; table_id = "events_raw"
  external_data_configuration {
    autodetect = true; source_format = "PARQUET"; source_uris = ["gs://$BUCKET_NAME/events/*.parquet"]
    connection_id = google_bigquery_connection.conn.name
    hive_partitioning_options { mode = "AUTO"; source_uri_prefix = "gs://$BUCKET_NAME/events/"; require_partition_filter = true }
  }
}
TF

# 4. UPHILL SNOWBALL (Cloud Workstations)
cat <<TF > infra/workstations/main.tf
resource "google_workstations_workstation_cluster" "antigravity" {
  provider = google
  workstation_cluster_id = "antigravity-cluster"
  network = "default"; subnetwork = "default"; location = "$REGION"
}
resource "google_workstations_workstation_config" "god_mode" {
  provider = google
  workstation_config_id = "god-mode-config"
  workstation_cluster_id = google_workstations_workstation_cluster.antigravity.workstation_cluster_id
  location = "$REGION"
  host { gce_instance { machine_type = "e2-standard-8"; boot_disk_size_gb = 100 } }
  container { image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest" }
}
TF

# 5. TREASURY (Budget)
cat <<TF > infra/treasury/budget.tf
resource "google_billing_budget" "budget" {
  billing_account = "011219-FBD1F1-F5AB42"; display_name = "Antigravity-Safety-Net"
  amount { specified_amount { currency_code = "USD"; units = "100" } }
  threshold_rules { threshold_percent = 0.5 }
}
TF

echo ">>> ✅ BLOCK 1 COMPLETE."
