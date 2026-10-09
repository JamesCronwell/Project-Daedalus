# Stores the restic password for the daily task (BRIEF 02). The owner's: tools\backup-owner-setup.ps1 calls it, in the
# owner's own PowerShell window. Claude never runs it.
# It asks once (paste it from the password manager; nothing is echoed) and stores it DPAPI-protected, readable only by
# this Windows user on this PC, at %LOCALAPPDATA%\Daedalus\restic-password.dpapi, where tools\backup.ps1 reads it. The
# password manager stays the real copy: this file dies with the PC, and the repositories can't be opened without it.
# It refuses to overwrite an existing file: delete that file yourself first if you mean to change the password.
$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:LOCALAPPDATA 'Daedalus'
$file = Join-Path $dir 'restic-password.dpapi'
if (Test-Path -LiteralPath $file) { throw "already exists: $file" }
$a = Read-Host -AsSecureString 'restic password (paste it from the password manager)'
if ($a.Length -lt 12) { throw 'shorter than 12 characters: nothing written' }
New-Item -ItemType Directory -Force -Path $dir | Out-Null
ConvertFrom-SecureString $a | Set-Content -LiteralPath $file -Encoding ascii
"stored: $file"
