#!/bin/bash
# debug_pr.sh: Comprehensive PR status audit for ShadowTag-v2
# Consistent with handle_prs.sh logging patterns.

LOG_FILE="gh_output.txt"

echo "Starting gh pr debug audit..." > "$LOG_FILE"

echo "--- PR Status Overview ---" >> "$LOG_FILE"
gh pr status >> "$LOG_FILE" 2>&1

echo -e "\n--- Detailed PR List (Open) ---" >> "$LOG_FILE"
# Including statusCheckRollup and mergeable to debug CI issues like PR 10
gh pr list --json number,title,url,state,mergeable,statusCheckRollup,author >> "$LOG_FILE" 2>&1

echo -e "\nFinished." >> "$LOG_FILE"
