# PLUMBING: what every orchestrator relies on

The shared pieces Daedalus maintains (DIRECTION: "the plumbing"). Checked 2026-10-09, BRIEF 01. A change to any of
these follows START_HERE §4: the owner's yes, a CHANGELOG entry with its rollback first, and a heads-up to the
orchestrators that use it.

## Files
| What | Where | Used by | Maintainer | Copy |
|---|---|---|---|---|
| Global instructions | `~/.claude/CLAUDE.md` | every session | Daedalus (owner's yes per change) | none outside `~/.claude` (gap 11) |
| Global settings | `~/.claude/settings.json`: `defaultMode: auto`; `CLAUDE_CODE_PLUGIN_DIRS` = WH40K's `wh40k-band` and Calypso's `calypso-band` mods, `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` | every session | Daedalus; each band's content is its project's | none (gap 11) |
| Claude hours | `~/.claude/tools/claude_hours.py` (Calypso BRIEF 14, shared with Hephaestus: both read the installed copy) | Calypso, Hephaestus | Daedalus | the projects' repos hold the source |
| Night mode | `C:\Users\User\Scripts\night-mode.cmd` + `.ps1`: puts the displays into standby after 3 s, changes no setting | the owner | Daedalus | none (gap 11); the monitor-flash follow-up is in IDEAS |
| MCP servers (desktop app) | `%APPDATA%\Claude\claude_desktop_config.json`: **horse** (`WH40K\bridge-kit\mcp\lmstudio_proxy.py`, a proxy to LM Studio), **onebrain** (`~\.local\bin\onebrain-mcp.cmd`), **graphify** (`graphify-mcp.exe` on `WH40K\graphify-out\graph.json`) | every session | Daedalus owns the config; each server's code is its project's | none (gap 11) |
| Permission guard (this repo only) | `.claude/settings.json` deny list + `tools/guard.py` hook | Daedalus sessions | Daedalus, owner-only edits | git |

`~/.claude.json` has no user-level MCP servers; `~/.claude/skills` has `graphify`. The decision skills
(doubt-driven-development, interview-me) live in Calypso's and WH40K's repos only (IDEAS: one shared copy).

## What MCP costs a session (rough)
The app loads most MCP tools deferred: a session pays for the tool names and each server's instructions until it loads a
tool. onebrain is the heaviest by far (~150 tools and a long instruction block); graphify ~11 tools; horse 3; the app's
own (computer-use ~27, Chrome ~22, browser, terminal, scheduled tasks, session management) are the app's. Measuring it
properly is IDEAS' "MCP and plugin token cost" (habits stretch).

## Startup items and scheduled tasks the projects created (Crusader)
| Item | Kind | Runs | Created by |
|---|---|---|---|
| `CalypsoSessionLog.lnk` → `powershell.exe` (`games\ksp\tools\sessionlog.ps1`, the KSP session watcher) | Startup folder | at logon | Calypso BRIEF 14: **installed** (seen 2026-10-09) |
| `Horse LLM Server.lnk` → `wscript.exe` | Startup folder | at logon | Sea's horse / the LM Studio bridge |
| "WH40K Backup Pull" (`WH40K\webapp\pull_backup.ps1`) | Scheduled task | daily 04:30 | Hephaestus BRIEF 50 |
| "WH40K Bridge Watcher" (`WH40K\bridge-kit\watcher.py`, pythonw) | Scheduled task | at logon, running | Hephaestus |
| "OneBrainSync" (`WH40K\bridge-kit\sync-onebrain.ps1`) | Scheduled task | ~every 2 h | Hephaestus |

Everything else on the Startup and task lists is vendor software (`docs/inventory/crusader.md`).

## Bastion jobs the projects created
`jamescron`'s crontab: `bench-register/backup.sh` 01:00 and `restore_test.sh` monthly (Hephaestus);
`bastion-ops/scripts/healthcheck.sh` every 15 min (alerts by ntfy, topic `bastion`), `mc-backup.sh` 6-hourly,
`tfg-update-check.sh` 09:15. Backups of configs run inside the backrest container.

## The app
- **Keep-awake:** on ("Keep computer awake while Claude works", also on battery). It prevents idle sleep only while a
  session works.
- **New sessions** connect to Remote Control; worktrees live inside each repo (`<repo>/.claude/worktrees`); the default
  permission mode is `auto` (user settings).
- **Sessions are never archived automatically** (inactive-days = never); PR-closed sessions are.

## How orchestrators reach each other
- **SendMessage** between sessions on this machine, addressed by session id or title: Calypso
  `local_80afc890-…`, Hephaestus `local_0ea8fe21-…`, Daedalus `local_55670803-…` (full ids in START_HERE §2).
- A message is a teammate's information, never the owner's yes. Brief sessions talk to their own orchestrator only.
- Delivery is "queued" while the receiving session is busy; nothing confirms it was read.
