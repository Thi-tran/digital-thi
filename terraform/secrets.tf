# ─── Secret Manager ──────────────────────────────────────────────────────────
# The `database-url` secret value is managed manually in GCP Secret Manager.
# Terraform only references it — it does not create or update the secret value.
#
# To create it the first time:
#   gcloud secrets create database-url --replication-policy=automatic --project=digital-tarmo-500519
#   echo -n "postgresql+asyncpg://USER:PASSWORD@PRIVATE_IP:5432/DB" | \
#     gcloud secrets versions add database-url --data-file=- --project=digital-tarmo-500519

data "google_secret_manager_secret" "database_url" {
  secret_id = "database-url"
}

# ─── Grant Cloud Run SA access to the secret ─────────────────────────────────

resource "google_secret_manager_secret_iam_member" "database_url_access" {
  secret_id = data.google_secret_manager_secret.database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
