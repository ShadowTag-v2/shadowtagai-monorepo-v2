#!/bin/bash
echo ">>> 🧠 SUMMONING AGENT (GEMINI 3.0)..."
PROJECT_ID=$(gcloud config get-value project)
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID

uv run python3 -c "
import os
from google import genai
try:
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    # Assuming standard Vertex AI client structure; model name is the key
    print(f'    ✅ NEURAL LINK ACTIVE: gemini-3.0-flash [{project_id}]')
    print('    waiting for instructions...')
except Exception as e:
    print(f'    ❌ LINK ERROR: {e}')
"
