# BRIEF 02: Crusader backs itself up every day - ~/.claude, the plumbing, the KSP saves - and a restore proves it

```
Status:     next
Commits:    -
Track:      safety
Machine:    Crusader
Touch:      tools/ (the backup script and its task definition), docs/BACKUP-MAP.md, docs/RUNBOOK-crusader.md,
            docs/CHANGELOG.md, docs/PLUMBING.md, docs/START_HERE.md (§1); on Crusader, each with the owner's yes and a
            CHANGELOG entry first: restic (winget), one scheduled task, the repos on G:, one scratch restore folder
            (deleted after the check)
Don't touch: KSP_Reborn beyond reading (Calypso's invariant: read-only); the 2025 KSP_Reborn copy on G: (45 craft F:
            lacks: the fresh copy goes next to it, never over it); the restic password (the owner creates it and
            stores it; Claude never sees it); Bastion
Suggested model: opus   (the first standing task on the owner's PC, and a credential-adjacent design)
Effort level:    high   (doubt-driven-development on the script's skip rules and its exclusions before the first run)
Parallel:   no   (it changes a machine)
Owner time: Drive's free space (a glance); a yes each for the install, the task and the one-off copy; creating the
            restic password (~5 min); the attended first run and test restore (~20 min)
Done when:  (1) restic is installed and the repo on G: is initialised, its password in the owner's password manager and
            in the task's protected store, never seen by Claude; (2) the daily task exists, one attended run made a
            snapshot of every source, and its skip rule was shown to skip the KSP saves while KSP_x64 runs (a harmless
            test); (3) a checksum-verified restore of that snapshot (~/.claude and both saves folders) into a scratch
            folder matched, and the folder is deleted; (4) the full KSP_Reborn copy sits on G: next to the 2025 copy,
            with its file count and size matching F:'s; (5) BACKUP-MAP shows gaps 1, 7, 8, 10 and 11 closed or
            narrowed, and the CHANGELOG has every change with its rollback; (6) Calypso had its heads-up before the
            first run
```

## Handover   (last stop: -)
```
State:     not started
Next:      Task 0
Ask owner: -
Dirty:     -
```

## Why
DIRECTION "Success 1", and BRIEF 01's gaps 1, 7, 8, 10 and 11: `~/.claude` (every orchestrator's memory, 941 MB) has
never been backed up. C: and F: are one physical disk (a WD_BLACK SN850X), so one failure loses Windows, the
orchestrators and every KSP save together. The owner's yes, 2026-10-09 (Orchestrator - Daedalus chat), to this brief as
restated: "yes, saves plus the one-off full copy, go", and "G:\My Drive\### Games\KSP" as the KSP backups' home. The
same answer was relayed earlier from Calypso's chat: "yes, tell Daedalus to back up the saves and Reborn".

## Tasks
0. **Check the destination first, read-only.** Measure Google Drive's free space and whether G: streams or mirrors.
   Bastion's old Drive repo was "quota-blocked" in September. If Drive can't hold about 2x the sources, stop and ask
   the owner.
   - **Research before building:** does restic behave on a Drive for desktop folder (lock files, partial uploads)?
     Fallbacks: restic with an rclone backend, or dated zip copies.
1. **The sources.**
   - `~/.claude` without `.credentials.json` or the caches. **The exclusions live in an exclude file** in `tools/`,
     which restic reads with `--exclude-file`. No command or script names the credentials file. That's the owner's
     choice on BRIEF 01's Ask owner 16 (2026-10-09, Orchestrator - Daedalus chat: "yes, exclude file"); the guard stays
     as it is. First check, harmlessly, that the guard lets a command naming only the exclude file through. If it
     doesn't, stop and ask the owner: don't change the guard and don't route around it.
   - `%APPDATA%\Claude\claude_desktop_config.json`;
   - `C:\Users\User\Scripts`;
   - the non-git folders under `C:\- Tools\- LLM`: Olympus, Atlas, Hephaestus's `Claude_UI_UX` and `EU5`. Restic reads
     them; Claude doesn't. `Ubuntu Commands.txt` may hold secrets;
   - `KSP_Calypso\saves` and `KSP_Reborn\saves`.
2. **Where.**
   - `~/.claude` and the plumbing go to `G:\My Drive\daedalus-backups\`.
   - The KSP backups go under `G:\My Drive\### Games\KSP` (owner): the saves to their own repo in `-- BACKUP --`.
     Confirm the exact folder with the owner at the start.
3. **The script and the task.** One script in `tools/`, and one daily scheduled task, at a time when the PC is usually
   on. Keep 14 daily and 8 weekly snapshots.
   - Skip the KSP saves while `KSP_x64` runs or a Calypso brief is deploying to KSP_Calypso. Calypso sends heads-ups
     when BRIEF 26 starts and stops. Send Calypso one before the first run.
   - A missed or failed run raises an alert (ntfy, like the media stack's).
   - The password: the owner creates it, saves it in their password manager, and stores it for the task (e.g. a
     DPAPI-protected file). The script names it by path only.
4. **The first run and the restore,** with the owner present: one run, then a restore of that snapshot into a scratch
   folder, `tools/manifest.py compare`, then delete the folder.
5. **The one-off KSP_Reborn copy.** On an evening without KSP: measure KSP_Reborn, then copy it whole to a new dated
   folder next to `G:\My Drive\### Games\KSP\-- BACKUP --\KSP_Reborn` (the 2025 copy stays), then compare the manifests.
6. **Records.** BACKUP-MAP (the gaps closed), RUNBOOK-crusader (restoring from restic, step by step), PLUMBING (the
   task), START_HERE §1.

## Rollback
- **restic:** `winget uninstall restic`.
- **The task:** the owner removes it in Task Scheduler. Claude is denied `Unregister-ScheduledTask`.
- **The repos on G::** the owner deletes the folders, after confirming nothing else lives there.
- **The KSP_Reborn copy:** the owner deletes the new dated folder. The 2025 copy was never touched.
- **The password:** the owner deletes the protected file and the password-manager entry.
