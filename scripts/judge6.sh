#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PWD}"
REPORT_DIR="${JUDGE6_REPORT_DIR:-${PROJECT_ROOT}/artifacts/judge6-reports}"
VIDEO_DIR="${JUDGE6_VIDEO_DIR:-${PROJECT_ROOT}/artifacts/videos}"
PROMPT_FILE="${PROJECT_ROOT}/prompts/judge6-cinematic.md"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
REPORT="${REPORT_DIR}/judge6-${TIMESTAMP}.md"
BUCKET="${JUDGE6_GCS_BUCKET:-}"
LOCATION="${REGION:-us-central1}"
MODEL="${JUDGE6_MODEL:-gemini-3.1-flash-lite-preview}"

mkdir -p "${REPORT_DIR}" "${VIDEO_DIR}"

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}" >&2
    exit 2
  fi
}

append_section() {
  local title="$1"
  {
    echo
    echo "## ${title}"
  } >> "${REPORT}"
}

find_latest_video() {
  find "${VIDEO_DIR}" -type f \( -name "*.webm" -o -name "*.mp4" \) -print0 \
    | xargs -0 ls -1t 2>/dev/null \
    | head -n 1
}

run_optional_check() {
  local label="$1"
  shift
  append_section "${label}"
  if "$@" >> "${REPORT}" 2>&1; then
    echo "PASS" >> "${REPORT}"
  else
    echo "FAIL" >> "${REPORT}"
    return 1
  fi
}

require_cmd jq
require_cmd curl

{
  echo "# Judge-6 Report"
  echo
  echo "- Timestamp: ${TIMESTAMP}"
  echo "- Project root: ${PROJECT_ROOT}"
  echo "- Model: ${MODEL}"
  echo "- Region: ${LOCATION}"
} > "${REPORT}"

static_failed=0

if command -v eslint >/dev/null 2>&1; then
  run_optional_check "ESLint" eslint . --format compact || static_failed=1
else
  append_section "ESLint"
  echo "SKIP: eslint not installed" >> "${REPORT}"
fi

if command -v gitleaks >/dev/null 2>&1; then
  run_optional_check "Gitleaks" gitleaks detect --source . --no-banner || static_failed=1
else
  append_section "Gitleaks"
  echo "SKIP: gitleaks not installed" >> "${REPORT}"
fi

if [ -f "${PROJECT_ROOT}/package.json" ] && command -v npm >/dev/null 2>&1; then
  append_section "npm audit"
  if npm audit --audit-level=high >> "${REPORT}" 2>&1; then
    echo "PASS" >> "${REPORT}"
  else
    echo "FAIL" >> "${REPORT}"
    static_failed=1
  fi
else
  append_section "npm audit"
  echo "SKIP: package.json not present" >> "${REPORT}"
fi

append_section "RAG Tech-Stack Gatekeeper"
if [ -f "${PROJECT_ROOT}/core/rag_evolve.py" ]; then
  if python3 "${PROJECT_ROOT}/core/rag_evolve.py" --gatekeeper >> "${REPORT}" 2>&1; then
    echo "PASS" >> "${REPORT}"
  else
    echo "FAIL" >> "${REPORT}"
    static_failed=1
  fi
else
  echo "SKIP: core/rag_evolve.py not found" >> "${REPORT}"
fi

append_section "Cinematic Verification"

if [ ! -f "${PROMPT_FILE}" ]; then
  echo "FAIL: prompt file missing: ${PROMPT_FILE}" >> "${REPORT}"
  static_failed=1
fi

VIDEO_FILE="$(find_latest_video || true)"
if [ -z "${VIDEO_FILE}" ]; then
  echo "FAIL: no video artifact found under ${VIDEO_DIR}" >> "${REPORT}"
  static_failed=1
fi

if [ -z "${BUCKET}" ]; then
  echo "FAIL: JUDGE6_GCS_BUCKET is not set" >> "${REPORT}"
  static_failed=1
fi

if [ -z "${GOOGLE_CLOUD_PROJECT:-}" ]; then
  echo "FAIL: GOOGLE_CLOUD_PROJECT is not set" >> "${REPORT}"
  static_failed=1
fi

if [ "${static_failed}" -ne 0 ]; then
  {
    echo
    echo "## Final Verdict"
    echo "BLOCKED"
    echo
    echo "One or more required checks failed before cinematic analysis."
  } >> "${REPORT}"
  cat "${REPORT}"
  exit 1
fi

if [ "${JUDGE6_LOCAL_ANE:-false}" == "true" ]; then
  echo "Route: Offline Apple Neural Engine (zero_cpu_router.py)"
  RESPONSE="$(python3 scripts/local-ane-infer.py "${PROMPT_FILE}" "${VIDEO_FILE}")"
  MODEL_TEXT="${RESPONSE}"
else
  # ── Original Google Cloud Pathway ──
  require_cmd gcloud

  GCS_PATH="${BUCKET%/}/videos/$(basename "${VIDEO_FILE%.*}")-${TIMESTAMP}.$(basename "${VIDEO_FILE##*.}")"
  gcloud storage cp "${VIDEO_FILE}" "${GCS_PATH}" --quiet

  ACCESS_TOKEN="$(gcloud auth print-access-token)"
  PROMPT_JSON="$(jq -Rs . < "${PROMPT_FILE}")"

  REQUEST_JSON="$(jq -n \
    --arg prompt "$(cat "${PROMPT_FILE}")" \
    --arg fileUri "${GCS_PATH}" \
    '{
      contents: [
        {
          role: "user",
          parts: [
            {text: $prompt},
            {
              fileData: {
                mimeType: "video/webm",
                fileUri: $fileUri
              }
            }
          ]
        }
      ],
      generationConfig: {
        temperature: 0,
        responseMimeType: "application/json"
      }
    }'
  )"

  if [[ "${VIDEO_FILE}" == *.mp4 ]]; then
    REQUEST_JSON="$(jq '.contents[0].parts[1].fileData.mimeType = "video/mp4"' <<< "${REQUEST_JSON}")"
  fi

  RESPONSE="$(
    curl -fsS -X POST \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "Content-Type: application/json" \
      "https://${LOCATION}-aiplatform.googleapis.com/v1/projects/${GOOGLE_CLOUD_PROJECT}/locations/${LOCATION}/publishers/google/models/${MODEL}:generateContent" \
      -d "${REQUEST_JSON}"
  )"

  MODEL_TEXT="$(jq -r '.candidates[0].content.parts[0].text // empty' <<< "${RESPONSE}")"
fi
if [ -z "${MODEL_TEXT}" ]; then
  {
    echo "FAIL: model response missing text payload"
    echo
    echo '```json'
    echo "${RESPONSE}"
    echo '```'
  } >> "${REPORT}"
  {
    echo
    echo "## Final Verdict"
    echo "BLOCKED"
  } >> "${REPORT}"
  cat "${REPORT}"
  exit 1
fi

VERDICT="$(jq -r 'fromjson | .verdict // "FAIL"' <<< "${MODEL_TEXT}")"
RISK_LEVEL="$(jq -r 'fromjson | .risk_level // "High"' <<< "${MODEL_TEXT}")"

{
  echo "- Video file: ${VIDEO_FILE}"
  echo "- Uploaded URI: ${GCS_PATH}"
  echo "- Verdict: ${VERDICT}"
  echo "- Risk level: ${RISK_LEVEL}"
  echo
  echo "### Model Payload"
  echo '```json'
  echo "${MODEL_TEXT}"
  echo '```'
} >> "${REPORT}"

{
  echo
  echo "## Final Verdict"
} >> "${REPORT}"

case "${VERDICT}:${RISK_LEVEL}" in
  PASS:Low|PASS:Medium)
    echo "APPROVED" >> "${REPORT}"
    cat "${REPORT}"
    exit 0
    ;;
  *)
    echo "BLOCKED" >> "${REPORT}"
    cat "${REPORT}"
    exit 1
    ;;
esac
