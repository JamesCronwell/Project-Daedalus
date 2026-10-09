# RUNBOOK: Crusader, rebuild from zero

Windows 11 Pro workstation "eternal-crusade" (Ryzen 7 9800X3D, RX 7900 XTX, 62 GB). Facts come from
`docs/inventory/crusader.md` (regenerate it before you rely on it) and `docs/BACKUP-MAP.md`. Written 2026-10-09, BRIEF 01.
Times are estimates for one attended evening; download times assume a fast line.

## If this disk died tonight
| Disk | Lost for good (today) | Comes back from | Time to restore |
|---|---|---|---|
| **WD_BLACK SN850X 4 TB: C: + F:** | up to a day of `~/.claude`, the plumbing, the non-git folders and the KSP saves (the daily restic run, 13:00, BRIEF 02), plus whatever Drive hadn't uploaded yet; uncommitted repo work (WH40K had 180 files, Calypso 2) and unpushed commits; KSP_Reborn's changes since the 2025 G: copy (until BRIEF 02 Task 5); the age private key unless it's in the password manager | Windows install media; GitHub (repos); Google Drive (Drive itself, the two restic repos, the bench dumps, the KSP_Reborn copy); Steam + CKAN (KSP installs) | ~1 day: Windows + drivers 2 h, apps 3 h, repos 15 min, Claude setup 1 h, KSP rebuild 3-4 h. Memory, plumbing, saves: restorable to the last daily snapshot (restic: below) |
| Samsung 870 EVO: D: GAMES | nothing irreplaceable known | the launchers | hours of downloads |
| Seagate ST2000DM008: E: TEXTURES | whatever on it isn't elsewhere (owner to say) | - | - |
| Google Drive account | the cloud copies (bench dumps, KSP_Reborn copy) and Drive content | nothing (Drive is the copy) | - |

The daily backup (BRIEF 02) runs since 2026-10-09: its first snapshots were restored and checked that evening (~/.claude
3469 files, the saves 281 + 668, all MATCH). BRIEF 01's one-off copy (2026-10-09 14:18) is still on G: as a fallback.

## Rebuild order
1. **Windows 11 Pro** on the new NVMe: partition as before (C: ~800 GB system, F: rest, label "LAUNCHERS - WD"). Chipset,
   GPU (AMD Adrenalin), Realtek audio. Sign in to the Microsoft account.
2. **The owner's essentials, by hand** (credentials are the owner's): password manager, Google Drive for desktop (G:),
   Tailscale (log in; device name `eternal-crusade`), GitHub Desktop / Git for Windows + Git Credential Manager.
3. **Toolchain:** Python 3.12 (and 3.10 if a project still needs it), Node 24, Git, `winget install` rclone, age, uv,
   poppler, platform-tools; Docker Desktop (Hephaestus's local beta copy; it isn't set to start with Windows today);
   LM Studio (`C:\- Tools\LM Studio`, runs as a service at login).
4. **Claude:** the desktop app, then restore `~/.claude`, the MCP config and the rest from restic ("Restoring from
   restic", below; the Daedalus repo comes first, step 5, for its `tools/`), then log in again: the login token isn't in
   the backup. The MCP config (horse, onebrain, graphify) goes back to the app's real folder,
   `%LOCALAPPDATA%\Packages\Claude_<id>\LocalCache\Roaming\Claude\` (the app is MSIX; start it once so the folder exists).
   Fallback: BRIEF 01's one-off copy `G:\My Drive\daedalus-backups\claude\2026-10-09_1418` (robocopy, then
   `manifest.py compare` against its `.manifest.tsv`).
5. **Repos:** clone into `C:\- Tools\- LLM\`: `JamesCronwell/Project-Calypso` → `Calypso`, `Project-Hephaestus` → `WH40K`,
   `Project-Daedalus` → `Daedalus`. Each project's own START_HERE takes it from there.
6. **SSH to Bastion:** the owner restores the SSH key from the password manager (Daedalus never handles keys), then
   `ssh jamescron@crusade-bastion` (Tailscale MagicDNS; Hephaestus's scripts use `jamescron@192.168.50.181` on the LAN).
7. **Scheduled tasks and Startup items the projects created** (the projects re-create them, each with the owner's yes):
   "WH40K Backup Pull" (daily 04:30, `WH40K\webapp\pull_backup.ps1`), "WH40K Bridge Watcher" (at logon), "OneBrainSync"
   (`WH40K\bridge-kit\sync-onebrain.ps1`), Startup shortcuts `CalypsoSessionLog.lnk` (Calypso BRIEF 14) and
   `Horse LLM Server.lnk`. The full list is in `docs/PLUMBING.md`.
8. **KSP:** Steam to `F:\Steam`; `F:\Steam_Modded_Variants\KSP_Calypso` rebuilt by Calypso (its deploy scripts and CKAN
   lists); KSP_Reborn from its newest G: copy under `-- BACKUP --` (the dated one from BRIEF 02 Task 5 once it exists,
   else the 2025 copy); then the saves from restic (below), over the installs' `saves` folders.
9. **Games and launchers** to D: and F: as wanted.
10. **The daily backup** again (owner, ~5 min): `winget install --id restic.restic --exact --scope user`, then
    `tools\backup-owner-setup.ps1` against the **existing** repos (it skips init when `config` is there; it stores the
    password from the password manager, runs, restores, compares, registers the task).
11. **Check:** `python -I tools/inventory.py crusader` and diff the result against the last committed
    `docs/inventory/crusader.md`.

## Restoring from restic (the owner; Claude never handles the password)
Two repos on G:, one password (the owner's password manager): `G:\My Drive\daedalus-backups\restic` (tag `plumbing`:
`~/.claude`, the MCP config, `C:\Users\User\Scripts`, Olympus, Atlas, `Hephaestus\Claude_UI_UX` and `EU5`) and
`G:\My Drive\### Games\KSP\-- BACKUP --\saves-restic` (tags `calypso-saves`, `reborn-saves`). Drive for desktop must be
signed in and the repo folders available (the first read downloads them).
1. Install restic: `winget install --id restic.restic --exact --scope user`. winget names the exe
   `restic_<ver>_windows_amd64.exe`: run `powershell -File tools\backup-restic.ps1` to print its path, and use that
   path for `restic` below.
2. In the owner's PowerShell, the password for this window only (nothing written): `$env:RESTIC_PASSWORD =
   [Net.NetworkCredential]::new('', (Read-Host -AsSecureString 'restic password')).Password`, and
   `$env:RESTIC_REPOSITORY = 'G:\My Drive\daedalus-backups\restic'` (or the saves repo).
3. Look: `restic snapshots` (per tag: `--tag plumbing`).
4. Restore one folder by subpath, into an empty scratch folder first (a full-path restore recreates `C:\Users` and
   fails on its permissions): `restic restore "latest:/C/Users/User/.claude" --tag plumbing --target D:\restore\claude
   --verify`. Saves: `"latest:/F/Steam_Modded_Variants/KSP_Reborn/saves" --tag reborn-saves` (or `KSP_Calypso`,
   `calypso-saves`). A single file: `restic dump latest:/path/in/snapshot > out`.
5. Check it: `--verify` re-reads every file against the snapshot. Then copy the folder into place (robocopy /E), and
   close the window (the password lived only in it).
6. If a repo complains: `restic check` (structure), `restic unlock` (a stale lock after a crash; only when no backup
   runs).

## Secrets the rebuild needs (named, never read; the owner restores them from the password manager)
- Windows user environment variables (since "Computer audit and debloat", 2026-10-06): `ONEBRAIN_TOKEN`,
  `GEMINI_API_KEY`, `ONEBRAIN_MCP_URL`. WH40K's `bridge-kit` (`watcher.py`, `twin_gbrain_bridge.py`) and the launcher
  `~\.local\bin\onebrain-mcp.cmd` read them. Also `MY_ACCESS_TOKEN`: nothing in `C:\- Tools\- LLM`, `C:\Users\User\Scripts`,
  `~/.claude`'s settings, skills, plugins and tools, the desktop app's MCP config or any scheduled task's action names it
  (searched by name, 2026-10-09); its purpose is unknown (owner/Cerberus).
- `~\.secrets\google\` (a Google OAuth client secret JSON).
- The SSH key Crusader uses for Bastion, and the age private key for the bench dumps.
- `Documents\PC-Audit-Backup-2026-10-06`: the debloat session's backup (token copies redacted in place).
- The restic password (BRIEF 02): the owner's password manager; the task's copy, `%LOCALAPPDATA%\Daedalus\
  restic-password.dpapi`, dies with the PC and is re-made by `tools\backup-owner-setup.ps1`.
