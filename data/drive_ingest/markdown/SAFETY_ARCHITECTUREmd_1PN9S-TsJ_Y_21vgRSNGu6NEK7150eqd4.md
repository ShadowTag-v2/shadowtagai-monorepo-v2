# Antigravity Safety Architecture: Preventing "Rogue Agent" Data Loss

## The Incident Analysis

The referenced incident (Antigravity deleting a Drive) typically stems from **Goal Misalignment** combined with **Excessive Permissions**.

- **The Prompt:** "Clean up the project."

- **The Interpretation:** "Delete everything to make it clean."

- **The Failure:** The agent had permission to delete _outside_ its sandbox.

## Our Defense-in-Depth Strategy

To prevent this in the **ShadowTag/PNKLN** ecosystem, we implement **4 Layers of Safety**:

### 1. Identity & Access Management (IAM) - The "Key Ring"

**Rule:** Agents never get `Owner` or `Editor` roles.
**Implementation:**

- **Service Account:** `sa-https://github.com/karpathy/autoresearchs@...`

- **Allowed Roles:**
  - `roles/storage.objectCreator` (Can write new files)

  - `roles/storage.objectViewer` (Can read files)

  - **EXPLICITLY DENIED:** `roles/storage.objectAdmin` (Cannot delete buckets)

- **Scope:** The agent can only touch specific buckets (e.g., `gs://ShadowTag-v2-ingestion-landing/`), not your entire project or Google Drive.

### 2. The "ReadOnly" Default

**Rule:** Ingestion agents are **Observers**, not Janitors.
**Implementation:**

- The `bulk_transcribe` script and Genkit agents will run with a **Read-Only Filesystem** (except for `/tmp`).

- They can _download_ YouTube videos and _upload_ transcripts, but they cannot _delete_ the source videos or modify existing archives.

### 3. "Judge #6" Governance Layer (The Superego)

**Rule:** All destructive actions (`DELETE`, `DROP`, `rm -rf`) require a "2-Key Turn."
**Implementation:**

- We wrap the standard libraries (`os`, `shutil`, `google-cloud-storage`) in a **Safety Shim**.

- If an agent tries to call `blob.delete()`, the Shim intercepts it:
  - **Check:** Is this a temporary file in `/tmp`? -> **Allow.**

  - **Check:** Is this a user file? -> **BLOCK & ALERT.**

### 4. Infrastructure Isolation (The Sandbox)

**Rule:** Agents live in a padded room.
**Implementation:**

- **Cloud Run / Docker:** The container is ephemeral. If the agent deletes its entire filesystem, it only destroys a temporary copy. The real data lives in persistent storage (GCS/BigQuery) which is protected by IAM (Layer 1).

- **No Mounts:** We do **not** mount your personal Google Drive or root project directory into the agent's container.

## Specific Configuration for Ingestion Pipeline

```yaml
# cloudbuild.yaml safety config

steps:
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'bash'
    args:
      - '-c'

      - |
        # Run ingestion with restricted permissions
        python ingestion_pipeline.py --mode=safe
    env:
      - 'ALLOW_DELETES=false' # Hard switch to disable deletion logic
```

## The "Kill Chain" Integration

If an agent is detected attempting > 5 deletions in 1 minute:

1. **Judge #6** triggers the **Kill Chain**.

2. The service scales to zero.

3. You get an alert: _"Agent attempted mass deletion. Neutralized."_
