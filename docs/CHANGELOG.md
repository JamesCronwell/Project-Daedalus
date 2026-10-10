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

## 2026-10-10  Discord (the owner's server)  Stage S9: the stale topic on `the-codex` (planned, session applies)
Brief:     03
Why:       the topic sends people to "the Cadet Room", which no longer exists, from the channel every newcomer reads first
Owner yes: "Fix all you need" (BRIEF 03 chat, 2026-10-10), after the session offered this one-line fix; the other topics
           in the layout are on archived channels or accurate, so nothing else needs it
Before:    `the-codex` topic: "Head over to the Cadet Room for further information"
Change:    topic -> "The house rules. Looking for a group? Head to #muster. Anything else: ask a High Marshal." with the
           `#muster` mention (its id is in the layout). One edit, nothing else
Rollback:  the previous `discord/layout.toml` from git (the S8 commit, 40b2201), `plan`, `apply`
Outcome:   applied by the session (the owner approving the prompts), 1 change; the next `plan` showed 0 changes, 11 yours,
           33 extras

## 2026-10-10  Discord (the owner's server)  Stage S8: the `muster` channel and the squad role names (planned, session applies)
Brief:     03
Why:       a place to ask for a group, with the squad roles pingable there; the squad roles get the Templars theme like the
           ranks and categories
Owner yes: "Yeah go a) / The squad name pass is good" (BRIEF 03 chat, 2026-10-10), to option A and the proposed names
Before:    S7 applied (layout commit 0f4e387); `Aviation Sqd.`, `Survivalist Sqd.`, `Miner Sqd.` and `Pathfinder Sqd.`
           are not mentionable, `HRT // SWAT Sqd.` is; no looking-for-group channel
Change:    create the text channel `muster` in REFECTORIUM under `the-codex` (inherits the category, everyone can post);
           rename Aviation Sqd. to Thunderhawk Wing, Pathfinder Sqd. to Scout Company, HRT // SWAT Sqd. to Assault Squad,
           Survivalist Sqd. to Wardens, Miner Sqd. to Servitors, War Reporter Sqd. to Chroniclers; make the first five
           mentionable (War Reporter stays as it is). Expect 1 create, 6 role edits and a reorder; nothing deleted
Rollback:  the previous `discord/layout.toml` from git (0f4e387), `plan`, `apply`; `muster` stays as an extra for the owner
           to delete by hand (the tool never deletes)
Outcome:   applied by the session (the owner approving the PowerShell prompts), 8 changes: 6 role edits, `muster`
           created, the REFECTORIUM reorder; the next `plan` showed 0 changes, 11 yours, 33 extras (the roles still to be
           deleted by hand)

## 2026-10-10  plumbing: Discord layout tool  A session may run `plan` and `apply` itself (owner's yes)
Brief:     03 (the tool is BRIEF 05's)
Why:       the owner will have only the mobile Claude app for the rest of the day and can't sit at the PC to paste
           commands
Owner yes: "if I approve the modifications you want to do, we're letting you do them" and, to the restated scope,
           "Yes, that's the scope - we'll see what is required on the go today" (BRIEF 03 chat, 2026-10-10)
Before:    the owner ran `plan` and `apply` in their own PowerShell; no session ran the tool
Change:    a session runs them through its PowerShell tool, each permission prompt approved by the owner; CHANGELOG entry
           first, the plan read before `apply`, only a matching plan applied, extras stop the run; the token is never read,
           printed or passed (the tool reads its `.dpapi` file); no deletes, no powerful bits. Docs updated:
           `docs/DISCORD-LAYOUT.md`, BRIEF 03's decision (2)
Rollback:  revert the two doc edits; the owner runs the tool by hand again. A leaked token: Reset Token in the Developer
           Portal, rerun `tools\discord-setpass.ps1`
Outcome:   -

## 2026-10-10  Discord (the owner's server)  Stage S7 and the 33 dead roles (planned, owner applies and deletes by hand)
Brief:     03
Why:       the 33 roles are empty ranks, visual dividers and roles for archived squads; `forge-audit` gives Discord's
           Safety Notifications and the bots' logs one private place; Mention Everyone off the ranks stops an accidental
           `@everyone`
Owner yes: "Do the roles too, then S7. I deleted the categories" (BRIEF 03 chat, 2026-10-10), to the lists in
           `docs/discord/delete-list.md` (sections 2 to 4) and to S7 as proposed (the audit channel; Mention Everyone off
           every rank but `Admin` and the bots' role)
Before:    the S6 layout minus the 12 categories (51 channels, 62 roles); High Marshal, Marshal, Castellan and Emperor's
           Champion hold Mention Everyone; the 33 roles exist, 7 with members (Technical Engineering Sqd. 14, Command
           Room #HP 11, Admin #HP 6, Dungeoneering - Member 4, Temu Worker Sqd. 4, Dungeoneering - Game Master 2, Archives
           #HP 1); no overwrite on a layout channel references them
Change:    (1) the session drops the 33 roles from `discord/layout.toml`, adds the text channel `forge-audit` under FORGE
           (hidden like `forge-log`: `@everyone` denied View, the bot allowed View) and takes Mention Everyone off the
           four ranks; (2) the owner runs `plan` and `apply` (1 channel created, 4 role edits); (3) by hand, the owner
           deletes the 33 roles (Server Settings > Roles), unhooks nothing else: members only lose the labels. The
           sections of old overwrites for O-6 (the "yours" BIT_52 lines) go with the O-6 role
Rollback:  the layout from git (the S6 commit 5cf0fb7, or a30ed07 for the categories); the four ranks' Mention Everyone
           is one tick each; `forge-audit` is the owner's to delete by hand (the tool never deletes); a deleted role
           can't be restored, only recreated and given back to its members by hand
Outcome:   S7 applied by the owner (8 changes: 4 role edits, `forge-audit` created with id 1558414206754103367, 3
           reorders); the next `plan` showed 0 changes, 11 yours, 33 extras (the roles, still to be deleted by hand).
           Open: the 33 role deletions, then a last `plan` for 0 extras; Safety Notifications pointed at `forge-audit`

## 2026-10-10  Discord (the owner's server)  The 12 empty old categories deleted by the owner (planned, owner does it by hand)
Brief:     03
Why:       the squad and command categories were emptied by the archive move (S3); they only clutter the sidebar
Owner yes: "Could I also delete the old categories?" (BRIEF 03 chat, 2026-10-10); the owner deletes them, a session
           never does (the brief's rule)
Before:    12 categories in the layout with no channel in them (`<<< COMMAND STRUCTURE >>>`, `// Administrative Hall //`,
           `// Command Centre //`, `<<< OP. SQUADS >>>`, `// MINECRAFT SQD. //`, `// Dungeoneering //`,
           `// Survivalist Sqd. //`, `// SWAT Sqd. //`, `// Technical Engineering Sqd. //`, `// Aviation Sqd. //`,
           `// Pathfinders Sqd. //`, `<<< OFF-DUTY >>>`); the last `plan` found 0 extras, so the layout matched the server
Change:    the session drops those 12 entries from `discord/layout.toml` (so the tool does not stop on a missing id); the
           owner right-clicks each category > Delete Category after checking it is empty in the sidebar
Rollback:  a deleted category can't be restored; recreate it by name by hand if wanted (nothing referenced them: no
           channel, no webhook, no bot setting). The layout comes back from git (the S6 commit, 5cf0fb7)
Outcome:   -

## 2026-10-10  Discord (the owner's server)  Stage S6: `company-movement-orders` becomes the visible `vox-music-bot` (planned, owner applies)
Brief:     03
Why:       the channel holds the music bot's instructions (owner, 2026-10-10); stage S5's plan moved it back into the
           hidden archive, where nobody can read them
Owner yes: "VOX, read-only" (BRIEF 03 chat, 2026-10-10)
Before:    `company-movement-orders` in ARCHIVUM, hidden from `@everyone` (View and Connect denied), the bot's View allowed
Change:    one channel, same id and history: renamed `vox-music-bot`, moved into VOX, overwrites as the other feeds
           (`@everyone` cannot send; `ADMIN / MECHANIZED TRANSPORT` can). Expect 1 move, 1 rename, a reorder, and the
           overwrite edits; nothing created or deleted
Rollback:  put the previous `discord/layout.toml` back from git (the S5 commit, 7fb2129), `plan`, `apply`
Outcome:   applied by the owner, 6 changes (rename, move, the bot's View overwrite dropped, two overwrites set, the VOX
           reorder); a second `plan` showed 0 changes, 27 yours

## 2026-10-10  Discord (the owner's server)  Stage S5: the Black Templars ladder and the Military x BT names (planned, owner applies)
Brief:     03
Why:       the owner likes the military ranks and chose to compress them into a Black Templars ladder and to theme the
           categories and channels the same way
Owner yes: "Yeah I agree" to the ladder and names table (BRIEF 03 chat, 2026-10-10); Manage Roles off the ranks is the
           owner's standing decision of 2026-10-09 ("every rank loses Administrator, Manage Server, Manage Roles, Kick
           and Ban")
Before:    stages S1-S4 applied (layout commits a4b20d1 and earlier); rank roles `O-10 / General`, `O-9`, `O-8` still hold
           Manage Roles; the nine populated ranks carry their US-military names
Change:    27 edits, all renames except 3 role-bit edits: the nine ranks (O-10 High Marshal, O-9 Marshal, O-8 Castellan,
           O-7 Emperor's Champion, O-3 Chaplain, WO-1 Sword Brother, E-9 Techmarine, E-1 Initiate, E-0 Neophyte), the four
           categories (REFECTORIUM, VOX, FORGE, ARCHIVUM), the Hangout (`refectorium`, `the-codex`, the voice channels
           `Refectorium`, `Cloister`), the nine feeds (`vox-*`) and `forge-log`; Manage Roles off O-10, O-9 and O-8.
           Kick, Ban and Manage Server stay by hand. Nothing created, moved or deleted
Rollback:  put the previous `discord/layout.toml` back from git (the S4 commit), `plan`, `apply`: every name comes back with
           its id, history, webhooks and follows
Outcome:   applied by the owner, 29 changes (the 27 above plus 2: the plan found `company-movement-orders` outside the
           archive and moved it back into ARCHIVUM, with the reorder that follows); a second `plan` showed 0 changes,
           27 yours. The owner then said that channel holds the music bot's instructions, so the move was unwanted:
           it is hidden in ARCHIVUM now and a visible home is being agreed (see BRIEF 03's Handover)

## 2026-10-10  Discord (the owner's server)  BRIEF 03's rebuild applied through the layout tool, under a bounded Administrator window on the bot's role (planned)
Brief:     03 (the tool is BRIEF 05's)
Why:       the old squad channels hide themselves from `@everyone`, so the bot (12 permission bits, no Administrator)
           can't see or edit them: the plan would skip the 8 feeds that must go public and the ~31 channels to archive.
           Administrator on the bot's own role gives it sight of them for the rebuild. The tool still caps what it SETS
           at its 12 bits whatever the bot holds (BOT_PERMS), so Administrator, Manage Server, Kick, Ban, the thread bits
           and removing the ranks' powers stay by hand
Owner yes: "Option 2, bounded admin window - fuck it, let's ball" (BRIEF 03 chat, 2026-10-10), to "a one-time exception to
           the standing narrow bot; ticked for the rebuild session, unticked after"
Before:    "Layout Admin Bot" (managed role, top of the role list) holds exactly the 12 bits of BOT_PERMS, no
           Administrator. The live layout: `discord/layout.toml` at c80d80f (61 roles, 59 channels and categories,
           imported 2026-10-10, 0 member overwrites left out). 6 roles hold Administrator (O-10 to O-6, the bots' role)
Change:    (0) the owner ticks Administrator on the role "Layout Admin Bot" (Server Settings > Roles); (1) four stages,
           each: the session writes the next layout into `discord/layout.toml`, the owner runs `plan`, the session reads
           the plan file, the owner runs `apply`, a second `plan` shows only the "yours" lines, the layout is committed
           (apply writes new ids back): S1 the `Admin` role (no Administrator: by hand), the categories MESS HALL, COMMS,
           ENGINEERING and the forum `engineering-log`, ARCHIVE renamed and given the bot's View; S2 the 15 feed and
           Hangout channels renamed, moved and made read-only; S3 the 31 channels moved to ARCHIVE; S4 the role-bit
           edits the bot can set. By hand, by the owner: Administrator on `Admin` and who holds it, the powers off the
           ranks and the bots' role, the 3 people out of the bots' role, MEE6 and carl-bot removed; (2) the owner
           UNTICKS Administrator on the bot's role, then `import` once more and a last `plan`
Rollback:  untick Administrator on "Layout Admin Bot" at any time (nothing depends on it after an apply). A stage: put
           the previous `discord/layout.toml` back from git, `plan`, `apply` (renames and moves come back with their
           ids; items it created stay as extras for the owner to delete by hand). The before snapshot
           `docs/discord/before-2026-10-09.template.json` holds every overwrite and role bit as it was. A leaked token
           during the window: Developer Portal > Bot > Reset Token, then untick
Outcome:   -

## 2026-10-10  Crusader  Docker Desktop started (not reconfigured) for Hephaestus's BRIEF 62 database tests
Brief:     - (a request from Hephaestus; its BRIEF 62 needs a throwaway local Postgres container, never on Bastion)
Why:       `webapp/api/test_writes.py` needs a local database
Owner yes: standing: "If Hephaestus needs small infrastructure work from you, accept but be mindful of destruction"
           (Orchestrator - Daedalus, 2026-10-10)
Before:    service com.docker.service Stopped, StartType Manual; no "Docker Desktop" process
Change:    start "C:\Program Files\Docker\Docker\Docker Desktop.exe". No setting changed; the start type stays Manual.
           If it hits the old stale-socket error, stop and ask: no folder renames
Rollback:  quit Docker Desktop (tray > Quit); `com.docker.service` back to Stopped
Outcome:   failed at 06:56 UTC, nothing changed. Docker Desktop 4.76.0 shows "An unexpected error occurred": it can't
           remove the stale socket `%LOCALAPPDATA%\Docker\run\dockerInference` ("The file cannot be accessed by the
           system"). The engine never came up, and com.docker.service stayed Stopped. The guard refused to stop the
           hung `docker version` call (a process kill). Waiting for the owner: click Quit in the dialog; the known fix
           is renaming `run` (and `secrets-engine` if needed), the owner's yes first
Step 2:    owner yes "Go for it Daedalus" (Orchestrator - Daedalus, 2026-10-10). Before: `%LOCALAPPDATA%\Docker` holds
           run, plus run.stale-20261008, run.stale2-20261008 and run.stale3-20261008 (three earlier renames on 10-08).
           Change: once Docker has quit, rename `run` to `run.stale-20261010`, then start Docker Desktop again.
           Rollback: quit Docker, rename it back
Outcome 2: `run` renamed to `run.stale-20261010` after the owner quit Docker; the restart then failed on the next
           stale socket, `%LOCALAPPDATA%\docker-secrets-engine\engine.sock` (the owner's screenshot)
Step 3:    the same yes ("run, and secrets-engine if needed"). Before: `%LOCALAPPDATA%` holds docker-secrets-engine
           (engine.sock only) plus .stale-20261008 and .stale2-20261008. Change: once Docker has quit, rename
           docker-secrets-engine to docker-secrets-engine.stale-20261010, then start Docker. Rollback: quit, rename back
Outcome 3: renamed; the restart failed again on `run\dockerInference`, in the fresh `run` folder the previous start
           had created. Each failed start leaves a socket the next start can't remove, so renaming loops. Stopped
           there: Docker is not running, nothing else changed. The renamed folders stay as they are (rollback above if
           wanted). Root cause not found; parked for the owner (docs/IDEAS.md)

## 2026-10-09  plumbing  Global CLAUDE.md: usage habits revised, `/compact` past ~250k instead of the morning `/clear`
Brief:     - (orchestrator; docs/DECISIONS.md, "Usage and the weekly limit")
Why:       Calypso and Hephaestus objected that `/clear` loses the working memory. This session's transcript: re-reading
           the context is 74% of its cost (97% if re-reads count fully), and it grew 70k -> 488k within one day, so
           in-day growth outweighs the overnight carry-over a morning reset targets
Owner yes: "yes, swap it for /compact", 2026-10-09
Before:    the "Usage habits" bullet's first two sub-bullets: "Each morning the owner types `/clear` in each orchestrator
           chat: the same session, ID and pin, with its context back to about 70k." and "Before that, the orchestrator
           appends the day's decisions to its repo's decision log, refreshes its live-state file, and leaves no
           interview half-done."
Change:    those two replaced by: past ~250k the orchestrator says so at a natural break, the owner types `/compact`
           (optional focus line), decisions logged first, no routine `/clear`; the 50% line notes it's live after a restart
Rollback:  put the two quoted sub-bullets back; the file is also in the daily restic backup (BRIEF 02)
Outcome:   done; Calypso and Hephaestus told in one bundled message

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

## 2026-10-09  plumbing  Discord layout tool (BRIEF 05): code only so far; bot and servers not touched yet
Brief:     BRIEF 05
Why:       the owner reshapes the Discord server often; a tool applies layout changes so they aren't done by hand
Owner yes: "yes, that's right, lock it in" (the interview, 2026-10-09); the bot's permission set: "Yes, bot gets those
           too" (2026-10-09). The yes to invite the bot to the TEST server and to the LIVE server is still to be given
Before:    no tool, no bot, no `discord/` folder
Change:    `tools/discord_layout.py`, `tools/discord_layout_test.py`, `tools/discord-setpass.ps1`, `docs/DISCORD-LAYOUT.md`;
           PLUMBING and BACKUP-MAP rows (the token's home). Still to come, with the owner: the Discord application and
           its token (password manager + `%LOCALAPPDATA%\Daedalus\discord-token.dpapi`), the bot joining the test server,
           then the live server (own entry before that invite), and `discord/layout.toml`
Rollback:  revert the commits; the owner deletes the application in the Developer Portal and the .dpapi file
Outcome:   tests green (`python -I tools/discord_layout_test.py`); nothing on any server or machine has changed
Update 2026-10-10: the owner created the bot and its token (password manager + `%LOCALAPPDATA%\Daedalus\discord-token.dpapi`)
           and added it to the owner's TEST server "Soundboard 2" (the owner's own act, in the BRIEF 03 session). The
           owner ran import, plan and apply there: two rounds, only structure on that test server; no deletes. Found and
           fixed one bug (a role that ties the bot's position). The LIVE server is not invited yet: its own entry first

## 2026-10-10  Discord (the owner's server)  The layout bot joins the live server "Mojo Dojo Casa House" (BRIEF 05 task 6)
Brief:     BRIEF 05
Why:       so the owner can import the live layout, then reshape it through plan and apply (BRIEF 03's rounds)
Owner yes: "yes, invite the bot to the live server 818168985383075863" (this session, 2026-10-10)
Before:    the bot is only on the test server "Soundboard 2"; the live server has no layout bot
Change:    the owner adds the bot (View Channels, Manage Channels, Manage Roles, Send Messages, Embed Links, Attach Files,
           Read Message History, Add Reactions, Mention Everyone, Manage Webhooks, Connect, Speak; never Administrator,
           Manage Server, Kick, Ban) and drags its role up. Then ONLY `import` and `check-template` (read-only). No
           plan is applied there in this brief
Rollback:  the owner kicks the bot (Server Settings > Members); its role goes with it. Nothing else changes
Outcome:   done 2026-10-10. The bot joined; the owner ran import (61 roles, 59 channels and categories) and plan (0
           changes, 0 yours, 0 extras). check-template: one difference, the category `// Kerbal Space Program //` with
           its only channel, deleted by hand by the owner. Nothing was applied on the live server. `discord/layout.toml`
           committed after the owner's names check
