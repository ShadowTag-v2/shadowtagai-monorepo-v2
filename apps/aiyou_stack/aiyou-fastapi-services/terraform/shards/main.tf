# Resource Manager Shards (Hybrid Billing Structure)
# Defines the folder hierarchy for "ShadowTag" sovereign separation.

resource "google_folder" "sovereign_root" {
  display_name = "ShadowTag Sovereign"
  parent       = "organizations/276384896282"
}

resource "google_folder" "shard_production" {
  display_name = "Shard: Production (God Mode)"
  parent       = google_folder.sovereign_root.name
}

resource "google_folder" "shard_research" {
  display_name = "Shard: Research (Deep Field)"
  parent       = google_folder.sovereign_root.name
}

resource "google_folder" "shard_billing_hybrid" {
  display_name = "Shard: Hybrid Billing Aggregator"
  parent       = google_folder.sovereign_root.name
}

# Project assignment (Example)
# resource "google_project" "omega_v2" {
#   project_id = "shadowtag-omega-v2"
#   folder_id  = google_folder.shard_production.name
# }
