# Finishing a Development Branch

## When to Use

When your feature branch is complete and you need to decide how to integrate it back to the main branch.

## The Decision Tree

```
Is branch ready?
├─ No → Continue development
└─ Yes
    ├─ Merge to main directly? (for simple, clean branches)
    ├─ Squash and merge? (for messy commit history)
    ├─ Rebase and merge? (for linear history)
    └─ Create Pull Request? (for review/approval)
```

## Pre-Finish Checklist

Before merging/creating PR:

```markdown
## Completeness
- [ ] All features implemented
- [ ] All tests passing
- [ ] No TODOs left incomplete
- [ ] Code reviewed (self-review at minimum)
- [ ] Documentation updated

## Code Quality
- [ ] No debug statements (console.log, print, debugger)
- [ ] No commented-out code
- [ ] No linter errors
- [ ] Follows project conventions
- [ ] Performance is acceptable

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Edge cases tested
- [ ] No regressions

## Integration
- [ ] Up to date with main branch
- [ ] Merge conflicts resolved
- [ ] Tests still pass after merge/rebase
- [ ] CI/CD passes

## Communication
- [ ] Team aware of changes
- [ ] Breaking changes documented
- [ ] Migration guide if needed
- [ ] CHANGELOG updated
```

## Integration Strategies

### Strategy 1: Merge Commit

**When to use:** Preserving full history is important

```bash
# Update your branch
git checkout feature-branch
git fetch origin
git merge origin/main

# Resolve any conflicts
# ... fix conflicts ...
git add .
git commit -m "Merge main into feature-branch"

# Run tests
npm test

# Merge to main
git checkout main
git merge feature-branch

# Push
git push origin main

# Delete branch
git branch -d feature-branch
git push origin --delete feature-branch
```

**Result:**
```
* Merge branch 'feature-branch' into main
|\
| * Commit 3
| * Commit 2
| * Commit 1
|/
* Previous main commit
```

**Pros:**
- Complete history preserved
- Easy to revert entire feature
- Shows when feature was integrated

**Cons:**
- History can get messy with many features
- Extra merge commits

### Strategy 2: Squash and Merge

**When to use:** Feature branch has messy commits, want clean history

```bash
# Update your branch
git checkout feature-branch
git fetch origin
git rebase origin/main

# Squash commits
git reset --soft origin/main
git add .
git commit -m "Add export feature

- CSV export service
- Export API endpoint
- Export UI button
- Comprehensive tests

Closes #123"

# Push (force if already pushed)
git push --force origin feature-branch

# Merge to main
git checkout main
git merge feature-branch --ff-only

# Push
git push origin main

# Delete branch
git branch -d feature-branch
git push origin --delete feature-branch
```

**Result:**
```
* Add export feature (single commit)
* Previous main commit
```

**Pros:**
- Clean, linear history
- One commit per feature
- Easy to revert
- Easy to understand history

**Cons:**
- Loses detailed commit history
- Can't see incremental progress

### Strategy 3: Rebase and Merge

**When to use:** Want clean commits but preserve incremental history

```bash
# Update your branch with rebase
git checkout feature-branch
git fetch origin
git rebase origin/main

# Resolve conflicts if any
# ... fix conflicts ...
git add .
git rebase --continue

# Clean up commits if needed (interactive rebase)
git rebase -i origin/main

# In editor:
# pick abc1234 Add CSV service
# squash def5678 Fix typo
# pick ghi9012 Add export endpoint
# squash jkl3456 Add tests

# Force push (rebase rewrites history)
git push --force origin feature-branch

# Run tests
npm test

# Merge to main (fast-forward)
git checkout main
git merge feature-branch --ff-only

# Push
git push origin main

# Delete branch
git branch -d feature-branch
git push origin --delete feature-branch
```

**Result:**
```
* Add export endpoint tests
* Add export endpoint
* Add CSV service
* Previous main commit
```

**Pros:**
- Linear history
- Clean, meaningful commits
- Shows incremental progress
- No merge commits

**Cons:**
- Rewrites history (force push needed)
- More complex than simple merge
- Can be confusing for beginners

### Strategy 4: Pull Request (Recommended for Teams)

**When to use:** Team requires code review, CI/CD checks

```bash
# Update your branch
git checkout feature-branch
git fetch origin
git rebase origin/main  # or merge, depending on team preference

# Push to remote
git push origin feature-branch

# Create PR (using GitHub CLI)
gh pr create \
  --title "Add CSV export feature" \
  --body "$(cat <<EOF
## Summary
Adds CSV export functionality to user list page.

## Changes
- CSV export service with special character handling
- Export API endpoint
- Export button in UI
- Comprehensive test coverage

## Testing
- All tests pass (158/158)
- Manual testing in Chrome, Firefox, Safari
- Performance tested with 1000 records

## Closes
#123
EOF
)"

# Wait for review and approval
# Address review comments
# ... make changes ...
git add .
git commit -m "Address review feedback"
git push origin feature-branch

# After approval, merge via GitHub
# (or via command line)
gh pr merge --squash  # or --merge, or --rebase
```

## Cleaning Up After Merge

### Local Cleanup

```bash
# Delete local branch
git branch -d feature-branch

# Update main
git checkout main
git pull origin main

# Prune deleted remote branches
git fetch --prune

# List remaining branches
git branch -a
```

### Remote Cleanup

```bash
# Delete remote branch
git push origin --delete feature-branch

# Or via GitHub UI/CLI
gh pr close 123
```

## Handling Common Scenarios

### Scenario 1: Merge Conflicts

```bash
# During merge/rebase
git merge origin/main
# CONFLICT in app/api/routes/users.py

# Fix conflicts manually
# Edit app/api/routes/users.py
# Remove conflict markers: <<<<<<<, =======, >>>>>>>

# Mark as resolved
git add app/api/routes/users.py

# Continue merge
git commit

# Or continue rebase
git rebase --continue

# Verify tests still pass
npm test
```

### Scenario 2: Failing CI

```bash
# CI fails after pushing

# Check CI logs
gh pr checks 123

# Fix the issue locally
# ... make fix ...
git add .
git commit -m "Fix failing CI tests"
git push origin feature-branch

# CI runs again automatically
```

### Scenario 3: Need to Update PR

```bash
# PR needs changes after review

# Make changes
# ... edit files ...
git add .
git commit -m "Address review feedback: improve error handling"

# Push
git push origin feature-branch

# PR updates automatically
```

### Scenario 4: Long-Running Branch

```bash
# Branch has diverged significantly from main

# Option 1: Rebase (cleaner)
git checkout feature-branch
git fetch origin
git rebase origin/main
# ... resolve conflicts ...
git push --force origin feature-branch

# Option 2: Merge (safer)
git checkout feature-branch
git fetch origin
git merge origin/main
# ... resolve conflicts ...
git push origin feature-branch

# Run full test suite
npm test

# May need multiple rounds of conflict resolution
```

## Decision Matrix

| Situation | Recommended Strategy |
|-----------|---------------------|
| Solo developer, feature complete | Squash and merge |
| Team project, needs review | Pull Request |
| Want to preserve commit history | Rebase and merge |
| Quick fix, single commit | Merge commit (fast-forward) |
| Complex feature, many commits | Pull Request with squash |
| Experimental branch | Squash and merge |
| Hotfix to production | Pull Request (expedited review) |

## Branch Lifecycle

```
1. Create branch
   git checkout -b feature-x

2. Develop
   - Implement feature
   - Write tests
   - Commit regularly

3. Keep updated
   git fetch origin
   git rebase origin/main  # or merge

4. Finish development
   - Complete checklist
   - Self-review
   - Update docs

5. Prepare for merge
   - Clean up commits (if needed)
   - Final rebase/merge with main
   - Run full test suite

6. Integrate
   - Create PR (team) or merge directly (solo)
   - Address feedback if PR
   - Merge to main

7. Clean up
   - Delete branch locally
   - Delete branch remotely
   - Update local main

8. Verify
   - Check main branch
   - Verify CI passes
   - Verify deploy successful
```

## Quick Checklist

```markdown
Before merging:
- [ ] Feature complete
- [ ] All tests pass
- [ ] No TODOs
- [ ] Documentation updated
- [ ] Up to date with main
- [ ] Self-reviewed
- [ ] CI passes (if applicable)

After merging:
- [ ] Branch deleted locally
- [ ] Branch deleted remotely
- [ ] Main branch updated locally
- [ ] CI/CD successful
- [ ] Verified in staging/production
```

## Remember

- **Finish completely** - Don't merge half-done work
- **Clean up history** - Make it readable for others
- **Test thoroughly** - After every merge/rebase
- **Delete branches** - Keep repo clean
- **Verify integration** - Check CI and deployments

**A finished branch is: complete, tested, reviewed, merged, and deleted.**
