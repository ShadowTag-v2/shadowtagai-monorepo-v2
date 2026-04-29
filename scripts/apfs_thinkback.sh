#!/bin/bash
# apfs_thinkback.sh
# APFS snapshot utility replicating tengu_thinkback

set -e

if [ "$1" == "create" ]; then
    echo "Creating local APFS snapshot..."
    tmutil localsnapshot
    echo "Snapshot created successfully."
elif [ "$1" == "list" ]; then
    echo "Listing local snapshots..."
    tmutil listlocalsnapshots /
else
    echo "Usage: ./apfs_thinkback.sh [create|list]"
    exit 1
fi
