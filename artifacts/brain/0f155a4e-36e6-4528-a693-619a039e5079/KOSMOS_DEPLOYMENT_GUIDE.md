# KOSMOS DEPLOYMENT GUIDE (CLOUD RUN)

## 1. Architecture
*   **Runtime**: Python 3.11 (Custom Container).
*   **Orchestration**: Cloud Run Jobs (NOT Services).
*   **Reason**: "Scientist" loops need 12-hour timeouts for deep research. Services timeout at 60 mins.

## 2. GitHub to Cloud Run Setup
### Step A: Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install playwright && playwright install deps
COPY . .
CMD ["python", "app.py"] # For Service
# CMD ["python", "research_task.py"] # For Job
```

### Step B: Build & Push
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/kosmos-monkeys-v2
```

### Step C: Deploy (12-Hour Job)
```bash
gcloud run jobs create kosmos-scientist \
  --image gcr.io/$PROJECT_ID/kosmos-monkeys-v2 \
  --tasks 1 \
  --task-timeout 43200s \  # 12 Hours (Max 24h)
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars PROJECT_ID=$PROJECT_ID
```

### Step D: Execution
```bash
gcloud run jobs execute kosmos-scientist
```

## 3. Troubleshooting: "squadron-commander-func"
If your orchestration function is failing:

**Diagnosis**:
1.  **Tail Logs**:
    ```bash
    gcloud logging read "resource.type=cloud_run_revision resource.labels.service_name=squadron-commander-func severity>=ERROR" --limit=50
    ```
2.  **Common Issues**:
    *   "Container failed to start" (Health check timeout).
    *   OOM (Out of Memory).

**Fix**:
1.  **Boost Resources**:
    ```bash
    gcloud run services update squadron-commander-func --memory=4Gi --cpu=2 --timeout=600s
    ```
2.  **Redeploy**:
    ```bash
    gcloud run deploy squadron-commander-func --source=. --async --logs-tail
    ```

## 4. The Optimized Cycle Strategy ("Dual-Mode")

### A. For Consumers: The "Bennett Hunter" Loop (Speed)
> **Use Case**: "Buy this deal before it vanishes." (e.g., 3:10 AM Kirks & Caicos).
> **Cycle**: **Event-Driven** or **5-Minute Heartbeat**.
> **Config**:
> *   **Trigger**: Cloud Scheduler (Every 5 mins) or Webhook.
> *   **Timeout**: 300s (5 mins).
> *   **Logic**: "Scan -> Detect -> Transact -> Alert".
> *   **Why**: 12 hours is too slow for lifestyle/trends. You need "Sniper" speed.

### B. For Business: The "UphillSnowball" Loop (Depth)
> **Use Case**: "Migrate AWS to GCloud" or "Analyze Competitor 10-Ks".
> **Cycle**: **Nightly Batch (6-8 Hours)**.
> **Config**:
> *   **Trigger**: Daily at 10 PM.
> *   **Timeout**: 28800s (8 Hours).
> *   **Logic**: "Hypothesize -> Simulate (10k runs) -> Judge -> Commit".
> *   **Why**: Aligns with the "Whie I Sleep" narrative. Deep work requires sustained compute, but stays within a single "sleep cycle" for daily reporting.
