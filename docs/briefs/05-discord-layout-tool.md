# BRIEF 05: The Discord layout lives in the repo, and the owner applies changes with plan and apply

```
Status:     in progress (tasks 1-3 done; 4-7 wait for the owner)
Commits:    -
Track:      plumbing (the owner's own infrastructure, DIRECTION)
Machine:    none: the owner's test server, then "Mojo Dojo Casa House"; the token's protected file on Crusader
Touch:      tools/discord_layout.py, tools/discord_layout_test.py, discord/layout.toml (structure only; committed after
            the names check), docs/discord/ (local, gitignored: plan files, the import's cross-check), docs/PLUMBING.md,
            docs/BACKUP-MAP.md (the token's home), docs/CHANGELOG.md, this brief
Don't touch: the token: the session never reads, prints or passes it; the owner runs import, plan and apply. The live
            server beyond import and plan: nothing is applied there in this brief. Who holds which role, messages, bots,
            webhooks, follows, server settings. Deleting anything, anywhere. BRIEF 03's local files beyond reading
            docs/discord/channels.md section F and checklist.md
Suggested model: sonnet   (the design is locked; the subtle parts are spelled out under "Orchestrator's notes")
Effort level:    high     (permission bits and overwrite semantics are easy to get subtly wrong)
Parallel:   yes  (touches neither machine's configuration; its files are disjoint from BRIEF 04's)
Owner time: ~10 min creating the bot, its token and the protected file; ~15 min watching import, plan and apply on the
            test server; ~5 min inviting the bot to the live server and running import and one plan
Done when:  (1) `python -I tools/discord_layout_test.py` passes: the diff, never-delete, a rename keeps its id, member
            overwrites survive an apply, the owner's bits are flagged and skipped, a stale plan is refused, 429 retry,
            the TOML round trip;
            (2) on the test server: import, then a layout edit (a rename, a move, a new channel, a read-only overwrite,
            a new role), then plan shows exactly those, apply makes them, and a second plan shows no changes. The
            renamed channel kept its id, and nothing was deleted;
            (3) on the test server, a bit the bot can't set shows as "yours" in the plan, and apply skips it instead of
            stopping halfway;
            (4) on the live server: the bot is in, with its role. Import's layout matches
            docs/discord/before-2026-10-09.template.json by name and position (`check-template`), or every difference
            is listed for the owner;
            (5) discord/layout.toml is committed after the owner confirmed its names list (no people's names). The token
            lives only in the password manager and the protected file, and PLUMBING and BACKUP-MAP say so.
            BRIEF 03 then edits the layout to its target and applies its rounds through the tool.
```

## Handover   (last stop: 2026-10-09, after the tool and its tests)
```
State:     tasks 1-3 done. Done-when (1) is green: `python -I tools/discord_layout_test.py` runs 23 tests against an
           in-memory fake (diff, never-delete, rename keeps its id, member overwrites survive, owner's bits flagged and
           skipped with apply carrying on, stale plan refused, stop-at-first-error, 429 retry, TOML round trip,
           check-template, the full loop ending in a second empty plan).
           - Written: tools/discord_layout.py (import, check-template, names, plan, apply, invite),
             tools/discord_layout_test.py, tools/discord-setpass.ps1, docs/DISCORD-LAYOUT.md (the owner's steps),
             PLUMBING row, BACKUP-MAP row 18, a CHANGELOG entry (code only; the bot and servers are untouched).
           - Design points the owner should know: apply writes new ids back into the layout file; a role overwrite the
             layout drops is neutralised (0/0), never deleted, and the API client refuses DELETE; the "yours" set is
             computed from the bot's real permissions per channel, so a channel the bot can't see is skipped and
             listed; extras sink nowhere (they stay put, listed); channel order is refilled around extras.
           - NOT verified here: the DPAPI token read (`read_token`; the dummy-token check was denied) and every real
             Discord behaviour (task 5 proves them on the test server): that creating a channel with an explicit empty
             `permission_overwrites` list doesn't inherit the category's, that Discord accepts the PUTs when the live
             overwrite already holds bits the bot lacks, and the bot's 403 rules.
           - 2026-10-10, test server "Soundboard 2" (the owner ran everything; I read each plan): bot created, token in
             the password manager and the .dpapi file (the DPAPI read works), import + plan = 0 changes; round 1 (rename,
             move, new channel with a read-only overwrite, new role) planned as 6 changes, applied, second plan 0:
             the renamed channel kept its id, ids were written back, nothing deleted. Round 2: Kick and Ban on a role
             showed as "yours", apply did the topic edit and skipped them, the next plan listed them again and nothing
             else. Done-when (1), (2), (3) are met.
           - A real-Discord bug found and fixed (c3dcf5a): a new role can share the bot's position number, and the older
             role ranks higher; the tool now ranks by (position, age). Known gap: a role REORDER while positions tie
             isn't proven (it reuses the slots' position values); not needed so far.
Next:      task 6, the live server: a CHANGELOG entry first, then the owner's separate yes, invite, import, then
           `check-template` against docs/discord/before-2026-10-09.template.json. Task 7: `names` check with the owner,
           commit discord/layout.toml (no people's names), mark the brief done and move it to done/
Ask owner: - the yes to invite the bot to the LIVE server (Mojo Dojo Casa House), and its server id; the bot's role
             dragged above the roles it should edit; Done-when (4)'s `check-template` output to read
Dirty:     nothing on any machine or server; no secret anywhere. Not pushed (the orchestrator pushes main)
```

## Why
DIRECTION's "owner's own infrastructure" section. The owner reshapes the Discord server often (new things, moves,
themes), so the layout is applied by a tool rather than by hand. The interview ran in the BRIEF 03 session and the
owner locked it: "yes, that's right, lock it in" (2026-10-09). BRIEF 03's rounds (a)-(g) wait for this tool, and its
by-hand checklist stays as the fallback.

## The locked decisions (BRIEF 03's Handover)
1. **Layout as code.** One file in this repo holds the categories, channels, roles and permission overwrites. Each item
   has a stable key tied to its Discord id, so a rename keeps history, webhooks and follows. It holds no people, so it
   is committed. Guild, channel and role ids are not secrets.
2. **The loop.** The owner tells a session what to change; a theme is just a rename. The session edits the file and
   shows the diff. The owner runs `plan`, which reads the live server and writes a diff file the session may read, and
   then runs `apply`. No session ever holds the token.
3. **Scope: structure only.** Role membership, messages, bots, webhooks, follows and server settings aren't managed.
4. **It never deletes.** Extras are flagged, or channels move to the archive. Real deletes stay by hand (the first one
   is `kerbal-space-launches`, the owner's by hand).
5. **A standing bot the owner owns.** Its role sits high enough to edit the roles below it. Administrator, Manage
   Server, Kick and Ban stay by hand, and the plan flags them as "yours". The token goes in the owner's password manager
   plus a protected file, like BRIEF 02's restic password.
6. **The test server first.** It's a rehearsal, not a blue/green swap: Discord can't swap servers. Only then does the
   bot join the live one.
7. **The first real run** shows exactly the BRIEF 03 changes, applied in the checklist's round order with a plan
   approved between rounds.
8. **Python standard library only.**

## Orchestrator's notes (facts found while writing this brief)
1. **The template has no real ids.** Its channels are numbered 1 to 61 and its roles from 0, so the stable keys can't
   come from it. The starting layout comes from `import`, which the owner runs: it reads the live server and writes
   the layout with real ids. `check-template` compares that with the "before" template by name and position, so
   decision 7 still holds: BRIEF 03 edits the imported layout to its target, and the first plan shows exactly its
   changes.
2. **Templates drop member overwrites, and the live server may have some.** The tool never puts them in the layout and
   never shows them in a plan beyond a count, and an apply never removes them. Write overwrites one at a time
   (`PUT /channels/{id}/permissions/{target}`). A whole-list `PATCH` of `permission_overwrites` deletes every overwrite
   it doesn't list.
3. **A bot can only allow or deny the bits it holds itself.** That's Discord's rule for channel overwrites and role
   edits, as the orchestrator recalls it; task 5 proves it on the test server. With only Manage Channels, Manage Roles
   and View Channels, the bot couldn't make a feed read-only (a deny of Send Messages), nor give the bots' role Embed
   Links or Mention Everyone. **The owner's decision** ("Yes, bot gets those too", 2026-10-09): besides those three,
   it holds the everyday bits the layout sets (Send Messages, Embed Links, Attach Files, Read Message History, Add
   Reactions, Mention Everyone, Manage Webhooks, Connect, Speak), and never Administrator, Manage Server, Kick or Ban.
   Anything outside its set is "yours" in the plan.
4. **Discord rejects urllib's default User-Agent.** Send `DiscordBot (<repo url>, <version>)`, and honour a 429's
   `retry_after`.
5. **TOML** keeps the diffs readable. `tomllib` reads it; `import` needs a small writer for this fixed schema.
6. **Names.** A channel or role name can hold a person's name. Before the first commit, the session lists every name
   in the layout and the owner confirms.

## Tasks
1. **The schema.** Categories, channels (type, parent, position, name, topic, read-only by overwrites), roles (name,
   colour, hoist, mentionable, permissions, position) and role overwrites, each keyed by a stable name with its id.
   Document it in the tool's docstring.
2. **The tool,** `tools/discord_layout.py`, with four commands:
   - `import` writes the layout from the live server;
   - `check-template <template.json>` compares a layout with a template by name and position;
   - `plan` re-reads the live server and writes `docs/discord/plan-<UTC time>.md` (local): creates, renames, moves,
     overwrite changes, role changes, the extras it won't delete, the "yours" bits, and the unmanaged member
     overwrites (a count only);
   - `apply <plan file>` re-reads the live server, refuses if it changed since the plan, and makes only what the plan
     lists, one call at a time, stopping at the first error with a list of what was done.

   The token is read from the protected file the same way BRIEF 02 reads restic's password, and only inside the
   owner's own run.
3. **Tests,** `tools/discord_layout_test.py`: `unittest` against an in-memory fake of the Discord API, no network.
   Cover everything in Done-when (1).
4. **The bot (owner, ~10 min).** The session writes the steps: create the application and bot in the Developer Portal,
   then store the token in the password manager and in the protected file (the owner runs the setup, as in BRIEF 02).
   The session also prints the invite URL with the permission integer from note 3; it holds no secret.
5. **The test server.** The owner invites the bot, then runs import, plan and apply as in Done-when (2) and (3). The
   session reads each plan file and checks it.
6. **The live server.** A CHANGELOG entry goes in before the bot is invited (what, why, the owner's yes, the rollback).
   The owner invites it and runs `import`, then `check-template` against the "before" template.
7. **Records.** The names check, then commit `discord/layout.toml`. PLUMBING gets the tool, the bot and the loop;
   BACKUP-MAP gets the token's home and how to rotate it.

## Rollback
- **The tool and the layout file:** revert the commits. Nothing on a machine changes.
- **An apply on the test server:** put the previous layout back from git, then plan and apply. Items it created stay
  as extras until the owner deletes them by hand.
- **The bot on a server:** the owner kicks it. To retire it, the owner deletes the application in the Developer Portal
  and removes the protected file.
- **A leaked token:** the owner resets it in the Developer Portal, then updates the password manager and the protected
  file.
