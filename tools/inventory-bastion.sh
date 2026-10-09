#!/usr/bin/env bash
# Read-only inventory of Bastion, run over ssh by tools/inventory.py:  ssh jamescron@crusade-bastion bash -s < this
# Prints "=== section" blocks; inventory.py renders and redacts them. No sudo (it would prompt), no writes, and
# no reading of secrets: files under secrets/, *.env, db_password.txt, the backrest config and rclone config are
# named by path only, never opened.
# BRIEF 01. After Sea's machine_inventory.ps1 (github.com/seatemplar10-dev/Horse-Inner-workings), rewritten here.
export LC_ALL=C.UTF-8
s() { echo "=== $1"; }

s host;      hostname; . /etc/os-release && echo "$PRETTY_NAME"; uname -r; echo "up since $(uptime -s)"
             nproc; awk '/MemTotal/ {printf "%.1f GiB RAM\n", $2/1048576}' /proc/meminfo
s disks;     lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL -e7
s df;        df -h -x tmpfs -x squashfs -x overlay -x efivarfs -x devtmpfs
s fstab;     grep -v '^\s*#' /etc/fstab | grep -v '^\s*$' | awk '{print $2, $3, $4}'
s smart;     ls /mnt/cache/appdata/scrutiny >/dev/null 2>&1 && echo "scrutiny container watches SMART (web UI)"
s memory;    free -h
s services;  systemctl list-units --type=service --state=running --no-legend --no-pager | awk '{print $1}'
s failed;    systemctl --failed --no-legend --no-pager
s timers;    systemctl list-timers --all --no-legend --no-pager | awk '{for(i=1;i<=NF;i++) if ($i ~ /\.timer$/) {print $i; break}}'
s cron_user; crontab -l 2>/dev/null | grep -v '^\s*#' | grep -v '^\s*$'
s cron_system; ls /etc/cron.d /etc/cron.daily /etc/cron.weekly 2>/dev/null
s containers; docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}'
s compose_dirs; docker ps -aq | xargs -r docker inspect --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' | sort | uniq -c
s volumes;   docker volume ls --format '{{.Name}}'
s docker_df; docker system df
s tailscale_serve; tailscale serve status 2>&1
s ports;     ss -tlnH | awk '{print $4}' | sort -u
s backups;   ls -la --time-style=+%F_%R /mnt/backups 2>&1
             echo "-- bench-register dumps (newest 3, last_ok)"
             ls -lt --time-style=+%F_%R /mnt/backups/bench-register/*.dump.age 2>/dev/null | head -3 | awk '{print $6, $5, $7}'
             cat /mnt/backups/bench-register/last_ok 2>/dev/null
             echo "-- restic repos: newest snapshot file, count, size"
             for r in /mnt/backups/restic/*/; do
                 echo "$r $(ls -t --time-style=+%F_%R -l "$r/snapshots" 2>/dev/null | sed -n 2p | awk '{print $6}') $(ls "$r/snapshots" 2>/dev/null | wc -l) $(du -sh "$r" 2>/dev/null | cut -f1)"
             done
             echo "-- state logs (last line each)"
             for f in ~/bastion-ops/state/*.log; do echo "$(basename "$f"): $(tail -1 "$f" 2>/dev/null | cut -c1-160)"; done
             echo "-- health problems"; cat ~/bastion-ops/state/health.problems 2>/dev/null
s line_endings; for f in ~/bench-register/*.sh ~/bastion-ops/scripts/*.sh; do
                 file "$f" | grep -q CRLF && echo "CRLF: $f"; done; echo "(checked)"
s home;      ls -la --time-style=+%F ~ | awk 'NR>1 {print $6, $7}'
s sizes;     du -sh ~/bench-register ~/bastion-ops /mnt/cache/appdata /mnt/cache/compose /var/lib/docker/volumes/bench-register_pgdata 2>/dev/null
s secrets_by_path; ls -d ~/bastion-ops/secrets ~/bench-register/db_password.txt /mnt/cache/appdata/backrest/config /mnt/cache/appdata/backrest/rclone ~/.ssh 2>/dev/null
s packages;  dpkg-query -W -f '${binary:Package}\n' 2>/dev/null | wc -l; snap list 2>/dev/null | awk 'NR>1 {print $1}' | tr '\n' ' '; echo
s updates;   cat /var/run/reboot-required 2>/dev/null || echo "no reboot required"
s generated; date -Is
