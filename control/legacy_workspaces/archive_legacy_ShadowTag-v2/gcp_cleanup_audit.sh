#!/bin/zsh

# A script to audit a GCP project and list potentially unused or forgotten resources.
# This script is READ-ONLY by default but provides interactive prompts to DELETE resources.

set -e # Exit immediately if a command exits with a non-zero status.

if [[ -z "$1" ]]; then
  echo "🛑 Error: No GCP Project ID provided."
  echo "Usage: ./gcp_cleanup_audit.sh YOUR_PROJECT_ID"
  exit 1
fi

PROJECT_ID=$1

echo "››› Setting gcloud config to project ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# --- Helper function for confirmation ---
confirm() {
    echo -n "❓ Do you want to delete them? [y/N] "
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        return 0 # Success (yes)
    else
        return 1 # Failure (no)
    fi
}

echo "\n››› 1. Finding stopped GCE VM instances..."
STOPPED_INSTANCES=$(gcloud compute instances list --filter="status=TERMINATED" --format="value(name,zone)")
if [[ -n "$STOPPED_INSTANCES" ]]; then
    echo "🔍 Found the following stopped instances:"
    echo "$STOPPED_INSTANCES" | awk '{printf "  - Instance: %s, Zone: %s\n", $1, $2}'
    if confirm; then
        echo "$STOPPED_INSTANCES" | while read -r name zone; do
            echo "  🔥 Deleting instance '$name' in zone '$zone'..."
            gcloud compute instances delete "$name" --zone="$zone" --quiet
        done
    else
        echo "  Skipping deletion."
    fi
else
    echo "  ✅ No stopped instances found."
fi

echo "\n››› 2. Finding unattached GCE disks..."
UNATTACHED_DISKS=$(gcloud compute disks list --filter="-users:*" --format="value(name,zone)")
if [[ -n "$UNATTACHED_DISKS" ]]; then
    echo "🔍 Found the following unattached disks:"
    echo "$UNATTACHED_DISKS" | awk '{printf "  - Disk: %s, Zone: %s\n", $1, $2}'
    if confirm; then
        echo "$UNATTACHED_DISKS" | while read -r name zone; do
            echo "  🔥 Deleting disk '$name' in zone '$zone'..."
            gcloud compute disks delete "$name" --zone="$zone" --quiet
        done
    else
        echo "  Skipping deletion."
    fi
else
    echo "  ✅ No unattached disks found."
fi

echo "\n››› 3. Finding unused reserved static IP addresses..."
UNUSED_IPS=$(gcloud compute addresses list --filter="addressType=EXTERNAL AND status=RESERVED" --format="value(name,region)")
if [[ -n "$UNUSED_IPS" ]]; then
    echo "🔍 Found the following unused static IPs:"
    echo "$UNUSED_IPS" | awk '{printf "  - IP Name: %s, Region: %s\n", $1, $2}'
    if confirm; then
        echo "$UNUSED_IPS" | while read -r name region; do
            echo "  🔥 Deleting IP '$name' in region '$region'..."
            gcloud compute addresses delete "$name" --region="$region" --quiet
        done
    else
        echo "  Skipping deletion."
    fi
else
    echo "  ✅ No unused static IPs found."
fi

echo "\n››› 4. Finding untrafficked Cloud Run revisions..."
UNPROVISIONED_REVISIONS=$(gcloud run revisions list --filter="status.traffic:[]" --format="value(name,region)")
if [[ -n "$UNPROVISIONED_REVISIONS" ]]; then
    echo "🔍 Found the following untrafficked revisions:"
    echo "$UNPROVISIONED_REVISIONS" | awk '{printf "  - Revision: %s, Region: %s\n", $1, $2}'
    if confirm; then
        echo "$UNPROVISIONED_REVISIONS" | while read -r name region; do
            echo "  🔥 Deleting revision '$name' in region '$region'..."
            gcloud run revisions delete "$name" --region="$region" --quiet
        done
    else
        echo "  Skipping deletion."
    fi
else
    echo "  ✅ No untrafficked revisions found."
fi

echo "\n--- Resources for Manual Review ---"
echo "\n››› 5. Listing Cloud SQL instances for manual review..."
# Determining if a SQL instance is "unused" requires monitoring data. This just lists them.
gcloud sql instances list --format="table(name,databaseVersion,settings.tier,state)"

echo "\n››› 6. Listing GCS buckets for manual review..."
# Consider applying lifecycle policies to auto-clean old objects.
gcloud storage buckets list --format="table(name,location,storageClass)"

echo "\n››› 7. Listing old container images in Artifact Registry (older than 90 days)..."
CUTOFF_DATE=$(date -v-90d +%Y-%m-%d)
gcloud artifacts docker images list --repository-format --filter="update_time<${CUTOFF_DATE}" --format="table(name,update_time)"

echo "\n✅ Audit complete for project: ${PROJECT_ID}"
echo "ℹ️  Review the manually listed resources above to identify other potential cleanup targets."
