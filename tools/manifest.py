"""Checksum manifests, for proving a restore.

    python -I tools/manifest.py make SRC OUT.tsv [--exclude GLOB ...]   sha256 of every file under SRC
    python -I tools/manifest.py compare A.tsv B.tsv                      exit 0 only if identical
    python -I tools/manifest.py verify SRC RESTORED [--exclude GLOB ...] make both and compare (one step)

A manifest is "relative/path<TAB>size<TAB>sha256", sorted. It holds hashes and names, never content; keep it out of
the repo all the same (scratch folder). Read-only on SRC. Live folders change while they're read (~/.claude is written
by every session), so compare a restore against the manifest taken when the backup was made, not against the live
folder.
BRIEF 01. After Sea's manifest.py (github.com/seatemplar10-dev/Horse-Inner-workings), rewritten here.
"""
import fnmatch
import hashlib
import os
import sys


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def excluded(rel, patterns):
    rel = rel.replace("\\", "/")
    return any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(os.path.basename(rel), p) for p in patterns)


def make(src, patterns):
    rows, errors = [], []
    for root, dirs, files in os.walk(src):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(root, name)
            rel = os.path.relpath(full, src).replace("\\", "/")
            if excluded(rel, patterns):
                continue
            try:
                rows.append((rel, os.path.getsize(full), sha256(full)))
            except OSError as e:
                errors.append("%s: %s" % (rel, e.strerror))
    return sorted(rows), errors


def write(rows, out):
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for rel, size, digest in rows:
            f.write("%s\t%d\t%s\n" % (rel, size, digest))


def read(path):
    rows = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            rel, size, digest = line.rstrip("\n").split("\t")
            rows[rel] = (int(size), digest)
    return rows


def compare(a, b):
    missing = sorted(set(a) - set(b))
    extra = sorted(set(b) - set(a))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    for label, items in (("missing from restore", missing), ("extra in restore", extra), ("differs", changed)):
        for k in items[:20]:
            print("%s: %s" % (label, k))
        if len(items) > 20:
            print("%s: ... %d more" % (label, len(items) - 20))
    ok = not (missing or extra or changed)
    print("%s: %d files in A, %d in B, %d missing, %d extra, %d differ" % (
        "MATCH" if ok else "MISMATCH", len(a), len(b), len(missing), len(extra), len(changed)))
    return 0 if ok else 1


def args_excludes(argv):
    pats, rest, i = [], [], 0
    while i < len(argv):
        if argv[i] == "--exclude" and i + 1 < len(argv):
            pats.append(argv[i + 1])
            i += 2
        else:
            rest.append(argv[i])
            i += 1
    return rest, pats


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd, (rest, pats) = argv[0], args_excludes(argv[1:])
    if cmd == "make" and len(rest) == 2:
        rows, errors = make(rest[0], pats)
        write(rows, rest[1])
        for e in errors:
            print("unreadable:", e)
        print("%d files, %d bytes, %d unreadable -> %s" % (len(rows), sum(r[1] for r in rows), len(errors), rest[1]))
        return 1 if errors else 0
    if cmd == "compare" and len(rest) == 2:
        return compare(read(rest[0]), read(rest[1]))
    if cmd == "verify" and len(rest) == 2:
        a, ea = make(rest[0], pats)
        b, eb = make(rest[1], pats)
        for e in ea + eb:
            print("unreadable:", e)
        return compare({r[0]: r[1:] for r in a}, {r[0]: r[1:] for r in b}) or (1 if ea or eb else 0)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
