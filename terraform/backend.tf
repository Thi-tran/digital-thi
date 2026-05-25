# ─── Cloud Run (Backend) ──────────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "backend" {
  name     = "digital-tarmo-backend"
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      min_instance_count = 1
      max_instance_count = 5
    }

    timeout = "3600s"

    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    containers {
      image = var.backend_image
      name  = "backend"

      ports {
        container_port = 3001
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      # Plain env vars
      env {
        name  = "FRONTEND_URL"
        value = var.frontend_url
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }

      # Secret from Secret Manager (managed outside Terraform)
      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.database_url.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_secret_manager_secret_iam_member.database_url_access,
    google_vpc_access_connector.connector,
  ]
}

# ─── Allow unauthenticated invocations (public endpoint) ─────────────────────

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
