# IDEAS: not commitments

Each one gets an interview with the owner before it becomes a brief (global rule).

- **Cerberus.** A future security guard dog, "SOMETIME in the future, as like a 1% weekly security guard" (owner,
  2026-10-09). It would own what Daedalus may never touch: security settings, credentials, the firewall, accounts,
  exposure. It gets its own interview first.

  **Its starting list,** from what Daedalus has seen (2026-10-09):
  - qBittorrent with no password on the LAN and tailnet;
  - SSH password login on Bastion (harden-5 waits for the owner);
  - Bazarr's empty login;
  - an old rclone token in backrest's `rclone.conf`;
  - `MY_ACCESS_TOKEN`, which nothing names;
  - Administrator held by many people on Discord, until BRIEF 03's checklist lands;
  - Calypso's LunaServer (LMP) on UDP `[::]:8800` during co-op tests, on a portable .NET 6 (end of life) under
    `F:\Steam_Modded_Variants\LMP_Server`.
- **The night protocol for the monitors.** The night-mode script (`C:\Users\User\Scripts\night-mode.cmd`) puts the
  screens into standby. The monitors still flash "No signal" because their own input scan is on, so turn off Auto
  Source / Input Auto Switch in each monitor's menu. Windows' "Remember window locations based on monitor connection"
  stops the window shuffle. RGB off through OpenRGB, if the devices are supported.
- **Session and worktree hygiene.** Archiving finished chips, removing merged worktrees and branches, and pruning
  `~/.claude/projects/*` transcripts by age, as one script the orchestrators call. Today each orchestrator does it by
  hand.
- **The MCP and plugin token cost.** Count what each MCP server and plugin adds to every session's context, across all
  orchestrators, and prune the unused ones (habits stretch).
- **WizTree** for the file-structure pass (the owner installs it).
- **One shared copy of the decision skills.** `doubt-driven-development` and `interview-me` live in Calypso's and
  WH40K's `.claude/skills/`, and the two copies have drifted apart (2026-10-09). Daedalus has none. Either one copy in
  `~/.claude/skills/` (shared plumbing, Daedalus's) or a sync script. Part of the drift is deliberate: Calypso adapted
  WH40K's copy (brief header, KSP examples), per the Calypso orchestrator. So a shared core plus per-project notes,
  diffed with both orchestrators first.
- **The Minecraft server.** Kept, not running (owner, 2026-10-09): it waits for the modpack's version 14 update and
  for the group to want it, and the owner may modify the modpack later. Its offsite copy was dropped on 2026-10-03 on
  purpose, to stay inside R2's 10 GB free tier. While stopped, the world doesn't change, so one copy is enough.
  Interview when it comes back.
- **The Discord server as code** (owner, 2026-10-09: "maybe we can still do some proper automation at some point").
  After BRIEF 03's manual rework: the layout in a declarative file, diffed against the live server and applied by a bot
  the owner owns, dry run first. Its own interview.
