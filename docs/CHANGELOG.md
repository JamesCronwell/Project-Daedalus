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

## 2026-10-09  plumbing  Daedalus repo created (no machine change)
Brief:     -
Why:       the owner's yes to the Daedalus direction (docs/DIRECTION.md), from the Calypso orchestrator's chat
Owner yes: "yes, set up the Daedalus repo" (Calypso orchestrator chat, 2026-10-09)
Before:    `C:\- Tools\- LLM\Daedalus` did not exist
Change:    this repo (docs, `.claude/settings.json` deny list, BRIEF 01); one roster line added to `~/.claude/CLAUDE.md`
Rollback:  delete the folder; remove the roster lines from `~/.claude/CLAUDE.md`
Outcome:   local git repo, first commit 8c1700e; pushed to the private GitHub repo JamesCronwell/Project-Daedalus the same day
