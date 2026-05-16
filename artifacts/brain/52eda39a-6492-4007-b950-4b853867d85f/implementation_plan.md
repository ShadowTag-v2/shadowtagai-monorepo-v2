# Implementation Plan - Fix CI Workflow

The user has requested to apply a fix to the CI workflow, specifically referencing a GitHub Actions snippet. The snippet indicates adding a `uv run pytest` step to the `summary` job in `.github/workflows/ci.yml`.

## User Review Required

> [!WARNING]
> The requested change adds a test execution step (`uv run pytest`) to the `summary` job.
>
> 1. The `summary` job runs `if: always()`, meaning tests might run even if dependencies failed setup.
> 2. The `summary` job runs on `self-hosted`. Ensure `uv` is installed on the runner.
> 3. Typically, tests run in dedicated jobs (`python-services`, `integration-tests`), not in the summary. I will proceed as requested but please verify this intent.

## Proposed Changes

### .github/workflows

#### [MODIFY] [ci.yml](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/.github/workflows/ci.yml)

- Update the `summary` job to include the `Tests (pytest)` step at the end.
- Verify `integration-tests` job matches the provided snippet (it appears identical, but I will ensure consistency).

## Verification Plan

### Automated Tests

- Since I cannot run GitHub Actions locally, I will rely on static verification of the YAML syntax.
- I will parse the YAML to ensure no syntax errors are introduced.
