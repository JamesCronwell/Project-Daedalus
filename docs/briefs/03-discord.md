# BRIEF 03: The Discord server, rebuilt around how the group actually uses it

```
Status:     waiting-owner: channels.md answers, the feed bots' Manage pages, 3 Members tabs
Commits:    -
Track:      plumbing (the owner's own infrastructure, DIRECTION)
Machine:    none: the owner's Discord server "Mojo Dojo Casa House"
Touch:      docs/discord/ (local only, gitignored: it holds friends' names), tools/discord_tree.py,
            docs/CHANGELOG.md (one entry per checklist round), docs/PLUMBING.md (the feeds), this brief
Don't touch: the server itself. The owner applies every step, permission changes always. No bot token, no Discord
            login, no browser session in Discord. Message content (structure and metadata only). Deleting anything:
            channels, roles, bots
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
           - The bots' role is held by 8 bots and 3 people (as top role); the Admin role goes to the 6 holders of
             O-10 and O-9. O-6 and O-5 show no top-role holders, so hidden holders are possible.
Next:      the owner answers channels.md (Q1-Q8, then the `?` rows, ~10 min). Then task 3: write the checklist
           (rounds a-g, each with its rollback) and the round-1 CHANGELOG entry (plumbing: Discord) before the owner
           applies round (a). Never touch the server; every step is the owner's
Ask owner: - the channels.md answers (Q1 PatchBot pings, Q2 drop the MINECRAFT category, Q3 wh40k visible to all,
             Q4 archive hidden, Q5 carl-bot reaction roles, Q6 strip Mention All from squad roles; whether D&D still
             meets; the `?` rows)
           - each feed bot's Manage page (PatchBot, SnailBot, MEE6, Free Stuff): channel names only, never a webhook URL
           - the Members tab of ADMIN / MECHANIZED TRANSPORT, O-6 / Colonel and O-5 / Lieutenant Colonel
           - a Roles screenshot showing the bot-managed roles
           - (answered earlier) the three people in the bots' role lose Administrator: the checklist removes them from
             it before it is cut down; they keep their other roles
Dirty:     docs/discord/* is local only and gitignored (it holds friends' names). Nothing on the server is changed
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
