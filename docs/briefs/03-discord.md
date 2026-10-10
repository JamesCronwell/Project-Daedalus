# BRIEF 03: The Discord server, rebuilt around how the group actually uses it

```
Status:     in progress: stage S1 of 4 prepared in discord/layout.toml; waiting for the owner's Administrator window
Commits:    -
Track:      plumbing (the owner's own infrastructure, DIRECTION)
Machine:    none: the owner's Discord server "Mojo Dojo Casa House"
Touch:      docs/discord/ (local only, gitignored: it holds friends' names), tools/discord_tree.py, discord/layout.toml
            (BRIEF 05's layout file, edited to the target in stages; owner's yes 2026-10-10),
            docs/CHANGELOG.md (one entry per checklist round), docs/PLUMBING.md (the feeds), this brief
Don't touch: the server itself. The owner applies every step, permission changes always. No bot token, no Discord
            login (the owner signs in). Message content (structure and metadata only). Deleting anything:
            channels, roles, bots.
            Amended 2026-10-09 (owner, in this session: "you can just take control and check for a bit"): the session
            may LOOK at Server Settings (Roles, Integrations, Members) in the owner's signed-in Discord, read-only: no
            Save, toggle, move or delete; no channel opened, no message read; no password typed
Suggested model: sonnet   (tables and a checklist; the owner applies them)
Effort level:    high     (permission overwrites and the bots' role are easy to get subtly wrong)
Parallel:   yes  (touches neither machine)
Owner time: the inputs (~10 min: member list grouped by role, each feed bot's Manage page); the channel check (~10 min);
            applying the checklist (~45 min, in rounds); one template sync at the end
Done when:  (1) the "after" template, diffed against before-2026-10-09, matches the agreed channel table; (2) every
            feed has posted, or been test-fired, in its new place; (3) Administrator, Manage Server, Manage Roles, Kick
            and Ban sit only on the Admin role and the bots' minimum; (4) everyone can see and talk in the Hangout;
            (5) the before and after snapshots, the role holders, the feed map and the checklist with its rollbacks are
            in docs/discord/ (local); the brief's Handover summarises them without friends' names
```

## Handover   (last stop: 2026-10-09, after the channel check was pre-filled)
```
State:     tasks 1-2 started; the owner's answers are the gate for task 3.
           - The "before" snapshot: docs/discord/before-2026-10-09.template.json (template rz3WdmpSVFVQ, 2026-10-09
             09:52 UTC). `python -I tools/discord_tree.py <it>` renders it.
           - The owner's screenshots are in docs/discord/inputs-2026-10-09/ (all read this session).
           - Written locally (gitignored): channels.md (the channel check: decisions Q1-Q8, then a row per channel
             with my guess and `?` where unsure), feeds.md (the 8 bots, which feed is seen where, what is unplaced),
             role-holders-2026-10-09.md (top roles from members-1..2).
           - Findings that change the plan:
             (1) PatchBot pings roles only with Premium ($1.49/mo), so the Minecraft, Squad and Helldivers feeds
             can't ping for free (SnailBot's two already do);
             (2) `wh40k` is hidden from everyone but the Dungeoneering roles, so moving it to the Feeds reveals it;
             (3) the bot-managed roles are not in the template, so their powers are unseen;
             (4) the squad roles HRT // SWAT, Aviation and Pathfinder hold "Mention @everyone, @here and All Roles";
             (5) a MINECRAFT category would hold one channel once the feeds move;
             (6) once Administrator leaves the bots' role, a bot-account feed (aviation-sqd-news) needs an explicit
             Send overwrite and the pinging bots Mention Everyone, or the ping roles must be made mentionable;
             (7) no Community server, so game roles are self-service via carl-bot's reaction roles.
           - The bots' role is held by 8 bots, 3 people and 3 hidden holders (almost certainly O-10/O-9, who get Admin
             anyway). O-6 and O-5 have 0 members.
           - Owner's answers (this session): Helldivers is cast out; PatchBot goes if useless; no new ping roles and no
             carl-bot reaction roles (pruning); no MINECRAFT category; wh40k visible to all; the existing hidden ARCHIVE is
             reused; D&D never started (archived); quiet-lounge, The Safe Room and the old chats archived; Project Zomboid
             voice kept as a Hangout spare; MEE6 and carl-bot "nuke" (the owner removes them by hand, later).
           - The owner allowed a read-only look at Server Settings in their signed-in Discord (the brief's Don't touch was
             amended). Read 2026-10-09: docs/discord/live-read-2026-10-09.md (local). It found:
             (a) wh40k, aviation-sqd-news, pathfinding-and-exiles, survivalist-files and swat-files are fed by 11 Discord
             announcement follows (War Thunder, PoE, Project Zomboid, Ready Or Not, a Warhammer release channel):
             moves keep them; archiving survivalist-files and swat-files would hide the Zomboid and Ready Or Not news;
             (b) `donations` is the Free Stuff (free-games) feed; kerbal-space-launches has no poster at all;
             (c) PatchBot and SnailBot also post into the owner's hidden tech-engineering and assembly-line;
             (d) MEE6's own role is renamed `ADMIN / MOTORIZED TRANSPORT` and carries Manage Roles, Kick, Ban; MEE6's 31
             webhooks look like one per channel, not feeds; removing the app removes both;
             (e) SnailBot holds the Aviation Sqd. role (that is where its ping comes from), so Mention Everyone must not
             be stripped from the bots' role or that role without a replacement; MCStatus has no role of its own and
             lives on the bots' role, so the cut bots' role must keep View, Send and Embed.
           - Layout confirmed by the owner ("yes, write the checklist", 2026-10-09; channels.md section F): MESS HALL (6),
             COMMS (9 read-only feeds incl. Zomboid and Ready Or Not), ENGINEERING (a new private forum), ARCHIVE (31,
             the whole Technical Engineering set included). Community is on (rules channel = welcome, kept visible as
             `briefing-room`; updates channel = base-announcements, stays hidden in ARCHIVE).
           - Task 3 done: docs/discord/checklist.md (local), rounds a-g with rollbacks. CHANGELOG entry for rounds (a)+(b)
             written; (c)-(g) get theirs when reached. Nothing is applied yet.
           - **The automation interview is done and locked** (owner, 2026-10-09: "yes, that's right, lock it in"). The
             owner reshapes the server often (new things, moves, themes), so the layout is applied by a tool, not by hand.
             Decisions: (1) layout as code in the Daedalus repo: a layout file of categories, channels, roles and
             permission overwrites, each with a stable key tied to its Discord id (a rename keeps history, webhooks and
             follows); the file holds no people, so it is committed; (2) the loop: the owner tells a session what to
             change (a theme is a rename), the session edits the file and shows the diff, the OWNER runs `plan` (reads
             the live server, writes a diff file the session may read) and then `apply`; no session ever holds the token;
             (3) scope: structure only; who holds which role, messages, bots, webhooks, follows and server settings are
             not managed; (4) it never deletes: extras are flagged, or channels go to the archive; real deletes stay by
             hand; (5) a standing bot the owner owns with only Manage Channels, Manage Roles and View Channels, its role
             high enough to edit the roles below it; the powerful toggles (Administrator, Manage Server, Kick, Ban) stay
             by hand and the plan flags them as "yours"; the token sits in the owner's password manager plus a protected
             file, like BRIEF 02's restic password; (6) tested first on the owner's existing test server (a rehearsal, not
             a blue/green swap: Discord can't swap servers), only then the bot joins the live one; (7) the first real run:
             the layout file starts from the "before" snapshot, so the first plan shows exactly the BRIEF 03 changes,
             applied in stages in the checklist's round order with a plan approved between stages; (8) stdlib-only
             Python; the by-hand checklist stays as the fallback. A new brief (BRIEF 04+; the orchestrator numbers it)
             builds it; this brief's rounds wait for it
           - 2026-10-10: BRIEF 05 is done (the bot is on the live server, the live layout is imported and committed).
             The owner chose a BOUNDED ADMINISTRATOR WINDOW ("Option 2 ... let's ball"): Administrator ticked on the
             bot's own role for the rebuild, unticked after. Why: the bot can't see the hidden legacy channels. What it
             does NOT change: the tool caps what it sets at its 12 bits (BOT_PERMS) even with Administrator, so
             Administrator on `Admin`, the ranks' and the bots' role powers, the thread bits and who holds roles stay
             by hand. CHANGELOG entry written first (2026-10-10, "planned").
           - The target is applied in four stages, each its own layout: S1 the Admin role, categories MESS HALL, COMMS,
             ENGINEERING, the forum `engineering-log`, ARCHIVE renamed (10 changes); S2 the 15 feed and Hangout channels
             (69); S3 the 31 archive moves (110); S4 the role bits the bot can set (5). Simulated offline against a fake
             server; real plans differ only where the live server holds things the layout file doesn't (member
             overwrites, bits outside the 12). Hidden categories also carry an explicit View allow for the bot's role,
             so the narrow bot keeps managing them after the window.
Next:      S1 is in discord/layout.toml (uncommitted until applied). The owner ticks Administrator on the bot's role,
           runs `plan`, the session reads the plan file, the owner runs `apply`, then `plan` again; then the session
           writes S2 from the updated file (ids written back), and so on. Commit the layout after each stage. After
           S4 and the by-hand part, the owner unticks Administrator; then `import`, a last `plan`, the template sync
           for the after-diff
Ask owner: - nothing open. Answered 2026-10-09: `kerbal-space-launches` is empty and the owner deletes it by hand (so
             ARCHIVE holds 31, not 32); `engineering-log` is private (Admin only); the channel and category names are as
             proposed in channels.md section F
           - (answered earlier) the three people in the bots' role lose Administrator: the checklist removes them from
             it before it is cut down; they keep their other roles
Dirty:     docs/discord/* is local only and gitignored (it holds friends' names). Nothing on the server is changed
           (one click expanded a Channels Followed row and was collapsed again; no change made)
```

## Why
DIRECTION's "owner's own infrastructure" section (owner's yes, 2026-10-09). The interview ran in the Orchestrator -
Daedalus chat on 2026-10-09 and the owner confirmed this restatement with "yes, write BRIEF 03".

**What the interview found:**
- **The server:** a small gaming server for the owner and their friends. A community plan didn't take.
- **The structure:** 14 categories, 47 channels and 52 roles, mostly built by hand.
- **Where people really are:** everyone talks in the Minecraft squad (`general-and-media`, the `Mining Group` voice
  channel). The owner tried specialised chats and they didn't take.
- **What the squads became:** news feeds.
  - PatchBot posts Minecraft to `mining-incorporated`, Squad to `army-rangers-applications-files`, and Helldivers 2 to
    `helldiving-quarters`.
  - SnailBot posts War Thunder to `aviation-sqd-news`, pinging @Aviation Sqd., and Path of Exile to
    `pathfinding-and-exiles`, pinging @Pathfinder Sqd. That channel also follows the official Path of Exile
    announcement channel.
  - `wh40k` gets release and price posts.
  - MCStatus feeds `server-status`.
- **The bots:** 8 of them. MEE6 has 31 webhooks, PatchBot 4, SnailBot 3, Free Stuff 1. The others are Readybot, carl-bot,
  MCStatus and Jockie Music. The bots are renamed after vehicles. brainmuncher1848 is the owner's alt; Jockie Music was
  added by a friend.
- **The power:** six roles carry Administrator: O-10, O-9, O-8, O-7, O-6, and `ADMIN / MECHANIZED TRANSPORT`, which looks
  like the bots' role. O-5 has Manage Server, Manage Roles, Kick and Ban.

**Inputs read by the orchestrator** (members-1..2, 2026-10-09):
- **46 members,** 8 of them bots.
- **O-10 has 3 holders,** one of them the owner: "Leucalin Monstrulescu" is `jamescronwell`.
- **O-9 has 3 holders.** So the new Admin role goes to 6 people.
- **O-8 has 2 holders, and O-7 has 1,** `brainmuncher1848`, the owner's alt. Both ranks lose their powers.
- **The bots' role is held by people too.** `ADMIN / MECHANIZED TRANSPORT` is held by the 8 bots and also by three
  people (named in docs/discord/inputs-2026-10-09/members-*). The owner's decision: they lose Administrator. The owner takes them out of
  the bots' role, and they keep everything else.

**The theme** (owner, 2026-10-09: "the entire theme is very military oriented"). New category and channel names stay in
it: squads, ranks, the bots named after vehicles. Propose themed names in the channel check, e.g. a mess hall or
barracks for the Hangout, and comms or signals for the Feeds. The owner picks; the table below uses working names.

## The agreed shape
| Category | What goes there |
|---|---|
| **HANGOUT** | Minecraft's `general-and-media` and the `Mining Group` voice channel, moved and renamed (history kept); one or two spare voice channels |
| **MINECRAFT** | `server-status` (MCStatus); `mining-incorporated` if the channel check keeps it |
| **FEEDS** | the existing feed channels, moved, renamed and made read-only (the bot posts, people read). Each pings its game's role: Minecraft, Squad, Helldivers, War Thunder, Path of Exile, WH40K, KSP launches, free games |
| **DUNGEONEERING** | only if the D&D group still meets (the channel check decides) |
| **TECHNICAL ENGINEERING** | the owner's; hidden; untouched |
| **ARCHIVE** | everything else, read-only, including the command structure and community scaffolding (welcome, donations, Administrative Hall, Command Centre) and the dead squads' chat and files channels |

**Rules:**
- Archive, never delete. Any delete is the owner's, by hand, later.
- Moving and renaming keep both message history and webhooks (a webhook is tied to the channel's id, not its name).
- A permission change is checked against the bots' role before it's applied, and each feed is checked right after.

**Roles:**
- **The ranks stay as cosmetics:** colours, and the member list grouped by rank.
- **Every rank loses** Administrator, Manage Server, Manage Roles, Kick and Ban.
- **A new plain `Admin` role** goes to the people who hold O-10 or O-9 today, and only it carries those powers.
- **The bots' role** is cut to what each feed needs: View, Send, Embed, Manage Webhooks where a bot uses webhooks, and
  Mention Roles for the feeds that ping.
- **Squad roles** become game-ping roles ("ping me about this game").
- **Roles that do nothing** (`Temu Worker Sqd.`, `Archives #HP`, `INACTIVE -- PENDING REMOVAL`, the empty divider roles
  if unwanted) are listed for the owner to delete by hand, after the role holders are recorded.

## Tasks
1. **Inputs from the owner:**
   - screenshots of the member list grouped by role, recorded as `docs/discord/role-holders-<date>.md`, names as shown;
   - each feed bot's Manage page (MEE6, PatchBot, SnailBot, Free Stuff), recorded as `docs/discord/feeds.md`, saying
     which channel each webhook posts to;
   - **never a webhook URL:** it's a credential.
2. **The channel check.** A table in `docs/discord/channels.md` with one row per channel: what it is now (feed and its
   bot, human chat, files, voice, scaffolding), its access, and what it becomes. Pre-fill it with this brief's
   findings; the owner corrects it. It settles Dungeoneering, `mining-incorporated`, `kerbal-space-launches`, where Free
   Stuff and MEE6's 31 webhooks post, the Command Centre's `quiet-lounge` and `The Safe Room`, and the spare voice
   channels.
3. **The checklist.** `docs/discord/checklist.md`, ordered in rounds, each step with its rollback:
   - (a) create the Admin role and give it to the O-10 and O-9 holders;
   - (b) create the new categories;
   - (c) move and rename;
   - (d) set read-only and role pings on the feeds, then check each feed;
   - (e) archive;
   - (f) strip the powers from the ranks, then from the bots' role, checking the feeds after each;
   - (g) set the server's system-messages channel if `welcome` is archived.

   A CHANGELOG entry goes in before each round.
4. **The owner applies it, round by round.** The session waits, then checks each round against the table, using a fresh
   template sync when one is needed.
5. **After.** The owner syncs the template. Save it as `docs/discord/after-<date>.template.json` and diff it against the
   "before".

## Later (not this brief)
- **Proper automation** (owner, 2026-10-09: "maybe we can still do some proper automation at some point"). That means
  the server's layout as code: a declarative file of categories, channels, roles and overwrites, diffed against the
  live server and applied by a bot the owner owns, with a dry run first. The token stays the owner's and is stored like
  BRIEF 02's restic password. It gets its own interview.
- **Trimming the 8 bots,** once the feed map shows what each one feeds. carl-bot, MEE6 and Readybot overlap.

## Rollback
- **A move or rename:** move or rename it back. The checklist records each channel's old category, position and name.
- **A permission change:** restore the overwrite or role permissions recorded in the "before" snapshot.
- **The Admin role:** the owner removes it after restoring the ranks' powers from the "before" snapshot.
- **Archiving:** move the channel back and restore its overwrites from the snapshot.
- **Nothing is deleted** in this brief, so nothing needs undeleting.
