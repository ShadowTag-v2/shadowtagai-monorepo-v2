# Workflow: Cloud Run Deployment

**Trigger:** "Deploy to Cloud Run", "Update deployment".

**Prerequisite Check:**
- Ensure `gcloud auth login` has been run (User action).

## Scenarios

### 1. New Deployment (Zero to Hero)
1.  **Analyze:** Determine build steps (Node/Python/Go).
2.  **Containerize:** Create `Dockerfile` and `.dockerignore`.
3.  **Build:** Run local Docker build to verify.
4.  **Deploy:** `gcloud run deploy [service-name] --source . --region us-central1 --allow-unauthenticated`.
5.  **Recovery:** If fail, read logs and fix config.

### 2. Update/Hotfix
1.  **Build & Push:** Build image, push to GCR/Artifact Registry.
2.  **Update:** Update Cloud Run service with `latest` tag.
3.  **Verify:** Ping the service URL.

### 3. Debug Deployment
1.  **Fetch Logs:** `gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 20`.
2.  **Analyze:** Propose fix for `Dockerfile` or YAML.
3.  **Retry:** Attempt deployment again.

// turbo
