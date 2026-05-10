
resource "google_developer_connect_connection" "github_connection" {
  provider = google-beta
  location = var.deployment_region
  connection_id = "github-connection-${var.environment}"

  github_config {
    github_app = "DEVELOPER_CONNECT"
  }
}
