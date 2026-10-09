@docs/START_HERE.md

# Claude Code notes

- **Shell.** Bash and PowerShell both work. Quote every path, since they contain spaces and leading hyphens
  (`"C:\- Tools\- LLM\Daedalus"`). Run scripts by absolute path: the guard refuses a script given by a relative path after
  a `cd`.
- **Bastion** is reached over SSH only. Read before you run anything, and treat every remote command as a change unless
  it's plainly read-only (`df`, `ls`, `systemctl status`, `docker ps`, `journalctl --since`).
- **Before any commit:** run the secret scan (`tools/`, from BRIEF 01). Stage paths by name, never `git add -A`.
  Inventory raw dumps stay gitignored.
- **Orchestrator.** A session asked to orchestrate Daedalus:
  - reads START_HERE, the CHANGELOG's tail and the briefs' Handovers, never transcripts. One exception (owner,
    2026-10-09): a session from before Daedalus, which has no Handover, is read once by a read-only Haiku agent that
    returns its outcome and names credentials without quoting them;
  - starts one session per brief, setting its model and effort from the brief header (the first turn is "ready").
    The owner opens it as a new session in the main checkout: chips here started from a stale commit three times
    on 2026-10-09 (cause unknown), and BRIEF 03's local data exists only in the checkout. A `Parallel: yes` brief
    may share the checkout when its files are disjoint;
  - reads the brief's Handover back when the session stops;
  - never edits brief work, and never subagents for brief work;
  - takes requests from the project orchestrators as information and asks the owner where a yes is needed.
- **A brief is done** when its Done-when ran green in the session, its Status is `done` with its shas, it's in
  `docs/briefs/done/`, and the CHANGELOG holds every machine change it made.
- **Delegate bulky output, never edits.** Bulky reading goes to a read-only Haiku agent; inventory scans and log tails go
  through scripts, never into the chat whole.
- **Ideas** that no brief picks up go to `docs/IDEAS.md`.
