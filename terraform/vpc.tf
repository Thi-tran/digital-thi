# ─── VPC Network ─────────────────────────────────────────────────────────────

resource "google_compute_network" "vpc" {
  name                    = "digital-tarmo-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "private" {
  name                     = "digital-tarmo-private"
  ip_cidr_range            = "10.0.0.0/24"
  region                   = var.region
  network                  = google_compute_network.vpc.id
  private_ip_google_access = true
}

# ─── VPC Serverless Connector (Cloud Run → VPC) ───────────────────────────────

resource "google_vpc_access_connector" "connector" {
  provider      = google-beta
  name          = "digital-tarmo"
  region        = var.region
  network       = google_compute_network.vpc.name
  ip_cidr_range = "10.8.0.0/28"
  min_instances = 2
  max_instances = 3
}

# ─── Private Services Access (VPC → Cloud SQL) ───────────────────────────────

resource "google_compute_global_address" "private_ip_range" {
  name          = "digital-tarmo-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# ─── Firewall: deny all external ingress to the VPC (Cloud SQL is private-only)

resource "google_compute_firewall" "deny_external_db" {
  name    = "deny-external-db"
  network = google_compute_network.vpc.name

  deny {
    protocol = "tcp"
    ports    = ["5432"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["db"]
  priority      = 1000
}

resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
  }

  # Only allow traffic from within the VPC CIDR and the serverless connector range
  source_ranges = ["10.0.0.0/24", "10.8.0.0/28"]
  priority      = 900
}
