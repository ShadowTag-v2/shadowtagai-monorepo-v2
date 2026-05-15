#!/bin/bash
# Pnkln GKE Validation Sprint - Cost Tracker
# Purpose: Monitor cloud spend and enforce $5K budget cap
# Alert threshold: $4K (80% of budget)

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-pnkln-validation}"
BUDGET_CAP=5000
ALERT_THRESHOLD=4000
REPORT_FILE="cost_report_$(date +%Y%m%d_%H%M%S).json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI not found"
    exit 1
fi

log_info "Fetching billing data for project: ${PROJECT_ID}"

# Get current month's billing data
CURRENT_MONTH=$(date +%Y-%m)
BILLING_ACCOUNT=$(gcloud beta billing projects describe "${PROJECT_ID}" --format="value(billingAccountName)" 2>/dev/null || echo "")

if [ -z "$BILLING_ACCOUNT" ]; then
    log_error "No billing account found for project ${PROJECT_ID}"
    log_error "This project may not have billing enabled"
    exit 1
fi

log_info "Billing Account: ${BILLING_ACCOUNT}"

# Query billing data using BigQuery (requires billing export to BigQuery)
# Note: This assumes billing export is configured
BILLING_DATASET="billing_export"

log_info "Querying cost data for ${CURRENT_MONTH}..."

# Query current month's spend
QUERY="
SELECT
  SUM(cost) AS total_cost,
  currency
FROM
  \`${PROJECT_ID}.${BILLING_DATASET}.gcp_billing_export_v1_*\`
WHERE
  project.id = '${PROJECT_ID}'
  AND FORMAT_TIMESTAMP('%Y-%m', usage_start_time) = '${CURRENT_MONTH}'
GROUP BY
  currency
"

# Execute query (this requires billing export setup)
COST_DATA=$(bq query --use_legacy_sql=false --format=json "$QUERY" 2>/dev/null || echo "[]")

if [ "$COST_DATA" = "[]" ]; then
    log_warn "No billing data found. Billing export may not be configured."
    log_info "To enable billing export, visit: https://console.cloud.google.com/billing"

    # Fallback: Estimate based on GKE resources
    log_info "Estimating costs based on GKE resource usage..."

    # Get GPU node count
    GPU_NODES=$(kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-l4 -o json 2>/dev/null | jq '.items | length' || echo 0)

    # Rough cost estimation (L4 GPU node ~$0.85/hr)
    GPU_COST_PER_HOUR=0.85
    HOURS_IN_MONTH=730
    ESTIMATED_COST=$(echo "$GPU_NODES * $GPU_COST_PER_HOUR * $HOURS_IN_MONTH" | bc)

    log_info "Estimated monthly cost: \$${ESTIMATED_COST} (${GPU_NODES} GPU nodes)"
    TOTAL_COST=$ESTIMATED_COST
else
    TOTAL_COST=$(echo "$COST_DATA" | jq -r '.[0].total_cost // 0')
fi

# Display cost summary
log_info "=================================="
log_info "COST SUMMARY - ${CURRENT_MONTH}"
log_info "=================================="
log_info "Total Spend: \$${TOTAL_COST}"
log_info "Budget Cap: \$${BUDGET_CAP}"
log_info "Alert Threshold: \$${ALERT_THRESHOLD}"

REMAINING=$(echo "$BUDGET_CAP - $TOTAL_COST" | bc)
PERCENT_USED=$(echo "scale=1; ($TOTAL_COST / $BUDGET_CAP) * 100" | bc)

log_info "Remaining: \$${REMAINING} (${PERCENT_USED}% used)"
log_info "=================================="

# Check thresholds
if (( $(echo "$TOTAL_COST >= $BUDGET_CAP" | bc -l) )); then
    log_error "BUDGET CAP EXCEEDED!"
    log_error "Immediate action required: Scale down or shut down validation sprint"
    exit 2
elif (( $(echo "$TOTAL_COST >= $ALERT_THRESHOLD" | bc -l) )); then
    log_warn "Cost approaching budget cap (${PERCENT_USED}% used)"
    log_warn "Consider scaling down non-essential resources"
fi

# Generate detailed cost breakdown
log_info "Generating detailed cost breakdown..."

BREAKDOWN_QUERY="
SELECT
  service.description AS service,
  SUM(cost) AS cost
FROM
  \`${PROJECT_ID}.${BILLING_DATASET}.gcp_billing_export_v1_*\`
WHERE
  project.id = '${PROJECT_ID}'
  AND FORMAT_TIMESTAMP('%Y-%m', usage_start_time) = '${CURRENT_MONTH}'
GROUP BY
  service
ORDER BY
  cost DESC
LIMIT 10
"

BREAKDOWN=$(bq query --use_legacy_sql=false --format=json "$BREAKDOWN_QUERY" 2>/dev/null || echo "[]")

if [ "$BREAKDOWN" != "[]" ]; then
    log_info "Top 10 services by cost:"
    echo "$BREAKDOWN" | jq -r '.[] | "\(.service): $\(.cost)"'
fi

# Save report
REPORT_JSON=$(cat <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_id": "$PROJECT_ID",
  "month": "$CURRENT_MONTH",
  "total_cost": $TOTAL_COST,
  "budget_cap": $BUDGET_CAP,
  "alert_threshold": $ALERT_THRESHOLD,
  "remaining": $REMAINING,
  "percent_used": $PERCENT_USED,
  "status": "$([ $(echo "$TOTAL_COST >= $BUDGET_CAP" | bc -l) -eq 1 ] && echo "OVER_BUDGET" || echo "OK")",
  "breakdown": $BREAKDOWN
}
EOF
)

echo "$REPORT_JSON" > "$REPORT_FILE"
log_info "Cost report saved to: $REPORT_FILE"

# Return appropriate exit code
if (( $(echo "$TOTAL_COST >= $BUDGET_CAP" | bc -l) )); then
    exit 2  # Over budget
elif (( $(echo "$TOTAL_COST >= $ALERT_THRESHOLD" | bc -l) )); then
    exit 1  # Warning
else
    exit 0  # OK
fi
