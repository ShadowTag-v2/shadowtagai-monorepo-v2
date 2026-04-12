terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "shadowtag-omega-v2"
  region  = "us-central1"
}

provider "google-beta" {
  project = "shadowtag-omega-v2"
  region  = "us-central1"
}

# 1. The Cluster (The Docking Station)
resource "google_workstations_workstation_cluster" "antigravity_v2" {
  provider               = google-beta
  workstation_cluster_id = "antigravity-cluster-v2"
  network                = "projects/shadowtag-omega-v2/global/networks/default"
  subnetwork             = "projects/shadowtag-omega-v2/regions/us-central1/subnetworks/default"
  location               = "us-central1"

  labels = {
    "intent" = "sovereign-landing-pad"
  }
}

# 2. The Configuration (The Spec)
resource "google_workstations_workstation_config" "cockpit_config" {
  provider               = google-beta
  workstation_config_id  = "antigravity-cockpit-config"
  workstation_cluster_id = google_workstations_workstation_cluster.antigravity_v2.workstation_cluster_id
  location               = "us-central1"

  host {
    gce_instance {
      machine_type      = "e2-standard-4"
      boot_disk_size_gb = 100
      pool_size        = 1 # Min 1 warm instance for fast connection
    }
  }

  container {
    image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest"
    env = {
      "ANTIGRAVITY_MODE" = "SOVEREIGN"
    }
  }
}

# 3. The Workstation (The Cockpit)
resource "google_workstations_workstation" "cockpit" {
  provider               = google-beta
  workstation_id         = "antigravity-cockpit"
  workstation_config_id  = google_workstations_workstation_config.cockpit_config.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.antigravity_v2.workstation_cluster_id
  location               = "us-central1"

  labels = {
    "role" = "command-center"
  }
}

output "tunnel_command" {
  value = "gcloud workstations start antigravity-cockpit --cluster=antigravity-cluster-v2 --config=antigravity-cockpit-config --region=us-central1 --project=shadowtag-omega-v2 && gcloud workstations ssh antigravity-cockpit --cluster=antigravity-cluster-v2 --config=antigravity-cockpit-config --region=us-central1 --project=shadowtag-omega-v2"
}
