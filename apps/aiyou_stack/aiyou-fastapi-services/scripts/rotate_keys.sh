#!/bin/bash
# scripts/rotate_keys.sh
# Usage: ./rotate_keys.sh [temporal|hf] [new-key-value]

SECRET_TYPE=$1
NEW_VAL=$2

PROJECT_ID="shadowtag-omega-v2"

if [ -z "$SECRET_TYPE" ] || [ -z "$NEW_VAL" ]; then
    echo "Usage: $0 [temporal|hf] [new-key-value]"
    echo "Example: $0 temporal sk-123456789"
    exit 1
fi

case $SECRET_TYPE in
    temporal)
        SECRET_ID="temporal-api-key"
        ;;
    hf)
        SECRET_ID="hugging-face-token"
        ;;
    *)
        echo "Invalid type. Use 'temporal' or 'hf'."
        exit 1
        ;;
esac

echo "Rotating secret $SECRET_ID in project $PROJECT_ID..."
printf "$NEW_VAL" | gcloud secrets versions add $SECRET_ID --data-file=- --project=$PROJECT_ID

echo "Done. Cloud Run will pick up the new 'latest' version on next deployment or instance replacement."
echo "To force update immediately: gcloud run services update [SERVICE_NAME] --project $PROJECT_ID"
