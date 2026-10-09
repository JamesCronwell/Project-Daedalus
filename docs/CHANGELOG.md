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
Outcome:   -

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
