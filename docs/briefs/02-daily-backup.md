# BRIEF 02: Crusader backs itself up every day - ~/.claude, the plumbing, the KSP saves - and a restore proves it

```
Status:     waiting-owner
Commits:    -
Track:      safety
Machine:    Crusader
Touch:      tools/ (the backup script and its task definition), docs/BACKUP-MAP.md, docs/RUNBOOK-crusader.md,
            docs/CHANGELOG.md, docs/PLUMBING.md, docs/START_HERE.md (§1); on Crusader, each with the owner's yes and a
            CHANGELOG entry first: restic (winget), one scheduled task, the repos on G:, one scratch restore folder
            (deleted after the check)
Don't touch: KSP_Reborn beyond reading (Calypso's invariant: read-only); the 2025 KSP_Reborn copy on G: (45 craft F:
            lacks: the fresh copy goes next to it, never over it); the restic password (the owner creates it and
            stores it; Claude never sees it); Bastion; `F:\Steam_Modded_Variants\KSP_Coop_A`, `KSP_Coop_B` and
            `LMP_Server` (Calypso's BRIEF 20, throwaway: out of every backup set and out of the saves scope, at
            Calypso's request, 2026-10-09); `calypso_cache` (re-fetchable)
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

## Handover   (last stop: 2026-10-09, the sitting done; waiting on the owner's upload check)
```
State:     The owner's sitting is done (CHANGELOG): repos created, the first run snapshotted every source, restores of
           ~/.claude and both saves verified by restic and MATCHed by manifest (sitting 2, 19:44), scratch folder
           deleted, task "Daedalus daily backup" Ready, daily 13:00. Sitting 1 stopped on a false compare alarm
           (a file-history copy keeps its original's modified date; fixed) and showed the MCP config's real path
           (MSIX: %LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\; fixed). Calypso had its
           heads-up (the orchestrator, after "26 done").
           Done-when: (1) done; (2) done pending the upload check; (3) done pending the upload check; (4) not
           started; (5) records written (BACKUP-MAP rows 1, 3, 4, 5, 17; RUNBOOK-crusader "Restoring from restic";
           PLUMBING; START_HERE §1): gaps 1, 7, 11 closed pending the upload check, 10 narrowed, 8 waits for Task 5;
           (6) done.
           Not yet tested: an ntfy alert actually arriving (a test post is a message: the orchestrator put it to the
           owner). The skip-ksp-saves flag as Calypso's deploy-window switch: **no** (the owner via Calypso, relayed
           by the orchestrator, 2026-10-09: "no flag"): Calypso's deploys write only `GameData\CalypsoKSP` and
           `Ships\Script\calypso`, never saves; its only saves writer is the rare `hangar_copy.py` (worst case one
           partial daily snapshot, healed by the next run); the KSP_x64 rule covers the real risk; deploy heads-ups
           stay messages to the orchestrator. The flag stays only for `backup-owner-setup.ps1 -SkipSaves`.
           Drive quota: G: reports exactly 2.00 TB (1,473 GB used + 527 GB free); the owner says the plan is 5 TB.
           Asked the owner to check which account holds the 5 TB plan (one.google.com/storage) before recording it.
           The 2025 KSP_Reborn copy: keep it until Task 5 and a read-only manifest diff list what only it holds
           (the 45 craft); the owner then keeps what they want and deletes the old copy themselves (proposed to the owner).
           Earlier: owner, this chat, 2026-10-09: "yes A and saves-restic, install it, (a), 13:00". restic 0.19.1 installed
           (CHANGELOG); the exe has no `restic` alias, so tools/backup-restic.ps1 finds it. A scratch-only test (a
           --insecure-no-password repo in the session scratchpad) showed: the anchored $VAR excludes work (top-level
           cache\ and a file dropped, keep\cache kept); dry-run -vv prints `new       /C/x/y, saved in ...`, which
           -CheckExcludes parses; a full-path restore fails ("Access is denied" restoring C:\Users's timestamp, exit 1),
           so the sitting restores by `latest:/C/...` subpath: exit 0, --verify ok, manifest MATCH. Left in the
           scratchpad: `rt\restore\C\Users` may carry C:\Users's ACL (temp, not the owner's folders).
           Option 2 (owner, relayed by the orchestrator): Claude never runs what touches the password. The owner's one
           sitting is `tools/backup-owner-setup.ps1` (password, init, exclusion check, manifests, first run, restore
           --verify, compare, scratch deleted on MATCH, the task: the guard refuses Register-ScheduledTask too). Log:
           %LOCALAPPDATA%\Daedalus\owner-setup.log. The skip rule moved to `tools/backup-skip.ps1` (no secrets).
           Skip test done (Done-when 2's part), 2026-10-09: with a renamed ping.exe as KSP_x64 both saves were
           skipped ("from outside F:\Steam_Modded_Variants"); with the flag file, both skipped; with nothing, both
           backed up. The per-install branch (KSP_x64 from KSP_Calypso: only its saves) isn't tested: a fake there
           would write into Calypso's install. CHANGELOG entries for the install and the sitting written, yes PENDING.
           Earlier: design, relayed by Orchestrator - Daedalus from the owner's answer in its chat ("A, and saves-restic is
           fine", 2026-10-09): backend A, restic straight onto G:; the saves repo at
           `G:\My Drive\### Games\KSP\-- BACKUP --\saves-restic`; plumbing repo `G:\My Drive\daedalus-backups\restic`.
           Drafted, untested, nothing installed: `tools/backup.ps1` (daily run, -DryRun, -CheckExcludes, -Init, -Restic
           passthrough; skip rules; ntfy alerts to topic bastion; forget daily, prune and a 1/8 data check on Sundays),
           `tools/backup-setpass.ps1` (the owner's, DPAPI), `tools/backup-task.ps1` (daily, logged-on only).
           **The guard refuses to run backup.ps1** ("reads a secret from the environment": it sets
           $env:RESTIC_PASSWORD from the DPAPI file). Not worked around, guard unchanged.
           Upload check (the orchestrator's condition for A): no reliable read-only way to tell that DriveFS has
           uploaded a file. No shell property, no alternate stream, no CLI, and its logs are binary
           (structured_log_*). So the owner confirms in the Drive web view (or the app's Sync status) before Done-when
           (2) and (3) count, and the per-run "previous upload finished" line isn't cheaply possible.
           ntfy: https://crusade-bastion.taild871d5.ts.net:2586 is healthy, topic bastion readable without auth
           (GET only; nothing sent).
           Slip: `winget show restic.restic` ran with --accept-source-agreements (read-only show, but that flag
           accepts winget's source terms; reported to the owner).
           Task 0 (earlier): done. G: is Drive for desktop in stream mode (virtual drive, DriveFS 132; no local "My Drive"
           mirror; its cache is %LOCALAPPDATA%\Google\DriveFS on C:, the same physical disk until uploaded).
           G: 527 GB free of ~2 TB; C: 425 GB free. Sources (totals only): ~/.claude ~0.96 GB (BRIEF 01's copy);
           Scripts, Olympus, Atlas tiny; Claude_UI_UX 0.04 GB; EU5 empty; KSP_Calypso\saves 0.15 GB (281 files);
           KSP_Reborn\saves 3.66 GB (668); KSP_Reborn whole 65.21 GB (57,169 files) vs the 2025 copy on G: 60.25 GB
           (56,142). All in, ~70 GB: 2x fits. restic not installed; rclone 1.75.1 is (winget).
           Research: no restic-on-DriveFS corruption reports found; the risks are the sync client's (the Box-folder
           analogue on restic's forum; DriveFS 84.0 lost unsynced files in Nov 2023). Bastion's "quota-blocked"
           Drive repo used rclone and the Drive API; DriveFS uses Google's own client.
           Task 1: `tools/backup-exclude.txt` written (restic --iexclude-file, $USERPROFILE-anchored). The guard lets a
           reading command naming only it through (Get-Content, 2026-10-09). Not yet verified with --dry-run.
Next:      the first unattended run 2026-10-10 13:00 (read backup.log); Task 5 (KSP_Reborn copy) on an evening
           without KSP, with its own yes and CHANGELOG entry; then Done-when (4), and the brief closes
Ask owner: confirm in drive.google.com (or Drive's Sync status) that `daedalus-backups/restic` and
           `### Games/KSP/-- BACKUP --/saves-restic` finished uploading
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
