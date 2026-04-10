# Gemini Code Assist Enterprise - Custom Code Configuration

This directory contains the configuration for enabling **Custom Code** (Codebase Awareness) in Gemini Code Assist Enterprise.

## 1. `gemini_custom_code.json`

This file defines the **Repository Group** to be indexed. You need to replace the placeholders with your actual Google Cloud resources.

### Prerequisites

1. **Developer Connect**: successfuly connected your GitHub/GitLab repository to Google Cloud Developer Connect.

2. **Permissions**: Ensure you have `Gemini Code Assist Enterprise User` role.

### How to fill the JSON

Run the following command to find your connection details:

```bash
gcloud developer-connect connections list --location=YOUR_REGION

```

And to list linked repositories:

```bash
gcloud developer-connect connections git-repository-links list --connection=YOUR_CONNECTION_ID --location=YOUR_REGION

```

Then update `gemini_custom_code.json`:

```json
[
  {
    "resource": "projects/PROJECT_ID/locations/REGION/connections/CONNECTION_ID/gitRepositoryLinks/REPO_ID",
    "branch_pattern": "main"
  }
]
```

## 2. Create the Repository Group

Once the JSON is ready, create the repository group using `gcloud`:

```bash
gcloud gemini-code-assist repository-groups create GROUP_NAME \
    --project=PROJECT_ID \
    --location=REGION \
    --repositories=gemini_custom_code.json \
    --labels=env=prod

```

## 3. Indexing Status

Check the status of the indexing:

```bash
gcloud gemini-code-assist repository-groups list --location=REGION

```

## 4. Exclusion (`.aiexclude`)

To exclude files from being sent to Gemini, create a `.aiexclude` file in your repository root (similar to `.gitignore`).

Example `.aiexclude`:

```

secrets/
*.env
tests/legacy/

```
