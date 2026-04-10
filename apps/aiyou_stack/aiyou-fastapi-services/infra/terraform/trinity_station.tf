# TRINITY INFRASTRUCTURE MANIFEST (ANTIGRAVITY V1)
# Provider: Google Cloud Platform
# Layer: Sec+ (Infrastructure Security)

# --- 1. THE VAULT (Private Networking) ---
resource "google_compute_network" "trinity_vpc" {
  name                    = "trinity-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "trinity_subnet" {
  name          = "trinity-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.trinity_vpc.id
  private_ip_google_access = true # Required for Vertex AI / GCS access from private IP
}

# --- 2. THE MEMORY (Google Cloud Storage) ---
resource "google_storage_bucket" "trinity_knowledge" {
  name          = "trinity-knowledge-vault-${var.project_id}"
  location      = "US"
  force_destroy = true
  
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

# --- 3. THE LABORATORY (Cloud Workstations) ---
resource "google_workstations_workstation_cluster" "trinity_cluster" {
  provider               = google-beta
  workstation_cluster_id = "trinity-cluster-alpha"
  network                = google_compute_network.trinity_vpc.id
  subnetwork             = google_compute_subnetwork.trinity_subnet.id
  location               = var.region
  
  private_cluster_config {
    enable_private_endpoint = true
  }
}

resource "google_workstations_workstation_config" "trinity_config" {
  provider               = google-beta
  workstation_config_id  = "trinity-agent-v1"
  workstation_cluster_id = google_workstations_workstation_cluster.trinity_cluster.workstation_cluster_id
  location               = var.region

  host {
    gce_instance {
      machine_type      = "e2-standard-4" # 4 vCPU, 16GB RAM
      boot_disk_size_gb = 50
      
      # ANTIGRAVITY SECURITY: No Public IP
      disable_public_ip_addresses = true 
      service_account             = google_service_account.trinity_sa.email
    }
  }

  container {
    image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest"
    env = {
        TRINITY_MODE = "PRODUCTION"
        GCS_BUCKET   = google_storage_bucket.trinity_knowledge.name
    }
  }
}

resource "google_workstations_workstation" "trinity_agent_01" {
  provider               = google-beta
  workstation_id         = "trinity-updater-001"
  workstation_config_id  = google_workstations_workstation_config.trinity_config.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.trinity_cluster.workstation_cluster_id
  location               = var.region
}

# --- 4. THE ID CARD (Service Account) ---
resource "google_service_account" "trinity_sa" {
  account_id   = "trinity-agent-sa"
  display_name = "Trinity Agent Service Account"
}

# --- 5. THE BRAIN PERMISSIONS (IAM) ---
# Grants the workstation permission to read/write Storage and use Vertex AI
resource "google_project_iam_member" "workstation_gcs_access" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.trinity_sa.email}"
}

resource "google_project_iam_member" "workstation_vertex_access" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.trinity_sa.email}"
}
