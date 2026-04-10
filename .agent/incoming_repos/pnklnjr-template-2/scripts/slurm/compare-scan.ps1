param(
  [Parameter(Mandatory=$true)][string]$Before,
  [Parameter(Mandatory=$true)][string]$After,
  [string]$Repo = "pnkln-api"
)

function Load-Folder($path){
  Get-ChildItem -Path $path -Recurse -Filter *.json | ForEach-Object {
    [pscustomobject]@{ name=$_.FullName; json = Get-Content $_.FullName -Raw | ConvertFrom-Json }
  }
}

$bRepo = Join-Path $Before $Repo
$aRepo = Join-Path $After  $Repo

$kpi = [pscustomobject]@{
  prs_open_before = if (Test-Path (Join-Path $bRepo 'prs.json')) { (Get-Content (Join-Path $bRepo 'prs.json') -Raw | ConvertFrom-Json | Where-Object { $_.state -eq 'OPEN' }).Count } else { $null }
  prs_open_after  = if (Test-Path (Join-Path $aRepo 'prs.json')) { (Get-Content (Join-Path $aRepo 'prs.json') -Raw | ConvertFrom-Json | Where-Object { $_.state -eq 'OPEN' }).Count } else { $null }
}

$kpi | Format-List

