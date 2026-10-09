# Read-only inventory of Crusader. Prints one JSON object on stdout; tools/inventory.py renders and redacts it.
# Every command here only reads (Get-*, Test-Path, git status/log/rev-list, docker version/info/ps/context ls, wsl -l).
# KSP may be live: F:\Steam_Modded_Variants gets names and dates only, never a recursive scan or checksum.
# BRIEF 01. After Sea's machine_inventory.ps1 (github.com/seatemplar10-dev/Horse-Inner-workings), rewritten here.
$ErrorActionPreference = 'SilentlyContinue'
$out = [ordered]@{}

$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
$gpu = Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }
$out.os = [ordered]@{
    host = $env:COMPUTERNAME; caption = $os.Caption; version = $os.Version; build = $os.BuildNumber
    installed = $os.InstallDate.ToString('yyyy-MM-dd'); last_boot = $os.LastBootUpTime.ToString('yyyy-MM-dd HH:mm')
    cpu = $cpu.Name.Trim(); ram_gb = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1); gpu = @($gpu)
}

$out.volumes = @(Get-Volume | Where-Object DriveLetter | Sort-Object DriveLetter | ForEach-Object {
    [ordered]@{ letter = "$($_.DriveLetter):"; label = $_.FileSystemLabel; fs = $_.FileSystem
        size_gb = [math]::Round($_.Size / 1GB, 1); free_gb = [math]::Round($_.SizeRemaining / 1GB, 1)
        health = "$($_.HealthStatus)" } })
$out.disks = @(Get-PhysicalDisk | ForEach-Object {
    [ordered]@{ model = $_.FriendlyName; media = "$($_.MediaType)"; size_gb = [math]::Round($_.Size / 1GB, 0)
        health = "$($_.HealthStatus)"; bus = "$($_.BusType)" } })
# Google Drive for desktop mounts G: as a virtual drive, so Get-Volume misses it
$out.google_drive = [ordered]@{ present = (Test-Path 'G:\My Drive') }

$keys = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
$out.programs = @(Get-ItemProperty $keys | Where-Object { $_.DisplayName -and -not $_.SystemComponent -and -not $_.ParentKeyName } |
    Sort-Object DisplayName -Unique | ForEach-Object {
        [ordered]@{ name = $_.DisplayName; version = "$($_.DisplayVersion)"; publisher = "$($_.Publisher)"
            installed = "$($_.InstallDate)" } })
$out.store_apps_count = @(Get-AppxPackage | Where-Object { -not $_.IsFramework -and $_.SignatureKind -eq 'Store' }).Count

# services: everything not shipped in C:\Windows, plus any Windows service that is set to Auto but stopped
$out.services = @(Get-CimInstance Win32_Service | Where-Object {
        ($_.PathName -and $_.PathName -notmatch '(?i)\\windows\\(system32|syswow64|servicing|microsoft\.net)\\|svchost\.exe') -or
        ($_.StartMode -eq 'Auto' -and $_.State -ne 'Running' -and $_.PathName -notmatch '(?i)svchost') } |
    Sort-Object Name | ForEach-Object {
        [ordered]@{ name = $_.Name; display = $_.DisplayName; state = $_.State; start = $_.StartMode
            path = ($_.PathName -replace '"', '') } })

$startup = @()
$startup += Get-CimInstance Win32_StartupCommand | ForEach-Object {
    [ordered]@{ name = $_.Name; command = $_.Command; location = $_.Location; user = $_.User } }
foreach ($f in "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
               "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup") {
    Get-ChildItem -LiteralPath $f -Force | Where-Object Name -ne 'desktop.ini' | ForEach-Object {
        $target = ''
        if ($_.Extension -eq '.lnk') { $target = (New-Object -ComObject WScript.Shell).CreateShortcut($_.FullName).TargetPath }
        $startup += [ordered]@{ name = $_.Name; command = $target; location = $f; user = '' } }
}
# Task Manager's on/off switch for each Run entry (read-only: StartupApproved)
$approved = @{}
foreach ($k in 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run',
               'HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run',
               'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder') {
    $p = Get-ItemProperty $k
    if ($p) { $p.PSObject.Properties | Where-Object { $_.Value -is [byte[]] } | ForEach-Object {
        $approved[$_.Name] = $(if ($_.Value[0] % 2 -eq 0) { 'enabled' } else { 'disabled' }) } }
}
foreach ($s in $startup) { $s.enabled = $(if ($approved.ContainsKey($s.name)) { $approved[$s.name] } else { 'enabled?' }) }
$out.startup = $startup

$out.scheduled_tasks = @(Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' } | ForEach-Object {
    $i = $_ | Get-ScheduledTaskInfo
    [ordered]@{ task = $_.TaskPath + $_.TaskName; state = "$($_.State)"
        last_run = $(if ($i.LastRunTime -and $i.LastRunTime.Year -gt 2000) { $i.LastRunTime.ToString('yyyy-MM-dd HH:mm') } else { '' })
        last_result = '0x{0:X}' -f $i.LastTaskResult
        next_run = $(if ($i.NextRunTime) { $i.NextRunTime.ToString('yyyy-MM-dd HH:mm') } else { '' })
        action = (($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)".Trim() }) -join ' | ') } })

# WSL: wsl.exe prints UTF-16
$wsl = ''
if (Get-Command wsl.exe) {
    $prev = [Console]::OutputEncoding; [Console]::OutputEncoding = [Text.Encoding]::Unicode
    $wsl = (wsl.exe -l -v 2>&1 | Out-String).Trim()
    [Console]::OutputEncoding = $prev
}
$out.wsl = $wsl

$dk = [ordered]@{ cli = [bool](Get-Command docker) }
$dsvc = Get-Service com.docker.service
$dk.service = $(if ($dsvc) { "$($dsvc.Status) / $($dsvc.StartType)" } else { 'absent' })
$dk.desktop_running = [bool](Get-Process 'Docker Desktop')
$dk.pipe_docker_engine = Test-Path '\\.\pipe\docker_engine'
$dk.pipe_desktop_linux = Test-Path '\\.\pipe\dockerDesktopLinuxEngine'
if ($dk.cli) {
    $dk.context = (docker context ls --format '{{.Name}}{{if .Current}} (current){{end}} {{.DockerEndpoint}}' 2>&1 | Out-String).Trim()
    $dk.server = (docker version --format '{{.Server.Version}}' 2>&1 | Out-String).Trim()
    $dk.containers = (docker ps -a --format '{{.Names}}  {{.Image}}  {{.Status}}' 2>&1 | Out-String).Trim()
    $dk.volumes = (docker volume ls -q 2>&1 | Out-String).Trim()
}
$out.docker = $dk

$out.tailscale = $(if (Get-Command tailscale) { (tailscale status 2>&1 | Out-String).Trim() } else { 'absent' })

# repos under C:\- Tools\- LLM: branch, remote, unpushed and uncommitted counts (read-only git)
$out.repos = @(Get-ChildItem 'C:\- Tools\- LLM' -Directory | Where-Object { Test-Path (Join-Path $_.FullName '.git') } | ForEach-Object {
    $r = $_.FullName
    $up = (git -C $r rev-parse --abbrev-ref '@{u}' 2>$null)
    [ordered]@{ repo = $_.Name; branch = (git -C $r branch --show-current 2>$null)
        remote = ((git -C $r remote get-url origin 2>$null) -replace '//[^@/]+@', '//')
        upstream = "$up"
        unpushed = $(if ($up) { [int](git -C $r rev-list --count '@{u}..HEAD' 2>$null) } else { -1 })
        unpushed_all_branches = [int](git -C $r rev-list --count --branches --not --remotes 2>$null)
        dirty = @(git -C $r status --porcelain 2>$null).Count
        last_commit = (git -C $r log -1 --format='%cs %h' 2>$null)
        worktrees = @(git -C $r worktree list --porcelain 2>$null | Where-Object { $_ -like 'worktree *' }).Count } })

# names and dates only (KSP may be running)
$out.ksp_variants = @(Get-ChildItem 'F:\Steam_Modded_Variants' -Force | ForEach-Object {
    [ordered]@{ name = $_.Name; modified = $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm') } })
$out.ksp_running = [bool](Get-Process KSP_x64)

$claude = Join-Path $env:USERPROFILE '.claude'
$files = Get-ChildItem -LiteralPath $claude -Recurse -File -Force
$out.claude_dir = [ordered]@{ path = $claude; files = $files.Count
    mb = [math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 1)
    top = @(Get-ChildItem -LiteralPath $claude -Force | ForEach-Object { $_.Name }) }

$out.generated = (Get-Date).ToString('yyyy-MM-dd HH:mm')
$out | ConvertTo-Json -Depth 6 -Compress
