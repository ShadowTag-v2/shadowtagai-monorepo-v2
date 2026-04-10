# Gemini Setup Guide (Keyless / Secure)

This guide provides steps to enable and use Gemini (Gemini Cloud Assist / Gemini API) in the **ShadowTagAi** project using secure, keyless authentication methods.

---

## Prerequisites

- Google Cloud SDK (`gcloud`) installed.
- Project ID: `acquired-jet-478701-b3`.
- IAM Role: `roles/aiplatform.user` and `roles/geminicloudassist.user` (Already granted to your user/service account).

---

## 1. Enable Required APIs

```bash
gcloud config set project acquired-jet-478701-b3
gcloud services enable aiplatform.googleapis.com geminicloudassist.googleapis.com
```

---

## 2. Local Development: Use User Credentials (ADC)

Instead of managing risky service account keys, use your own user credentials locally.

1.  **Login for Application Default Credentials (ADC):**

    ```bash
    gcloud auth application-default login
    ```

    _This will open a browser window. Log in with `founder@shadowtagai.com`._

2.  **Install Python Client:**

    ```bash
    pip install google-cloud-aiplatform
    ```

3.  **Verify Access:**
    Create `gemini_test.py`:

    ```python
    from google.cloud import aiplatform

    aiplatform.init(project="acquired-jet-478701-b3", location="us-central1")

    client = aiplatform.ModelServiceClient()
    parent = "projects/acquired-jet-478701-b3/locations/us-central1"
    for model in client.list_models(parent=parent):
        print(model.name)
    ```

    Run it: `python gemini_test.py`

---

## 3. Production (GKE/Cloud Run): Use Workload Identity

For deployments, use Workload Identity to impersonate the service account `gemini-sa`.

1.  **Create Service Account (Done):** `gemini-sa@acquired-jet-478701-b3.iam.gserviceaccount.com`
2.  **Grant Roles (Done):** `aiplatform.user`, `geminicloudassist.user`.
3.  **Bind Kubernetes Service Account (KSA) to Google Service Account (GSA):**

    ```bash
    # Example for 'default' namespace and 'gemini-ksa' KSA
    gcloud iam service-accounts add-iam-policy-binding gemini-sa@acquired-jet-478701-b3.iam.gserviceaccount.com \
        --role roles/iam.workloadIdentityUser \
        --member "serviceAccount:acquired-jet-478701-b3.svc.id.goog[default/gemini-ksa]"

    kubectl annotate serviceaccount gemini-ksa \
        --namespace default \
        iam.gke.io/gcp-service-account=gemini-sa@acquired-jet-478701-b3.iam.gserviceaccount.com
    ```

---

## 4. Enable Gemini Cloud Assist (Console)

1.  Open [Gemini Cloud Assist](https://console.cloud.google.com/gemini).
2.  Ensure your user has the `geminicloudassist.user` role (Granted).

---

**Status:** APIs enabled, Service Account created. Local access requires `gcloud auth application-default login`.
