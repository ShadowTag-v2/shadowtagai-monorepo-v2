# 1. Create a Custom VPC (Don't use 'default' for Enterprise)
resource "google_compute_network" "agent_vpc" {
  name                    = "agent-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "agent_subnet" {
  name          = "agent-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.agent_vpc.id

  # Enable Google Private Access so agents can reach BigQuery/GCS without public IP
  private_ip_google_access = true
}

# 2. IP Range for Filestore & Private Services
resource "google_compute_global_address" "private_ip_alloc" {
  name          = "private-ip-alloc"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.agent_vpc.id
}

# 3. Peer the VPC with Google Services
resource "google_service_networking_connection" "private_service_access" {
  network                 = google_compute_network.agent_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}
