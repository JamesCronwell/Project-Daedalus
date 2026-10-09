# Find-Restic (BRIEF 02), dot-sourced by tools\backup.ps1 and tools\backup-owner-setup.ps1: restic's path, or $null.
# winget (user scope, no symlinks) puts the package folder on PATH but leaves the exe named restic_<ver>_windows_amd64.exe,
# so `restic` alone doesn't resolve. The newest version in that folder wins.
function Find-Restic {
    $c = Get-Command restic -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $dir = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages\restic.restic_Microsoft.Winget.Source_8wekyb3d8bbwe'
    $exe = Get-ChildItem -LiteralPath $dir -Filter 'restic*.exe' -ErrorAction SilentlyContinue |
        Sort-Object { $v = [regex]::Match($_.Name, '\d+(\.\d+)+').Value; if ($v) { [version]$v } else { [version]'0.0' } } |
        Select-Object -Last 1
    if ($exe) { return $exe.FullName }
    $null
}

if ($MyInvocation.InvocationName -ne '.') { $r = Find-Restic; if ($r) { $r } else { 'restic: not found' } }
