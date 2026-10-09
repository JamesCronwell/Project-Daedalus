# BACKUP MAP: what would hurt to lose, and where its copy is

Checked read-only on 2026-10-09 (BRIEF 01); rows 1, 3, 4, 5 and 17 rewritten that evening by BRIEF 02. Ages are as of
that day. "Tested" means a restore was run and checked, not
that a copy exists. Sources: `docs/inventory/*.md` (regenerate: `python -I tools/inventory.py`) plus the checks named
in each row. Rewrite this file when a copy, a schedule or a test changes; the gaps' fixes wait in BRIEF 01's Handover
(`docs/briefs/done/01-safety-net.md`).

## Crusader's disks (one disk holds most of it)
| Physical disk | Volumes | What dies with it |
|---|---|---|
| WD_BLACK SN850X 4 TB (NVMe) | **C:** (system, `~/.claude`, `C:\- Tools`, the repos) **and F:** (KSP installs, CKAN cache) | Windows, every orchestrator's memory and transcripts, uncommitted repo work, all KSP installs and saves |
| Samsung 870 EVO 2 TB (SATA SSD) | D: GAMES | games (re-downloadable) |
| Seagate ST2000DM008 2 TB (HDD) | E: TEXTURES | textures (owner to say whether any are irreplaceable) |
| Google Drive (cloud, streamed as G:) | G: | nothing local: it's the off-machine copy |

## Bastion's disks
| Physical disk | Mount | What lives there |
|---|---|---|
| Samsung 970 EVO Plus 250 GB (NVMe) | `/`, `/boot/efi` | OS, `/home/jamescron` (`bench-register/`, `bastion-ops/`, gbrain), Docker's volumes incl. `bench-register_pgdata` (the live database) |
| Samsung 970 EVO Plus 1 TB (NVMe) | `/mnt/cache` | `compose/` (the media stack's compose project) and `appdata/` (every app's config, Homepage, backrest) |
| WD 12 TB WD120EFGX (HDD) | `/mnt/storage` | media library 8.6 TB (80% full) |
| Seagate ST3000DM001 3 TB (HDD, NTFS via ntfs-3g, `nofail`) | `/mnt/backups` | the bench-register dumps and the local restic repo: **both of Bastion's on-box copies on one old disk** |

## The items
| # | Item | Where it lives | Copy | Age of newest copy | Restore tested? |
|---|---|---|---|---|---|
| 1 | `~/.claude` (memory, transcripts, settings, `tools/`, skills; 3469 files, 1.1 GB) | Crusader C: | **daily restic** (BRIEF 02): repo `G:\My Drive\daedalus-backups\restic`, tag `plumbing`, task "Daedalus daily backup" 13:00, 14 daily + 8 weekly; leaves out what `tools/backup-exclude.txt` lists (the login token, the caches). Also the one-off copy `G:\My Drive\daedalus-backups\claude\2026-10-09_1418` (kept until restic's copy is confirmed uploaded) | snapshot 362e2d09, 2026-10-09 19:43; daily from 10-10 | yes: 2026-10-09 19:44, restored by `latest:/C/Users/User/.claude` to a scratch folder, `restic restore --verify` ok, manifest MATCH 3469 (2 changed live during the run). Uploaded: Drive for desktop "Up to date" (owner, ~20:10) |
| 2 | Repos Calypso, WH40K (Hephaestus), Daedalus | `C:\- Tools\- LLM\*` | private GitHub remotes | Calypso 0 unpushed / 2 uncommitted; WH40K 0 unpushed / **180 uncommitted**; Daedalus main 7 unpushed (the orchestrator merges, the owner pushes) | clone works daily |
| 3 | Non-git folders under `C:\- Tools\- LLM`: Olympus (the owner's server notes `Ubuntu Commands.txt`, a house plan), Atlas, Hephaestus (`Claude_UI_UX`, `EU5`) | Crusader C: | **daily restic**, with item 1 (same snapshot, tag `plumbing`): Olympus, Atlas, `Hephaestus\Claude_UI_UX`, `Hephaestus\EU5` (empty). Restic reads them; Claude doesn't. Not covered: `Hephaestus\Claude_UI_UX.zip` (next to the folder; the owner to say if it matters) | 2026-10-09 19:43 | in the snapshot (restic `check` clean); not restored separately. Gap 10 narrowed |
| 4 | Plumbing: `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/tools/claude_hours.py`, `C:\Users\User\Scripts\night-mode.*`, the desktop app's MCP config `claude_desktop_config.json` (MSIX: the real file is `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\`; the app and its sessions see it as `%APPDATA%\Claude\`) | Crusader C: | **daily restic**, with item 1 (tag `plumbing`): all of them | 2026-10-09 19:43 | the `~/.claude` parts: yes, with item 1; Scripts and the MCP config: in the snapshot, not restored separately. Gap 11 closed |
| 5 | KSP saves: `KSP_Calypso\saves` (281 files, 150 MB: "Reborn Hangar", 2 test scenarios, training) and `KSP_Reborn\saves` (668 files, 3.7 GB) | Crusader F: | **daily restic** (BRIEF 02): repo `G:\My Drive\### Games\KSP\-- BACKUP --\saves-restic`, tags `calypso-saves`, `reborn-saves`; skipped while KSP_x64 runs or the flag `%LOCALAPPDATA%\Daedalus\skip-ksp-saves` exists; an alert after 3 days without one | e2ab6108 / 56b51ae1, 2026-10-09 19:43 | yes: 2026-10-09 19:44, both restored by subpath, `--verify` ok, manifest MATCH 281 and 668. Uploaded (Drive "Up to date"). Gap 7 closed |
| 6 | KSP_Calypso install (modded) | Crusader F: | rebuildable: Steam KSP + CKAN from Calypso's repo lists and `manual_mods`; `CKAN_cache` and `calypso_cache` speed it up but sit on the same disk | - | not rehearsed |
| 7 | KSP_Reborn (read-only reference install) | Crusader F: | `G:\My Drive\### Games\KSP\-- BACKUP --\KSP_Reborn` | folders dated 2025-02-28 / GameData 2025-04-10; F:'s copy was last modified 2026-04-10: **likely a year stale** | no: gap 8 |
| 8 | `F:\Steam_Modded_Variants\KSP Backups` (Ships, 2026-04-10) | Crusader F: | same disk as what it backs up | - | n/a |
| 9 | bench-register database (Hephaestus BRIEF 50) | Bastion `/` (Docker volume `bench-register_pgdata`) | (a) nightly `pg_dump` 01:00 UTC to `/mnt/backups/bench-register` (14 kept, + weekly/ 8 kept), age-encrypted; (b) Crusader's "WH40K Backup Pull" copies the newest `.age` to `G:\My Drive\--- Hobbies\Warhammer 40K\bench-register-backups` daily 04:30 local (14 kept); (c) restic `config-daily` picks up the dumps folder (row 10); (d) R2 `webapp-offsite` daily 05:30 (row 11) | `bench-20261009-0945.dump.age` 555,761 bytes, `last_ok` 2026-10-09T09:45:08Z (Hephaestus's manual run after the CRLF fix); the 2026-10-09 01:00 run had failed | restic restore byte-identical 2026-09-26 (configs); the server copy of the restore test passed 15 tables on 2026-10-07; monthly `restore_test.sh` first runs 1 Nov; the attended drill is Hephaestus's, ~7 Nov |
| 10 | Bastion configs: `/mnt/cache/appdata` (all apps, Homepage), `/mnt/cache/compose`, `~/bastion-ops`, crontabs, `/etc/{fstab,docker,systemd/system,sudoers.d,cockpit}`, bench dumps; Minecraft world (`/opt/minecraft/tfg-modern`, 1.7 GB, server stopped until the modpack's v14) | Bastion | backrest (restic) plans `config-daily` 04:30 (7d/4w/6m; Plex Cache/Logs/Codecs/Drivers excluded) and `minecraft-6h` (run by `mc-backup.sh`); local repo `/mnt/backups/restic/bastion` (25 snapshots, 11 GB) | newest snapshot 2026-10-09 06:00 UTC | yes: byte-identical test restore 2026-09-26 and `restic check` clean (ops notes, `~/bastion-ops/CLAUDE.md` section 6) |
| 11 | Offsite of 9 and 10 ("the Cloudflare backups") | Cloudflare R2 bucket via backrest | **only the bench dumps** (`webapp-offsite`, daily 05:30, 7d/4w/6m). Configs and Minecraft have **no offsite copy since 2026-10-03**: the owner emptied R2 to stay inside the 10 GB free tier. **Accepted risk** (owner, 2026-10-09, via the orchestrator); a slim plan is proposed below | the webapp repo's last run: not verified (backrest UI needs a login) | the 2026-09-26 R2 restore (level.dat, server.properties, dashboard.yml) was of the old repo, since emptied |
| 12 | `G:\My Drive\bastion-restic` | Google Drive | the old `gdrive` restic repo, removed from Backrest on 2026-09-26 (quota-blocked); **0 snapshots**, unused | - | n/a: a leftover the owner may delete (gap 5) |
| 13 | The age private key that decrypts every dump | Crusader only (per `backup.sh`); `restore_drill.sh` expects it from the owner's password manager | owner's password manager? | - | gap 6 |
| 14 | Bastion media library (8.6 TB) | Bastion `/mnt/storage` | none (re-acquirable through the *arr stack) | - | accepted? gap 14 |
| 15 | Tailscale serve mappings, ports | Bastion tailscaled state | recorded in `docs/inventory/bastion.md` (regenerate) | 2026-10-09 | rebuild by hand from the inventory |
| 16 | gbrain (`~/gbrain-vault`, `~/gbrain-backups`) | Bastion `/home` | `~/gbrain-backups/gbrain-…-20261006-1745.tgz` (same disk); whether restic covers `/home` beyond `bastion-ops` is unknown | 2026-10-06 | no |
| 17 | The restic password for Crusader's two repos (rows 1, 3, 4, 5): without it they can't be opened | the owner's password manager; for the task, `%LOCALAPPDATA%\Daedalus\restic-password.dpapi` (DPAPI, this Windows user only: dies with the PC) | the password manager is the copy | 2026-10-09 | used by the sitting's restore 2026-10-09 (from the DPAPI file); the password-manager copy: the owner's |
| 18 | The Discord layout bot's token (BRIEF 05): without it the owner runs no plan or apply; the bot's structure is in `discord/layout.toml` | the owner's password manager; for the tool, `%LOCALAPPDATA%Daedalusdiscord-token.dpapi` (DPAPI, this Windows user only: dies with the PC) | the password manager is the copy | 2026-10-09 | rotate: Developer Portal > Bot > Reset Token, update the manager, delete the .dpapi file, run `toolsdiscord-setpass.ps1`. A leak: reset at once |

## Hephaestus's chain, checked (BRIEF 01 Done-when 4)
- **Now (re-read 2026-10-09 ~10:00 UTC):** newest dump `bench-20261009-0945.dump.age` 555,761 bytes, `last_ok`
  2026-10-09T09:45:08Z; the four scripts in `~/bench-register` are LF (`file` no longer says CRLF); cron unchanged (01:00).
- **What happened:** `backup.sh` was redeployed with CRLF line endings at 2026-10-08 19:56 UTC, so the 2026-10-09 01:00 run
  died (`set: pipefail: invalid option name`). Found read-only by BRIEF 01; Hephaestus fixed it with the owner's yes
  (originals in `~/crlf-backup-20261009`) and has an LF guard in `deploy.sh` and a nightly failure alert queued.
- **Owned by Hephaestus, in progress (not Daedalus gaps):** the pull's 26 h gate misses a single lost night; the nightly
  run's own failure alert.
- **The drill stays Hephaestus's** (~7 Nov).

## Slim offsite: what the old 7.2 GB config plan covered, measured (`du`, 2026-10-09)
| Keep offsite (irreplaceable) | MB | Rebuilds itself (leave out) | MB |
|---|---|---|---|
| `/mnt/cache/compose`, `~/bastion-ops` minus `secrets/`, crontabs, `/etc` bits | ~4 | Plex `Metadata` | 3,437 |
| *arr databases + their own scheduled backup zips: sonarr 108, radarr 52, prowlarr 10, bazarr 27, kavita 39, pinchflat 23, audiobookshelf config 7, cleanuparr 21, recyclarr 79, qbittorrent 10 | ~376 | Plex `Media` (thumbnails, previews) | 1,735 |
| Plex: the newest library DB copy (`library.db` 89 + `blobs.db` 238) and `Preferences.xml`: watch history, libraries | ~330 | Plex older DB copies, `Cache`, `Drivers`, `Scanners`, `Logs`, `Codecs` | ~2,000 |
| Homepage, ntfy, diun, hsts, scrutiny config; backrest config **without secrets** | ~5 | *arr `MediaCover` (radarr 563, sonarr 115), kavita `covers` 688, pinchflat metadata 62, audiobookshelf metadata 78, bazarr cache, every `logs/` | ~1,700 |
| **Subtotal** | **~0.7 GB** | | ~8.9 GB |
| Minecraft world `/opt/minecraft/tfg-modern` (static while stopped) | 1,695 | | |

Restic deduplicates, so retention (7d/4w/6m) adds little on top of these. Proposal in BRIEF 01's Handover (gap 15).
