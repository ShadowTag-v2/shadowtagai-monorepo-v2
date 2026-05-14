resource "google_workstations_workstation_cluster" "default" {
  provider              = google-beta
  workstation_cluster_id = "antigravity-cluster-v2"
  network               = google_compute_network.antigravity_vpc.id
  subnetwork            = google_compute_subnetwork.antigravity_subnet.id
  location              = "us-central1"

  # Wait for API enablement
  depends_on = [google_compute_network.antigravity_vpc]
}

# 4. WORKSTATION CONFIG (The Blueprint)
resource "google_workstations_workstation_config" "default" {
  provider               = google-beta
  workstation_config_id  = "antigravity-cockpit-config"
  workstation_cluster_id = google_workstations_workstation_cluster.default.workstation_cluster_id
  location              = "us-central1"

  host {
    gce_instance {
      machine_type      = "e2-standard-8"  # 8 vCPU, 32GB RAM (Heavy Duty)
      boot_disk_size_gb = 100
      disable_public_ip_addresses = false # Simplifies access for this stage
    }
  }

  container {
    image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest"
    # Alternatively use: "intellij-ultimate" or "pycharm-professional"
    env = {
      ANTIGRAVITY_MODE = "TRUE"
    }
  }
}

# 5. THE COCKPIT (The Actual Instance)
resource "google_workstations_workstation" "default" {
  provider               = google-beta
  workstation_id         = "antigravity-cockpit"
  workstation_config_id  = google_workstations_workstation_config.default.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.default.workstation_cluster_id
  location              = "us-central1"
}

output "ssh_command" {
  value = "gcloud workstations ssh antigravity-cockpit --region us-central1 --cluster antigravity-cluster-v2 --config antigravity-cockpit-config"
}
