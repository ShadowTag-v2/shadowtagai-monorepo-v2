#Requires -Version 7.2
<#
  Bourne/Strict posture • pnklnJR Purpose • Doctrine Reasons • Army RM Brakes
  Connectors: slurm_github, slurm_github_commits, slurm_github_issues, slurm_github_pulls, slurm_notion
#>
param(
  [Parameter(Mandatory=$true)][string]$Owner,
  [Parameter(Mandatory=$true)][string]$Repo,
  [string]$Branch = "main",
  [int]$SinceDays = 14,
  [switch]$DryRun,
  [string]$NotionToken,
  [string]$NotionDatabaseId,
  [string]$OutDir = ".\.slurm\out"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Say([string]$msg, [string]$level = "INFO") {
  $ts = (Get-Date).ToString("u")
  $color = switch ($level) { "INFO" {"Cyan"} "WARN" {"Yellow"} "ERR" {"Red"} "OK" {"Green"} default {"Gray"} }
  Write-Host "[$ts][$level] $msg" -ForegroundColor $color
}

Say "Bourne posture engaged: Strict=On, pnklnJR Purpose, Doctrine Reasons, Army RM Brakes" "OK"
if ($DryRun) { Say "DryRun: no external mutations" "WARN" }

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force -Path $OutDir | Out-Null }
$OutDir = Resolve-Path $OutDir
$repoSlug = "$Owner/$Repo"
$sinceIso = (Get-Date).AddDays(-$SinceDays).ToString("s") + "Z"

function Require-Cli($name, $help){ if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { Say "$name missing. $help" "ERR"; throw "$name required" } }
Require-Cli gh "https://cli.github.com"

function Check-GitHub {
  try { gh auth status --hostname github.com | Out-Null; $u = (gh api user --jq '.login' 2>$null); if (-not $u) { throw "no user" }; Say "GitHub visible as $u" "OK"; return $true } catch { Say "GitHub NOT visible. Run gh auth login" "ERR"; return $false }
}

function slurm_github([string]$Owner,[string]$Repo){
  Say "slurm_github: $repoSlug"
  $data = @{ repo=$repoSlug; now=(Get-Date).ToString("u"); default_branch=$null; open_issues=0; open_prs=0; last_commit=$null }
  $repoJson = gh api repos/$Owner/$Repo | ConvertFrom-Json
  $data.default_branch = $repoJson.default_branch
  $data.open_issues = $repoJson.open_issues_count
  $prs = gh pr list -R $repoSlug --json number,state,createdAt | ConvertFrom-Json
  $data.open_prs = @($prs | Where-Object { $_.state -eq 'OPEN' }).Count
  $lastCommit = gh api repos/$Owner/$Repo/commits --paginate --jq '.[0]' | ConvertFrom-Json
  if ($lastCommit) { $data.last_commit = @{ sha=$lastCommit.sha; date=$lastCommit.commit.author.date; msg=$lastCommit.commit.message.Split("`n")[0]; author=$lastCommit.commit.author.name } }
  $data | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $OutDir "github_health.json") -Encoding UTF8
}

function slurm_github_commits([string]$Owner,[string]$Repo,[string]$SinceIso){
  Say "slurm_github_commits: since $SinceIso"
  $commits = gh api repos/$Owner/$Repo/commits --paginate -F since=$SinceIso --jq '[ .[] | {sha:.sha,date:.commit.author.date,author:.commit.author.name,email:.commit.author.email,msg:.commit.message} ]' | ConvertFrom-Json
  $commits | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $OutDir ("commits_{0}.json" -f $SinceIso.Replace(':','-'))) -Encoding UTF8
}

function slurm_github_issues([string]$Owner,[string]$Repo){
  Say "slurm_github_issues"
  $issues = gh issue list -R $repoSlug --state open --json number,title,author,createdAt,updatedAt,labels,url | ConvertFrom-Json
  $issues | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $OutDir "issues_open.json") -Encoding UTF8
}

function slurm_github_pulls([string]$Owner,[string]$Repo){
  Say "slurm_github_pulls"
  $prs = gh pr list -R $repoSlug --json number,title,author,createdAt,updatedAt,headRefName,baseRefName,state,mergeable,url | ConvertFrom-Json
  $prs | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $OutDir "prs_all.json") -Encoding UTF8
}

function slurm_notion([string]$Token,[string]$DatabaseId){
  if (-not $Token -or -not $DatabaseId) { Say "slurm_notion: skipped" "WARN"; return }
  $headers=@{"Authorization"="Bearer $Token";"Notion-Version"="2022-06-28";"Content-Type"="application/json"}
  $body=@{page_size=50}|ConvertTo-Json
  try{ $resp=Invoke-RestMethod -Method Post -Uri "https://api.notion.com/v1/databases/$DatabaseId/query" -Headers $headers -Body $body; $resp|ConvertTo-Json -Depth 10|Set-Content (Join-Path $OutDir ("notion_{0}.json" -f $DatabaseId)) -Encoding UTF8 } catch { Say "Notion query failed: $($_.Exception.Message)" "ERR" }
}

if (-not (Check-GitHub)) { throw "GitHub not visible" }
slurm_github $Owner $Repo
slurm_github_commits $Owner $Repo $sinceIso
slurm_github_issues $Owner $Repo
slurm_github_pulls $Owner $Repo
slurm_notion $NotionToken $NotionDatabaseId
Say "All connectors complete -> $OutDir" "OK"

