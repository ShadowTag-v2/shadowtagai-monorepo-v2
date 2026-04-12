resource "google_project_service" "apis" {
  for_each = toset([
    "alloydb.googleapis.com",
    "compute.googleapis.com",
    "run.googleapis.com",
    "servicenetworking.googleapis.com",
    "iap.googleapis.com"
  ])
  service = each.key
  project = var.project_id
  disable_on_destroy = false
}

resource "google_compute_network" "omega_vpc" {
  name                    = "omega-vpc"
  auto_create_subnetworks = true
  project                 = var.project_id
}

resource "google_compute_global_address" "private_ip_alloc" {
  name          = "omega-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.omega_vpc.id
  project       = var.project_id
}

resource "google_service_networking_connection" "omega_vpc_connection" {
  network                 = google_compute_network.omega_vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_alloc.name]
}

resource "google_alloydb_cluster" "omega_cluster" {
  cluster_id = "omega-cluster"
  location   = var.region
  network    = google_compute_network.omega_vpc.id
  project    = var.project_id

  depends_on = [google_service_networking_connection.omega_vpc_connection]
}

resource "google_alloydb_instance" "omega_primary" {
  cluster       = google_alloydb_cluster.omega_cluster.name
  instance_id   = "omega-primary"
  instance_type = "PRIMARY"
  project       = var.project_id

  machine_config {
    cpu_count = 2
  }
}
