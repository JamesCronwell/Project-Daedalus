# BRIEF 01: Safety net - guardrails in code, an inventory of both machines, a proven backup map and a rebuild runbook

```
Status:     done (2026-10-09): all six Done-when green
Commits:    0b05cee (tools, docs, guard), 075eff0 (sha, inventory CR fix), b5d09c7 (merge to main); the closing commit
            (Done-when 1 and 4, the move to done/) is the one that adds this line
Track:      safety
Machine:    both
Touch:      tools/ (guard hook, inventory, manifest, secret scan), .claude/settings.json (deny list: tighten only),
            docs/inventory/ (generated), docs/RUNBOOK-crusader.md, docs/RUNBOOK-bastion.md, docs/CHANGELOG.md,
            docs/START_HERE.md (§1, §6); one scratch restore folder outside every repo (deleted after the check)
Don't touch: anything on either machine beyond reading, except the scratch restore folder; Hephaestus's backup script
            and its drill (verify them, don't run or change them); project repos; ~/.ssh keys and any token or .env
Suggested model: opus   (planning, and the first reach into Bastion)
Effort level:    high   (the guard is a safety boundary: doubt-driven-development on it before commit)
Parallel:   no   (the first session on the machines)
Owner time: the Bastion SSH alias (or a yes to read ~/.ssh/config host names); one attended test restore of ~/.claude
            into the scratch folder (~15 min); reading the gap list (~10 min)
Done when:  (1) the guard hook refuses a destructive command (locally and inside an ssh command) in a harmless test,
            and the deny list loads; (2) the inventory script regenerates docs/inventory/crusader.md and bastion.md
            read-only; (3) the backup map lists every item that would hurt to lose, with where its copy is, its age and
            whether a restore was ever tested; (4) a checksum-verified test restore of ~/.claude has run, and
            Hephaestus's database chain has been checked (the last dump's age and size; its restore drill stays
            Hephaestus's, ~7 Nov); (5) RUNBOOK-crusader.md and RUNBOOK-bastion.md answer "if this disk died tonight:
            what is lost, and how long is the restore"; (6) every gap has a proposed fix in Ask owner
```

## Handover   (last stop: 2026-10-09, closing session on main)
```
State:     DONE. Tasks 0-6 done; Done-when (1)-(6) green.
           (1) live, in a fresh session on main at 6d8070d: the hook refused `ssh -o ConnectTimeout=2 guard-canary.invalid
               'rm -rf /tmp/daedalus-guard-canary'` (recursive delete) and `find "$TEMP/daedalus-canary-does-not-exist"
               -delete` (find with delete), both "Daedalus guard: refused". `shred --version` was refused by the hook
               first, so the deny list was shown separately: `nft list ruleset` passes the guard (read-only) and was
               denied by the new `Bash(nft:*)` rule. (A Read of a nonexistent `.netrc` in the scratchpad wasn't denied:
               inconclusive, the existence check or the `**` glob outside the project may come first.) Unit tests as before:
               386 refuse / 166 allow / 9 protocol (`python -I tools/guard_test.py`).
           (2) `python -I tools/inventory.py` regenerates docs/inventory/{crusader,bastion}.md read-only, redacted.
           (4) Hephaestus's chain checked (BACKUP-MAP.md). ~/.claude: G: had 528 GB free; with the owner's yes the copy
               went to `G:\My Drive\daedalus-backups\claude\2026-10-09_1418` (2985 files, 958 MB, + `.manifest.tsv`).
               The guard refused `tools/backup-claude.ps1` (it names the credentials file in robocopy's /XF exclusion),
               so the owner ran it in their own PowerShell. Restored by robocopy into `%TEMP%\daedalus-restore-test`
               (2985 copied, 0 failed); `manifest.py compare` MATCH: 2985 = 2985, 0 missing / extra / differ. The
               restore read Drive's local copy, so it proves the copy, not Drive's upload. The copy stays on G:; BRIEF
               02 decides whether it stays. The owner deleted the scratch folder by hand (the guard refuses recursive
               deletes); checked gone.
           Doubt-driven development on the guard: 3 cycles, a fresh Opus reviewer each (cycle 1: 26 misses, cycle 2: 14
           miss classes + 4 false-block classes, cycle 3: 15 findings incl. the hook reading stdin as cp1252 and
           `git -C "<quoted path>"` hiding the subcommand); every actionable finding fixed and in the tests. Stopped at
           3 cycles as the method says. Accepted limits are in guard_core.py's docstring and Ask owner 14. Single-model
           findings only: the Codex second opinion wasn't offered (no owner in this chat).
           Found and handed over: bench-register's backup.sh was CRLF since a 2026-10-08 redeploy, the 10-09 dump
           failed; Hephaestus fixed it with the owner's yes (dump 2026-10-09 09:45).
           Sea's repo couldn't be cloned (the auto-mode classifier blocked it as untrusted code): the tools were written
           here from scratch, after Sea's design.
Next:      BRIEF 02 (Status `next`). Its scripts will hit Ask owner 16 below: decide that before BRIEF 02's first run.
Ask owner: (each one's own yes; "owner/Cerberus" = security, never Daedalus's)
           16. NEW, before BRIEF 02: the guard refuses any command or script that names the credentials file, even only
              to leave it out (robocopy /XF, a Where-Object name filter), so Daedalus can't run tools/backup-claude.ps1
              and BRIEF 02's restic excludes will be refused the same way. Options: (a, recommended) the owner changes
              guard_core.py so a secret file's name after an exclusion flag (robocopy /XF, restic/rsync --exclude,
              `--exclude-file`) isn't a read, with tests; a fresh session picks it up. (b) BRIEF 02 keeps the excludes
              in an exclude file the scripts point at, never naming the file in a command (the guard still reads
              scripts; check whether it reads exclude files). (c) the owner runs each backup command by hand. Changing
              the guard is the owner's (Edit/Write are denied on it). Also noted, no change proposed: `-Recurse -Force`
              on a read-only listing and `>` into the scratchpad are refused too; pipes and Bash `find` work
           1. gap 1, ~/.claude: (a) DONE 2026-10-09, one copy on G: and a matched test restore (State (4)).
              (b) standing, recommended, now BRIEF 02: restic (`winget install restic`) with a repo on G:,
              a daily scheduled task, keep 14 daily / 8 weekly, password in your password manager; covering ~/.claude,
              %APPDATA%\Claude\claude_desktop_config.json, C:\Users\User\Scripts, the non-git LLM folders (gap 10) and
              the KSP saves (gap 7)
           2. gap 7, KSP saves (Reborn Hangar...) have no copy off F:: add KSP_Calypso\saves to (1b), skipped while
              KSP_x64 runs. Calypso gets told first
           3. gap 8, the KSP_Reborn copy on G: is from 2025 (F:'s copy changed 2026-04-10): measure its size on an evening
              without KSP, then a fresh copy to G:
           4. gap 15, Bastion configs + Minecraft have no offsite (accepted risk since 10-03). Proposal: a slim R2 plan,
              ~0.7 GB of irreplaceable configs (BACKUP-MAP.md's table) + 1.7 GB Minecraft = ~2.5 GB, inside a 3 GB budget
              of R2's 10 GB. Option B: G:, pulled by a Crusader task like Hephaestus's dump pull (only when the PC is on).
              Recommend R2
           5. gap 3, /mnt/backups is one ST3000DM001 (~4.5 years on) holding both on-box copies: keep Scrutiny's watch
              and budget a replacement disk; 4 lowers the stakes
           6. gap 6, the age private key: confirm it's in your password manager (without it no dump can be restored)
           7. gap 5, G:\My Drive\bastion-restic is the dropped Drive repo (0 snapshots): yours to delete or keep
           8. gap 9, repos: WH40K has 180 uncommitted files (tell Hephaestus); Daedalus main: the orchestrator now
              pushes it (owner, 2026-10-09); it matched origin/main at this session's start
           9. gap 11, plumbing outside any repo (~/.claude/CLAUDE.md, settings.json, claude_hours.py, night-mode.*, the
              MCP config): covered by 1b; also mirror CLAUDE.md into this repo on each change?
           10. gap 16, gbrain on Bastion (~/gbrain-vault, ~/.gbrain) isn't in backrest's sources: add to config-daily?
           11. gap 12, the last Bastion config restore test was 2026-09-26: a quarterly attended restic restore test?
           12. gap 14, the 8.6 TB media library has no copy (re-acquirable): accept?
           13. gap 13, E: TEXTURES: anything on it irreplaceable?
           14. the guard is a seatbelt, not a wall (a pattern list can't be complete against an agent set on dodging it).
               For a real wall on Bastion: a restricted key for Daedalus (`command="<read-only script>",restrict` in
               authorized_keys) so it can only run reviewed read-only commands: owner/Cerberus. Changing the guard
               later is yours too (Edit/Write are denied on it)
           15. Sea's repo: clone it yourself into a scratch folder (or allow it) if you want Sea's tools compared
           owner/Cerberus, named only: qBittorrent without a password on LAN/tailnet; SSH password login (harden-5,
           steps drafted in RUNBOOK-bastion.md, "DRAFT, OWNER TO VERIFY"); Bazarr's empty login; the dropped Drive
           repo's rclone token still in backrest's rclone.conf; MY_ACCESS_TOKEN (no file, config or task names it)
           Hephaestus's, in progress: the LF guard in deploy.sh, a nightly failure alert, the 26 h pull gate missing one
           lost night
Dirty:     on Crusader: the copy `G:\My Drive\daedalus-backups\claude\2026-10-09_1418` (+ manifest), kept on purpose.
           Scratch folder `%TEMP%\daedalus-restore-test`: deleted by the owner, checked gone. Nothing else changed on either machine
```

## Why
DIRECTION "Success 1": the safety net comes before any improvement. An agent that improves things before it knows what
is backed up is how every project gets nuked.

## Tasks
0. **Guardrails in code first.**
   - A PreToolUse guard hook for Bash and PowerShell. It refuses destructive patterns anywhere in the command, including
     inside `ssh ... '<cmd>'`: recursive deletes, disk and partition tools, `reg delete` / `reg add`, firewall and
     service changes, `docker system prune` and volume removal, forced pushes, `chmod`/`chown -R`, shutdown and reboot.
   - Review `.claude/settings.json`'s deny list (tighten only).
   - Test with harmless strings, then run doubt-driven-development on it.
   - Reference: Sea's safety design, which says boundaries live in code (horse-guard.js, ro_barrier.ps1).
1. **Inventory, read-only, script-generated.** Start from Sea's tools (machine_inventory.ps1, manifest.py,
   secret_scan.py, redact_configs.py) in https://github.com/seatemplar10-dev/Horse-Inner-workings. It's private: clone
   it with the owner's GitHub access into a scratch folder. Sea gave permission: "we can use this freely". Note their
   origin in a comment.
   - **Crusader:** OS and drives (free space), installed programs, services, startup items, scheduled tasks, and
     WSL/Docker if present.
   - **Bastion:** distro, disks, services, containers, cron and systemd timers, Tailscale serve, open ports (read
     only).
   - No secrets in the output; redact before writing.
2. **The backup map.** Per item: where its copy is, how old, restore ever tested?
   - `~/.claude` (memory, transcripts, settings, `tools/`).
   - The repos (GitHub remotes; any unpushed work).
   - F: (`Steam_Modded_Variants`: the KSP installs, the CKAN cache, `calypso_cache`).
   - G: Drive backups (the KSP_Reborn backup; Hephaestus's pulled dumps).
   - Bastion: Hephaestus's BRIEF 50 chain (nightly pg_dump, weekly copies, age, the pull to G: by a Crusader scheduled
     task), the media stack's config, Homepage, the Cloudflare backups.
3. **The test restore.** Restore `~/.claude` from its backup into the scratch folder and compare checksums
   (manifest.py), with the owner present. If no backup exists, that's gap #1. Then propose the backup, don't make it.
4. **The runbooks.** RUNBOOK-crusader.md and RUNBOOK-bastion.md: rebuild from zero, in order, with what's lost and the
   time to restore.
5. **The plumbing map.** In START_HERE or a short `docs/PLUMBING.md`:
   - `~/.claude/CLAUDE.md`, `~/.claude/settings.json`, `~/.claude/tools/claude_hours.py`;
   - the MCP servers (and roughly what each costs per session);
   - the Startup items and scheduled tasks the projects created (Calypso's session watcher, BRIEF 14);
   - `C:\Users\User\Scripts\night-mode.*`;
   - the app's keep-awake setting;
   - how orchestrators reach each other (SendMessage).
6. **What was done before.** Earlier one-off sessions touched these machines: "Computer audit and debloat", "Bastion
   RAM/HDD usage investigation", "Crusader-Bastion unified control dashboard", "Cloudflare backups cleanup",
   "Cleanuparr" and "Homepage UI".
   - Ask the Daedalus orchestrator for their outcomes. It can read their transcripts' ends; this session doesn't.
   - `C:\- Tools\- LLM\Olympus\Ubuntu Commands.txt` is the owner's server notes. Ask before reading: it may hold secrets.

## Rollback
- The only writes are this repo and the scratch folder (deleted after task 3). Nothing on either machine changes in this
  brief.
- Every fix it finds is proposed, not applied.
