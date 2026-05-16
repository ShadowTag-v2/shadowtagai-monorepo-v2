# third_party

## Purpose
This directory is the canonical home for intentionally vendored third-party dependencies in the monorepo.

## Policy
Use `third_party/` only when one of the following is true:
1. The dependency cannot be consumed cleanly through the normal package manager flow
2. The dependency must be patched locally
3. The dependency must be pinned and audited as source
4. The dependency is part of reproducible build infrastructure

## Rules
- Do not vendor dependencies ad hoc inside app directories.
- Do not maintain duplicate copies of the same dependency in multiple app trees.
- Prefer one version of each dependency across the monorepo where feasible.
- Every vendored dependency must include: source origin, version or commit, reason for vendoring, patch policy, and owner.

## Required metadata
Each dependency directory should contain a metadata file:

```yaml
name: example-lib
source: https://github.com/example/example-lib
version: v1.2.3
owner: @ehanc69
reason: local patch required for Bazel build
patches:
  - fix-build.patch
status: active
```

## Not allowed
- Vendored copies under `apps/.../vendor` unless explicitly approved and scheduled for migration
- Duplicate mirrors under `external_memory`, `external_repos`, backups, or recovered trees
- Using vendored code as an excuse to bypass monorepo dependency policy

## Migration rule
If a vendored dependency currently exists outside `third_party/`, it must be:
1. Moved into `third_party/`
2. Referenced from canonical build metadata
3. Removed from the old location after validation
