# Registers the daily backup task (BRIEF 02). Runs only with the owner's yes and a CHANGELOG entry first.
#   powershell -NoProfile -File "C:\- Tools\- LLM\Daedalus\tools\backup-task.ps1" [-At 13:00]
# The task "Daedalus daily backup" runs tools\backup.ps1 as this user, only while they're logged on (the DPAPI-protected
# password needs their logon; no Windows password is stored in the task), hidden, once a day at -At. A run missed while
# the PC was off starts as soon as it's back (StartWhenAvailable); a run is stopped after 3 h.
# Rollback: the owner deletes the task in Task Scheduler (Claude is denied Unregister-ScheduledTask).
param([string]$At = '13:00')
$ErrorActionPreference = 'Stop'
$name = 'Daedalus daily backup'
if (Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue) { throw "already exists: $name" }
$script = Join-Path $PSScriptRoot 'backup.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -Daily -At $At
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3) `
    -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Principal $principal `
    -Description 'BRIEF 02 (Daedalus): restic backup of ~/.claude, the plumbing and the KSP saves to G:. Log: %LOCALAPPDATA%\Daedalus\backup.log' |
    Out-Null
Get-ScheduledTask -TaskName $name | Select-Object TaskName, State, @{ n = 'At'; e = { $At } }
