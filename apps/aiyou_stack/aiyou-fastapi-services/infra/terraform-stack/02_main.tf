# 02_main.tf
# Save this in a folder named 'terraform-stack'

terraform {
  required_providers {
    google = { source = "hashicorp/google", version = ">= 5.0.0" }
  }
}
provider "google" { project = "shadowtag-omega-v2"; region = "us-central1" }

# 1. NETWORK & STORAGE
resource "google_compute_network" "vpc" {
  name = "shadowtag-vpc"
  auto_create_subnetworks = false
}
resource "google_compute_subnetwork" "subnet" {
  name = "shadowtag-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region = "us-central1"
  network = google_compute_network.vpc.id
  private_ip_google_access = true
}
resource "google_filestore_instance" "fs" {
  name = "shadowtag-fs"
  location = "us-central1-a"
  tier = "BASIC_HDD"
  file_shares {
    capacity_gb = 1024
    name = "shadow_share"
  }
  networks {
    network = google_compute_network.vpc.name
    modes = ["MODE_IPV4"]
  }
}

# 2. IDENTITY (Least Privilege)
resource "google_service_account" "brain_sa" {
  account_id = "brain-sa"
  display_name = "ShadowTag Brain (Cloud Run)"
}
resource "google_service_account" "hands_sa" {
  account_id = "hands-sa"
  display_name = "ShadowTag Hands (Workstation)"
}
# Grant Firestore Access
resource "google_project_iam_member" "brain_fs" {
  project = "shadowtag-omega-v2"
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.brain_sa.email}"
}
resource "google_project_iam_member" "hands_fs" {
  project = "shadowtag-omega-v2"
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.hands_sa.email}"
}

# 3. WORKSTATION (The Hands)
resource "google_workstations_workstation_cluster" "cluster" {
  workstation_cluster_id = "shadowtag-cluster"
  network = google_compute_network.vpc.id
  subnetwork = google_compute_subnetwork.subnet.id
  location = "us-central1"
}
resource "google_workstations_workstation_config" "config" {
  workstation_config_id = "shadowtag-config"
  workstation_cluster_id = google_workstations_workstation_cluster.cluster.workstation_cluster_id
  location = "us-central1"

  host {
    gce_instance {
      machine_type = "e2-standard-4"
      boot_disk_size_gb = 50
      disable_public_ip_addresses = true
      service_account = google_service_account.hands_sa.email
    }
  }
  container {
    image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/base:latest"
    env {
      name = "FILESTORE_IP"
      value = google_filestore_instance.fs.networks[0].ip_addresses[0]
    }
    env {
      name = "PROJECT_ID"
      value = "shadowtag-omega-v2"
    }
    # STARTUP: Points to the self-healing script
    command = ["/bin/bash", "-c", "curl -s https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/06_startup.sh | bash && sleep infinity"]
  }
}
resource "google_workstations_workstation" "vm" {
  workstation_id = "shadowtag-vm"
  workstation_config_id = google_workstations_workstation_config.config.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.cluster.workstation_cluster_id
  location = "us-central1"
}

# 4. ARTIFACT REPO
resource "google_artifact_registry_repository" "repo" {
  location = "us-central1"
  repository_id = "shadowtag-repo"
  format = "DOCKER"
}

output "repo_url" { value = "us-central1-docker.pkg.dev/shadowtag-omega-v2/shadowtag-repo" }
