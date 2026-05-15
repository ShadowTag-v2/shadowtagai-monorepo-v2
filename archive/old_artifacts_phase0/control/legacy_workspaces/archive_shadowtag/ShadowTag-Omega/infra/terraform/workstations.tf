resource "google_workstations_workstation_cluster" "antigravity" {
  provider = google
  workstation_cluster_id = "antigravity-cluster"
  network = "default"; subnetwork = "default"; location = "us-central1"
}
resource "google_workstations_workstation_config" "god_mode" {
  provider = google
  workstation_config_id = "god-mode-config"
  workstation_cluster_id = google_workstations_workstation_cluster.antigravity.workstation_cluster_id
  location = "us-central1"
  host { gce_instance { machine_type = "e2-standard-8"; boot_disk_size_gb = 100 } }
  container { image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest" }
}
