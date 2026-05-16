terraform { required_providers { google = { source = "hashicorp/google", version = "~> 5.0" } } }
provider "google" { project = "shadowtag-omega-v2"; region = "us-central1" }

resource "google_storage_bucket" "lake" { name = "acquired-jet-velocity-lake"; location = "US"; uniform_bucket_level_access = true }
resource "google_bigquery_connection" "conn" { connection_id = "velocity-conn"; location = "US"; cloud_resource {} }
resource "google_storage_bucket_iam_member" "iam" { bucket = google_storage_bucket.lake.name; role = "roles/storage.objectViewer"; member = "serviceAccount:${google_bigquery_connection.conn.cloud_resource[0].service_account_id}" }

resource "google_bigquery_dataset" "ds" { dataset_id = "velocity_dataset"; location = "US" }
resource "google_bigquery_table" "tbl" {
  dataset_id = google_bigquery_dataset.ds.dataset_id; table_id = "events_raw"
  external_data_configuration {
    autodetect = true; source_format = "PARQUET"; source_uris = ["gs://acquired-jet-velocity-lake/events/*.parquet"]
    connection_id = google_bigquery_connection.conn.name
    hive_partitioning_options { mode = "AUTO"; source_uri_prefix = "gs://acquired-jet-velocity-lake/events/"; require_partition_filter = true }
  }
}
