# Cloud SQL Setup & Connection Guide

This guide details how to set up and connect to Google Cloud SQL (MySQL) for the `pnkln-stack-fastapi-services` project.

## 1. Prerequisites

- **Google Cloud SDK (`gcloud`)**: Must be installed and authenticated.

- **Cloud SQL Auth Proxy**: Recommended for secure local development without whitelisting IPs.

### Install Cloud SQL Auth Proxy (macOS)

```bash
brew install cloud-sql-proxy

```

_Or download specifically for your architecture from [Google Cloud Docs](https://cloud.google.com/sql/docs/mysql/connect-auth-proxy)._

## 2. Gcloud Configuration

Ensure you are set to the correct project:

```bash
gcloud config set project acquired-jet-478701-b3

```

## 3. Connecting to the Database

### Option A: Using the Helper Script

We've provided a script to simplify connections:

```bash
./scripts/connect_cloud_sql.sh [INSTANCE_NAME] [PORT]

```

### Option B: Using Cloud SQL Auth Proxy Directly

1. **Start the Proxy**:

   ```bash
   cloud-sql-proxy acquired-jet-478701-b3:us-central1:[INSTANCE_NAME]
   ```

   _Replace `[INSTANCE_NAME]` with your actual Cloud SQL instance name._

2. **Connect via MySQL Client**:
   ```bash
   mysql -u [USER] -p --host 127.0.0.1 --port 3306
   ```

### Option C: Using `gcloud sql connect` (Quick Checks)

This method temporarily authorizes your IP.

```bash
gcloud sql connect [INSTANCE_NAME] --user=[USER] --quiet

```

## 4. Useful Commands

- **List Instances**: `gcloud sql instances list`

- **List Databases**: `gcloud sql databases list --instance=[INSTANCE_NAME]`

- **Create Instance**:
  ```bash
  gcloud sql instances create [INSTANCE_NAME] \
    --database-version=MYSQL_8_0 \
    --cpu=2 --memory=8Gi \
    --region=us-central1
  ```
