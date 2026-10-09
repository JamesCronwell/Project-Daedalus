# One-off copy of ~/.claude to a dated folder, with a checksum manifest taken from the copy (BRIEF 01, gap 1).
# PROPOSED: runs only with the owner's yes, in a session they attend. It copies; it never deletes or mirrors.
#   powershell -NoProfile -File tools\backup-claude.ps1 [-Dest 'G:\My Drive\daedalus-backups\claude']
# Leaves out .credentials.json (the login token: the owner logs in again) and the throwaway caches. Prints the copy's
# path and its manifest's path. A restore is the copy back into a folder, then
#   python -I tools\manifest.py make <restored> restored.tsv; python -I tools\manifest.py compare <manifest> restored.tsv
param([string]$Dest = 'G:\My Drive\daedalus-backups\claude')
$ErrorActionPreference = 'Stop'
$src = Join-Path $env:USERPROFILE '.claude'
$stamp = Get-Date -Format 'yyyy-MM-dd_HHmm'
$target = Join-Path $Dest $stamp
if (Test-Path $target) { throw "already exists: $target" }
New-Item -ItemType Directory -Path $target | Out-Null
# /E subfolders, /COPY:DAT data+attributes+times, /R:1 /W:1 don't hang on a locked file, /NP /NFL /NDL quiet
robocopy $src $target /E /COPY:DAT /R:1 /W:1 /NP /NFL /NDL /XF .credentials.json /XD cache session-env shell-snapshots
if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE)" }   # 0-7 are success codes
$manifest = "$target.manifest.tsv"
python -I (Join-Path $PSScriptRoot 'manifest.py') make $target $manifest
"copy:     $target"
"manifest: $manifest"
