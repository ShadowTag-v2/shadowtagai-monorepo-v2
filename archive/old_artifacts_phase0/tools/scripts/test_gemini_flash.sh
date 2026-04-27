#!/bin/bash

# Load environment variables from specific .env if it exists
ENV_PATH="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.env"
if [ -f "$ENV_PATH" ]; then
  export $(grep -v '^#' "$ENV_PATH" | xargs)
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: GEMINI_API_KEY is not set. Please add GEMINI_API_KEY=your_key_here to your .env file."
    echo "You can generate one here: https://console.cloud.google.com/vertex-ai/studio/settings/api-keys?project=shadowtag-omega-v4"
    exit 1
fi

echo "Sending request to Gemini Flash Lite..."

curl "https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key=${GEMINI_API_KEY}" \
-X POST \
-H "Content-Type: application/json" \
-d '{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Explain how AI works in a few words"
        }
      ]
    }
  ]
}'
