resource "google_compute_network" "antigravity_vpc" {
  name                    = "antigravity-net"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "antigravity_subnet" {
  name          = "antigravity-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = "us-central1"
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
