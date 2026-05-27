variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "digital-tarmo-497317"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "digitalthi_db"
}

variable "db_user" {
  description = "PostgreSQL database user"
  type        = string
  default     = "digitalthi"
}

variable "db_password" {
  description = "PostgreSQL database password — pass via TF_VAR_db_password, never in tfvars"
  type        = string
  sensitive   = true
}

variable "backend_image" {
  description = "Full Artifact Registry image URL for the backend"
  type        = string
  default     = "europe-west1-docker.pkg.dev/digital-tarmo-497317/digitaltarmo-repo/backend:latest"
}

variable "frontend_url" {
  description = "Allowed frontend origin for CORS"
  type        = string
  default     = "https://digital-tarmo.vercel.app"
}
