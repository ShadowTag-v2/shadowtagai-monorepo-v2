#!/bin/zsh
# -----------------------------------------------------------------------------
# ▛///▞ ANTIGRAVITY :: GCP RESOURCE AUDIT (INTERACTIVE)
# "We distinguish between Engines (which do work) and Guardrails (which permit work)."
# -----------------------------------------------------------------------------

set -e

if [[ -z "$PROJECT_ID" ]]; then
    echo "❌ ERROR: PROJECT_ID environment variable not set."
    echo "Usage: export PROJECT_ID='your-project-id' && ./gcp_cleanup_audit.sh"
    exit 1
fi

echo "⚔️  AUDITING GCP PROJECT: ${PROJECT_ID}"

confirm() {
    echo -n "❓ DELETE these resources? [y/N] "
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        return 0
    else
        return 1
    fi
}

# 1. STOPPED INSTANCES
echo "\n››› 1. Checking for STOPPED GCE VM instances..."
STOPPED_INSTANCES=$(gcloud compute instances list --filter="status=TERMINATED" --format="value(name,zone)")
if [[ -n "$STOPPED_INSTANCES" ]]; then
    echo "🔍 Found stopped instances:"
    echo "$STOPPED_INSTANCES" | awk '{printf "  - %s (Zone: %s)\n", $1, $2}'
    if confirm; then
        echo "$STOPPED_INSTANCES" | while read -r name zone; do
            echo "  🔥 Deleting instance '$name'..."
            gcloud compute instances delete "$name" --zone="$zone" --quiet &
        done
        wait
    else
        echo "  Skipping."
    fi
else
    echo "  ✅ No stopped instances."
fi

# 2. UNATTACHED DISKS
echo "\n››› 2. Checking for UNATTACHED GCE Disks..."
UNATTACHED_DISKS=$(gcloud compute disks list --filter="-users:*" --format="value(name,zone)")
if [[ -n "$UNATTACHED_DISKS" ]]; then
    echo "🔍 Found unattached disks:"
    echo "$UNATTACHED_DISKS" | awk '{printf "  - %s (Zone: %s)\n", $1, $2}'
    if confirm; then
        echo "$UNATTACHED_DISKS" | while read -r name zone; do
            echo "  🔥 Deleting disk '$name'..."
            gcloud compute disks delete "$name" --zone="$zone" --quiet &
        done
        wait
    else
        echo "  Skipping."
    fi
else
    echo "  ✅ No unattached disks."
fi

# 3. UNTRAFFICKED REVISIONS
echo "\n››› 3. Checking for UNTRAFFICKED Cloud Run Revisions..."
# Note: Be careful not to delete revisions needed for rollback if you care about that.
# This aggressive script assumes 'junk' should go.
UNPROVISIONED=$(gcloud run revisions list --filter="status.traffic:[]" --format="value(name,region)")
if [[ -n "$UNPROVISIONED" ]]; then
    echo "🔍 Found untrafficked revisions:"
    echo "$UNPROVISIONED" | awk '{printf "  - %s (Region: %s)\n", $1, $2}'
    if confirm; then
        echo "$UNPROVISIONED" | while read -r name region; do
            echo "  🔥 Deleting revision '$name'..."
            gcloud run revisions delete "$name" --region="$region" --quiet &
        done
        wait
    else
        echo "  Skipping."
    fi
else
    echo "  ✅ No untrafficked revisions."
fi

echo "\n✨ AUDIT COMPLETE. The cloud is lighter."
