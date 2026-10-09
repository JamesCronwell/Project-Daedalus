"""Secret scan: run before every commit (CLAUDE.md). Also provides redact() for the inventory.

    python -I tools/secret_scan.py            scan the staged files (git diff --cached)
    python -I tools/secret_scan.py PATH...    scan these files or folders

Exit 1 on a finding. A finding prints path:line and the rule, never the value.
BRIEF 01. After Sea's secret_scan.py and redact_configs.py (github.com/seatemplar10-dev/Horse-Inner-workings),
rewritten here.
"""
import os
import re
import subprocess
import sys

RULES = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("age secret key", re.compile(r"AGE-SECRET-KEY-1[0-9A-Z]{20,}")),
    ("GitHub token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("Anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("OpenAI-style key", re.compile(r"\bsk-(proj-)?[A-Za-z0-9]{32,}")),
    ("AWS key id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Tailscale key", re.compile(r"\btskey-[a-z]+-[A-Za-z0-9-]{10,}")),
    ("ntfy token", re.compile(r"\btk_[a-z0-9]{29}\b")),
    ("Cloudflare/R2 secret", re.compile(r"(?i)(cf|cloudflare|r2)[_-]?(api[_-]?)?(token|secret|key)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{20,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("password assignment", re.compile(
        r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|token)\b\s*[:=]\s*['\"]?(?!\$|<|\{|\(|%|none\b|null\b|true\b|false\b|redacted\b|\*)[^\s'\"#,;]{8,}")),
    ("URL with credentials", re.compile(r"[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]{3,}@[^\s/]+")),
]
EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SKIP_DIRS = {".git", "__pycache__", "raw", "worktrees"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".gz", ".tgz", ".pdf", ".exe", ".dll"}
# lines that document the rules themselves (this file, the guard's tests) are allowed to name patterns
ALLOW_FILES = {"secret_scan.py"}


def redact(text):
    """Replace secret-looking values and e-mail addresses (Tailscale prints the account's) with [REDACTED]."""
    for _, rx in RULES:
        text = rx.sub("[REDACTED]", text)
    text = EMAIL.sub("[email]", text)
    return re.sub(r"\b[A-Za-z0-9._%+-]+@(?=\s)", "[user]@", text)  # `tailscale status` truncates the account


def scan_file(path):
    hits = []
    if os.path.basename(path) in ALLOW_FILES or os.path.splitext(path)[1].lower() in SKIP_EXT:
        return hits
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                for name, rx in RULES:
                    if rx.search(line):
                        hits.append("%s:%d: %s" % (path, n, name))
    except OSError as e:
        hits.append("%s: unreadable (%s)" % (path, e))
    return hits


def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for f in files:
                    yield os.path.join(root, f)
        elif os.path.exists(p):
            yield p


def main(argv):
    if argv:
        files = list(walk(argv))
    else:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                             capture_output=True, text=True, check=True).stdout
        files = [f for f in out.splitlines() if f]
    hits = [h for f in files for h in scan_file(f)]
    for h in hits:
        print(h)
    print("secret scan: %d files, %d findings" % (len(files), len(hits)))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
