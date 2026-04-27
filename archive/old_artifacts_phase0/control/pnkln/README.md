# pnkln Multi-Agent System

This repository contains the core infrastructure and agent logic for the `pnkln` system.

## Setup

1.  Configure your environment variables (e.g., in a `.env` file).
    ```
    SUPABASE_URL="your-supabase-url"
    SUPABASE_KEY="your-supabase-key"
    GCP_PROJECT_ID="your-gcp-project-id"
    GCP_BUCKET="your-gcp-bucket-name"
    ```
2.  Run the setup script to install dependencies:
    ```bash
    bash scripts/setup.sh
    ```

## Usage

Run tasks via the main entrypoint:
```bash
python main.py "your task description here"
```
