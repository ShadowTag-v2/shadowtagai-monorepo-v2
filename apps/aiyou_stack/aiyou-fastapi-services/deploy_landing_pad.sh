#!/bin/bash
# ==============================================================================
# 🛸 ANTIGRAVITY LANDING PAD GENERATOR (V2 - BETA FIX)
# ==============================================================================
# Provisions the 'antigravity-cluster-v2' required for the Tunnel Injection.
# Isolates Terraform state to 'infra/landing_pad' to avoid lock conflicts.
# ==============================================================================

PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
ZONE="us-central1-a"

# 0. Enable Required APIs (Fast Path)
echo ">>> 🔌 Enabling Cloud Workstations API..."
gcloud services enable workstations.googleapis.com --project=$PROJECT_ID

mkdir -p infra/landing_pad
cd infra/landing_pad

echo ">>> 📝 Generating Terraform for Antigravity Landing Pad..."

cat <<TF > main.tf
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
  project = "$PROJECT_ID"
  region  = "$REGION"
}

provider "google-beta" {
  project = "$PROJECT_ID"
  region  = "$REGION"
}

# 1. The Cluster (The Docking Station)
resource "google_workstations_workstation_cluster" "antigravity_v2" {
  provider               = google-beta
  workstation_cluster_id = "antigravity-cluster-v2"
  network                = "projects/$PROJECT_ID/global/networks/default"
  subnetwork             = "projects/$PROJECT_ID/regions/$REGION/subnetworks/default"
  location               = "$REGION"

  labels = {
    "intent" = "sovereign-landing-pad"
  }
}

# 2. The Configuration (The Spec)
resource "google_workstations_workstation_config" "cockpit_config" {
  provider               = google-beta
  workstation_config_id  = "antigravity-cockpit-config"
  workstation_cluster_id = google_workstations_workstation_cluster.antigravity_v2.workstation_cluster_id
  location               = "$REGION"

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
  location               = "$REGION"

  labels = {
    "role" = "command-center"
  }
}

output "tunnel_command" {
  value = "gcloud workstations start antigravity-cockpit --cluster=antigravity-cluster-v2 --config=antigravity-cockpit-config --region=$REGION --project=$PROJECT_ID && gcloud workstations ssh antigravity-cockpit --cluster=antigravity-cluster-v2 --config=antigravity-cockpit-config --region=$REGION --project=$PROJECT_ID"
}
TF

echo ">>> 🚀 Deploying Landing Pad..."

# Initialize
terraform init -upgrade

# 3.1. Hijack Protocol (Import Existing Cluster to bypass Quota 429)
echo ">>> 🕵️‍♀️ Detecting existing infrastructure..."
terraform import google_workstations_workstation_cluster.antigravity_v2 projects/$PROJECT_ID/locations/$REGION/workstationClusters/antigravity-cluster-v2 || true

# Apply
terraform apply -auto-approve

echo ">>> ✅ Landing Pad Deployed."
echo ">>> 📡 You can now execute the Tunnel Injection command."
