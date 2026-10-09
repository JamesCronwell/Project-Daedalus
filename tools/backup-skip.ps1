# The KSP saves' skip rule (BRIEF 02), dot-sourced by tools\backup.ps1. It holds nothing secret, so it also runs alone,
# for the harmless test (Done-when 2): it prints, for each install, why its saves would be skipped right now.
#   powershell -NoProfile -File "C:\- Tools\- LLM\Daedalus\tools\backup-skip.ps1"
# The rule: -SkipSaves; the flag file <StateDir>\skip-ksp-saves (a Calypso deploy window); a KSP_x64 process (from that
# install: its saves only; from elsewhere under the KSP root, or of unknown path: both).
param([string]$StateDir = (Join-Path $env:LOCALAPPDATA 'Daedalus'), [string]$Ksp = 'F:\Steam_Modded_Variants')

function Get-KspBlocker([string]$install, [bool]$skip, [string]$stateDir, [string]$kspRoot) {   # a reason, or $null
    if ($skip) { return '-SkipSaves' }
    if (Test-Path -LiteralPath (Join-Path $stateDir 'skip-ksp-saves')) { return 'the skip-ksp-saves flag file' }
    foreach ($p in @(Get-Process -Name 'KSP_x64' -ErrorAction SilentlyContinue)) {
        $path = $null
        try { $path = $p.Path } catch {}
        if (-not $path) { return "KSP_x64 (pid $($p.Id), path unknown)" }
        if ($path -like (Join-Path $kspRoot "$install\*")) { return "KSP_x64 from $install (pid $($p.Id))" }
        $other = $path -like "$kspRoot\*"
        if (-not $other) { return "KSP_x64 from outside $kspRoot (pid $($p.Id)): $path" }
    }
    $null
}

if ($MyInvocation.InvocationName -ne '.') {
    foreach ($install in 'KSP_Calypso', 'KSP_Reborn') {
        $why = Get-KspBlocker $install $false $StateDir $Ksp
        '{0}\saves: {1}' -f $install, $(if ($why) { "skip ($why)" } else { 'back up' })
    }
}
