# Grounded Generation with Google Search

This module provides a service and API endpoint for generating content grounded in Google Search using Vertex AI (Gemini).

## Features

- **Model**: `gemini-1.5-pro` (default)
- **Caching**: SQLite caching to avoid redundant API calls.
- **Batch Processing**: Script for high-concurrency batch generation with templating support.
- **IAM**: Automated setup script for Google Cloud permissions.

## Setup

1.  **IAM Configuration**:
    Run the setup script to enable APIs and create a service account.
    ```bash
    chmod +x scripts/setup_grounded_gen_iam.sh
    ./scripts/setup_grounded_gen_iam.sh
    ```
    Export the key:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/grounded-gen-sa-key.json
    ```

2.  **Install Dependencies**:
    ```bash
    pip install google-cloud-discoveryengine aiohttp
    ```

## Usage

### API Endpoint

Start the server:
```bash
uvicorn src.main:app --reload
```

Generate content:
```bash
curl -X POST "http://localhost:8000/api/v1/grounded-generation/generate" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Who won the 2024 Super Bowl?", "model_id": "gemini-1.5-pro"}'
```

### Batch Processing

Run the batch script with a list of prompts:
```bash
python3 scripts/batch_grounded_gen.py scripts/sample_prompts.json --concurrency 10
```

Run with templating:
```bash
python3 scripts/batch_grounded_gen.py scripts/sample_template_input.json \
    --template "Tell me about {topic}" \
    --concurrency 10
```

## Caching

Responses are cached in `grounded_gen_cache.db` (SQLite) in the root directory. The cache key is a hash of `prompt:model_id`.
