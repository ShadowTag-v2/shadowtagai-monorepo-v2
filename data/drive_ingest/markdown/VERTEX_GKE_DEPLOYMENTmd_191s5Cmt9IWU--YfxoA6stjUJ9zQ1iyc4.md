## Vertex Workbench & GKE Native Deployment

**Memory-enabled consensus orchestrator for Google Cloud Platform**

## Overview

Deploy the Ultrathink consensus system to Google Cloud with persistent memory synced across:
- **Vertex AI Workbench** notebooks
- **GKE** (Google Kubernetes Engine) clusters
- **Cloud Run** serverless containers
- **Local development** machines

**All environments** share the same memory via **Google Cloud Storage**.

---

## Architecture

```
Local Memory (~/.claude-code/memory.md)
    ↓ (sync)
GCS Bucket (gs://consensus-memory/)
    ↓ (init container)
GKE Pods ← ConfigMap ← GCS
    ↓
Vertex Notebooks (startup script syncs from GCS)
    ↓
Cloud Run (mounts GCS via Cloud Storage FUSE)
```

**Benefits:**
- ✅ Single source of truth (GCS)
- ✅ Cross-device memory sync
- ✅ No manual copying
- ✅ Versioned in GCS (object versioning)
- ✅ Accessible from any GCP service

---

## Quick Start

### Prerequisites

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Install Python dependencies
pip install google-cloud-storage PyYAML
```

### 1. Create GCS Bucket

```bash
# Create bucket for memory storage
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://consensus-memory

# Enable versioning (keep history)
gsutil versioning set on gs://consensus-memory

# Set lifecycle (optional: delete old versions after 30 days)
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 5,
          "isLive": false
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://consensus-memory
```

### 2. Upload Initial Memory

```bash
cd ~/ShadowTag-v2-fastapi-services/voice_consensus

# Sync local memory to GCS
python vertex_gke_deployment.py sync-to-gcs
```

**Output:**
```
Syncing local memory to GCS...
[GCS] Uploaded: gs://consensus-memory/memories/current_memory.md
✓ Memory uploaded to GCS
```

### 3. Verify Upload

```bash
# Check GCS
gsutil ls -lh gs://consensus-memory/memories/

# Download to verify
gsutil cat gs://consensus-memory/memories/current_memory.md | head -20
```

---

## Deployment Options

### Option 1: Vertex AI Workbench

**Best for:** Interactive development, Jupyter notebooks

#### Setup

**1. Generate startup script**

```bash
python vertex_gke_deployment.py create-vertex-startup
```

This creates `vertex/startup-script.sh`:
```bash
#!/bin/bash
# Auto-syncs memory from GCS on notebook startup

MEMORY_DIR=/home/jupyter/.claude-code
mkdir -p $MEMORY_DIR

gsutil cp gs://consensus-memory/memories/current_memory.md $MEMORY_DIR/memory.md
git clone https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git
...
```

**2. Upload startup script to GCS**

```bash
gsutil cp vertex/startup-script.sh gs://consensus-memory/scripts/
```

**3. Create Vertex Workbench instance**

Via Console:
```
Vertex AI → Workbench → New Notebook
  - Environment: Python 3
  - Startup script: gs://consensus-memory/scripts/startup-script.sh
  - Service account: consensus-sa@YOUR_PROJECT.iam.gserviceaccount.com
```

Via CLI:
```bash
gcloud notebooks instances create consensus-notebook \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --metadata="startup-script-url=gs://consensus-memory/scripts/startup-script.sh" \
  --service-account=consensus-sa@YOUR_PROJECT.iam.gserviceaccount.com
```

**4. Access notebook**

```bash
# Get URL
gcloud notebooks instances describe consensus-notebook \
  --location=us-central1-a \
  --format="value(proxyUri)"
```

**5. Verify memory loaded**

In Jupyter terminal:
```bash
cat ~/.claude-code/memory.md
```

#### Usage

**Sync latest memory:**

```bash
# In notebook terminal
gsutil cp gs://consensus-memory/memories/current_memory.md ~/.claude-code/memory.md
```

**Update memory from notebook:**

```bash
# Run consensus queries
cd ~/ShadowTag-v2-fastapi-services/voice_consensus
python claude_code_memory.py sync

# Upload to GCS
python vertex_gke_deployment.py sync-to-gcs
```

---

### Option 2: GKE Deployment

**Best for:** Production API, autoscaling, high availability

#### Setup

**1. Create GKE cluster**

```bash
gcloud container clusters create consensus-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=n1-standard-2 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5
```

**2. Create service account with GCS access**

```bash
# Create service account
gcloud iam service-accounts create consensus-sa \
  --display-name="Consensus Orchestrator"

# Grant GCS access
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:consensus-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Enable workload identity
gcloud iam service-accounts add-iam-policy-binding \
  consensus-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:YOUR_PROJECT_ID.svc.id.goog[default/consensus-sa]"
```

**3. Create Kubernetes secret for API keys**

```bash
kubectl create secret generic api-keys \
  --from-literal=google-api-key=$GOOGLE_API_KEY \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=xai-api-key=$XAI_API_KEY \
  --from-literal=perplexity-api-key=$PERPLEXITY_API_KEY
```

**4. Generate deployment manifests**

```bash
python vertex_gke_deployment.py create-deployment
```

This creates `k8s/consensus-deployment.yaml`:
- **Deployment** with init container for memory sync
- **Service** (LoadBalancer)
- **PersistentVolumeClaim** for archive storage

**5. Customize deployment**

Edit `k8s/consensus-deployment.yaml`:
```yaml
# Update project ID
env:
- name: GOOGLE_CLOUD_PROJECT
  value: "YOUR_PROJECT_ID"  # ← Change this

# Update image
containers:
- name: orchestrator
  image: gcr.io/YOUR_PROJECT_ID/consensus-orchestrator:latest  # ← Change this
```

**6. Build and push Docker image**

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy consensus code
COPY voice_consensus/ /app/

# Install dependencies
RUN pip install --no-cache-dir \
    aiohttp \
    anthropic \
    google-generativeai \
    openai

# Expose port
EXPOSE 8000

# Run orchestrator as API
CMD ["python", "api_server.py"]
EOF

# Build
docker build -t gcr.io/YOUR_PROJECT_ID/consensus-orchestrator:latest .

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/consensus-orchestrator:latest
```

**7. Deploy to GKE**

```bash
# Apply manifests
kubectl apply -f k8s/consensus-deployment.yaml

# Check status
kubectl get pods
kubectl logs -f deployment/consensus-orchestrator

# Get external IP
kubectl get service consensus-orchestrator
```

#### Init Container Workflow

The **init container** runs before the main app:

```yaml
initContainers:
- name: memory-sync
  image: google/cloud-sdk:alpine
  command:
  - sh
  - -c
  - |
    echo "Syncing memory from GCS..."
    gsutil cp gs://consensus-memory/memories/current_memory.md /memory/memory.md
    echo "Memory sync complete"
  volumeMounts:
  - name: memory-volume
    mountPath: /memory
```

**What happens:**
1. Pod starts
2. Init container runs `gsutil cp` to download memory
3. Memory written to `/memory/memory.md`
4. Main container starts with memory available

**Update memory:**

```bash
# Upload new memory to GCS
python vertex_gke_deployment.py sync-to-gcs

# Restart pods to reload
kubectl rollout restart deployment/consensus-orchestrator
```

---

### Option 3: Cloud Run

**Best for:** Serverless, pay-per-use, zero maintenance

#### Setup

**1. Create Cloud Run service**

```bash
gcloud run deploy consensus-orchestrator \
  --image=gcr.io/YOUR_PROJECT_ID/consensus-orchestrator:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID" \
  --set-secrets="GOOGLE_API_KEY=google-api-key:latest,ANTHROPIC_API_KEY=anthropic-api-key:latest"
```

**2. Mount GCS with Cloud Storage FUSE**

Add to Dockerfile:
```dockerfile
# Install gcsfuse
RUN apt-get update && apt-get install -y gcsfuse

# Mount GCS on startup
ENTRYPOINT ["sh", "-c", "gcsfuse consensus-memory /memory && python api_server.py"]
```

**3. Deploy**

```bash
gcloud run deploy consensus-orchestrator \
  --image=gcr.io/YOUR_PROJECT_ID/consensus-orchestrator:latest \
  --platform=managed \
  --region=us-central1 \
  --execution-environment=gen2 \  # Required for gcsfuse
  --service-account=consensus-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

---

## Cross-Device Sync Workflow

### Scenario: Work from Multiple Locations

**Machine 1 (Local):**
```bash
# Run consensus queries
python atomic_consensus_orchestrator.py "Your question"

# Extract patterns
python claude_code_memory.py sync

# Upload to GCS
python vertex_gke_deployment.py sync-to-gcs
```

**Machine 2 (Vertex Notebook):**
```bash
# Notebook auto-syncs on startup via startup script
# Or manually sync:
gsutil cp gs://consensus-memory/memories/current_memory.md ~/.claude-code/memory.md
```

**Machine 3 (GKE Pod):**
```bash
# Pod auto-syncs on restart via init container
# Or trigger rollout:
kubectl rollout restart deployment/consensus-orchestrator
```

**Result:** All environments have latest memory within minutes.

---

## Memory Versioning

GCS object versioning keeps history:

```bash
# List all versions
gsutil ls -a gs://consensus-memory/memories/current_memory.md

# Restore old version
gsutil cp gs://consensus-memory/memories/current_memory.md#1700000000000000 \
  gs://consensus-memory/memories/current_memory.md
```

**Automatic cleanup** (via lifecycle policy):
- Keeps latest 5 versions
- Deletes older versions after 30 days

---

## ConfigMap Approach (Alternative)

Instead of GCS + init container, use **Kubernetes ConfigMap**:

### Generate ConfigMap

```bash
python vertex_gke_deployment.py create-configmap
```

This creates `k8s/memory-configmap.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: consensus-memory
data:
  memory.md: |
    <!-- Memory content here -->
```

### Mount ConfigMap in Deployment

```yaml
containers:
- name: orchestrator
  volumeMounts:
  - name: memory-volume
    mountPath: /memory
    readOnly: true

volumes:
- name: memory-volume
  configMap:
    name: consensus-memory
```

### Update Memory

```bash
# Regenerate ConfigMap
python vertex_gke_deployment.py create-configmap

# Apply
kubectl apply -f k8s/memory-configmap.yaml

# Restart pods
kubectl rollout restart deployment/consensus-orchestrator
```

**Pros:**
- No GCS dependency
- Faster (no download)
- Native K8s

**Cons:**
- Manual updates required
- 1MB ConfigMap limit
- Not shared outside K8s

**Recommendation:** Use **GCS + init container** for cross-platform sync.

---

## Monitoring & Debugging

### Check Memory Sync

**Vertex Notebook:**
```bash
ls -lh ~/.claude-code/memory.md
head ~/.claude-code/memory.md
```

**GKE Pod:**
```bash
# View init container logs
kubectl logs POD_NAME -c memory-sync

# Exec into pod
kubectl exec -it POD_NAME -- cat /memory/memory.md
```

**Cloud Run:**
```bash
# View logs
gcloud run logs read consensus-orchestrator --limit=50
```

### Common Issues

#### Issue: Init container fails

**Symptoms:**
```
Error from server (BadRequest): container "memory-sync" in pod "..." is waiting to start: PodInitializing
```

**Debug:**
```bash
kubectl describe pod POD_NAME
kubectl logs POD_NAME -c memory-sync
```

**Fix:**
- Check service account has GCS access
- Verify bucket exists: `gsutil ls gs://consensus-memory/`
- Check memory file exists: `gsutil ls gs://consensus-memory/memories/`

#### Issue: Memory not loading in Vertex

**Debug:**
```bash
# Check startup script ran
cat /var/log/daemon.log | grep startup-script

# Check GCS access
gsutil ls gs://consensus-memory/memories/
```

**Fix:**
- Verify startup script URL is correct
- Check notebook service account has GCS permissions
- Restart notebook instance

---

## Cost Analysis

### GCS Storage

**Memory file:** ~2 KB
**Versions:** 5 kept
**Total:** ~10 KB

**Cost:** $0.00000023/month (negligible)

### GCS Operations

**Per sync:**
- 1 write operation: $0.000005
- 1 read operation: $0.0000004

**Daily sync (30 days):**
- Cost: 30 × $0.0000054 = **$0.000162/month**

### GKE Init Container

**Per pod restart:**
- 1 GCS read: $0.0000004
- Init time: ~2 seconds

**Cost:** Negligible (< $0.01/month even with 100 restarts)

### Total Cost

**Monthly:** < **$0.01**

**Conclusion:** Essentially free

---

## Best Practices

### 1. Automate Sync

**Cron job on local machine:**
```cron
# Daily sync to GCS at 8 PM
0 20 * * * cd ~/ShadowTag-v2-fastapi-services/voice_consensus && python vertex_gke_deployment.py sync-to-gcs
```

### 2. Version Control

**Track memory changes in git:**
```bash
cd ~
git add .claude-code/memory.md
git commit -m "Update memory $(date +%Y-%m-%d)"
git push

# Also sync to GCS
python vertex_gke_deployment.py sync-to-gcs
```

### 3. Monitor Sync Status

**Cloud Monitoring alert:**
```bash
# Alert if memory file older than 7 days
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Memory Sync Alert" \
  --condition-display-name="Memory file stale" \
  --condition-threshold-value=604800 \
  --condition-threshold-duration=0s
```

### 4. Backup to Cloud Storage Archive

**Monthly backup:**
```bash
#!/bin/bash
# Backup memory to archive

DATE=$(date +%Y%m)
gsutil cp gs://consensus-memory/memories/current_memory.md \
  gs://consensus-memory/backups/memory_$DATE.md
```

---

## Advanced Features

### Multi-Region Replication

**Replicate to multiple regions:**

```bash
# Create bucket in Europe
gsutil mb -l europe-west1 gs://consensus-memory-eu

# Enable cross-region replication
gsutil rsync -r gs://consensus-memory/ gs://consensus-memory-eu/
```

### Memory Encryption

**Customer-managed encryption keys:**

```bash
# Create KMS key
gcloud kms keyrings create consensus-keyring --location=global
gcloud kms keys create memory-key --location=global --keyring=consensus-keyring --purpose=encryption

# Upload with encryption
gsutil -o "GSUtil:encryption_key=projects/YOUR_PROJECT/locations/global/keyRings/consensus-keyring/cryptoKeys/memory-key" \
  cp memory.md gs://consensus-memory/memories/
```

### Audit Logging

**Track memory access:**

```bash
# Enable data access logs
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="allUsers" \
  --role="roles/logging.viewer"

# View logs
gcloud logging read "resource.type=gcs_bucket AND resource.labels.bucket_name=consensus-memory"
```

---

## Summary

**Vertex Workbench / GKE Deployment gives you:**

✅ **Cross-platform memory sync** (Vertex, GKE, Cloud Run, local)
✅ **Automatic updates** via init containers
✅ **Version control** with GCS versioning
✅ **Zero maintenance** (fully automated)
✅ **Negligible cost** (< $0.01/month)
✅ **High availability** (GCS 99.999% uptime)

**Setup time:** 15 minutes
**Maintenance:** None (automated)
**Cost:** Essentially free

---

**Your consensus system now runs anywhere in Google Cloud with persistent memory.**