# ─── Cloud SQL (PostgreSQL 16 with pgvector) ─────────────────────────────────

resource "google_sql_database_instance" "postgres" {
  name             = "digital-db"
  database_version = "POSTGRES_16"
  region           = var.region

  # Prevent accidental deletion
  deletion_protection = true

  settings {
    tier              = "db-g1-small"
    availability_type = "ZONAL"
    disk_size         = 20
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    ip_configuration {
      ipv4_enabled                                  = false  # No public IP
      private_network                               = google_compute_network.vpc.id
      enable_private_path_for_google_cloud_services = true
    }

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      binary_log_enabled = false
    }

    maintenance_window {
      day          = 7 # Sunday
      hour         = 4
      update_track = "stable"
    }
  }

  depends_on = [google_service_networking_connection.private_vpc_connection]
}

resource "google_sql_database" "db" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}
