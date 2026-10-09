# The owner runs this once, in their own PowerShell window (BRIEF 02). Claude never runs it.
#   powershell -NoProfile -File "C:\- Tools\- LLM\Daedalus\tools\backup-setpass.ps1"
# It asks for the restic password twice (nothing is echoed) and stores it DPAPI-protected, readable only by this Windows
# user on this PC, at %LOCALAPPDATA%\Daedalus\restic-password.dpapi, where tools\backup.ps1 reads it. Keep the password
# in the password manager too: this file dies with the PC, and the repositories can't be opened without the password.
# It refuses to overwrite an existing file: delete that file yourself first if you mean to change the password.
$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:LOCALAPPDATA 'Daedalus'
$file = Join-Path $dir 'restic-password.dpapi'
if (Test-Path -LiteralPath $file) { throw "already exists: $file" }
$a = Read-Host -AsSecureString 'restic password'
$b = Read-Host -AsSecureString 'again'
$pa = [Net.NetworkCredential]::new('', $a).Password
$pb = [Net.NetworkCredential]::new('', $b).Password
if ($pa -ne $pb) { throw 'the two entries differ: nothing written' }
if ($pa.Length -lt 12) { throw 'shorter than 12 characters: nothing written' }
$pa = $null; $pb = $null
New-Item -ItemType Directory -Force -Path $dir | Out-Null
ConvertFrom-SecureString $a | Set-Content -LiteralPath $file -Encoding ascii
"stored: $file"
