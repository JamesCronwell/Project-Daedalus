# CHANGELOG: every change to a machine or the shared plumbing

Newest first. Write an entry **before** the change: what, where, why, the owner's yes (quoted, with the date and the
chat), and the rollback. Complete it afterwards with the outcome and how it was checked. A change without a rollback
note doesn't happen.

```
## YYYY-MM-DD  <machine: Crusader | Bastion | plumbing>  <one-line what>
Brief:     NN
Why:       <reason>
Owner yes: "<quote>" (<chat>, <time>)
Before:    <the state it changes, captured: command + output, or a file's backup path>
Change:    <exact commands / files>
Rollback:  <exact steps that restore Before>
Outcome:   <what happened; how it was checked>
```

## 2026-10-09  plumbing  Global CLAUDE.md: the orchestrators' usage habits (morning /clear, decisions first, batched messages)
Brief:     - (orchestrator; the usage discussion, docs/DECISIONS.md)
Why:       an orchestrator's every turn re-reads its whole context, and each message between orchestrators costs the
           receiver one such turn
Owner yes: "Yes go for it" to the wording shown in the Orchestrator - Daedalus chat, 2026-10-09
Before:    `C:\Users\User\.claude\CLAUDE.md`, "# Orchestrators", ended with the get_usage / Sunday bullet
Change:    one bullet, "Usage habits", added at the end of "# Orchestrators" (the wording as shown)
Rollback:  delete that bullet; the file is also in the daily restic backup (BRIEF 02)
Outcome:   done; the bullet was read back after the edit. Calypso and Hephaestus were told in one bundled message

## 2026-10-09  plumbing  Auto-compact safety net at 50% for every Claude Code session (made by the owner)
Brief:     - (orchestrator; the usage discussion, docs/DECISIONS.md)
Why:       sessions have a 1M-token window and auto-compacted only at 97%, so the orchestrators grew all day (346-505k)
           and every turn re-read it all. 50% is a safety net. The owner rejected 30% to protect throughput. The main
           saving is meant to come from the morning `/clear`.
Owner yes: the owner made the change themselves and pasted the result into the Orchestrator - Daedalus chat, 2026-10-09
Before:    `C:\Users\User\.claude\settings.json` `env` held only CLAUDE_CODE_PLUGIN_DIRS and CLAUDE_CODE_PLUGIN_DIR_WATCH;
           each session's readout showed autoCompactsAtPercent 97
Change:    the owner added `"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50"` to that `env` block
Rollback:  the owner removes that line and restarts the Claude app; the readouts return to 97
Outcome:   pending. It applies only to sessions started after the edit (or after an app restart). The check: each
           session's readout shows 50. If it still shows 97 (reported bug: an env block ignored), the fallback is a
           Windows user environment variable of the same name, then an app restart.

## 2026-10-09  plumbing: Discord  Rounds (a)+(b): a new Admin role, and the MESS HALL, COMMS and ENGINEERING categories (planned, owner applies)
Brief:     03
Why:       the owner's Discord server "Mojo Dojo Casa House" is rebuilt around how the group really uses it (BRIEF 03):
           the Hangout, read-only feeds, one private engineering forum, an archive; only one `Admin` role keeps the powers
Owner yes: "yes, write the checklist" to the layout restated in this session (BRIEF 03 chat, 2026-10-09). The session never
           touches the server: the owner applies each step; the session only reads Server Settings afterwards
Before:    the "before" snapshot `docs/discord/before-2026-10-09.template.json` (local, gitignored: it holds members' names;
           template rz3WdmpSVFVQ, 2026-10-09 09:52 UTC). 6 roles hold Administrator (O-10 to O-6 and the bots' role)
Change:    (a) create the role `Admin` (Administrator only) and give it to the 6 holders of O-10 and O-9; (b) create the
           categories MESS HALL, COMMS (read-only for @everyone; the bots' role may send) and ENGINEERING (private, with a
           forum `engineering-log`); rename `// ARCHIVE //` to `ARCHIVE`. Nothing is moved, stripped or deleted in these
           two rounds; (c)-(g) follow, each with its own entry first (docs/discord/checklist.md, local)
Rollback:  remove `Admin` from the 6 and delete the (empty) new categories and forum by hand; rename ARCHIVE back
Outcome:   -

## 2026-10-09  Crusader  The 3 craft only the 2025 KSP_Reborn copy holds, copied out next to it
Brief:     02 (towards retiring the 2025 copy after Task 5)
Why:       a names-only, read-only diff (2026-10-09): of the 2025 G: copy's 292 craft names, 3 are in neither F:'s
           KSP_Reborn (293) nor `KSP_Calypso\saves\Reborn Hangar` (119)
Owner yes: "yes, copy the 3 craft out" (BRIEF 02 chat, 2026-10-09)
Before:    `G:\My Drive\### Games\KSP\-- BACKUP --\KSP_Reborn-2025-only-craft` doesn't exist. The sources, in the 2025
           copy: `saves\USA\Ships\VAB\- INSP\Juno_I_-_Explorer_1.craft` (247,297 B), `saves\USA\Subassemblies\HAPS-1.craft`
           (109,382 B), `saves\USA\Subassemblies\SLS Ascension.craft` (173,220 B)
Change:    Copy-Item of each into `...\-- BACKUP --\KSP_Reborn-2025-only-craft\` under the same relative path; the 2025
           copy is only read; nothing overwritten (the folder is new)
Rollback:  the owner deletes `KSP_Reborn-2025-only-craft`
Outcome:   2026-10-09: all 3 copied, sizes as Before, sha256 of each copy equals its source's. Read Drive's local
           view (the upload is Drive's). Names-only diff: same-named craft may differ in content; the full manifest
           diff after Task 5 covers the rest of the 2025 copy (saves, settings)

## 2026-10-09  Crusader  The owner's sitting: restic password, both repositories, first run, test restore, daily task
Brief:     02 (tasks 3 and 4)
Why:       BACKUP-MAP gaps 1, 7, 10 and 11: a daily, versioned copy of ~/.claude, the plumbing and the KSP saves off the
           C:+F: disk. The owner chose option 2 (relayed by Orchestrator - Daedalus, 2026-10-09): Claude never runs what
           touches the password; the guard also refuses Register-ScheduledTask, so the task is in the same sitting
Owner yes: "yes A and saves-restic, install it, (a), 13:00" (BRIEF 02 chat, 2026-10-09): (a) is one sitting, once
           Calypso's BRIEF 26 is done, with the saves; the task at 13:00 (the script's default). The owner runs it
Before:    no `%LOCALAPPDATA%\Daedalus`; no `G:\My Drive\daedalus-backups\restic`; no
           `G:\My Drive\### Games\KSP\-- BACKUP --\saves-restic`; no task "Daedalus daily backup"
Change:    the owner runs `tools\backup-owner-setup.ps1` in their own PowerShell: stores the password DPAPI-protected at
           `%LOCALAPPDATA%\Daedalus\restic-password.dpapi`; `restic init` both repositories; the exclusion check; the
           first run (`tools\backup.ps1`); restores it into `%LOCALAPPDATA%\Daedalus\restore-check` with `--verify`;
           manifests compared; that folder deleted only on a full MATCH; registers "Daedalus daily backup" (daily,
           logged-on only, hidden). With -SkipSaves it leaves `%LOCALAPPDATA%\Daedalus\skip-ksp-saves`
Rollback:  the owner deletes the task in Task Scheduler; deletes `G:\My Drive\daedalus-backups\restic` and
           `...\-- BACKUP --\saves-restic` (and empties them from Drive's bin), after checking nothing else is in them;
           deletes `%LOCALAPPDATA%\Daedalus` (password file, log, stamps) and the password-manager entry. The sources
           are only read
Outcome:   sitting 1, 2026-10-09 19:38-19:42 (owner-setup.log): password stored; repos created (plumbing 832abfff5e,
           saves ee86e1949c); exclusion check 5538 entries, 0 excluded paths in; first run ok: plumbing ea7e8029
           (4584 files, 1.086 GiB, 521 MiB stored), calypso-saves f0859780 (281 files, 150 MiB), reborn-saves f3f7e346
           (668 files, 3.665 GiB, 458 MiB stored), forget + check "no errors were found" on both; restores of
           ~/.claude and both saves verified by restic; manifests: calypso-saves MATCH 281, reborn-saves MATCH 668,
           ~/.claude "MISMATCH, 1": a file-history copy created at 19:41:20 (between the manifest and the snapshot)
           keeping its original's 19:13 modified date, which the date test missed. Its restored sha256 equals the
           live file's (aa7863b0...). A false alarm: the test now takes the later of created/modified. So the
           scratch folder was kept and the task not registered. Also: the MCP config was "does not exist": the
           desktop app is MSIX, its real path is %LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\
           Claude\ (backup.ps1 fixed). Sitting 2: the owner deletes the scratch folder and runs the script again.
           Sitting 2, 19:43-19:44: "=== BRIEF 02 owner setup: OK ===". Exclusion check 5557 entries, 0 excluded paths
           in; run ok: plumbing 362e2d09 (no "does not exist", no unreadable file: the MCP config is in),
           calypso-saves e2ab6108, reborn-saves 56b51ae1; restores of ~/.claude and both saves verified by restic;
           ~/.claude MATCH 3469 files (2 changed live during the run, by their dates); calypso-saves MATCH 281;
           reborn-saves MATCH 668; scratch folder deleted (checked: `Test-Path` False); task registered:
           `schtasks /query /v`: Ready, daily 13:00, next 2026-10-10 13:00, Interactive only, run as User,
           powershell.exe -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File
           "...\tools\backup.ps1". Upload: the owner's screenshot of Drive for desktop, 2026-10-09 ~20:10: "Up to
           date, Synced 27 minutes ago" (both repos were last written 19:44): off the machine

## 2026-10-09  Crusader  Install restic (winget)
Brief:     02 (task 3)
Why:       the daily backup's tool (backend A: restic straight onto G:, the owner's choice relayed 2026-10-09)
Owner yes: "yes A and saves-restic, install it, (a), 13:00" (BRIEF 02 chat, 2026-10-09)
Before:    `Get-Command restic`: not found. `winget show --id restic.restic --exact`: 0.19.1 available
Change:    `winget install --id restic.restic --exact --scope user --accept-package-agreements
           --accept-source-agreements` (the flags accept restic's BSD-2 license and winget's source terms: part of the
           yes asked)
Rollback:  `winget uninstall --id restic.restic --exact`
Outcome:   installed 2026-10-09 (hash verified by winget): `restic 0.19.1 compiled with go1.26.4 on windows/amd64`.
           winget made no `restic` alias: it added
           `%LOCALAPPDATA%\Microsoft\WinGet\Packages\restic.restic_Microsoft.Winget.Source_8wekyb3d8bbwe` to the user
           PATH (HKCU\Environment, checked with `reg query`), and the exe there is `restic_0.19.1_windows_amd64.exe`.
           tools\backup-restic.ps1 finds it; nothing was renamed

## 2026-10-09  Crusader  One copy of ~/.claude to Google Drive, and a checksum-verified test restore
Brief:     01 (task 3, gap 1 (a))
Why:       ~/.claude (memory, transcripts, settings, tools) had no copy and dies with the C:+F: disk (BACKUP-MAP gap 1)
Owner yes: "Yes, go" to the copy, the restore into %TEMP%\daedalus-restore-test and the checksum compare, the copy left
           on G:, the owner deleting the scratch folder (BRIEF 01 closing session, 2026-10-09)
Before:    `G:\My Drive\daedalus-backups` doesn't exist; G: 528 GB free (1.47 TB used, `Get-PSDrive G`);
           `%TEMP%\daedalus-restore-test` doesn't exist. ~/.claude without cache, session-env, shell-snapshots: 2976
           files, 951 MB
Change:    `powershell -NoProfile -File tools\backup-claude.ps1` (robocopy /E, no mirror, no delete; leaves out
           .credentials.json and the caches) → `G:\My Drive\daedalus-backups\claude\<stamp>` + `<stamp>.manifest.tsv`;
           robocopy that copy → `%TEMP%\daedalus-restore-test\claude`; `python -I tools\manifest.py make` on it, then
           `compare` against the copy's manifest. The guard and the deny list refuse recursive deletes, so the owner
           deletes `%TEMP%\daedalus-restore-test` by hand after the check
Rollback:  the owner deletes `G:\My Drive\daedalus-backups` (and empties it from Drive's bin) and
           `%TEMP%\daedalus-restore-test`. Nothing else changes: the source is only read
Outcome:   copy `G:\My Drive\daedalus-backups\claude\2026-10-09_1418`: 2985 files, 958 MB, + `.manifest.tsv` (2985
           lines). The guard refused the script (it names the credentials file in robocopy's /XF), so the owner ran it
           in their own PowerShell; comm of the file lists: only the credentials file missing, as intended. Restore:
           robocopy 2985 copied, 0 failed; `manifest.py compare` MATCH, 2985 = 2985, 0 missing / extra / differ. It read
           Drive's local copy (proves the copy, not Drive's upload). Scratch folder: deleted by the owner
           by hand, checked gone (`ls` "No such file or directory")

## 2026-10-09  plumbing  Guard hook and a tighter deny list for Daedalus sessions (no machine change)
Brief:     01 (task 0)
Why:       DIRECTION's guardrails: "the boundary lives in code"
Owner yes: BRIEF 01's Touch list ("tools/ (guard hook ...), .claude/settings.json (deny list: tighten only)"), sent with
           "go" by the Daedalus orchestrator (2026-10-09). The hook only refuses; it changes nothing on a machine
Before:    `.claude/settings.json` at 164dbe9: 53 deny rules, no hooks; no `.gitattributes` (Crusader's Git has
           `core.autocrlf=true`, so scripts checked out CRLF)
Change:    `tools/guard.py` + `tools/guard_core.py` as a PreToolUse hook on Bash, PowerShell, Monitor and the Terminal
           panel's run_in_terminal; deny list 53 → 150 rules (none removed), including Edit/Write on the guard, its
           tests and the settings; `.gitattributes` (`* text=auto eol=lf`; CRLF only for .ps1/.cmd/.bat); the guard
           refuses to pipe a CRLF script to a remote host, and `tools/inventory.py` strips CR and sends bytes
Rollback:  `git revert` the BRIEF 01 commit, or the owner removes the "hooks" block from `.claude/settings.json`. Hooks and
           deny rules load when a session starts, so a running session keeps the old ones
Outcome:   classification tests green (`python -I tools/guard_test.py`: 386 refused, 166 allowed, 9 protocol checks,
           fail-closed on a broken rules file, UTF-8 input, a 4 s deadline under the 15 s hook timeout). Three doubt cycles (BRIEF 01's
           Handover). The live check (a fresh session refusing the canaries) is still open: hooks don't load mid-session

## 2026-09-26 .. 2026-10-08  both  Changes made before Daedalus existed (recorded after the fact)
Brief:     - (one-off sessions: "Homepage UI", "Cloudflare backups cleanup", "Bastion", "Cleanuparr Mobland search loop",
           "Computer audit and debloat", "Crusader-Bastion unified control dashboard", "Cleanuparr errors on Sonarr")
Why:       BRIEF 01 task 6: so this log holds what changed on the machines before it existed
Owner yes: given in those sessions; not re-checked
Before:    unknown in detail
Change:    summarised in `docs/RUNBOOK-bastion.md` ("What earlier sessions changed") and `docs/RUNBOOK-crusader.md`
           ("Secrets the rebuild needs"): new containers (Scrutiny, Diun, Kavita, Pinchflat), R2 offsite set up then
           narrowed to the bench dumps (2026-10-03, owner, free tier), 40 OS packages + reboot (2026-10-07), media-stack
           tuning, gbrain 0.54 → 0.60, OneBrain token rotation, Crusader secrets moved to user environment variables
Rollback:  per those sessions' own backups: `Documents\PC-Audit-Backup-2026-10-06`, `~/gbrain-backups/`, the Bazarr and
           Cleanuparr `.bak` files, `~/bastion-ops/patches/`
Outcome:   leads from the orchestrator's read-only summary of the transcripts' last 80 messages; the backup facts were
           checked against Bastion on 2026-10-09 (inventory, `~/bastion-ops/CLAUDE.md`), the rest were not

## 2026-10-09  plumbing  Daedalus repo created (no machine change)
Brief:     -
Why:       the owner's yes to the Daedalus direction (docs/DIRECTION.md), from the Calypso orchestrator's chat
Owner yes: "yes, set up the Daedalus repo" (Calypso orchestrator chat, 2026-10-09)
Before:    `C:\- Tools\- LLM\Daedalus` did not exist
Change:    this repo (docs, `.claude/settings.json` deny list, BRIEF 01); one roster line added to `~/.claude/CLAUDE.md`
Rollback:  delete the folder; remove the roster lines from `~/.claude/CLAUDE.md`
Outcome:   local git repo, first commit 8c1700e; pushed to the private GitHub repo JamesCronwell/Project-Daedalus the same day
