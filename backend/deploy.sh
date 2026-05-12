docker build --platform linux/amd64 -t europe-west1-docker.pkg.dev/digital-tarmo/digitaltarmo-repo/backend:latest ./backend
docker push europe-west1-docker.pkg.dev/digital-tarmo/digitaltarmo-repo/backend:latest
gcloud run deploy digital-tarmo-backend \
  --image=europe-west1-docker.pkg.dev/digital-tarmo/digitaltarmo-repo/backend:latest \
  --min-instances=1 \
  --region=europe-west1 \
  --platform=managed \
  --service-account=digital-tarmo-compute@digital-tarmo.iam.gserviceaccount.com \
  --vpc-connector=digital-tarmo \
  --vpc-egress=private-ranges-only \
  --set-cloudsql-instances=digital-tarmo:europe-west1:digital-db \
  --update-secrets=DATABASE_URL=database-url:latest \
  --update-secrets=OLLAMA_BASE_URL=ollama-base-url:latest \
  --set-env-vars=FRONTEND_URL=https://digital-tarmo.vercel.app \
  --port=3001 \
  --timeout=3600 \
  --allow-unauthenticated