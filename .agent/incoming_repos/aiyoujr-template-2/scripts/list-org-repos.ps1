param([Parameter(Mandatory=$true)][string]$Org)
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { Write-Error "gh CLI not found"; exit 1 }
gh repo list $Org --limit 200 --json name,defaultBranchRef,isPrivate,pushedAt,sshUrl,httpUrl | Out-File -Encoding UTF8 -FilePath "org_$Org_repos.json"
Write-Host "Wrote org_$Org_repos.json"

