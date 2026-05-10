#!/bin/bash
echo "Processing Dependabot PRs (Attempt 2)..." > dependabot_ops_v2.log

# 1. Stash changes
echo "Stashing local changes..." >> dependabot_ops_v2.log
git stash push -m "Auto-stash for PR processing" >> dependabot_ops_v2.log 2>&1

for PR in 5 6 7; do
  echo ">>> Processing PR $PR" >> dependabot_ops_v2.log

  # Fetch to ensure we know about the PR branch locally if checkout fails
  gh pr fetch $PR >> dependabot_ops_v2.log 2>&1

  if gh pr checkout $PR >> dependabot_ops_v2.log 2>&1; then
      echo "Checked out PR $PR." >> dependabot_ops_v2.log

      echo "Rebasing PR $PR on main..." >> dependabot_ops_v2.log
      if git rebase main >> dependabot_ops_v2.log 2>&1; then
        echo "Rebase successful. Pushing..." >> dependabot_ops_v2.log
        git push origin HEAD --force >> dependabot_ops_v2.log 2>&1

        echo "Merging PR $PR..." >> dependabot_ops_v2.log
        # Try to merge immediately
        if gh pr merge $PR --merge --delete-branch >> dependabot_ops_v2.log 2>&1; then
          echo "PR $PR merged." >> dependabot_ops_v2.log
        else
          echo "PR $PR merge failed (checks might be pending). Enabling auto-merge." >> dependabot_ops_v2.log
          gh pr merge $PR --auto --merge --delete-branch >> dependabot_ops_v2.log 2>&1
        fi
      else
        echo "Rebase failed for PR $PR. Aborting rebase." >> dependabot_ops_v2.log
        git rebase --abort >> dependabot_ops_v2.log 2>&1
      fi
  else
      echo "Failed to check out PR $PR." >> dependabot_ops_v2.log
  fi
done

# 2. Return to original branch (if needed) and pop stash
# We assume we want to end up on main or the last branch.
git checkout main >> dependabot_ops_v2.log 2>&1
echo "Popping stash..." >> dependabot_ops_v2.log
git stash pop >> dependabot_ops_v2.log 2>&1

echo "Done handling dependabot PRs." >> dependabot_ops_v2.log
