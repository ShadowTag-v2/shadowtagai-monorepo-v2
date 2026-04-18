#!/bin/bash
# vendor_import.sh
# Usage: ./vendor_import.sh <list_of_repos_file> <target_dir>

REPO_LIST=$1
TARGET_BASE=$2
LOG_FILE="migration.log"

# Blacklist of heavy repos to skip
SKIP_LIST=("xla" "rumdl")

if [ -z "$REPO_LIST" ] || [ -z "$TARGET_BASE" ]; then
  echo "Usage: $0 <repo_list_file> <target_base_dir>"
  exit 1
fi

mkdir -p "$TARGET_BASE"

count=0
total=$(wc -l < "$REPO_LIST" | tr -d ' ')

echo "Restarting migration (SKIPPING: ${SKIP_LIST[*]}) at $(date)" | tee -a "$LOG_FILE"

while IFS= read -r repo_path; do
  # Skip empty lines
  [ -z "$repo_path" ] && continue

  dirname=$(basename "$repo_path")

  # Check against skip list
  skip_repo=false
  for skip in "${SKIP_LIST[@]}"; do
    if [[ "$dirname" == "$skip" ]]; then
      skip_repo=true
      break
    fi
  done

  if [ "$skip_repo" = true ]; then
    echo "[$((++count))/$total] EXPLICITLY SKIPPED $dirname (Heavy)" | tee -a "$LOG_FILE"
    continue
  fi

  if [ -d "$repo_path" ]; then
    target="$TARGET_BASE/$dirname"

    ((count++))

    if [ -d "$target" ]; then
      # Silent skip for existing
      :
    else
      # Copy content excluding heavy junk
      mkdir -p "$target"
      if rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' --exclude='.DS_Store' "$repo_path/" "$target/"; then
         echo "[$count/$total] Migrated $dirname" | tee -a "$LOG_FILE"
      else
         echo "[$count/$total] FREAKOUT: Failed to migrate $dirname" | tee -a "$LOG_FILE"
      fi
    fi
  else
    echo "Warning: Source $repo_path not found" >> "$LOG_FILE"
  fi
done < "$REPO_LIST"

echo "Migration complete." | tee -a "$LOG_FILE"
