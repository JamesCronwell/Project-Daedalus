# BRIEF 01: Safety net - guardrails in code, an inventory of both machines, a proven backup map and a rebuild runbook

```
Status:     next
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

## Handover   (last stop: 2026-10-09, written at repo setup by the Calypso orchestrator)
```
State:     not started
Next:      Task 0
Ask owner: -
Dirty:     -
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
