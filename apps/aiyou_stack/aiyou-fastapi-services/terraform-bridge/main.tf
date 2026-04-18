# ---------------------------------------------------------
# 1. ENABLE REQUIRED APIS
# ---------------------------------------------------------
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "workstations.googleapis.com",
    "compute.googleapis.com"
  ])
  service            = each.key
  disable_on_destroy = false
}

# ---------------------------------------------------------
# 2. ARTIFACT REGISTRY (Docker Repo)
# ---------------------------------------------------------
resource "google_artifact_registry_repository" "bridge_repo" {
  location      = var.region
  repository_id = "bridge-repo"
  description   = "Docker repository for Bridge Server"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# ---------------------------------------------------------
# 3. SERVICE ACCOUNTS
# ---------------------------------------------------------
# Identity for the Cloud Run Bridge
resource "google_service_account" "bridge_sa" {
  account_id   = "bridge-server-sa"
  display_name = "Bridge Server Service Account"
}

# Identity for the Cloud Workstation (Browser)
resource "google_service_account" "workstation_sa" {
  account_id   = "browser-workstation-sa"
  display_name = "Browser Workstation Service Account"
}

# ---------------------------------------------------------
# 4. CLOUD RUN SERVICE (The HTTP Bridge)
# ---------------------------------------------------------
resource "google_cloud_run_v2_service" "bridge_server" {
  name     = "bridge-server"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.bridge_sa.email
    containers {
      # INSTRUCTION: Initially uses a placeholder.
      # Later, your CI/CD will update this to:
      # region-docker.pkg.dev/PROJECT/bridge-repo/bridge-server:latest
      image = "us-docker.pkg.dev/cloudrun/container/hello"

      env {
        name  = "NODE_ENV"
        value = "production"
      }
      ports {
        container_port = 8080
      }
    }
  }
  depends_on = [google_project_service.apis]
}

# Allow public access to the Bridge (Optional - restrict if needed)
resource "google_cloud_run_service_iam_binding" "public_access" {
  location = google_cloud_run_v2_service.bridge_server.location
  service  = google_cloud_run_v2_service.bridge_server.name
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}

# ---------------------------------------------------------
# 5. CLOUD WORKSTATION (The Agent Environment)
# ---------------------------------------------------------
resource "google_workstations_workstation_cluster" "default" {
  provider               = google-beta
  workstation_cluster_id = "agent-cluster"
  network                = google_compute_network.agent_vpc.id # Use Custom VPC
  subnetwork             = google_compute_subnetwork.agent_subnet.id
  location               = var.region
  depends_on             = [google_project_service.apis]
}

resource "google_workstations_workstation_config" "default" {
  provider               = google-beta
  workstation_config_id  = "agent-config-heavy"
  workstation_cluster_id = google_workstations_workstation_cluster.default.workstation_cluster_id
  location               = var.region

  host {
    gce_instance {
      machine_type      = "e2-standard-8" # Beefier machine for data processing
      boot_disk_size_gb = 100
      service_account   = google_service_account.workstation_sa.email

      # Security: No public IP, access via Gateway only
      disable_public_ip_addresses = true
    }
  }

  # Persistent directory for Chrome Profile
  persistent_directories {
    mount_path = "/home"
    gce_pd {
      size_gb        = 200
      fs_type        = "ext4"
      disk_type      = "pd-standard"
      reclaim_policy = "RETAIN"
    }
  }

  # -------------------------------------------------------
  # AUTOMOUNT FILESTORE AND RUN STARTUP SCRIPT
  # -------------------------------------------------------
  container {
    image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/base:latest"

    env = {
      FILESTORE_IP    = google_filestore_instance.shared_drive.networks[0].ip_addresses[0]
      FILE_SHARE_NAME = "agent_share"
    }

    # Run our script on boot
    command = ["/bin/bash", "-c", "curl -s https://raw.githubusercontent.com/YOUR_ORG/repo/main/startup.sh | bash && sleep infinity"]
  }
}

resource "google_workstations_workstation" "default" {
  provider               = google-beta
  workstation_id         = "brave-agent-workstation"
  workstation_config_id  = google_workstations_workstation_config.default.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.default.workstation_cluster_id
  location               = var.region
}
