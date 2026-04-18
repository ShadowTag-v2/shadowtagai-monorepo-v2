# ---------------------------------------------------------
# 1. FIRESTORE (Agent State & Task Queue)
# ---------------------------------------------------------
resource "google_firestore_database" "agent_db" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# ---------------------------------------------------------
# 2. FILESTORE (Enterprise NFS for Large Downloads)
# ---------------------------------------------------------
resource "google_filestore_instance" "shared_drive" {
  name     = "agent-shared-storage"
  location = "${var.region}-a" # Filestore is zonal
  tier     = "BASIC_HDD"       # Or ENTERPRISE for critical IO

  file_shares {
    capacity_gb = 1024         # 1 TB Minimum for Basic
    name        = "agent_share"
  }

  networks {
    network = google_compute_network.agent_vpc.name
    modes   = ["MODE_IPV4"]
  }

  depends_on = [google_service_networking_connection.private_service_access]
}

# ---------------------------------------------------------
# 3. DATA LAKE (GCS + Iceberg/BigLake)
# ---------------------------------------------------------
# A. Raw Data Bucket (The "Lake")
resource "google_storage_bucket" "data_lake" {
  name          = "${var.project_id}-agent-lake"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
}

# B. BigQuery Dataset (The Catalog)
resource "google_bigquery_dataset" "iceberg_ds" {
  dataset_id  = "agent_lakehouse"
  description = "Iceberg tables managed by BigLake"
  location    = var.region
}

# C. BigLake Connection (The Glue)
# Allows BigQuery to query files in GCS securely
resource "google_bigquery_connection" "iceberg_connection" {
  connection_id = "iceberg-conn"
  location      = var.region
  cloud_resource {}
}

# Grant the Connection SA permission to read the bucket
resource "google_storage_bucket_iam_member" "biglake_access" {
  bucket = google_storage_bucket.data_lake.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.iceberg_connection.cloud_resource[0].service_account_id}"
}
