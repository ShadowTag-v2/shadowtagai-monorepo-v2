resource "google_cloud_run_v2_service_iam_member" "member" {
  for_each = var.iam_bindings
  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = each.key
  member   = each.value
}
