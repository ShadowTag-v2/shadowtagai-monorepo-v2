#!/bin/bash
# ==============================================================================
# 🌌 ANTIGRAVITY LAUNCHPAD // TERRAFORM GENERATOR
# ==============================================================================
# Creates the Cloud Workstation environment required to receive the payload.
# STACK: VPC + Workstation Cluster + "God Mode" Config + Instance
# ==============================================================================

# CONFIGURATION (Edit if necessary)
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
ZONE="us-central1-a"
CLUSTER_ID="antigravity-cluster-v2"
CONFIG_ID="antigravity-cockpit-config"
WORKSTATION_ID="antigravity-cockpit"

echo ">>> 🦍 INITIALIZING ANTIGRAVITY PROTOCOL..."
echo ">>> 🎯 Target Project: $PROJECT_ID"
echo ">>> 📍 Region: $REGION"

# Create a clean directory for Terraform
mkdir -p antigravity_infra
cd antigravity_infra

# 1. PROVIDER SETUP
cat <<EOF > providers.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "$PROJECT_ID"
  region  = "$REGION"
  zone    = "$ZONE"
}
EOF

# 2. NETWORK (The Void)
# Workstations need a Private Service Connect compliant network
cat <<EOF > network.tf
resource "google_compute_network" "antigravity_vpc" {
  name                    = "antigravity-net"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "antigravity_subnet" {
  name          = "antigravity-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "$REGION"
  network       = google_compute_network.antigravity_vpc.id
}

# Firewall Rule (Internal Comms)
resource "google_compute_firewall" "allow_internal" {
  name    = "antigravity-allow-internal"
  network = google_compute_network.antigravity_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "icmp"
  }
  source_ranges = ["10.0.0.0/24"]
}
EOF

# 3. WORKSTATION CLUSTER (The Space Station)
cat <<EOF > main.tf
resource "google_workstations_workstation_cluster" "default" {
  workstation_cluster_id = "$CLUSTER_ID"
  network               = google_compute_network.antigravity_vpc.id
  subnetwork            = google_compute_subnetwork.antigravity_subnet.id
  location              = "$REGION"

  # Wait for API enablement
  depends_on = [google_compute_network.antigravity_vpc]
}

# 4. WORKSTATION CONFIG (The Blueprint)
resource "google_workstations_workstation_config" "default" {
  workstation_config_id  = "$CONFIG_ID"
  workstation_cluster_id = google_workstations_workstation_cluster.default.workstation_cluster_id
  location              = "$REGION"

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
    env {
      name  = "ANTIGRAVITY_MODE"
      value = "TRUE"
    }
  }
}

# 5. THE COCKPIT (The Actual Instance)
resource "google_workstations_workstation" "default" {
  workstation_id         = "$WORKSTATION_ID"
  workstation_config_id  = google_workstations_workstation_config.default.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.default.workstation_cluster_id
  location              = "$REGION"
}

output "ssh_command" {
  value = "gcloud workstations ssh ${WORKSTATION_ID} --region ${REGION} --cluster ${CLUSTER_ID} --config ${CONFIG_ID}"
}
EOF

# 6. DEPLOYMENT SEQUENCE
echo ">>> 🔨 Enabling APIs (this takes a moment)..."
gcloud services enable workstations.googleapis.com compute.googleapis.com --project "$PROJECT_ID"

echo ">>> 🚀 Launching Terraform..."
terraform init
terraform apply -auto-approve

echo ">>> ✅ Antigravity Deployed."
echo ">>> To Enter: Run the SSH command output above."
