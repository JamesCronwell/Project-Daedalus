# Crusader's daily backup (BRIEF 02): restic onto Google Drive for desktop (G:, streamed), two repositories.
#   plumbing: ~/.claude, the desktop app's MCP config, C:\Users\User\Scripts, the non-git folders under C:\- Tools\- LLM
#             -> G:\My Drive\daedalus-backups\restic          (exclusions: tools\backup-exclude.txt, never named here)
#   saves:    KSP_Calypso\saves, KSP_Reborn\saves, one snapshot each
#             -> G:\My Drive\### Games\KSP\-- BACKUP --\saves-restic
# Run by the scheduled task (tools\backup-task.ps1), or by hand:
#   powershell -NoProfile -File tools\backup.ps1 [-SkipSaves] [-DryRun]   the daily run (-DryRun: decisions only)
#   powershell -NoProfile -File tools\backup.ps1 -CheckExcludes           dry-run the plumbing set; count what each
#                                                                         exclude line would still let in (must be 0)
#   powershell -NoProfile -File tools\backup.ps1 -Init                    initialise both repositories (owner's yes)
#   & '<abs path>\tools\backup.ps1' -Repo saves -Restic @('snapshots')   any restic command on one repository (from a
#                                                                         PowerShell prompt: -File can't pass --flags)
# The password: the owner stores it once with tools\backup-setpass.ps1 (DPAPI, this Windows user only). This script
# decrypts it into its own process's environment and never prints it. Nothing in tools\ prints it.
# Skip rules for the saves, checked right before each saves snapshot: -SkipSaves; the flag file $StateDir\skip-ksp-saves
# (a Calypso deploy window); a KSP_x64 process (from that install: its saves only; from elsewhere: both).
# Alerts (ntfy, topic bastion): a failure; no good plumbing run for 36 h (a missed run, seen by the next one); a saves
# folder with no snapshot for 3 days. The log: $StateDir\backup.log.
param(
    [switch]$SkipSaves,
    [switch]$DryRun,
    [switch]$CheckExcludes,
    [switch]$Init,
    [ValidateSet('plumbing', 'saves')][string]$Repo,
    [string[]]$Restic,
    [string]$StateDir = (Join-Path $env:LOCALAPPDATA 'Daedalus'),
    [string]$Ntfy = 'https://crusade-bastion.taild871d5.ts.net:2586/bastion'
)
$ErrorActionPreference = 'Stop'
$Repos = @{
    plumbing = 'G:\My Drive\daedalus-backups\restic'
    saves    = 'G:\My Drive\### Games\KSP\-- BACKUP --\saves-restic'
}
$Plumbing = @(
    (Join-Path $env:USERPROFILE '.claude'),
    (Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'),
    'C:\Users\User\Scripts',
    'C:\- Tools\- LLM\Olympus',
    'C:\- Tools\- LLM\Atlas',
    'C:\- Tools\- LLM\Hephaestus\Claude_UI_UX',
    'C:\- Tools\- LLM\Hephaestus\EU5'
)
$Ksp = 'F:\Steam_Modded_Variants'
$Saves = [ordered]@{ 'calypso-saves' = 'KSP_Calypso'; 'reborn-saves' = 'KSP_Reborn' }
$ExcludeFile = Join-Path $PSScriptRoot 'backup-exclude.txt'
$PassFile = Join-Path $StateDir 'restic-password.dpapi'
$LogFile = Join-Path $StateDir 'backup.log'
$HostName = 'eternal-crusade'
$Keep = @('--keep-daily', '14', '--keep-weekly', '8')

function Log([string]$msg) {   # to the log and the console, never into a function's return value
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -LiteralPath $LogFile -Value $line -Encoding utf8
    Write-Host $line
}

function Alert([string]$title, [string]$msg, [string]$priority = 'high') {
    Log "ALERT: $title - $msg"
    if ($DryRun) { return }
    try {
        Invoke-RestMethod -Method Post -Uri $Ntfy -Body $msg -TimeoutSec 15 `
            -Headers @{ Title = "Crusader backup: $title"; Priority = $priority; Tags = 'floppy_disk' } | Out-Null
    } catch { Log "ntfy failed: $($_.Exception.Message)" }
}

function Stamp([string]$name) { Join-Path $StateDir "last-ok-$name.txt" }

function Age([string]$name) {   # hours since the last good run of $name, or since the first run if it never had one
    $f = Stamp $name
    if (-not (Test-Path -LiteralPath $f)) { $f = Stamp 'first-run' }
    ((Get-Date) - [datetime]::Parse((Get-Content -LiteralPath $f -TotalCount 1))).TotalHours
}

function Mark([string]$name) { Set-Content -LiteralPath (Stamp $name) -Value (Get-Date -Format 'o') -Encoding utf8 }

function Unlock-Password {
    if (-not (Test-Path -LiteralPath $PassFile)) { throw "no password file at $PassFile (the owner runs tools\backup-setpass.ps1)" }
    $sec = Get-Content -LiteralPath $PassFile -TotalCount 1 | ConvertTo-SecureString
    $env:RESTIC_PASSWORD = [Net.NetworkCredential]::new('', $sec).Password
}

function Invoke-Restic([string]$repo, [string[]]$resticArgs) {   # returns restic's exit code; its output goes to the log
    $env:RESTIC_REPOSITORY = $Repos[$repo]
    $ErrorActionPreference = 'Continue'   # 5.1 turns a native stderr line into an error record under 2>&1
    $out = & $script:ResticExe @resticArgs 2>&1
    $code = $LASTEXITCODE
    foreach ($l in $out) { Log ("  [$repo] " + "$l".TrimEnd()) }
    $code
}

function Ksp-Blocker([string]$install) {   # why the saves of $install must be skipped now, or $null
    if ($SkipSaves) { return '-SkipSaves' }
    if (Test-Path -LiteralPath (Join-Path $StateDir 'skip-ksp-saves')) { return 'the skip-ksp-saves flag file' }
    foreach ($p in @(Get-Process -Name 'KSP_x64' -ErrorAction SilentlyContinue)) {
        $path = $null
        try { $path = $p.Path } catch {}
        if (-not $path) { return "KSP_x64 (pid $($p.Id), path unknown)" }
        if ($path -like (Join-Path $Ksp "$install\*")) { return "KSP_x64 from $install (pid $($p.Id))" }
        if (-not ($path -like "$Ksp\*")) { return "KSP_x64 from elsewhere: $path" }
    }
    $null
}

New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
$script:ResticExe = (Get-Command restic -ErrorAction SilentlyContinue).Source
$failed = $false
try {
    if (-not $ResticExe -and -not $DryRun) { throw 'restic is not installed (winget install restic.restic)' }
    if (-not (Test-Path -LiteralPath 'G:\My Drive')) { throw 'G:\My Drive is missing: is Drive for desktop running?' }
    $env:RESTIC_PROGRESS_FPS = '0.0167'   # a progress line a minute at most, if any

    if ($Restic) {
        if (-not $Repo) { throw '-Restic needs -Repo plumbing|saves' }
        Unlock-Password
        $env:RESTIC_REPOSITORY = $Repos[$Repo]
        $ErrorActionPreference = 'Continue'
        & $ResticExe @Restic
        exit $LASTEXITCODE
    }

    if ($Init) {
        Unlock-Password
        foreach ($r in 'plumbing', 'saves') {
            if (Test-Path -LiteralPath (Join-Path $Repos[$r] 'config')) { Log "init $r`: already initialised"; continue }
            $code = Invoke-Restic $r @('init')
            if ($code -ne 0) { throw "restic init $r failed ($code)" }
            Log "init $r`: done"
        }
        exit 0
    }

    if ($CheckExcludes) {
        Unlock-Password
        $env:RESTIC_REPOSITORY = $Repos['plumbing']
        $ErrorActionPreference = 'Continue'
        # each would-be-saved entry, normalised to /C/x/y whichever form restic prints (C:\x\y or /C/x/y)
        $lines = & $ResticExe backup --dry-run -vv --host $HostName --iexclude-file $ExcludeFile @Plumbing 2>&1 |
            ForEach-Object { "$_" } | Where-Object { $_ -match '^\s*(new|modified|unchanged)\s' } |
            ForEach-Object { ($_ -replace '\\', '/') -replace '\s/?([A-Za-z]):?/', ' /$1/' }
        if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 3) { throw "dry run failed ($LASTEXITCODE)" }
        $ErrorActionPreference = 'Stop'
        $leaks = 0
        foreach ($pat in Get-Content -LiteralPath $ExcludeFile) {
            if ($pat -match '^\s*(#|$)') { continue }
            $p = [Environment]::ExpandEnvironmentVariables(($pat.Trim() -replace '\$(\w+)', '%$1%')).TrimEnd('\')
            $rp = '/' + ($p -replace '^([A-Za-z]):', '$1' -replace '\\', '/')
            $rx = '(?i)\s' + [regex]::Escape($rp) + '($|[/,\s])'
            $n = @($lines | Where-Object { $_ -match $rx }).Count
            $leaks += $n
            'exclude line ...\{0}: {1} would-be-saved entries match' -f ($pat.Trim() -replace '^.*\\', ''), $n
        }
        $claude = @($lines | Where-Object { $_ -match '(?i)/\.claude/' }).Count
        "would save $(@($lines).Count) entries ($claude under .claude); $leaks match an exclude line (must be 0)"
        if (@($lines).Count -eq 0 -or $claude -eq 0) { 'nothing parsed: the check proves nothing, read restic''s output format'; exit 2 }
        exit ([int]($leaks -ne 0))
    }

    # --- the daily run
    Log "run start$(if ($DryRun) { ' (dry run)' })$(if ($SkipSaves) { ' -SkipSaves' })"
    if (-not (Test-Path -LiteralPath (Stamp 'first-run'))) { if (-not $DryRun) { Mark 'first-run' } }
    elseif ((Age 'plumbing') -gt 36) { Alert 'missed runs' ("no good plumbing backup for {0:N0} h" -f (Age 'plumbing')) }
    if (-not $DryRun) {
        Unlock-Password
        foreach ($r in 'plumbing', 'saves') {
            if (-not (Test-Path -LiteralPath (Join-Path $Repos[$r] 'config'))) { throw "repository $r is not initialised: $($Repos[$r])" }
        }
    }

    # plumbing
    if ($DryRun) { Log 'plumbing: would back up' }
    else {
        $code = Invoke-Restic 'plumbing' (@('backup', '--host', $HostName, '--tag', 'plumbing', '--iexclude-file', $ExcludeFile) + $Plumbing)
        if ($code -eq 0 -or $code -eq 3) {   # 3: snapshot made, some files unreadable (open in a session)
            Mark 'plumbing'; Log "plumbing: snapshot made$(if ($code -eq 3) { ' (some files unreadable, see above)' })"
        } else { $failed = $true; Alert 'plumbing failed' "restic backup exit $code (see $LogFile)" }
    }

    # saves, one snapshot per install
    foreach ($tag in $Saves.Keys) {
        $install = $Saves[$tag]
        $why = Ksp-Blocker $install
        if ($why) {
            Log "$tag`: skipped ($why)"
            if ((Test-Path -LiteralPath (Stamp 'first-run')) -and (Age $tag) -gt 72) {
                Alert "$tag stale" ("no snapshot for {0:N0} h; skipped today: {1}" -f (Age $tag), $why) 'default'
            }
            continue
        }
        if ($DryRun) { Log "$tag`: would back up"; continue }
        $code = Invoke-Restic 'saves' @('backup', '--host', $HostName, '--tag', $tag, (Join-Path $Ksp "$install\saves"))
        if ($code -eq 0) { Mark $tag; Log "$tag`: snapshot made" }
        else { $failed = $true; Alert "$tag failed" "restic backup exit $code (see $LogFile)" }
    }

    # retention and checks: forget daily, prune and a data sample on Sundays
    if (-not $DryRun) {
        $sunday = (Get-Date).DayOfWeek -eq 'Sunday'
        foreach ($r in 'plumbing', 'saves') {
            $f = @('forget', '--host', $HostName, '--group-by', 'host,tags') + $Keep
            if ($sunday) { $f += '--prune' }
            $code = Invoke-Restic $r $f
            if ($code -ne 0) { $failed = $true; Alert "$r forget failed" "exit $code" }
            $c = @('check')
            if ($sunday) { $c += '--read-data-subset=1/8' }
            $code = Invoke-Restic $r $c
            if ($code -ne 0) { $failed = $true; Alert "$r check failed" "restic check exit ${code}: the repository needs a look" }
        }
    }
    Log "run end$(if ($failed) { ': with failures' } else { ': ok' })"
} catch {
    $failed = $true
    Alert 'run failed' $_.Exception.Message
} finally {
    Remove-Item Env:RESTIC_PASSWORD -ErrorAction SilentlyContinue
}
exit ([int]$failed)
