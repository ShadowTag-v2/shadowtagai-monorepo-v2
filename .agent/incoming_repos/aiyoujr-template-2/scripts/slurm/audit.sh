#!/usr/bin/env bash
set -euo pipefail
ORG=${1:-<YOUR_ORG>}
shift || true
REPOS=("pnkln-stack-api" "fastapi-services" "infra")
if [ "$#" -gt 0 ]; then REPOS=("$@"); fi
OUT="$PWD/slurm_github_scan"; mkdir -p "$OUT"

for r in "${REPOS[@]}"; do
  echo "==> $r"
  base="$OUT/$r"; mkdir -p "$base"
  gh api "repos/$ORG/$r/commits" --paginate -q '.[].{sha:.sha,author:(.commit.author.name),date:(.commit.author.date),msg:(.commit.message)}' > "$base/commits.json"
  gh pr list -R "$ORG/$r" --state all --limit 200 --json number,title,state,createdAt,mergedAt,updatedAt,author,headRefName,baseRefName > "$base/prs.json"
  gh issue list -R "$ORG/$r" --state open --limit 200 --json number,title,labels,createdAt,updatedAt,author > "$base/issues_open.json"
  gh run list -R "$ORG/$r" --limit 50 --json databaseId,headBranch,status,conclusion,createdAt,updatedAt,event > "$base/ci_runs.json"
  gh api "repos/$ORG/$r" > "$base/repo.json"
done

echo "Scan complete: $OUT"
