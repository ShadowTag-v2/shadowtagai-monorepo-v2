#!/bin/bash
set -e

# WARNING: THIS SCRIPT PERFORMS A HISTORY REWRITE ON THE 'main' BRANCH.
# This is a DANGEROUS operation on a shared branch that will require all
# collaborators to manually recover their local branches.
#
# PROCEED ONLY IF you have coordinated with your entire team.
# The recommended tool for this task is 'git-filter-repo'.

LOG_FILE="fix_large_file.log"
echo "Optimizing git history (DANGEROUS OPERATION)..." > "$LOG_FILE"

FILE_PATH_1="libs/pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl"
FILE_PATH_2="pnkln_intelligence/knowledge_base/gucci_content_lake.jsonl"

# 1. Clean up 'main'
echo "Checking out main..." >> "$LOG_FILE"
git checkout main >> "$LOG_FILE" 2>&1

echo "Removing large file from the latest commit on main..." >> "$LOG_FILE"
# NOTE: This 'amend' approach only works if the file was added in the MOST RECENT commit.
# If the file is deeper in history, this will NOT remove it from the repository size.
git rm --cached "$FILE_PATH_1" &>> "$LOG_FILE" || true
git rm --cached "$FILE_PATH_2" &>> "$LOG_FILE" || true

echo "Amending main's HEAD commit..." >> "$LOG_FILE"
git commit --amend --no-edit >> "$LOG_FILE" 2>&1

# 2. Add to gitignore to prevent re-addition
echo "Updating .gitignore..." >> "$LOG_FILE"
# Make the .gitignore update idempotent
grep -qF "$FILE_PATH_1" .gitignore || echo "$FILE_PATH_1" >> .gitignore
grep -qF "$FILE_PATH_2" .gitignore || echo "$FILE_PATH_2" >> .gitignore
git add .gitignore >> "$LOG_FILE"
git commit -m "chore: ignore large jsonl file" >> "$LOG_FILE" 2>&1

# 3. Fix the feature branch
echo "Rebasing feature branch 'fix-ci-workflow-replacement' onto new main..." >> "$LOG_FILE"
git checkout fix-ci-workflow-replacement >> "$LOG_FILE" 2>&1
git rebase main >> "$LOG_FILE" 2>&1

echo "--------------------------------------------------------" | tee -a "$LOG_FILE"
echo "✅ HISTORY REWRITE COMPLETE. MANUAL ACTION REQUIRED:" | tee -a "$LOG_FILE"
echo "1. Force-push the 'main' branch: git push origin main --force" | tee -a "$LOG_FILE"
echo "2. Force-push this feature branch: git push origin fix-ci-workflow-replacement --force-with-lease" | tee -a "$LOG_FILE"
echo "3. NOTIFY ALL COLLABORATORS to fetch the new main and rebase their work." | tee -a "$LOG_FILE"
echo "--------------------------------------------------------" | tee -a "$LOG_FILE"

echo "Done. See $LOG_FILE and follow manual push instructions."
