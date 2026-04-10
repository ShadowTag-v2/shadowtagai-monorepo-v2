#!/bin/bash
echo "Processing PRs..." > pr_action.log

# Merge passing PRs
echo "Squash-merging PR 5..." >> pr_action.log
gh pr merge 5 --squash --delete-branch >> pr_action.log 2>&1

echo "Squash-merging PR 6..." >> pr_action.log
gh pr merge 6 --squash --delete-branch >> pr_action.log 2>&1

echo "Squash-merging PR 7..." >> pr_action.log
gh pr merge 7 --squash --delete-branch >> pr_action.log 2>&1

# Fix PR 10 (CI)
echo "Handling PR 10 replacement..." >> pr_action.log
# Create a new branch with the current workspace changes (ci.yml fix)
git checkout -b fix-ci-workflow-replacement >> pr_action.log 2>&1
git add .github/workflows/ci.yml >> pr_action.log 2>&1
git commit -m "fix(ci): add uv run pytest to summary job as requested" >> pr_action.log 2>&1
git push -u origin fix-ci-workflow-replacement >> pr_action.log 2>&1

# Create the PR
gh pr create --title "fix(ci): add uv run pytest to summary" --body "Fixes CI by adding missing step. Supercedes PR #10." >> pr_action.log 2>&1

echo "Done." >> pr_action.log
