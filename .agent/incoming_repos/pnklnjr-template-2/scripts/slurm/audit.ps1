param(
  [string]$Org = "<YOUR_ORG>",
  [string[]]$Repos = @("pnkln-api","fastapi-services","infra"),
  [string]$OutDir = "$PWD/slurm_github_scan"
)

$ErrorActionPreference = "Continue"
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Write-Error "gh CLI not found. Install GitHub CLI."; exit 1 }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

foreach ($r in $Repos) {
  Write-Host "==> $r"
  $base = Join-Path $OutDir $r; New-Item -ItemType Directory -Force -Path $base | Out-Null

  gh api "repos/$Org/$r/commits" -q '.[].{sha:.sha,author:(.commit.author.name),date:(.commit.author.date),msg:(.commit.message)}' --paginate `
    | Out-File (Join-Path $base 'commits.json')

  gh pr list -R "$Org/$r" --state all --limit 200 --json number,title,state,createdAt,mergedAt,updatedAt,author,headRefName,baseRefName `
    | Out-File (Join-Path $base 'prs.json')

  gh issue list -R "$Org/$r" --state open --limit 200 --json number,title,labels,createdAt,updatedAt,author `
    | Out-File (Join-Path $base 'issues_open.json')

  gh run list -R "$Org/$r" --limit 50 --json databaseId,headBranch,status,conclusion,createdAt,updatedAt,event `
    | Out-File (Join-Path $base 'ci_runs.json')

  gh api "repos/$Org/$r" | Out-File (Join-Path $base 'repo.json')
}

Write-Host "Scan complete: $OutDir"

