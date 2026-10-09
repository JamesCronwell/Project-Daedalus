# RUNBOOK: Bastion, rebuild from zero

Ubuntu 24.04.5 server `crusade-bastion` (8 threads, 31 GiB), user `jamescron`, reached as
`ssh jamescron@crusade-bastion` over Tailscale (LAN 192.168.50.181). Facts come from `docs/inventory/bastion.md`
(regenerate before relying on it) and `docs/BACKUP-MAP.md`. Written 2026-10-09, BRIEF 01. Times are estimates.
The bench-register app is Hephaestus's: its deploy and restore are run from the Hephaestus chat with the owner's yes.

## If this disk died tonight
| Disk | Lost for good (today) | Comes back from | Time to restore |
|---|---|---|---|
| **250 GB NVMe: `/`** (OS, `/home`, Docker volumes) | bench-register writes since the last good dump (today: since 2026-10-08 01:00, because backup.sh is broken); anything in `/home` that restic doesn't cover (gbrain? the audit scripts); Tailscale node identity (re-login) | the dumps on `/mnt/backups` or G: (age key needed); configs from restic on `/mnt/backups`; the WH40K repo (app) | ~4 h: Ubuntu 1 h, Docker + mounts 30 min, restic restore of `~/bastion-ops` and `/etc` bits 30 min, bench-register deploy + DB restore 1 h (Hephaestus), Tailscale serve 30 min |
| **1 TB NVMe: `/mnt/cache`** (`compose/`, `appdata/`) | appdata changes since the last restic snapshot (6-hourly; 2026-10-09 06:00) | restic `/mnt/backups/restic/bastion` (or R2 if that disk died too) | ~2 h: restore `appdata` + `compose`, `docker compose up -d` |
| **3 TB Seagate: `/mnt/backups`** | the local dump history (14 nightly + weekly) and the local restic history | nothing on-box; offsite: G: (newest 14 pulled dumps) and R2 (restic) | the live data is untouched; ~1 h to put a new disk in and re-seed (backrest re-init, backup.sh run) |
| **12 TB WD: `/mnt/storage`** | the media library (8.6 TB) | re-acquired through Sonarr/Radarr/Prowlarr | days of downloads |

## Rebuild order
1. **Ubuntu Server 24.04** on the 250 GB NVMe; user `jamescron`; OpenSSH; the owner adds Crusader's public key.
2. **Mounts:** recreate `/etc/fstab` from the restic copy (`/sources/etc/fstab`) or from the inventory:
   `/mnt/cache` ext4 `defaults,noatime`; `/mnt/storage` ext4 `defaults,noatime`; `/mnt/backups` ntfs-3g
   `defaults,uid=1000,gid=1000,umask=022,nofail`.
3. **Docker Engine + compose plugin**; Tailscale (`tailscale up`, owner logs in; MagicDNS name `crusade-bastion`).
4. **Restore configs** from restic (backrest's repo `/mnt/backups/restic/bastion`, or R2 if `/mnt/backups` is gone; the
   repo password and R2 keys come from the owner's password manager): `appdata`, `compose`, `bastion-ops`, crontabs,
   `/etc/docker`, `/etc/systemd/system`, `/etc/sudoers.d`, `/etc/cockpit`, Minecraft.
5. **Media stack:** `cd /mnt/cache/compose && docker compose up -d` (20 containers: Plex, *arr, qBittorrent, Homepage,
   backrest, ntfy, scrutiny, dozzle, ...).
6. **bench-register (Hephaestus):** `deploy.sh` from the WH40K repo, then restore the newest dump: decrypt the `.age`
   with the owner's private key, `pg_restore` into the new `db` container. Hephaestus runs this.
7. **Crontab** (`crontab -l` is in the inventory): `backup.sh` 01:00, `restore_test.sh` monthly, `healthcheck.sh` every
   15 min, `mc-backup.sh` 6-hourly, `tfg-update-check.sh` 09:15.
8. **Tailscale serve:** re-create each mapping listed in `docs/inventory/bastion.md` ("Tailscale serve"): ports
   443 (/ → 8420, /hsts → 8081), 2586 (ntfy), 5000, 6767, 8082, 11011, 13378, and the rest listed.
9. **Check:** `python -I tools/inventory.py bastion` from Crusader and diff it against the last committed inventory;
   Homepage's widgets green; the healthcheck's `state/health.problems` empty.

## SSH keys-only (harden-5): the owner's steps. DRAFT, OWNER TO VERIFY
Security is the owner's (Cerberus later). Daedalus never runs this; it only wrote these steps after reading
`~/bastion-ops/prep/harden-5.sh` (2026-09-26, 31 lines) on 2026-10-09. Check each step yourself before running anything.

What the script does: refuses to run unless `~/.ssh/authorized_keys` holds at least 2 keys (or `--force`); writes
`/etc/ssh/sshd_config.d/10-keys-only.conf` (`PasswordAuthentication no`, `KbdInteractiveAuthentication no`,
`PermitRootLogin no`, `X11Forwarding no`; `10-` sorts before `50-cloud-init.conf`, which turns passwords on, and sshd
keeps the first value it reads); runs `sshd -t`; reloads ssh; prints the effective settings.

1. **The phone's key.** On "atlas" (the Android phone), in the SSH app (Termius, JuiceSSH or ConnectBot), generate an
   ed25519 key and copy its **public** key. On Bastion, from Crusader's working key session, append it as one line to
   `/home/jamescron/.ssh/authorized_keys`. Then `grep -cE '^(ssh-|ecdsa-|sk-)' ~/.ssh/authorized_keys` should say 2 or more.
2. **Prove key login before anything changes.** From the phone, log in with the new key (password login is still on, so
   check that the app really used the key: most apps say so, or try it with the password field empty). From Crusader,
   `ssh -o PreferredAuthentications=publickey jamescron@crusade-bastion` must work too.
3. **Keep a lifeline open.** Open one SSH session from Crusader and **leave it open** for the whole change. Do the rest in
   a second session.
4. **Run it** in the second session: `sudo bash ~/bastion-ops/prep/harden-5.sh`. Read the "Effective:" line: it should
   show `passwordauthentication no`, `permitrootlogin no`, `x11forwarding no`.
5. **Test fresh logins** from Crusader and from the phone, each as a new connection, while the lifeline stays open. Also
   check a password login is now refused (e.g. `ssh -o PubkeyAuthentication=no jamescron@crusade-bastion` should fail).
6. **Only then** close the lifeline.

**Roll back** (from the lifeline, or the console if every session is gone):
`sudo rm /etc/ssh/sshd_config.d/10-keys-only.conf && sudo systemctl reload ssh`. Then password login is back as before.

**Two things to check before you run it** (Daedalus's reading, unverified):
- If `sshd -t` fails, the script stops (`set -e`) **after** writing the file and before the reload, so the running sshd is
  unchanged, but the file stays and would break sshd at the next restart or reboot. If that happens, remove the file
  straight away (the rollback line) before anything restarts ssh.
- Ubuntu 24.04 can run ssh socket-activated (`ssh.socket`). The script's `systemctl reload ssh` assumes `ssh.service`
  is running; check `systemctl status ssh ssh.socket` first, and after step 4 confirm the settings with `sudo sshd -T`.

## What earlier sessions changed (before Daedalus, from the orchestrator's notes of their transcripts)
Leads only, checked where it says so. Sessions: "Homepage UI" (09-26), "Bastion RAM/HDD usage" (09-27, read-only),
"Cloudflare backups cleanup" (10-03), "Bastion" (10-05), "Cleanuparr Mobland search loop" (10-06), "Computer audit and
debloat" (10-06, both machines), "Crusader-Bastion unified control dashboard" (10-07), "Cleanuparr errors on Sonarr"
(10-08).
- **Containers added 09-26:** Scrutiny (disk health, a 15-min watchdog alerts on a flagged disk), Diun (daily image-update
  check to ntfy), Kavita, Pinchflat. Confirmed in the inventory.
- **Backups:** R2 offsite set up 09-26, narrowed to the bench dumps on 10-03 (owner, free tier). The Google Drive restic
  repo was dropped on 09-26 (its data still sits in `G:\My Drive\bastion-restic`). Confirmed against `~/bastion-ops/CLAUDE.md`.
- **10-07, via the control panel:** 40 OS packages (kernel 6.8.0-146, Docker 29.8.2), reboot at ~16:02 UTC (`uptime -s`
  confirms), old kernel 6.8.0-139 removed; Minecraft start-at-boot off; RAPL power permissions re-applied by a udev rule.
- **Media stack tuning:** Sonarr/Radarr upgrades, qBittorrent disk I/O POSIX (RAM ~290 MB), release profiles blocking
  fake ".exe" and ETHEL releases, Cleanuparr cleanup; 49 zero-header files still in the library (~1,600 Bazarr errors a
  day: the owner's).
- **gbrain** upgraded 0.54.1.1 → 0.60.95.0 on 10-06; backup `~/gbrain-backups/gbrain-0.54.1.1-20261006-1745.tgz`.
- **Owner/Cerberus items** (named, not acted on): qBittorrent reachable without a password from LAN and tailnet; SSH
  password login on (harden-5 above); Bazarr's login empty; the OneBrain token rotated 10-06; an rclone token for the
  dropped Drive repo still in backrest's `rclone.conf`.
