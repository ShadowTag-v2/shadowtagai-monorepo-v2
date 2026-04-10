resource "google_storage_bucket" "lake" { name = "acquired-jet-velocity-lake"; location = "US"; uniform_bucket_level_access = true }
resource "google_bigquery_dataset" "ds" { dataset_id = "velocity_dataset" }
