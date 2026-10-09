# BRIEF 01: Safety net - guardrails in code, an inventory of both machines, a proven backup map and a rebuild runbook

```
Status:     waiting-owner: the attended ~/.claude backup + test restore (Done-when 4); the live guard check in a
            fresh session after the merge (Done-when 1)
Commits:    -
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

## Handover   (last stop: 2026-10-09, session on branch claude/goofy-lumiere-32bf51)
```
State:     Tasks 0, 1, 2, 4, 5, 6 done; task 3 waits for the owner. Done-when: (2) (3) (5) (6) green; (1) and (4) open.
           (1) guard: 386 refuse / 166 allow / 9 protocol cases green (`python -I tools/guard_test.py`); the hook's own
               command line run by hand refuses a destructive ssh line (exit 2) and passes `ls` (exit 0). Hooks and new
               deny rules load only when a session starts, so the live check in a session is still to do. The old deny
               rules load (`dd --version` was denied in this session).
           (2) `python -I tools/inventory.py` regenerates docs/inventory/{crusader,bastion}.md read-only, redacted.
           (4) Hephaestus's chain checked (BACKUP-MAP.md). The ~/.claude restore can't run: there is no backup (gap 1).
           Doubt-driven development on the guard: 3 cycles, a fresh Opus reviewer each (cycle 1: 26 misses, cycle 2: 14
           miss classes + 4 false-block classes, cycle 3: 15 findings incl. the hook reading stdin as cp1252 and
           `git -C "<quoted path>"` hiding the subcommand); every actionable finding fixed and in the tests. Stopped at
           3 cycles as the method says. Accepted limits are in guard_core.py's docstring and Ask owner 14. Single-model
           findings only: the Codex second opinion wasn't offered (no owner in this chat).
           Found and handed over: bench-register's backup.sh was CRLF since a 2026-10-08 redeploy, the 10-09 dump
           failed; Hephaestus fixed it with the owner's yes (dump 2026-10-09 09:45).
           Sea's repo couldn't be cloned (the auto-mode classifier blocked it as untrusted code): the tools were written
           here from scratch, after Sea's design.
Next:      1. Fresh session on main after the merge: run the canaries (Done-when 1) with harmless strings, e.g.
              `ssh -o ConnectTimeout=2 guard-canary.invalid 'rm -rf /tmp/daedalus-guard-canary'` (an unresolvable host)
              and `find "$TEMP/daedalus-canary-does-not-exist" -delete` (a missing folder); both must say "Daedalus guard:
              refused". `shred --version` must be denied by the new deny list.
           2. With the owner present: gap 1 (a), then the test restore: `tools/backup-claude.ps1` once, restore that copy
              into `%TEMP%\daedalus-restore-test`, `python -I tools/manifest.py compare <copy>.manifest.tsv <restored>.tsv`,
              then delete the scratch folder (the owner's yes covers it).
           3. Then BRIEF 01 is done: Status, shas, move to done/.
Ask owner: (each one's own yes; "owner/Cerberus" = security, never Daedalus's)
           1. gap 1, ~/.claude has no backup (941 MB, 3016 files; dies with the C:+F: disk). (a) now, attended: one copy
              with tools/backup-claude.ps1 to G:\My Drive\daedalus-backups\claude (leaves out .credentials.json and caches)
              and the test restore above. (b) standing, recommended: restic (`winget install restic`) with a repo on G:,
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
           8. gap 9, repos: WH40K has 180 uncommitted files (tell Hephaestus); Daedalus main is 7 commits ahead of GitHub
              (push)
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
Dirty:     none on the machines. Scratch: this session's scratchpad only (guard test inputs); no restore folder yet
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
