# Using Git Worktrees

## When to Use

Use git worktrees when you need to work on multiple branches simultaneously:
- Testing a fix while continuing feature work
- Comparing implementations side-by-side
- Running long-running processes on one branch while working on another
- Code review without losing your working state
- Emergency hotfix while in middle of feature work

## What Are Worktrees?

**Multiple working directories for the same repository, each on different branches.**

```
Traditional approach:
your-repo/  (one working directory, switch branches)

Worktrees approach:
your-repo/          (main worktree, main branch)
your-repo-feature/  (worktree, feature branch)
your-repo-hotfix/   (worktree, hotfix branch)
```

## Basic Operations

### Create a Worktree

```bash
# Create worktree for existing branch
git worktree add ../myrepo-feature-x feature-x

# Create worktree with new branch
git worktree add ../myrepo-new-feature -b new-feature

# Create worktree from specific commit
git worktree add ../myrepo-hotfix -b hotfix abc1234
```

### List Worktrees

```bash
git worktree list

# Output:
# /Users/dev/myrepo              abc1234 [main]
# /Users/dev/myrepo-feature-x    def5678 [feature-x]
# /Users/dev/myrepo-hotfix       ghi9012 [hotfix]
```

### Remove a Worktree

```bash
# Remove worktree
git worktree remove ../myrepo-feature-x

# Or manually:
rm -rf ../myrepo-feature-x
git worktree prune
```

## Common Use Cases

### Use Case 1: Emergency Hotfix

```bash
# Scenario: You're in the middle of a feature, production breaks

# Current state: Working on feature
cd ~/myrepo
git status
# On branch feature-x
# Modified files: lots of WIP

# DON'T: Stash and switch branches (loses context)
# DO: Create worktree for hotfix

git worktree add ../myrepo-hotfix -b hotfix-urgent main

# Now work on hotfix in separate directory
cd ../myrepo-hotfix
# Fix the bug
git add .
git commit -m "Fix critical bug"
git push origin hotfix-urgent

# Return to feature work (unchanged!)
cd ../myrepo
# All your WIP still there, exactly as you left it

# Clean up hotfix worktree when done
cd ../myrepo
git worktree remove ../myrepo-hotfix
```

### Use Case 2: Code Review

```bash
# Scenario: Review PR while keeping your work intact

# Your current work
cd ~/myrepo
git status
# On branch my-feature
# Lots of uncommitted changes

# Create worktree for code review
git fetch origin
git worktree add ../myrepo-review -b review-pr-123 origin/feature-to-review

# Review in separate directory
cd ../myrepo-review
# Run tests, review code, make comments
npm test
code .

# Return to your work (unchanged)
cd ../myrepo
# All your changes still here

# Clean up when done
cd ~/myrepo
git worktree remove ../myrepo-review
```

### Use Case 3: Compare Implementations

```bash
# Scenario: Compare two different approaches

# Create worktree for approach A
git worktree add ../myrepo-approach-a -b approach-a

# Create worktree for approach B
git worktree add ../myrepo-approach-b -b approach-b

# Implement approach A
cd ../myrepo-approach-a
# ... implement ...
npm test

# Implement approach B
cd ../myrepo-approach-b
# ... implement ...
npm test

# Compare side-by-side
cd ..
diff -r myrepo-approach-a/src myrepo-approach-b/src

# Or open both in editors for visual comparison
code myrepo-approach-a myrepo-approach-b

# Keep the better one, delete the other
git worktree remove ../myrepo-approach-b
cd myrepo-approach-a
git push origin approach-a
```

### Use Case 4: Long-Running Processes

```bash
# Scenario: Run build/tests on one branch while working on another

# Main work
cd ~/myrepo
# On branch main

# Create worktree for long test run
git worktree add ../myrepo-tests feature-x

# Start long-running tests in that worktree
cd ../myrepo-tests
npm run test:integration &  # Runs in background

# Continue working on main branch
cd ../myrepo
# Work continues uninterrupted while tests run

# Check test results later
cd ../myrepo-tests
# See results
```

### Use Case 5: Parallel Development

```bash
# Scenario: Work on multiple features in parallel

# Main worktree
cd ~/myrepo  # main branch

# Feature A worktree
git worktree add ../myrepo-feature-a -b feature-a

# Feature B worktree
git worktree add ../myrepo-feature-b -b feature-b

# Feature C worktree
git worktree add ../myrepo-feature-c -b feature-c

# Now switch between features without git checkout
# Just switch directories!

cd ../myrepo-feature-a  # Work on feature A
cd ../myrepo-feature-b  # Work on feature B
cd ../myrepo-feature-c  # Work on feature C

# Each has its own:
# - Working directory
# - Uncommitted changes
# - Running processes
# - Open editor state
```

## Best Practices

### 1. Naming Convention

```bash
# Use consistent naming
<repo>-<branch-name>

# Examples:
myrepo-feature-auth
myrepo-bugfix-login
myrepo-hotfix-security
myrepo-review-pr-123

# This makes it easy to identify:
ls -la ../ | grep myrepo
```

### 2. Location Strategy

```bash
# Keep worktrees together
~/projects/
  myrepo/           # main worktree
  myrepo-feature-a/ # additional worktree
  myrepo-feature-b/ # additional worktree
  myrepo-hotfix/    # additional worktree

# NOT scattered:
~/projects/myrepo/
~/Desktop/fix/
~/Documents/test/
```

### 3. Clean Up Regularly

```bash
# List worktrees
git worktree list

# Remove finished worktrees
git worktree remove ../myrepo-feature-x

# Prune deleted worktrees
git worktree prune

# List all again to verify
git worktree list
```

### 4. One Branch Per Worktree

```bash
# DON'T: Check out same branch in multiple worktrees
# (Git prevents this anyway)

# DO: One branch per worktree
git worktree add ../myrepo-feature-a -b feature-a  ✓
git worktree add ../myrepo-feature-b -b feature-b  ✓
```

## Advanced Patterns

### Pattern 1: Main + Multiple Features

```bash
# Structure:
myrepo/          → main branch (stable, for quick fixes)
myrepo-feat-a/   → feature A (in progress)
myrepo-feat-b/   → feature B (in progress)
myrepo-review/   → for code reviews (ephemeral)

# Workflow:
# - Main worktree stays clean on main branch
# - Feature worktrees for active development
# - Review worktree for PR reviews (recreate as needed)
```

### Pattern 2: Development + Staging + Production

```bash
# Structure:
myrepo-dev/    → develop branch (active development)
myrepo-stage/  → staging branch (testing)
myrepo-prod/   → production branch (emergencies only)

# Workflow:
# - Work in dev worktree
# - Test in stage worktree
# - Emergency fixes in prod worktree
```

### Pattern 3: Experiment Freely

```bash
# Create experimental worktree
git worktree add ../myrepo-experiment -b experiment

cd ../myrepo-experiment
# Try crazy refactoring
# Break everything
# It's fine!

# If experiment fails:
cd ../myrepo
git worktree remove ../myrepo-experiment
git branch -D experiment

# If experiment succeeds:
cd ../myrepo-experiment
git push origin experiment
# Create PR
```

## Worktrees vs. Stashing

### When to Use Stash

```bash
# Quick branch switch, coming back soon
git stash
git checkout other-branch
# ... quick work ...
git checkout original-branch
git stash pop
```

### When to Use Worktrees

```bash
# Working on multiple branches for extended periods
# Each branch needs its own working state
# Don't want to lose context with stash/pop
```

## Troubleshooting

### Issue: Can't Remove Worktree

```bash
# Error: worktree contains modified or untracked files

# Option 1: Force remove (loses changes)
git worktree remove --force ../myrepo-feature

# Option 2: Clean up first
cd ../myrepo-feature
git add .
git commit -m "Save work"
cd ../myrepo
git worktree remove ../myrepo-feature
```

### Issue: Worktree Shows Wrong Branch

```bash
# List worktrees to verify
git worktree list

# Move to worktree and check
cd ../myrepo-worktree
git branch
git checkout correct-branch
```

### Issue: Accidentally Deleted Worktree Directory

```bash
# Prune removed worktrees
git worktree prune

# Verify it's gone
git worktree list
```

## Cheat Sheet

```bash
# Create worktree
git worktree add <path> -b <branch>

# Create from existing branch
git worktree add <path> <existing-branch>

# List worktrees
git worktree list

# Remove worktree
git worktree remove <path>

# Prune deleted worktrees
git worktree prune

# Remove worktree (force)
git worktree remove --force <path>
```

## Benefits

### ✅ Context Preservation
```
No more:
- git stash
- git checkout other-branch
- "Wait, where was I?"
- git checkout original-branch
- git stash pop
- "What was I doing?"

Instead:
- cd ../myrepo-other-branch
- Do work
- cd ../myrepo-original-branch
- Continue exactly where you left off
```

### ✅ Parallel Work
```
Work on multiple features simultaneously
Each feature in its own directory
No branch switching overhead
```

### ✅ Safe Experimentation
```
Try risky refactoring in separate worktree
Main work unaffected
Delete experiment if it fails
Merge if it succeeds
```

### ✅ Clean Code Reviews
```
Review PRs without disrupting your work
Run tests in review worktree
Your work stays untouched
```

## Remember

- **Worktrees = Multiple working directories**
- **One branch per worktree**
- **Clean up when done**
- **Use for parallel work**
- **Keep worktrees together**

**Worktrees eliminate context switching pain.**
