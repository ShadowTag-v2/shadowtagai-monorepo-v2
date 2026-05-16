# TASK.md: CounselConduit Firestore Stateless Integration

> [!IMPORTANT]
> This task defines the implementation of a stateless architecture for CounselConduit using Google Cloud Firestore instead of Redis.

## 1. Goal
Transition the `counselconduit` Cloud Run service to a stateless architecture to resolve memory limit constraints (512 MiB limit) by offloading session state, caches, and queues to Firestore.

## 2. Infrastructure
- **Service Account**: `counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com`
- **Database**: Google Cloud Firestore in native mode (`nam5` location or standard default)

## 3. Implementation Steps
1. **Dependencies**: Use `google-cloud-firestore` in `apps/counselconduit/pyproject.toml`.
2. **Connection Management**: Audit `apps/counselconduit/core/firebase_admin.py` to ensure a singleton Firestore client with `max_pool_size=5`.
3. **State Migration**: Refactor `workspace_alerts.py` to use Firestore real-time listeners or polling for pub/sub mechanics instead of in-memory dictionaries.
4. **Cache Migration**: Replace Python global dicts with Firestore documents featuring TTL indexes.
5. **Validation**: Test connections with a locally running Firestore emulator before deploying the updated image to Cloud Run.

## 4. Asynchronous Queue (Cloud Tasks)
*   **Stripe Webhooks**: Convert webhook handling to enqueue Cloud Tasks for asynchronous Firestore writes.
*   **Judge6 Background tasks**: Set up long-running evaluation as a Cloud Task with a 10-minute deadline to prevent Cloud Run request timeouts.

## 5. Security & Credentials
- Do not store any API keys in code. Authentication is via Application Default Credentials (ADC) attached to the Cloud Run service account.
