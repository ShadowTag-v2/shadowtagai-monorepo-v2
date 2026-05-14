#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="${PWD}"
REPORT_DIR="${PROJECT_ROOT}/docs/judge6-reports"
mkdir -p "${REPORT_DIR}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT="${REPORT_DIR}/judge6-${TIMESTAMP}.md"
VIDEO_FILE="${PROJECT_ROOT}/latest-run.mp4"
GCS_BUCKET="gs://pnkln-cinematic-artifacts"
GCS_PATH="${GCS_BUCKET}/videos/$(basename "${VIDEO_FILE}" .mp4)-${TIMESTAMP}.mp4"
echo "## Judge-6 Report - ${TIMESTAMP}" > "${REPORT}"
if [[ -f "${VIDEO_FILE}" ]]; then
  gcloud storage cp "${VIDEO_FILE}" "${GCS_PATH}" --quiet
  ACCESS_TOKEN=$(gcloud auth print-access-token)
  PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
  LOCATION="${REGION:-us-central1}"
  MODEL="gemini-2.5-pro"
  PROMPT=$(cat "${PROJECT_ROOT}/prompts/judge6-cinematic.md")
  RESPONSE=$(curl -s -X POST -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" "https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${LOCATION}/publishers/google/models/${MODEL}:generateContent" -d '{"contents":[{"role":"user","parts":[{"text":"'"${PROMPT}"'"},{"fileData":{"mimeType":"video/mp4","fileUri":"'"${GCS_PATH}"'"}}]}],"generationConfig":{"temperature":0.0,"responseMimeType":"application/json"}}')
  VERDICT=$(echo "${RESPONSE}" | jq -r '.candidates[0].content.parts[0].text | fromjson.verdict // "FAIL"')
  RISK_LEVEL=$(echo "${RESPONSE}" | jq -r '.candidates[0].content.parts[0].text | fromjson.risk_level // "High"')
  echo "Gemini 2.5 Pro: ${VERDICT} | Risk: ${RISK_LEVEL}" >> "${REPORT}"
  [[ "${VERDICT}" == "PASS" && "${RISK_LEVEL}" != "High" && "${RISK_LEVEL}" != "Extreme" ]] && CINEMATIC_PASS=true || CINEMATIC_PASS=false
else
  CINEMATIC_PASS=true
fi
echo -e "\n=== JUDGE-6 FINAL VERDICT ===" >> "${REPORT}"
if [[ "${CINEMATIC_PASS}" == "false" ]]; then
  echo "BLOCKED" >> "${REPORT}"
  cat "${REPORT}"
  exit 1
else
  echo "APPROVED" >> "${REPORT}"
  cat "${REPORT}"
  exit 0
fi
