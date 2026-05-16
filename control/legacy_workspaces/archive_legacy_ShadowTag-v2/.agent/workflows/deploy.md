---
description: Standard deployment workflow for Cloud Run.
---

# Deploy to Cloud Run

1.  **Test:** Run unit tests to ensure stability.
    // turbo
    `npm run test` (or `pytest`)

2.  **Build:** Build the container image.
    // turbo
    `gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/app`

3.  **Deploy:** Deploy the container to Cloud Run.
    // turbo
    `gcloud run deploy app --image gcr.io/$GCP_PROJECT_ID/app --platform managed --region us-central1 --allow-unauthenticated`

4.  **Verify:** Check the service URL.
    `gcloud run services list`
