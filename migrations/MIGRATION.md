# GCP Deployment / Migration to a New Project

## 1. Update project ID

In `terraform/variables.tf` and `terraform/terraform.tfvars`, replace the old project ID with the new one:
```
project_id    = "YOUR_NEW_PROJECT_ID"
backend_image = "europe-west1-docker.pkg.dev/YOUR_NEW_PROJECT_ID/digitaltarmo-repo/backend:latest"
```

## 2. Authenticate with the new GCP account

```bash
gcloud auth login
gcloud config set project YOUR_NEW_PROJECT_ID
```

## 3. Enable required GCP APIs

```bash
gcloud services enable \
  sqladmin.googleapis.com \
  run.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com \
  vpcaccess.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  aiplatform.googleapis.com \
  discoveryengine.googleapis.com \
  vertexai.googleapis.com
```

## 4. Create the Artifact Registry repository

```bash
gcloud artifacts repositories create digitaltarmo-repo \
  --repository-format=docker \
  --location=europe-west1 \
  --project=YOUR_NEW_PROJECT_ID
```

## 5. Build and push the backend container

```bash
gcloud auth configure-docker europe-west1-docker.pkg.dev

cd backend
docker build --platform linux/amd64 \
  -t europe-west1-docker.pkg.dev/YOUR_NEW_PROJECT_ID/digitaltarmo-repo/backend:latest .
docker push europe-west1-docker.pkg.dev/YOUR_NEW_PROJECT_ID/digitaltarmo-repo/backend:latest
```

## 6. Create the DATABASE_URL secret

After Terraform creates the Cloud SQL instance, get its private IP and create the secret:
```bash
PRIVATE_IP=$(gcloud sql instances describe digital-tarmo \
  --project=YOUR_NEW_PROJECT_ID \
  --format='value(ipAddresses[0].ipAddress)')

echo -n "postgresql://digitalthi:YOUR_DB_PASSWORD@${PRIVATE_IP}:5432/digitalthi_db" | \
  gcloud secrets create database-url \
  --data-file=- \
  --replication-policy=automatic \
  --project=YOUR_NEW_PROJECT_ID
```

## 7. Reset Terraform state and apply

```bash
cd terraform
rm -f terraform.tfstate terraform.tfstate.backup

terraform init
TF_VAR_db_password=YOUR_DB_PASSWORD terraform apply
```

## 8. Run database migrations and seed data

```bash
BACKEND_URL=$(gcloud run services describe digital-tarmo-backend \
  --region=europe-west1 \
  --project=YOUR_NEW_PROJECT_ID \
  --format='value(status.url)')

# Run migrations (creates tables and seeds CV sections)
curl -X POST "${BACKEND_URL}/api/run-migrations"

# Generate embeddings for CV sections
curl -X POST "${BACKEND_URL}/api/cv-sections/generate-embeddings"
```

## 9. Migrate chat history from old project

**Step 1 — Export chat history from the old project:**
- Go to GCP Console → Cloud SQL → old instance → Export
- Select format: **CSV**, database: `digitalthi_db`, table: `chat_history`
- Export to a Cloud Storage bucket and download the file

**Step 2 — Prepare the CSV:**
- Rename the downloaded file to `database.csv`
- Place it in the `migrations/` directory of this project

**Step 3 — Generate SQL INSERT statements:**
```bash
cd migrations
python3 csv_to_sql.py
# Produces: migrations/database_insert.sql
```

**Step 4 — Run the SQL in Cloud SQL Studio:**
- Go to GCP Console → Cloud SQL → new instance (`digital-tarmo`) → **Cloud SQL Studio**
- Select database: `digitalthi_db`, authenticate as user `digitalthi`
- Open `migrations/database_insert.sql`, copy the contents and paste into the SQL editor
- Click **Run**

## 10. Connect Cloud Run to GitHub repository (CI/CD)

This enables automatic deployments when you push to the repository.

- Go to GCP Console → **Cloud Run** → `digital-tarmo-backend` → **Edit & Deploy New Revision**
- Scroll down to **Continuous deployment** → click **Set up with Cloud Build**
- **Connect repository:**
  - Provider: GitHub
  - Authenticate and select your repository and branch (e.g. `main`)
- **Build configuration:**
  - Build type: `Dockerfile`
  - Dockerfile location: `/backend/Dockerfile`
- Click **Save**

From now on, every push to the connected branch will automatically build and deploy a new revision to Cloud Run.
