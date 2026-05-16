param(
  [ValidateSet("Baseline","Snapshot","Nightly")] [string]$Mode = "Snapshot",
  [string]$Owner = $env:GITHUB_OWNER,
  [string]$Repo  = $env:GITHUB_REPO,
  [int]$CpuSampleSeconds = 2,
  [double]$DriftPct = 20.0
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Resolve-Path (Join-Path $here "..")
$store = Join-Path $root "ops/.telemetry"
New-Item -ItemType Directory -Force -Path $store | Out-Null

$baselineFile = Join-Path $store "baseline.json"
$stamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$snapshotFile = Join-Path $store "snapshot_$stamp.json"
$reportFile = Join-Path $store "report_$stamp.md"

$Targets = @(
  @{ Name="cursor.exe";  Friendly="Cursor" },
  @{ Name="chatgpt.exe"; Friendly="ChatGPT" },
  @{ Name="node.exe";    Friendly="Node.js" }
)

function Get-ProcSample {
  param([string]$ImageName, [int]$seconds = 2)

  $procs = Get-Process | Where-Object { $_.ProcessName -ieq ($ImageName -replace ".exe$","") }
  if (-not $procs) { return @{ found=$false } }

  $cores = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
  $t0 = @{}
  foreach ($p in $procs) { $t0[$p.Id] = $p.TotalProcessorTime.TotalMilliseconds }

  Start-Sleep -Seconds $seconds

  $procs2 = Get-Process | Where-Object { $_.Id -in $t0.Keys }
  $cpuPct = 0.0
  $rssMB  = 0.0
  foreach ($p in $procs2) {
    $t1 = $p.TotalProcessorTime.TotalMilliseconds
    $delta = [math]::Max(0, $t1 - $t0[$p.Id])
    $cpuPct += 100.0 * ($delta / (1000.0 * $seconds * $cores))
    $rssMB  += [math]::Round($p.WorkingSet64 / 1MB, 1)
  }

  return @{ found=$true; cpuPct=[math]::Round($cpuPct,1); rssMB=$rssMB }
}

function Write-Json($obj,$path){ $obj | ConvertTo-Json -Depth 6 | Set-Content -Path $path -Encoding UTF8 }
function Load-Json($path){ if (Test-Path $path){ (Get-Content $path -Raw | ConvertFrom-Json) } else { $null } }

function Gh-Visible {
  try { $null = (gh auth status 2>&1) } catch { return @{ ok=$false; reason="gh not installed or not authenticated" } }
  if ($LASTEXITCODE -ne 0) { return @{ ok=$false; reason="gh not authenticated" } }
  if (-not $Owner -or -not $Repo) { return @{ ok=$false; reason="Owner/Repo not set" } }
  try { $null = gh api repos/$Owner/$Repo --silent 2>&1; if ($LASTEXITCODE -ne 0) { return @{ ok=$false; reason="Repo not visible" } } } catch { return @{ ok=$false; reason="Repo ping failed" } }
  return @{ ok=$true; reason="ok" }
}

# take measurement
$measure = @{}
foreach ($t in $Targets){ $measure[$t.Friendly] = Get-ProcSample -ImageName $t.Name -seconds $CpuSampleSeconds }

if ($Mode -eq "Baseline"){ Write-Json $measure $baselineFile; "[Baseline captured] -> $baselineFile"; exit 0 }

Write-Json $measure $snapshotFile
$baseline = Load-Json $baselineFile
$drifts = @()
if ($baseline -ne $null){
  foreach ($k in $measure.Keys){
    $cur = $measure[$k]; $base = $baseline.$k
    if ($cur.found -and $base){
      $cpuDrift = if ($base.cpuPct -gt 0) { 100.0*($cur.cpuPct - $base.cpuPct)/$base.cpuPct } else { 0 }
      $memDrift = if ($base.rssMB  -gt 0) { 100.0*($cur.rssMB  - $base.rssMB )/$base.rssMB  } else { 0 }
      $drifts += @{ name=$k; cpu=$cur.cpuPct; memMB=$cur.rssMB; baseCpu=$base.cpuPct; baseMemMB=$base.rssMB; cpuDrift=[math]::Round($cpuDrift,1); memDrift=[math]::Round($memDrift,1) }
    } else { $drifts += @{ name=$k; missing=$true } }
  }
}

$gh = Gh-Visible

$lines = @()
$lines += "# Resource Report ($stamp)"
$lines += ""
$lines += "- GitHub visibility: **" + ($(if($gh.ok){"OK"}else{"UNAVAILABLE"})) + "** (`$($gh.reason)`)"
$lines += "- Baseline present: " + $(if($baseline){ "yes" } else { "no (set one with -Mode Baseline)" })
$lines += ""
$lines += "## Measurements"
foreach ($d in $drifts){
  if ($d.missing){ $lines += "- **$($d.name)**: process not found ❌" }
  else { $lines += "- **$($d.name)**: CPU $($d.cpu)% (base $($d.baseCpu)%) Δ $($d.cpuDrift)%,  RAM $($d.memMB) MB (base $($d.baseMemMB) MB) Δ $($d.memDrift)%" }
}
$linesText = $lines -join "`r`n"
Set-Content -Path $reportFile -Value $linesText -Encoding UTF8

if ($Mode -eq "Nightly"){
  if (-not $gh.ok){ Write-Host "[ALERT] GitHub not visible: $($gh.reason)"; exit 10 }
}

Write-Host "Saved:`n  - $snapshotFile`n  - $reportFile"
if (-not $gh.ok){ Write-Host "[NOTICE] GitHub UNAVAILABLE: $($gh.reason)" }

