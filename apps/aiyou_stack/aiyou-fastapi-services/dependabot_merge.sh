#!/bin/bash
echo "Processing Dependabot PRs..." > dependabot_ops.log

for PR in 5 6 7; do
  echo ">>> Processing PR $PR" >> dependabot_ops.log
  gh pr checkout $PR >> dependabot_ops.log 2>&1

  echo "Rebasing PR $PR on main..." >> dependabot_ops.log
  if git rebase main >> dependabot_ops.log 2>&1; then
    echo "Rebase successful. Pushing..." >> dependabot_ops.log
    git push origin HEAD --force >> dependabot_ops.log 2>&1

    echo "Merging PR $PR..." >> dependabot_ops.log
    # Try to merge immediately
    if gh pr merge $PR --merge --delete-branch >> dependabot_ops.log 2>&1; then
      echo "PR $PR merged." >> dependabot_ops.log
    else
      echo "PR $PR merge failed (checks might be pending). Enabling auto-merge." >> dependabot_ops.log
      gh pr merge $PR --auto --merge --delete-branch >> dependabot_ops.log 2>&1
    fi
  else
    echo "Rebase failed for PR $PR. Aborting rebase." >> dependabot_ops.log
    git rebase --abort >> dependabot_ops.log 2>&1
  fi
done

echo "Done handling dependabot PRs." >> dependabot_ops.log
