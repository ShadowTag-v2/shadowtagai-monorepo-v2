resource "google_workstations_workstation_cluster" "omega" {
  workstation_cluster_id = "omega-cluster"
  network = "default"; subnetwork = "default"; location = "us-central1"
}
resource "google_workstations_workstation_config" "cockpit" {
  workstation_config_id = "cockpit-config"
  workstation_cluster_id = google_workstations_workstation_cluster.omega.workstation_cluster_id
  location = "us-central1"
  host { gce_instance { machine_type = "e2-standard-8"; boot_disk_size_gb = 100 } }
  container { image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest" }
}
