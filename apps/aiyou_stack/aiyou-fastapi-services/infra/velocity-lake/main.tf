terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "US"
}

resource "google_storage_bucket" "velocity_lake" {
  name          = "acquired-jet-velocity-lake"
  location      = "US"
  force_destroy = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition { age = 90 }
    action { type = "SetStorageClass", storage_class = "COLDLINE" }
  }
}

resource "google_bigquery_connection" "velocity_connect" {
  connection_id = "velocity-lake-connection"
  location      = "US"
  cloud_resource {}
}

resource "google_storage_bucket_iam_member" "biglake_access" {
  bucket = google_storage_bucket.velocity_lake.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.velocity_connect.cloud_resource[0].service_account_id}"
}

resource "google_bigquery_dataset" "velocity_ds" {
  dataset_id = "velocity_dataset"
  location   = "US"
}

resource "google_bigquery_table" "events_raw" {
  dataset_id          = google_bigquery_dataset.velocity_ds.dataset_id
  table_id            = "events_raw"
  deletion_protection = false

  external_data_configuration {
    autodetect    = true
    source_format = "PARQUET"
    source_uris = ["gs://${google_storage_bucket.velocity_lake.name}/events/*.parquet"]
    connection_id = google_bigquery_connection.velocity_connect.name
    hive_partitioning_options {
      mode                     = "AUTO"
      source_uri_prefix        = "gs://${google_storage_bucket.velocity_lake.name}/events/"
      require_partition_filter = true
    }
  }
  depends_on = [google_storage_bucket_iam_member.biglake_access]
}
