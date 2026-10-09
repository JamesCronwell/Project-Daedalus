# Stores the Discord layout bot's token (BRIEF 05). The owner's: run it in your own PowerShell window. Claude never runs it.
# It asks once (paste the token from the password manager; nothing is echoed) and stores it DPAPI-protected, readable only
# by this Windows user on this PC, at %LOCALAPPDATA%\Daedalus\discord-token.dpapi, where tools\discord_layout.py reads it.
# The password manager stays the real copy: this file dies with the PC.
# It refuses to overwrite an existing file: delete that file yourself first if you rotate the token.
$ErrorActionPreference = 'Stop'
$dir = Join-Path $env:LOCALAPPDATA 'Daedalus'
$file = Join-Path $dir 'discord-token.dpapi'
if (Test-Path -LiteralPath $file) { throw "already exists: $file" }
$a = Read-Host -AsSecureString 'Discord bot token (paste it from the password manager)'
if ($a.Length -lt 50) { throw 'shorter than 50 characters: that is not a bot token, nothing written' }
New-Item -ItemType Directory -Force -Path $dir | Out-Null
ConvertFrom-SecureString $a | Set-Content -LiteralPath $file -Encoding ascii
"stored: $file"
