# DECISIONS: what the owner decided, and why

Newest first. Each entry gives the question, the owner's answer (quoted where it matters), what was weighed or
rejected, and where the outcome now lives. **Before an orchestrator's `/clear`,** the day's decisions are appended here
and START_HERE §6 is refreshed (owner, 2026-10-09). The briefs, DIRECTION and IDEAS keep the outcomes; this file keeps
the trail. Friends' names never go here.

## 2026-10-09: Orchestrator - Daedalus, its first day

### How Daedalus runs
- **Pushing.** "Push main yourself, I trust it." The orchestrator pushes `main` after its commits and merges. Lives in
  START_HERE §0.
- **Old sessions' transcripts.** Pre-Daedalus sessions have no Handover, so a read-only Haiku agent reads each one
  once: "A, go with the Haiku agent", then "yes, commit it" for the wording. Rejected: skipping them (it would lose
  what was changed or deleted), and the owner recalling from memory. Lives in CLAUDE.md.
- **Brief sessions open in the main checkout.** Three chips started from a stale commit, cause unknown. The owner
  archived them ("yes, archive it") and opens sessions in the Daedalus folder. Lives in CLAUDE.md and START_HERE §5.
- **`.obsidian/` is gitignored** ("yes, gitignore .obsidian").

### BRIEF 01: the safety net
- **Reaching Bastion:** read only the `Host` lines of `~/.ssh/config` ("yes, read the Host lines"). There turned out to
  be no config; the route is `ssh jamescron@crusade-bastion`.
- **The R2 offsite drop on 2026-10-03 was deliberate.** It keeps R2 within its 10 GB free tier. Minecraft stays, for
  later (modpack v14). Lives in BACKUP-MAP as an accepted risk, and in IDEAS. Proposed but not taken up: a slim
  configs-only offsite plan, measured at about 2.5 GB.
- **Three read-only additions** ("yes, add all three"): measure the configs, draft the harden-5 steps (owner to
  verify), and search for `MY_ACCESS_TOKEN` by name.
- **The guard refused a secret file's name inside an exclusion** (Ask owner 16). The answer: an exclude file ("yes,
  exclude file"). Rejected: changing the guard. Lives in BRIEF 02.

### BRIEF 02: the daily backup
- **The brief:** "yes, saves plus the one-off full copy, go", with the KSP backups under `G:\My Drive\### Games\KSP`.
- **The backend:** "A, and saves-restic is fine", meaning restic straight onto G: through Drive for desktop.
  Rejected: B, rclone and the Drive API, the route that hit a quota on Bastion in September; and C, dated copies, with
  no encryption and no deduplication.
- **Anything that touches the password runs in the owner's own sitting:** "Go option 2, sure, as long as it's not
  very time consuming". Rejected: passing the password on stdin (it routes around the guard's intent), and changing
  the guard.
- **The task runs daily at 13:00.**
- **No skip flag for Calypso's deploys:** "no flag", via Calypso. Deploys never write the saves, and the KSP_x64 skip
  rule covers the real risk.
- **The old 2025 KSP_Reborn copy** stays until Task 5's fresh copy exists. Three craft found only in it are saved
  apart.

### BRIEF 03: the Discord server
- **In scope** as the owner's own infrastructure: "It's still infrastructure, just not yours, it's mine." Lives in
  DIRECTION.
- **The shape.**
  - A small gaming server for the owner and their friends. "Shrink it, archive the community stuff."
  - One place to talk. The squads had become feeds. The military theme stays.
  - The ranks stay as cosmetics. Admin goes to the O-10 and O-9 holders: "keep ranks as cosmetics, 0-10 and 0-9 Admin
    role".
  - The three people in the bots' role lose Administrator: "should not have admin, no".
- **The automation option** ("maybe we can still do some proper automation at some point"): the server as code, its own
  interview. Lives in IDEAS.
- **Friends' names stay out of git.** The permission classifier refused a push holding them, and we agreed with it.
  `docs/discord/` is local only.
- **Still open:** apply the checklist by hand, or automate.

### The KSP crash and BRIEF 04
- **The cause:** the GPU device was removed during KSP. Horse's 27B model sat wholly in VRAM, and commit stood at 94%.
  Not the driver: no timeouts were logged, and the newest driver's fixes target RDNA 4.
- **The owner's choice:** the machine side plus the Adrenalin extras. Lighter Parallax and Scatterer settings were
  declined: "3 should not be done".
- **Horse's model comes off by hand around KSP,** with two desktop shortcuts ("yes, with the shortcuts").
  - Rejected: JIT loading or idle unload. Horse's callers wait for "loaded", nothing reloads the model, and a JIT load
    would lack the MTP draft and the 16k context (Hephaestus).
  - Rejected: a watcher, "another watcher that watches over watching software".
- **The pagefile and the Adrenalin settings** are applied by the owner from guides, because they're system and app
  settings.

### Usage and the weekly limit (in discussion, before BRIEF 05)
- **The auto-compact override goes at 50%, not 30%.** The owner didn't want throughput hurt; 50% is a safety net only.
- **A morning `/clear` in the same orchestrator chat** keeps the session's id, pin and folder, and drops its context
  back to about 70k. Decisions are archived here before each one.
- **Messages between orchestrators get batched:** urgent ones now, information-only ones bundled and never answered.
- **MCP pruning** waits for the habits stretch, measured first.
- **Effort stays xhigh this week,** to use the Max plan (5x Pro, renews 2026-11-07). Revisit next week.
