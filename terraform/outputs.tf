output "backend_url" {
  description = "Cloud Run backend service URL"
  value       = google_cloud_run_v2_service.backend.uri
}

output "database_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.postgres.private_ip_address
  sensitive   = true
}

output "cloud_run_service_account" {
  description = "Service account email used by Cloud Run"
  value       = google_service_account.cloud_run_sa.email
}

output "vpc_connector_id" {
  description = "Serverless VPC connector ID"
  value       = google_vpc_access_connector.connector.id
}
