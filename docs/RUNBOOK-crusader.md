# RUNBOOK: Crusader, rebuild from zero

Windows 11 Pro workstation "eternal-crusade" (Ryzen 7 9800X3D, RX 7900 XTX, 62 GB). Facts come from
`docs/inventory/crusader.md` (regenerate it before you rely on it) and `docs/BACKUP-MAP.md`. Written 2026-10-09, BRIEF 01.
Times are estimates for one attended evening; download times assume a fast line.

## If this disk died tonight
| Disk | Lost for good (today) | Comes back from | Time to restore |
|---|---|---|---|
| **WD_BLACK SN850X 4 TB: C: + F:** | `~/.claude`'s changes since its one-off copy on G: (2026-10-09 14:18; BRIEF 02 makes it daily); uncommitted repo work (WH40K had 180 files, Calypso 2) and unpushed commits (Daedalus main had 7); the non-git folders Olympus, Atlas, Hephaestus; the night-mode scripts; the MCP server config; **the KSP saves** ("Reborn Hangar"); KSP_Reborn's changes since the 2025 G: copy; the age private key unless it's in the password manager | Windows install media; GitHub (repos); Google Drive (Drive itself, the bench dumps, the KSP_Reborn 2025 copy); Steam + CKAN (KSP installs) | ~1 day: Windows + drivers 2 h, apps 3 h, repos 15 min, Claude setup 1 h, KSP rebuild 3-4 h. Memory: restorable to 2026-10-09 14:18; saves: not restorable |
| Samsung 870 EVO: D: GAMES | nothing irreplaceable known | the launchers | hours of downloads |
| Seagate ST2000DM008: E: TEXTURES | whatever on it isn't elsewhere (owner to say) | - | - |
| Google Drive account | the cloud copies (bench dumps, KSP_Reborn copy) and Drive content | nothing (Drive is the copy) | - |

Gap 1's one-off copy is in place and its restore was tested (BRIEF 01, 2026-10-09: 2985 files matched, ~10 s from
Drive's local cache). Once BRIEF 02's daily backup runs, the memory loss shrinks to the hours since the last backup.

## Rebuild order
1. **Windows 11 Pro** on the new NVMe: partition as before (C: ~800 GB system, F: rest, label "LAUNCHERS - WD"). Chipset,
   GPU (AMD Adrenalin), Realtek audio. Sign in to the Microsoft account.
2. **The owner's essentials, by hand** (credentials are the owner's): password manager, Google Drive for desktop (G:),
   Tailscale (log in; device name `eternal-crusade`), GitHub Desktop / Git for Windows + Git Credential Manager.
3. **Toolchain:** Python 3.12 (and 3.10 if a project still needs it), Node 24, Git, `winget install` rclone, age, uv,
   poppler, platform-tools; Docker Desktop (Hephaestus's local beta copy; it isn't set to start with Windows today);
   LM Studio (`C:\- Tools\LM Studio`, runs as a service at login).
4. **Claude:** the desktop app, then restore `~/.claude` from its backup (`G:\My Drive\daedalus-backups\claude\<newest>`: robocopy
   it to `%USERPROFILE%\.claude`, check it with `python -I tools\manifest.py make` + `compare` against its
   `.manifest.tsv`, then log in again: the login token isn't in the copy) and the app's
   `%APPDATA%\Claude\claude_desktop_config.json` (MCP servers: horse, onebrain, graphify). Without a backup: reinstall the
   plugins and skills, rewrite `~/.claude/CLAUDE.md` from this repo's copy (gap 11), log in again.
5. **Repos:** clone into `C:\- Tools\- LLM\`: `JamesCronwell/Project-Calypso` → `Calypso`, `Project-Hephaestus` → `WH40K`,
   `Project-Daedalus` → `Daedalus`. Each project's own START_HERE takes it from there.
6. **SSH to Bastion:** the owner restores the SSH key from the password manager (Daedalus never handles keys), then
   `ssh jamescron@crusade-bastion` (Tailscale MagicDNS; Hephaestus's scripts use `jamescron@192.168.50.181` on the LAN).
7. **Scheduled tasks and Startup items the projects created** (the projects re-create them, each with the owner's yes):
   "WH40K Backup Pull" (daily 04:30, `WH40K\webapp\pull_backup.ps1`), "WH40K Bridge Watcher" (at logon), "OneBrainSync"
   (`WH40K\bridge-kit\sync-onebrain.ps1`), Startup shortcuts `CalypsoSessionLog.lnk` (Calypso BRIEF 14) and
   `Horse LLM Server.lnk`. The full list is in `docs/PLUMBING.md`.
8. **KSP:** Steam to `F:\Steam`; `F:\Steam_Modded_Variants\KSP_Calypso` rebuilt by Calypso (its deploy scripts and CKAN
   lists); KSP_Reborn from the G: copy (2025, stale); saves from their backup (gap 7: none today).
9. **Games and launchers** to D: and F: as wanted.
10. **Check:** `python -I tools/inventory.py crusader` and diff the result against the last committed
    `docs/inventory/crusader.md`.

## Secrets the rebuild needs (named, never read; the owner restores them from the password manager)
- Windows user environment variables (since "Computer audit and debloat", 2026-10-06): `ONEBRAIN_TOKEN`,
  `GEMINI_API_KEY`, `ONEBRAIN_MCP_URL`. WH40K's `bridge-kit` (`watcher.py`, `twin_gbrain_bridge.py`) and the launcher
  `~\.local\bin\onebrain-mcp.cmd` read them. Also `MY_ACCESS_TOKEN`: nothing in `C:\- Tools\- LLM`, `C:\Users\User\Scripts`,
  `~/.claude`'s settings, skills, plugins and tools, the desktop app's MCP config or any scheduled task's action names it
  (searched by name, 2026-10-09); its purpose is unknown (owner/Cerberus).
- `~\.secrets\google\` (a Google OAuth client secret JSON).
- The SSH key Crusader uses for Bastion, and the age private key for the bench dumps.
- `Documents\PC-Audit-Backup-2026-10-06`: the debloat session's backup (token copies redacted in place).
