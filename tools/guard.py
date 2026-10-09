"""Daedalus guard: a PreToolUse hook that refuses destructive shell commands (rules in tools/guard_core.py).

Wired in .claude/settings.json for Bash, PowerShell, Monitor and the Terminal panel's run_in_terminal. It reads the
hook's JSON on stdin and exits 2 (refuse, reason on stderr) or 0 (let the normal permission checks decide). Any error,
including a broken guard_core.py that won't import, exits 2: it fails closed.

There is no bypass switch on purpose (an agent could flip it), and the deny list keeps Edit/Write off this file, the
rules and the settings. What the guard refuses, the owner runs themselves. Commit messages: `git commit -F <file>`.
Test: python -I tools/guard_test.py
BRIEF 01, after Sea's horse-guard.js and ro_barrier.ps1 design (github.com/seatemplar10-dev/Horse-Inner-workings).
"""
import sys

GUARDED_TOOLS = {"Bash", "PowerShell", "Monitor", "mcp__terminal__run_in_terminal"}


def refuse(msg):
    sys.stderr.write("Daedalus guard: refused (%s). This repo never runs destructive commands; if the owner wants it, "
                     "they run it themselves. Read-only alternatives are fine. Rule: START_HERE section 4, "
                     "tools/guard_core.py.\n" % msg)
    return 2


def main():
    try:
        import json
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from guard_core import check
        # bytes, decoded as UTF-8: Windows' default (cp1252) would turn an en dash (PowerShell's -) into mojibake
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
        if data.get("tool_name", "") not in GUARDED_TOOLS:
            return 0
        tin = data.get("tool_input") or {}
        reason = check(tin.get("command") or "", tin.get("cwd") or data.get("cwd"))
    except BaseException as e:  # fail closed, whatever went wrong
        return refuse("the guard itself failed: %s: %s" % (type(e).__name__, e))
    return refuse(reason) if reason else 0


if __name__ == "__main__":
    sys.exit(main())
