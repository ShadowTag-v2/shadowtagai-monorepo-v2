# Cloud Build Trigger Setup

This guide documents how to set up the CI/CD triggers for `ShadowTag-v2-fastapi-services` on Google Cloud Build.

## Prerequisites

- Google Cloud Project: `acquired-jet-478701-b3`

- GitHub Repository connected to Cloud Build (2nd Gen / Cloud Build GitHub App).

- `gcloud` CLI installed and authenticated.

## Automated Setup

Run the provided helper script:

```bash
chmod +x scripts/setup_cloudbuild_triggers.sh
./scripts/setup_cloudbuild_triggers.sh

```

## Manual Setup Configuration

If you prefer to configure this via the [Google Cloud Console](https://console.cloud.google.com/cloud-build/triggers?project=acquired-jet-478701-b3), use the following settings:

### 1. CD Trigger (Main Branch)

| Setting           | Value                                         |
| :---------------- | :-------------------------------------------- |
| **Name**          | `antigravity-cd-main`                         |
| **Event**         | Push to a branch                              |
| **Source**        | `pikeymickey/ShadowTag-v2-fastapi-services` (GitHub) |
| **Branch**        | `^main$`                                      |
| **Configuration** | Cloud Build configuration file (yaml or json) |
| **Location**      | Repository                                    |
| **File location** | `cloudbuild-antigravity.yaml`                 |

### 2. CI Trigger (Pull Requests)

| Setting           | Value                                         |
| :---------------- | :-------------------------------------------- |
| **Name**          | `antigravity-ci-pr`                           |
| **Event**         | Pull Request                                  |
| **Source**        | `pikeymickey/ShadowTag-v2-fastapi-services` (GitHub) |
| **Base Branch**   | `^main$`                                      |
| **Configuration** | Cloud Build configuration file (yaml or json) |
| **Location**      | Repository                                    |
| **File location** | `cloudbuild.pr.yaml`                          |

## Verification

After creating the triggers:

1. Push a small change to a feature branch and open a PR to test `antigravity-ci-pr`.

2. Merge a change to `main` to test `antigravity-cd-main`.