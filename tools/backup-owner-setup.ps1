# The owner's one sitting (BRIEF 02, option 2): every step that touches the restic password, plus the task, which the
# guard keeps from Claude. Claude never runs this file. In the owner's own PowerShell window, after restic is installed:
#   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\- Tools\- LLM\Daedalus\tools\backup-owner-setup.ps1"
# Options: -SkipSaves (leave the KSP saves out, and leave the skip-ksp-saves flag so the task skips them too; running
# this again without -SkipSaves removes the flag and does the saves' run and restore); -At 13:00 (the task's time).
# In order: the password (asked once), both repositories initialised, the exclusions checked, checksum manifests of
# ~/.claude and the saves, the first run, a restore of it into a scratch folder (restic --verify), the manifests
# compared, the scratch folder deleted only if everything matched, the daily task registered.
# One result block at the end; the same lines in %LOCALAPPDATA%\Daedalus\owner-setup.log (Claude reads that). Safe to
# run again: done steps are skipped, a failed one stops the rest.
param([switch]$SkipSaves, [string]$At = '13:00')
$ErrorActionPreference = 'Stop'
$tools = $PSScriptRoot
$backup = Join-Path $tools 'backup.ps1'
$state = Join-Path $env:LOCALAPPDATA 'Daedalus'
$log = Join-Path $state 'owner-setup.log'
$scratch = Join-Path $state 'restore-check'
$claude = Join-Path $env:USERPROFILE '.claude'
$ksp = 'F:\Steam_Modded_Variants'
$saves = [ordered]@{ 'calypso-saves' = 'KSP_Calypso'; 'reborn-saves' = 'KSP_Reborn' }
$results = New-Object System.Collections.Generic.List[string]
New-Item -ItemType Directory -Force -Path $state | Out-Null

function Say([string]$m) {
    $l = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
    Add-Content -LiteralPath $log -Value $l -Encoding utf8
    Write-Host $l
}
function Result([string]$m) { $results.Add($m); Say "RESULT $m" }
function Manifest([string]$src, [string]$out, [string[]]$excl) {
    $a = @('-I', (Join-Path $tools 'manifest.py'), 'make', $src, $out)
    foreach ($e in $excl) { $a += @('--exclude', $e) }
    $o = & python @a 2>&1
    foreach ($l in $o) { Say "  $l" }
    $LASTEXITCODE
}
function Restored([string]$target, [string]$src) {   # where restic put $src under $target (C:\x -> <target>\C\x)
    Join-Path $target ($src -replace '^([A-Za-z]):', '$1')
}

$ok = $true
try {
    Say "=== owner setup start$(if ($SkipSaves) { ' (-SkipSaves)' })"
    if (-not (Get-Command restic -ErrorAction SilentlyContinue)) { throw 'restic is not installed yet (Claude installs it first)' }
    $flag = Join-Path $state 'skip-ksp-saves'
    if (-not $SkipSaves -and (Test-Path -LiteralPath $flag)) { Remove-Item -LiteralPath $flag; Result 'skip-ksp-saves flag: removed (the saves are clear)' }

    # 1. the password
    if (Test-Path -LiteralPath (Join-Path $state 'restic-password.dpapi')) { Result 'password: already stored' }
    else { & (Join-Path $tools 'backup-setpass.ps1') | Out-Null; Result 'password: stored (DPAPI)' }

    # 2. the repositories
    & $backup -Init
    if ($LASTEXITCODE -ne 0) { throw "init failed ($LASTEXITCODE)" }
    Result 'repositories: initialised'

    # 3. the exclusions, before anything is saved
    $o = & $backup -CheckExcludes 2>&1
    $code = $LASTEXITCODE
    foreach ($l in $o) { Say "  $l" }
    if ($code -ne 0) { throw "the exclusion check failed ($code): nothing was backed up" }
    Result "exclusions: $(@($o)[-1])"

    # 4. manifests of the sources, just before the run (the exclusions come from the exclude file, never named here)
    if (Test-Path -LiteralPath $scratch) { throw "a scratch folder is already there: $scratch (look, then delete it)" }
    New-Item -ItemType Directory -Path $scratch | Out-Null
    $excl = @()
    foreach ($line in Get-Content -LiteralPath (Join-Path $tools 'backup-exclude.txt')) {
        if ($line -match '^\s*\$USERPROFILE\\\.claude\\(.+?)\s*$') { $r = $Matches[1] -replace '\\', '/'; $excl += @($r, "$r/*") }
    }
    $t0 = Get-Date
    if ((Manifest $claude (Join-Path $scratch 'm0-claude.tsv') $excl) -gt 1) { throw 'manifest of ~/.claude failed' }
    $doSaves = @()
    if (-not $SkipSaves) {
        foreach ($tag in $saves.Keys) {
            if ((Manifest (Join-Path $ksp "$($saves[$tag])\saves") (Join-Path $scratch "m0-$tag.tsv") @()) -ne 0) {
                throw "manifest of $tag failed"
            }
            $doSaves += $tag
        }
    }

    # 5. the first run (the daily run itself)
    if ($SkipSaves) { & $backup -SkipSaves } else { & $backup }
    $code = $LASTEXITCODE
    if ($code -ne 0) { throw "the first run failed ($code): see %LOCALAPPDATA%\Daedalus\backup.log" }
    Result 'first run: ok'
    foreach ($tag in @($doSaves)) {   # a saves folder the run skipped (KSP started meanwhile) has no fresh stamp
        $st = Get-Item -LiteralPath (Join-Path $state "last-ok-$tag.txt") -ErrorAction SilentlyContinue
        if (-not $st -or $st.LastWriteTime -lt $t0) {
            $doSaves = @($doSaves | Where-Object { $_ -ne $tag }); $ok = $false
            Result "$tag`: NOT backed up by the run (skipped by the rule? see backup.log)"
        }
    }

    # 6. restore into the scratch folder, restic re-reading every restored file against the snapshot (--verify)
    $sets = @(@{ repo = 'plumbing'; tag = 'plumbing' }) + @($doSaves | ForEach-Object { @{ repo = 'saves'; tag = $_ } })
    foreach ($s in $sets) {
        $target = Join-Path $scratch "r-$($s.tag)"
        & $backup -Repo $s.repo -Restic @('restore', 'latest', '--tag', $s.tag, '--host', 'eternal-crusade', '--target', $target, '--verify')
        if ($LASTEXITCODE -ne 0) { throw "restore of $($s.tag) failed or didn't verify ($LASTEXITCODE)" }
        Result "restore $($s.tag): verified by restic"
    }

    # 7. the manifests compared. ~/.claude is written by every open session, so a difference counts only if the live
    #    file wasn't touched since just before the run.
    $live = 0
    $rc = Restored (Join-Path $scratch 'r-plumbing') $claude
    if (-not (Test-Path -LiteralPath $rc)) { throw "the restored ~/.claude isn't at ${rc}: look in $scratch" }
    if ((Manifest $rc (Join-Path $scratch 'm1-claude.tsv') $excl) -gt 1) { throw 'manifest of the restored ~/.claude failed' }
    $a = @{}; foreach ($l in Get-Content -LiteralPath (Join-Path $scratch 'm0-claude.tsv')) { $f = $l -split "`t"; $a[$f[0]] = "$($f[1])/$($f[2])" }
    $b = @{}; foreach ($l in Get-Content -LiteralPath (Join-Path $scratch 'm1-claude.tsv')) { $f = $l -split "`t"; $b[$f[0]] = "$($f[1])/$($f[2])" }
    $bad = @()
    foreach ($k in (@($a.Keys) + @($b.Keys) | Sort-Object -Unique)) {
        if ($a[$k] -eq $b[$k]) { continue }
        $p = Join-Path $claude ($k -replace '/', '\')
        $item = Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
        if ((-not $item) -or $item.LastWriteTime -ge $t0.AddSeconds(-5)) { $live++ } else { $bad += $k }
    }
    if ($bad.Count) {
        $ok = $false
        foreach ($k in $bad | Select-Object -First 20) { Say "  differs and unchanged since the run: $k" }
        Result "~/.claude: MISMATCH, $($bad.Count) files differ that weren't touched since the run"
    } else { Result "~/.claude: MATCH, $($b.Count) files ($live changed live during the run, by their dates)" }
    foreach ($tag in $doSaves) {
        $rs = Restored (Join-Path $scratch "r-$tag") (Join-Path $ksp "$($saves[$tag])\saves")
        if (-not (Test-Path -LiteralPath $rs)) { throw "the restored $tag isn't at ${rs}: look in $scratch" }
        if ((Manifest $rs (Join-Path $scratch "m1-$tag.tsv") @()) -ne 0) { throw "manifest of the restored $tag failed" }
        $o = & python -I (Join-Path $tools 'manifest.py') compare (Join-Path $scratch "m0-$tag.tsv") (Join-Path $scratch "m1-$tag.tsv") 2>&1
        $code = $LASTEXITCODE
        foreach ($l in $o) { Say "  $l" }
        if ($code -ne 0) { $ok = $false }
        Result "$tag`: $(@($o)[-1])"
    }

    # 8. the scratch folder goes only if everything matched
    if ($ok) { Remove-Item -LiteralPath $scratch -Recurse -Force; Result 'scratch folder: deleted' }
    else { Result "scratch folder: KEPT for a look: $scratch" }

    # 9. the daily task (only after a good run)
    if ($SkipSaves) { Set-Content -LiteralPath $flag -Value 'BRIEF 02: until Calypso BRIEF 26 is done' -Encoding utf8; Result 'skip-ksp-saves flag: set (the task skips the saves until this script runs again without -SkipSaves)' }
    if (-not $ok) { Result 'task: not registered (something did not match)' }
    elseif (Get-ScheduledTask -TaskName 'Daedalus daily backup' -ErrorAction SilentlyContinue) { Result 'task: already registered' }
    else { & (Join-Path $tools 'backup-task.ps1') -At $At | Out-Null; Result "task: registered, daily at $At" }
} catch {
    $ok = $false
    Result "STOPPED: $($_.Exception.Message)"
}
$head = "=== BRIEF 02 owner setup: $(if ($ok) { 'OK' } else { 'NOT OK' }) ==="
Say $head
Write-Host ''
Write-Host $head
$results | ForEach-Object { Write-Host "  $_" }
Write-Host "  log: $log"
Write-Host '  Last step, yours: in drive.google.com, check that daedalus-backups\restic and'
Write-Host '  ### Games\KSP\-- BACKUP --\saves-restic have finished uploading (the app''s Sync status shows nothing pending).'
