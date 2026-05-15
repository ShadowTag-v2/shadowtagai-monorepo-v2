# Rule 52 — GitHub-First Protocol

## Purpose
Force every agent session to maintain continuous awareness of GitHub repository state.
This rule applies to Claude Code CLI, Antigravity IDE, and any MCP-connected agent.

## Mandatory Pre-Flight (Every Session)

Before ANY file write, terminal command, or implementation plan:

1. **Check remote state**: Run `git fetch origin --prune` and `git status` to verify branch alignment.
2. **Check open PRs**: Run `gh pr list --state open --limit 10` to see active work.
3. **Check open issues**: Run `gh issue list --state open --limit 10 --label "priority:high"` to see blockers.
4. **Check CI status**: Run `gh run list --limit 5` to verify pipeline health.

## Mandatory Pre-Tool-Use Checks

Before executing any multi-step implementation:

1. **Verify no conflicting PRs** touch the same files you plan to edit.
2. **Verify the target branch** is up-to-date with remote.
3. **Verify CI is green** on the base branch.

## GitHub Context Injection

Every implementation plan MUST include:
- Current branch and its relationship to `main`
- Any open PRs that touch overlapping files
- Any open issues tagged for the current sprint
- Latest CI/CD run status

## Tool Priority

When GitHub context is needed:
1. **FIRST**: Use `gh` CLI (authenticated via GitHub App PEM)
2. **SECOND**: Use GitHub MCP server tools (if available)
3. **LAST**: Use `git` commands for local-only state

## Auto-Commit Protocol

After completing any task:
1. Stage changes: `git add -A`
2. Run pre-commit hooks: `pre-commit run --all-files`
3. Commit with conventional format
4. Push to remote
5. If changes warrant review: create a PR via `gh pr create`

## Continuous Sync

- Run `git fetch origin` every 15 minutes during active sessions
- Alert if remote has new commits on the working branch
- Alert if a new PR is opened that conflicts with current work

## Anti-Patterns (PROHIBITED)

- Writing code without checking `git status` first
- Committing without verifying CI status
- Creating a PR without checking for duplicate/conflicting PRs
- Ignoring open issues tagged with the current feature area
- Working on `main` directly for any feature work
