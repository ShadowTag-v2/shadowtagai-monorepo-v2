# ============================================================================
# GCS MODULE - POLICY CORPUS BUCKETS
# ============================================================================
# Purpose: Create GCS buckets for each vertical's policy corpus
# One bucket per vertical for isolated regulatory document storage
# ============================================================================

# Create a bucket for each vertical
resource "google_storage_bucket" "policy_corpus" {
  for_each = var.verticals

  name          = "${var.bucket_prefix}-${each.key}"
  project       = var.project_id
  location      = var.region
  force_destroy = false  # Prevent accidental deletion

  # Uniform bucket-level access
  uniform_bucket_level_access {
    enabled = true
  }

  # Versioning for regulatory compliance
  versioning {
    enabled = var.enable_versioning
  }

  # Lifecycle rules
  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_rules
    content {
      action {
        type          = lifecycle_rule.value.action.type
        storage_class = lookup(lifecycle_rule.value.action, "storage_class", null)
      }
      condition {
        age                   = lookup(lifecycle_rule.value.condition, "age", null)
        num_newer_versions    = lookup(lifecycle_rule.value.condition, "num_newer_versions", null)
        with_state            = lookup(lifecycle_rule.value.condition, "with_state", null)
      }
    }
  }

  # Labels
  labels = merge(
    var.labels,
    {
      vertical     = each.key
      regulations  = join("-", each.value.regulations)
      content_type = "policy-corpus"
    }
  )
}

# ============================================================================
# BUCKET STRUCTURE - CREATE SUBDIRECTORIES VIA OBJECTS
# ============================================================================

# Create placeholder objects to establish folder structure
resource "google_storage_bucket_object" "regulatory_docs_folder" {
  for_each = var.verticals

  name    = "regulatory/"
  content = "# Regulatory documents directory"
  bucket  = google_storage_bucket.policy_corpus[each.key].name
}

resource "google_storage_bucket_object" "org_policies_folder" {
  for_each = var.verticals

  name    = "org-policies/"
  content = "# Organization-specific policies directory"
  bucket  = google_storage_bucket.policy_corpus[each.key].name
}

resource "google_storage_bucket_object" "archive_folder" {
  for_each = var.verticals

  name    = "archive/"
  content = "# Archived policy versions directory"
  bucket  = google_storage_bucket.policy_corpus[each.key].name
}

# ============================================================================
# BUCKET NOTIFICATIONS (Optional - for corpus sync monitoring)
# ============================================================================

# Cloud Pub/Sub topic for bucket notifications
resource "google_pubsub_topic" "corpus_updates" {
  name    = "${var.bucket_prefix}-updates"
  project = var.project_id

  labels = var.labels
}

# Notification configuration for each bucket
resource "google_storage_notification" "corpus_notification" {
  for_each = var.verticals

  bucket         = google_storage_bucket.policy_corpus[each.key].name
  payload_format = "JSON_API_V1"
  topic          = google_pubsub_topic.corpus_updates.id

  event_types = [
    "OBJECT_FINALIZE",
    "OBJECT_DELETE"
  ]

  depends_on = [google_pubsub_topic_iam_member.gcs_publisher]
}

# Grant GCS permission to publish to Pub/Sub
data "google_storage_project_service_account" "gcs_account" {
  project = var.project_id
}

resource "google_pubsub_topic_iam_member" "gcs_publisher" {
  project = var.project_id
  topic   = google_pubsub_topic.corpus_updates.name
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

# ============================================================================
# OUTPUTS
# ============================================================================

output "bucket_names" {
  description = "Map of vertical names to bucket names"
  value = {
    for k, v in google_storage_bucket.policy_corpus : k => v.name
  }
}

output "bucket_urls" {
  description = "Map of vertical names to bucket URLs"
  value = {
    for k, v in google_storage_bucket.policy_corpus : k => "gs://${v.name}"
  }
}

output "bucket_details" {
  description = "Detailed bucket information"
  value = {
    for k, v in google_storage_bucket.policy_corpus : k => {
      name         = v.name
      url          = "gs://${v.name}"
      location     = v.location
      regulations  = var.verticals[k].regulations
      description  = var.verticals[k].description
    }
  }
}

output "pubsub_topic" {
  description = "Pub/Sub topic for corpus update notifications"
  value       = google_pubsub_topic.corpus_updates.name
}
