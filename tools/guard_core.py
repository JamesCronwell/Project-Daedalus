"""The Daedalus guard's rules. tools/guard.py is the hook entry point (it fails closed if this module won't import,
raises, or runs past its deadline).

check(cmd, cwd) returns a refusal reason, or None. It looks for destructive commands anywhere in the line, including
inside `ssh host '<cmd>'`, `bash -c`, `docker exec/run`, `cmd /c`, `powershell -Command`, `sudo`, `xargs`, `find -exec`,
if/for bodies and friends. Three views of the line are scanned:
  A. quotes become separators, so every quoted string is checked as a command of its own;
  B. quotes, carets and commas are deleted or spaced, so `r"m" -rf` and `ssh host rm -rf x` still read as rm;
  C. view B with backslashes removed too, so `r\\m -rf` reads as rm.
Before that, literal text that never executes is blanked: grep/rg/Select-String patterns, echo/Write-Host text, git
commit/tag messages and `git log --grep` (single-quoted, or double-quoted without `$` or a backtick), and a quoted
heredoc fed straight to git commit/tag. Never when the line also holds something that parses text again (ssh, eval,
bash, cmd, powershell, python ...).

WHAT IT IS: a seatbelt against mistakes and obvious injected commands. It is not a wall against an agent that sets
out to dodge it: shell is too rich for a pattern list to be complete. Known limits (BRIEF 01's Handover): a command
word assembled at run time is only caught when force+recursive flags ride along; scripts are scanned when run by a
path the guard can read, code reached any other way is not; if python is missing the hook can't run; switching
branches (`git checkout <branch>`) can swap the guard's files like any others. And one false block on purpose: with
ssh (or eval, bash -c ...) on the line, a quoted grep pattern is checked as a command, since the far shell parses it
again; search for such words without ssh, or rephrase the pattern.
BRIEF 01, after Sea's horse-guard.js and ro_barrier.ps1 design (github.com/seatemplar10-dev/Horse-Inner-workings).
"""
import fnmatch
import os
import re
import time

MAX_LEN = 8000       # longer commands are refused: a timed-out hook lets the call through
DEADLINE_S = 4.0     # the hook's timeout is 15 s; past this, refuse


class Deadline(Exception):
    pass


_t0 = [0.0]


def tick():
    if time.monotonic() - _t0[0] > DEADLINE_S:
        raise Deadline()


# --- normalising ------------------------------------------------------------------------------------------------------

def normalise(cmd):
    cmd = cmd.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")  # PowerShell takes en/em dashes
    cmd = re.sub(r"/\*.*?\*/", " ", cmd, flags=re.S)  # SQL comments: DROP/**/DATABASE
    return re.sub(r"\\\r?\n|`\r?\n", " ", cmd)        # bash and PowerShell line continuations


def split_statements(cmd):
    """Quote-aware split on ; && || | newline. Returns [(text, sep_before)] or None if the quotes don't balance."""
    out, buf, q, i, sep = [], [], None, 0, ""
    while i < len(cmd):
        c = cmd[i]
        if q:
            buf.append(c)
            if c == q:
                q = None
        elif c in "'\"":
            q = c
            buf.append(c)
        elif cmd.startswith(("&&", "||"), i):
            out.append(("".join(buf), sep))
            buf, sep = [], cmd[i:i + 2]
            i += 1
        elif c in ";|\n":
            out.append(("".join(buf), sep))
            buf, sep = [], c
        else:
            buf.append(c)
        i += 1
    if q:
        return None
    out.append(("".join(buf), sep))
    return out


# --- literal text that never executes --------------------------------------------------------------------------------

REPARSE = re.compile(r"(?i)(^|[^\w-])(ssh|eval|iex|invoke-expression|invoke-command|icm|bash|sh|zsh|dash|ksh|fish|cmd|"
                     r"cmd\.exe|powershell|powershell\.exe|pwsh|wsl|su|runuser|docker|podman|kubectl|start-process|"
                     r"saps|start-job|python|python3|py|node|perl|ruby|xargs|parallel|watch|source|exec)"
                     r"(?=$|[\s'\"(;|&])")
LITERAL_CMDS = {"grep", "egrep", "fgrep", "rg", "findstr", "select-string", "sls", "echo", "printf", "write-host",
                "write-output", "write-verbose", "write-warning", "jq"}
QUOTED = re.compile(r"'[^'\n]*'|\"[^\"$`]*\"")
GIT_HEREDOC = re.compile(r"(?im)^(\s*git\s+(?:commit|tag)\b[^\n;&|<]*<<)(['\"]?)(\w+)\2[ \t]*\n(.*?)^\3[ \t]*$",
                         re.S)


def strip_literals(cmd):
    if REPARSE.search(re.sub(r"'[^']*'|\"[^\"]*\"", "''", cmd)):
        return cmd  # something on this line parses text again: nothing is literal
    def heredoc(m):
        if not m.group(2) and re.search(r"[$`]", m.group(4)):
            return m.group(0)  # unquoted delimiter: the body expands, keep it
        return m.group(1) + m.group(2) + m.group(3) + m.group(2) + "\n" + m.group(3)
    cmd = GIT_HEREDOC.sub(heredoc, cmd)
    parts = split_statements(cmd)
    if parts is None:
        return cmd
    out = []
    for text, sep in parts:
        words = text.split()
        w = words[0].lower().lstrip("&") if words else ""
        literal = w in LITERAL_CMDS or (w == "git" and any(x.lower() in ("commit", "tag", "log") for x in words[1:3]))
        if literal and not (w == "rg" and "--pre" in text):
            text = QUOTED.sub("''", text)
            if w == "git":
                text = re.sub(r"(?i)(--grep=|--message=|-m)(\S+)", r"\1''", text)
        out.append(sep + text)
    return "".join(out)


# --- splitting into segments -------------------------------------------------------------------------------------------

SEP = re.compile(r"\r?\n|&&|\|\||[;|&(){}]|\$\(|<\(|>\(")
CMD_SWITCHES = re.compile(r"^([A-Za-z][\w.-]*)((?:/[A-Za-z?]+)+)$")  # rd/s/q, cmd/c


def tokens(seg):
    out = []
    for t in seg.split():
        m = CMD_SWITCHES.match(t)
        if m:
            out.append(m.group(1))
            out += ["/" + s for s in m.group(2).split("/") if s]
        elif re.fullmatch(r"(/[A-Za-z?])(/[A-Za-z?])+", t):
            out += ["/" + s for s in t.split("/") if s]  # /s/q
        else:
            out.append(t)
    return out


def views(cmd):
    view_a = cmd
    for q in "'\"`":
        view_a = view_a.replace(q, "\n")
    view_b = cmd
    for q in "'\"`^":
        view_b = view_b.replace(q, "")
    view_b = view_b.replace(",", " ")
    return view_a, view_b, view_b.replace("\\", "")


def segments(cmd):
    out = []
    for view in views(cmd):
        for seg in SEP.split(view):
            toks = tokens(seg)
            if toks:
                out.append(toks)
    return out


def word(tok):
    """A command word: basename, lower case, no .exe, no leading backslash, call operator or `!`."""
    t = tok.strip().lstrip("\\&!").lower()
    if t != ".":
        t = re.split(r"[\\/]", t)[-1]
    return t[:-4] if t.endswith(".exe") else t


def nonflags(args):
    return [a for a in args if not a.startswith("-")]


PS_PARAMS = {"-force", "-filter", "-include", "-exclude", "-path", "-literalpath", "-verbose", "-confirm", "-whatif",
             "-credential", "-stream", "-erroraction", "-errorvariable", "-warningaction", "-informationaction",
             "-outvariable", "-outbuffer", "-pipelinevariable", "-passthru", "-depth", "-name", "-directory", "-file",
             "-hidden", "-readonly", "-system", "-attributes", "-followsymlink", "-format", "-property"}


PS_OPERATORS = {"-or", "-xor", "-bor", "-bxor", "-and", "-band", "-not", "-bnot", "-eq", "-ne", "-gt", "-ge", "-lt",
                "-le", "-like", "-notlike", "-match", "-notmatch", "-replace", "-ireplace", "-creplace", "-contains",
                "-notcontains", "-in", "-notin", "-is", "-isnot", "-as", "-f", "-split", "-join", "-shl", "-shr",
                "-ceq", "-ieq", "-cne", "-cgt", "-clt", "-cge", "-cle", "-clike", "-cmatch"}


def qtokens(stmt):
    """Shell-like words of one statement: a quoted part stays inside its word (`"C:\\- Tools\\x.py"` is one word)."""
    return [re.sub(r"['\"]", "", m) for m in re.findall(r"(?:\"[^\"]*\"|'[^']*'|[^\s\"']+)+", stmt)]


def statements(cmd):
    parts = split_statements(cmd)
    if parts is None:
        return [" ".join(t) for t in segments(cmd)]
    return [p[0] for p in parts]


def short_cluster(a):
    """Letters of a single-dash cluster like -rf / -dfvir; '' for PowerShell words (-Force, -Filter, -ErrorAction)."""
    if not re.fullmatch(r"-[A-Za-z]+", a):
        return ""
    if len(a) >= 5 and any(p.startswith(a.lower()) for p in PS_PARAMS):
        return ""
    return a[1:]


def short_flags(args):
    out = set()
    for a in args:
        out.update(short_cluster(a))
    return out


def long_opt(args, full, minimum=4):
    """GNU and git accept unambiguous prefixes of long options: --re, --recu, --mirr ..."""
    for a in args:
        a = a.lower().split("=")[0]
        if a.startswith("--") and len(a) >= minimum and full.startswith(a):
            return True
    return False


def is_recurse_param(a):
    """PowerShell accepts any unambiguous prefix: -r, -re, -Rec:$true ..."""
    a = a.lower().split(":")[0]
    return len(a) >= 2 and "-recurse".startswith(a)


def recursive(args, ps=True):
    sf = short_flags(args)
    return ("r" in sf or "R" in sf or long_opt(args, "--recursive") or
            (ps and any(is_recurse_param(a) for a in args)))


# --- wrappers: things that run another command after their own options -------------------------------------------------

VALUE_OPTS = {
    "sudo": set("ughCDprtUT"), "doas": set("uC"), "ssh": set("bcDEeFIiJLlmOoPpQRSWw"),
    "xargs": set("ILnPdsaE"), "timeout": set("sk"), "nice": set("n"), "ionice": set("cnpt"), "watch": set("nd"),
    "env": set("uCS"), "flock": set("wEs"), "chroot": set(), "nohup": set(), "pkexec": set("u"),
}
VALUE_LONG = {"--user", "--group", "--host", "--prompt", "--chdir", "--role", "--type", "--close-from",
              "--other-user", "--max-args", "--max-procs", "--delimiter", "--arg-file", "--max-lines", "--max-chars",
              "--replace", "--signal", "--kill-after", "--adjustment", "--interval", "--unset", "--split-string",
              "--env", "--workdir", "--env-file", "--detach-keys", "--timeout", "--conflict-exit-code", "--userspec",
              "--groups", "--distribution", "--cd"}
DOCKER_GLOBAL_VALUE = {"--context", "-c", "-H", "--host", "--config", "-l", "--log-level", "--tlscacert",
                       "--tlscert", "--tlskey", "-f", "--file", "-p", "--project-name", "--project-directory",
                       "--profile", "--env-file", "--ansi", "--parallel", "--progress"}
SIMPLE_WRAPPERS = {"nohup", "time", "exec", "command", "builtin", "setsid", "unbuffer", "stdbuf", "strace", "nsenter",
                   "runuser", "su", "call", "start", "iex", "invoke-expression", "invoke-command", "icm",
                   "start-process", "saps", "start-job", "foreach-object", "%", "where-object", "sh", "bash", "zsh",
                   "dash", "ksh", "fish", "cmd", "powershell", "pwsh", "python", "python3", "py", "node", "perl",
                   "ruby", "busybox", "eval", "then", "do", "else", "elif", "if", "while", "until", "pkexec",
                   "winpty", "npx", "bunx", "pnpx", "source", "systemd-inhibit", "caffeinate", "script", ":",
                   "true"}
ALL_POSITIONS = {"taskset", "chrt", "numactl", "firejail", "cgexec", "prlimit", "parallel"}  # options too varied
PS_ARG_FLAGS = {"-filepath", "-argumentlist", "-args", "-scriptblock", "-command", "-c", "-file", "-noprofile",
                "-nop", "-noninteractive", "-noni", "-nologo", "-wait", "-nonewwindow", "-passthru", "-asjob",
                "-sta", "-mta", "-executionpolicy", "-ep", "-windowstyle", "-w", "-verb", "-workingdirectory",
                "-computername", "-cn", "-session", "-credential", "-process", "-begin", "-end"}
PS_ARG_VALUE = {"-executionpolicy", "-ep", "-windowstyle", "-w", "-verb", "-workingdirectory", "-computername",
                "-cn", "-session", "-credential"}
REDIRECT = re.compile(r"^\d*(>>?|<)&?(\S*)$")


def skip_opts(toks, i, letters):
    """Index after toks[i:]'s options, plus every value passed on the way (a value may really be the command:
    when unsure, check both). A cluster like -iu takes a value when its last letter does."""
    passed = []
    while i < len(toks) and toks[i].startswith("-") and toks[i] != "--":
        t = toks[i]
        takes = (t in VALUE_LONG) or (re.fullmatch(r"-[A-Za-z]+", t) is not None and t[-1] in letters)
        if takes and i + 1 < len(toks):
            passed.append(i + 1)
            i += 2
        else:
            i += 1
    if i < len(toks) and toks[i] == "--":
        i += 1
    return i, passed


def next_starts(toks, i):
    """Where the next command may begin after toks[i], if it is a wrapper. Returns (indices, via_xargs)."""
    w = word(toks[i])
    if re.match(r"^[$@][\w:.]+$", toks[i]) and i + 1 < len(toks) and re.match(r"^[-+*/]?=$", toks[i + 1]):
        return [i + 2], False  # PowerShell assignment: $x = <command>
    if re.match(r"^\$[\w:.]+=", toks[i]):
        return [i + 1], False
    if toks[i] in ("!", "&", "."):
        return [i + 1], False
    m = REDIRECT.match(toks[i])
    if m:
        return [i + 1 if m.group(2) else i + 2], False  # `2>/dev/null rm`, `> out rm`
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i]) or toks[i].lower().startswith("$env:"):
        return [i + 1], False  # VAR=value prefix
    low = [t.lower() for t in toks[i:i + 40]]  # a wrapper's own options are near it
    if w in ("sudo", "doas", "env", "timeout", "nice", "ionice", "watch", "flock", "chroot", "xargs", "pkexec"):
        j, passed = skip_opts(toks, i + 1, VALUE_OPTS.get(w, set()))
        if w == "env":
            while j < len(toks) and "=" in toks[j]:
                j += 1
        if w in ("timeout", "flock", "chroot") and j < len(toks):
            passed.append(j)
            j += 1  # the duration, lock file or new root
        return passed + [j], w == "xargs"
    if w == "ssh":
        j, passed = skip_opts(toks, i + 1, VALUE_OPTS["ssh"])
        k, more = skip_opts(toks, j + 1, VALUE_OPTS["ssh"])  # OpenSSH takes options after the host too
        return passed + more + [j, j + 1, k], False
    if w in ("docker", "podman", "docker-compose"):
        j = 1
        while j < len(low) and low[j].startswith("-"):
            j += 2 if toks[i + j] in DOCKER_GLOBAL_VALUE and "=" not in low[j] else 1
        if j < len(low) and low[j] == "compose":
            j += 1
            while j < len(low) and low[j].startswith("-"):
                j += 2 if toks[i + j] in DOCKER_GLOBAL_VALUE and "=" not in low[j] else 1
        if j < len(low) and low[j] in ("exec", "run", "create"):
            return list(range(i + j + 1, min(len(toks), i + j + 41))), False  # image/container or the command
        return [], False
    if w in ALL_POSITIONS:
        return list(range(i + 1, min(len(toks), i + 41))), False
    if w == "kubectl" and "--" in toks[i:]:
        return [toks.index("--", i) + 1], False
    if w == "find":
        return [i + k + 1 for k in range(len(low)) if low[k] in ("-exec", "-execdir", "-ok", "-okdir")], True
    if w == "wsl":
        j, passed = i + 1, []
        while j < len(toks) and toks[j].startswith("-"):
            if toks[j].lower() in ("-e", "--exec", "--"):
                j += 1
                break
            if toks[j].lower() in ("-d", "-u", "--distribution", "--user", "--cd"):
                passed.append(j + 1)
                j += 2
            else:
                j += 1
        return passed + [j], False
    if w in SIMPLE_WRAPPERS:
        j, passed = i + 1, []
        while j < len(toks):
            t = toks[j].lower()
            if t in PS_ARG_FLAGS:
                if t in PS_ARG_VALUE:
                    passed.append(j + 1)
                    j += 2
                else:
                    j += 1
            elif w == "cmd" and t.startswith("/"):
                j += 1
            elif w not in ("cmd", "powershell", "pwsh") and t.startswith("-"):
                j += 1
            else:
                break
        return passed + [j], False
    return [], False


def starts(toks):
    """Every index in toks where a command may begin, following wrappers, with whether it came through xargs/find."""
    todo, seen = [(0, False)], set()
    while todo:
        tick()
        i, via_xargs = todo.pop()
        if i >= len(toks) or i in seen:
            continue
        seen.add(i)
        if toks[i] == "--":
            todo.append((i + 1, via_xargs))
            continue
        yield i, via_xargs
        nxt, xa = next_starts(toks, i)
        todo.extend((k, via_xargs or xa) for k in nxt)


# --- rules on a command at its start ----------------------------------------------------------------------------------

RM_WORDS = {"rm", "del", "erase", "rd", "rmdir", "remove-item", "ri", "unlink", "shred", "srm"}
LISTERS = {"gci", "get-childitem", "ls", "dir", "find", "fd", "rg", "grep", "where"}
REG_PATH = re.compile(r"^(hklm|hkcu|hkcr|hku|hkcc|hkey_[a-z_]+)[:\\]|^registry::", re.I)
REG_ITEM_CMDS = {"new-item", "ni", "remove-item", "ri", "del", "rm", "erase", "rd", "rmdir", "set-item", "si",
                 "clear-item", "cli", "move-item", "mi", "move", "rename-item", "rni", "ren", "copy-item", "cpi",
                 "copy", "new-itemproperty", "set-itemproperty", "sp", "remove-itemproperty", "rp",
                 "clear-itemproperty", "clp", "rename-itemproperty", "rnp", "copy-itemproperty", "cpp",
                 "move-itemproperty", "mp"}
# system paths: never written by a command (the guard's own files are protected separately, for every command)
SYSTEM_PATH = re.compile(r"(?i)(^|[\\/'\"\s=:>])(/etc/|/proc/sysrq|/sys/|/boot/|authorized_keys|sudoers|crontabs?\b|"
                         r"/var/spool/cron)")
WRITERS = {"tee", "tee-object", "set-content", "add-content", "out-file", "ac", "sc", "cp", "copy", "copy-item",
           "cpi", "mv", "move", "move-item", "mi", "ln", "install", "new-item", "ni", "dd", "truncate", "rsync",
           "scp", "chmod", "chown", "rename-item", "ren", "curl", "wget", "invoke-webrequest", "iwr"}
DEST_LAST = {"cp", "copy", "copy-item", "cpi", "mv", "move", "move-item", "mi", "ln", "install", "rsync", "scp"}

NEVER = {
    # disks and partitions
    "fdisk": "disk tool", "sfdisk": "disk tool", "gdisk": "disk tool", "sgdisk": "disk tool", "cfdisk": "disk tool",
    "parted": "disk tool", "gparted": "disk tool", "wipefs": "disk tool", "blkdiscard": "disk tool",
    "mke2fs": "disk tool", "mkswap": "disk tool", "mkntfs": "disk tool", "mkdosfs": "disk tool",
    "mkexfatfs": "disk tool", "newfs": "disk tool", "diskpart": "disk tool", "format": "disk tool",
    "format-volume": "disk tool", "clear-disk": "disk tool", "initialize-disk": "disk tool",
    "remove-partition": "disk tool", "new-partition": "disk tool", "resize-partition": "disk tool",
    "set-partition": "disk tool", "set-disk": "disk tool", "repair-volume": "disk tool", "optimize-volume": "disk tool",
    "remove-virtualdisk": "disk tool", "remove-storagepool": "disk tool", "remove-physicaldisk": "disk tool",
    "lvremove": "disk tool", "vgremove": "disk tool", "pvremove": "disk tool", "lvreduce": "disk tool",
    "lvresize": "disk tool", "sdelete": "secure delete", "wipe": "secure delete", "truncate": "truncates a file",
    "clear-content": "truncates a file", "clc": "truncates a file",
    "clear-recyclebin": "permanent delete", "bcdedit": "boot configuration", "mountvol": "volume mount points",
    "rimraf": "recursive delete", "del-cli": "recursive delete", "trash": "delete",
    # shutdown and reboot
    "shutdown": "shutdown/reboot", "reboot": "shutdown/reboot", "halt": "shutdown/reboot",
    "poweroff": "shutdown/reboot", "kexec": "shutdown/reboot", "telinit": "shutdown/reboot",
    "stop-computer": "shutdown/reboot", "restart-computer": "shutdown/reboot", "logoff": "shutdown/reboot",
    "suspend-computer": "shutdown/reboot",
    # firewall, network and security settings (START_HERE section 4: never)
    "iptables-restore": "firewall", "ip6tables-restore": "firewall",
    "set-mppreference": "security settings", "add-mppreference": "security settings",
    "remove-mppreference": "security settings", "set-executionpolicy": "security settings",
    "disable-computerrestore": "security settings", "set-processmitigation": "security settings",
    "disable-bitlocker": "security settings", "suspend-bitlocker": "security settings",
    "set-acl": "permissions", "takeown": "permissions", "cacls": "permissions", "auditpol": "security settings",
    "secedit": "security settings", "setenforce": "security settings", "aa-disable": "security settings",
    "aa-complain": "security settings", "semanage": "security settings", "set-netconnectionprofile": "security settings",
    "disable-netadapter": "network change", "enable-netadapter": "network change", "restart-netadapter": "network change",
    "set-netadapter": "network change", "remove-netipaddress": "network change", "new-netipaddress": "network change",
    "set-netipinterface": "network change", "set-dnsclientserveraddress": "network change",
    "remove-netroute": "network change", "new-netroute": "network change",
    # accounts and credentials
    "useradd": "accounts", "userdel": "accounts", "usermod": "accounts", "adduser": "accounts", "deluser": "accounts",
    "groupadd": "accounts", "groupdel": "accounts", "groupmod": "accounts", "passwd": "accounts",
    "chpasswd": "accounts", "chage": "accounts", "gpasswd": "accounts", "visudo": "accounts",
    "new-localuser": "accounts", "remove-localuser": "accounts", "set-localuser": "accounts",
    "rename-localuser": "accounts", "disable-localuser": "accounts", "enable-localuser": "accounts",
    "add-localgroupmember": "accounts", "remove-localgroupmember": "accounts", "new-localgroup": "accounts",
    "remove-localgroup": "accounts", "set-localgroup": "accounts", "rename-localgroup": "accounts",
    "enable-psremoting": "WinRM settings", "disable-psremoting": "WinRM settings",
    "set-wsmanquickconfig": "WinRM settings", "enable-scheduledtask": "scheduled task change",
    "register-scheduledjob": "schedule", "unregister-scheduledjob": "schedule", "set-scheduledjob": "schedule",
    "enable-scheduledjob": "schedule", "disable-scheduledjob": "schedule",
    "ssh-copy-id": "credentials", "ssh-add": "credentials", "printenv": "prints the environment (secrets)",
    # services, processes and schedules (START_HERE: never on a schedule)
    "stop-service": "service change", "start-service": "service change", "restart-service": "service change",
    "set-service": "service change", "new-service": "service change", "remove-service": "service change",
    "suspend-service": "service change", "resume-service": "service change", "spsv": "service change",
    "sasv": "service change", "update-rc.d": "service change", "chkconfig": "service change",
    "rc-service": "service change", "rc-update": "service change", "systemd-run": "schedule/transient unit",
    "unregister-scheduledtask": "scheduled task change", "disable-scheduledtask": "scheduled task change",
    "set-scheduledtask": "scheduled task change", "register-scheduledtask": "scheduled task change",
    "new-scheduledtask": "scheduled task change", "atrm": "schedule", "invoke-cimmethod": "WMI/CIM method call",
    "invoke-wmimethod": "WMI/CIM method call", "taskkill": "process kill", "tskill": "process kill",
    "stop-process": "process kill", "spps": "process kill", "pkill": "process kill", "killall": "process kill",
    "xkill": "process kill",
    # databases and packages
    "dropdb": "database drop", "dropuser": "database drop", "pg_dropcluster": "database drop",
    "pg_ctlcluster": "database service change", "pg_ctl": "database service change",
    "uninstall-package": "uninstall", "msiexec": "install/uninstall",
}
SYSTEMCTL_MUTATE = {"start", "stop", "restart", "try-restart", "reload", "reload-or-restart", "try-reload-or-restart",
                    "kill", "clean", "freeze", "thaw", "enable", "disable", "reenable", "preset", "preset-all", "mask",
                    "unmask", "link", "revert", "add-wants", "add-requires", "edit", "set-property", "set-default",
                    "isolate", "daemon-reload", "daemon-reexec", "set-environment", "unset-environment",
                    "import-environment", "default", "rescue", "emergency", "halt", "poweroff", "reboot", "kexec",
                    "suspend", "hibernate", "hybrid-sleep", "suspend-then-hibernate", "soft-reboot", "switch-root",
                    "exit", "reset-failed", "bind", "mount-image"}
TAILSCALE_SAFE = {"status", "ip", "ping", "netcheck", "version", "whois", "metrics", "licenses", "dns", "help",
                  "exit-node", "--help", "-h", "--version"}
DOCKER_BAD = {"rm", "rmi", "stop", "kill", "restart", "prune"}
DOCKER_GROUP_BAD = {"prune", "rm", "remove", "stop", "kill", "restart", "leave", "disable", "rmi"}
COMPOSE_BAD = {"down", "rm", "stop", "kill", "restart", "pause", "config"}
IPTABLES_MUTATE = {"-A", "-I", "-D", "-F", "-X", "-P", "-N", "-R", "-Z", "-E", "--append", "--insert", "--delete",
                   "--flush", "--policy", "--new-chain", "--delete-chain", "--replace", "--zero", "--rename-chain"}


def docker_sub(args):
    """docker's subcommand words, skipping global options and their values."""
    out, j = [], 0
    while j < len(args):
        if args[j].startswith("-"):
            j += 2 if args[j] in DOCKER_GLOBAL_VALUE and "=" not in args[j] else 1
            continue
        out.append(args[j].lower())
        j += 1
    return out


GIT_SUBS = {"add", "am", "apply", "archive", "bisect", "blame", "branch", "bundle", "checkout", "cherry-pick", "clean",
            "clone", "commit", "config", "credential", "describe", "diff", "fetch", "filter-branch", "filter-repo",
            "format-patch", "fsck", "gc", "grep", "init", "log", "ls-files", "ls-remote", "merge", "mv", "notes",
            "prune", "pull", "push", "rebase", "reflog", "remote", "replace", "reset", "restore", "revert", "rm",
            "show", "stash", "status", "submodule", "switch", "tag", "update-ref", "worktree", "check-ignore",
            "rev-parse", "rev-list", "shortlog", "cat-file", "symbolic-ref", "sparse-checkout", "lfs", "maintenance"}


def git_rules(args):
    al = [a.lower() for a in args]
    # the subcommand is the first known git verb: a quoted `-C "C:\- Tools\..."` splits into several tokens
    j = next((k for k, a in enumerate(al) if a in GIT_SUBS and (k == 0 or al[k - 1] not in ("-c",))), None)
    if j is None:
        return None
    sub, rest = al[j], al[j + 1:]
    rest_raw = args[j + 1:]
    rsf = short_flags(rest_raw)
    lo = lambda full: long_opt(rest, full)
    if sub == "push" and (lo("--force") or lo("--force-with-lease") or lo("--mirror") or lo("--delete") or
                          lo("--prune") or any(a.startswith(("+", ":")) for a in rest) or "f" in rsf or "d" in rsf):
        return "forced or deleting push"
    if sub == "reset" and lo("--hard"):
        return "git reset --hard"
    if sub == "clean" and ("f" in rsf or lo("--force")):
        return "git clean"
    if sub == "branch" and ("D" in rsf or (("d" in rsf or lo("--delete")) and ("f" in rsf or lo("--force")))):
        return "git branch force delete"
    if sub == "stash" and not (rest[:1] and rest[0] in ("list", "show")):
        return "git stash changes the working tree (and the shared stash stack): use a WIP commit"
    if sub == "credential" or (sub == "config" and any("credential" in a or "token" in a for a in rest)):
        return "prints or changes a stored credential"
    if sub in ("filter-branch", "filter-repo") or (sub == "reflog" and rest[:1] in (["expire"], ["delete"])):
        return "git history rewrite"
    if sub in ("checkout", "switch") and ("f" in rsf or lo("--force") or lo("--discard-changes") or "--" in rest
                                          or "." in rest):
        return "git checkout/switch discarding work"
    if sub == "restore" and ("--staged" not in rest or any(a in ("--worktree", "-w", "-W") for a in rest)):
        return "git restore discarding work"
    if sub == "worktree" and rest[:1] == ["remove"] and ("f" in rsf or lo("--force")):
        return "git worktree remove --force"
    if sub == "update-ref" and ("d" in rsf or lo("--delete")):
        return "git update-ref -d"
    if sub == "rm" and ("f" in rsf or lo("--force")):
        return "git rm --force"
    return None


def check_at(toks, via_xargs):
    w = word(toks[0])
    args = toks[1:]
    al = [a.lower() for a in args]
    sf = short_flags(args)

    # a command word known only at run time ($X): refuse when a recursive flag rides along
    if toks[0].startswith(("$", "@(", "(")) and not toks[0].lower().startswith("$env:") and "=" not in toks[0] \
            and toks[1:2] != ["="] and any((re.fullmatch(r"-[A-Za-z]{0,3}[rR][A-Za-z]{0,3}", a) and
                                            a.lower() not in PS_OPERATORS) or is_recurse_param(a)
                                           or a in ("/s", "--recursive") for a in args):
        return "command built at run time with a recursive flag"
    # ... and a segment that starts with flags is what's left after ${X}, $(...) or backticks: force+recursive only
    if toks[0].startswith("-"):
        fl = [toks[0]] + args
        fs = short_flags(fl)
        if (("r" in fs or "R" in fs) and "f" in fs) or (any(is_recurse_param(a) for a in fl) and
                                                         any(a.lower().startswith("-force") for a in fl)):
            return "command built at run time with force+recursive flags"

    # truncation by a bare redirect: `> file`
    m = re.match(r"^>(?![>&])(\S*)$", toks[0])
    if m:
        target = (m.group(1) or (args[0] if args else "")).lower()
        if target not in ("/dev/null", "$null", "nul", "") and not target.startswith("&"):
            return "truncates a file"

    # recursive and mass deletes
    if w in RM_WORDS:
        if via_xargs:
            return "mass delete through xargs/find"
        if w in ("shred", "srm"):
            return "secure delete"
        if recursive(args):
            return "recursive delete"
        if w in ("del", "erase", "rd", "rmdir") and "/s" in al:
            return "recursive delete"
    if w == "find" and "-delete" in al:
        return "find with delete"
    if w == "rg" and any(a.startswith("--pre") for a in al):
        return "rg --pre runs a command per file"
    if w == "forfiles" and any(re.search(r"\b(del|erase|rd|rmdir|rm)\b", a) for a in al):
        return "forfiles with delete"
    if w == "rsync" and any(a.startswith(("--del", "--remove-source")) for a in al):
        return "rsync with delete"
    if w == "rclone" and nonflags(al)[:1] and nonflags(al)[0] in (
            "purge", "delete", "deletefile", "rmdir", "rmdirs", "sync", "cleanup", "dedupe", "move", "moveto",
            "bisync", "config"):
        return "rclone delete/sync/config"
    if w == "robocopy" and any(a in ("/mir", "/purge", "/move", "/mov") for a in al):
        return "robocopy mirror/purge"
    if w == "crontab" and "-l" not in al:
        return "crontab change"
    if w == "journalctl" and any(re.match(r"^--(vacuum|rotate|flush|relinquish)", a) for a in al):
        return "log deletion"
    if w in ("cp", "copy", "copy-item") and any(a in ("/dev/null", "nul", "$null") for a in al):
        return "truncates a file"

    # writes into system paths (cp/mv family: only the destination counts)
    if w in WRITERS or (w == "sed" and any(a.startswith(("-i", "--in-place")) for a in al)):
        targets = nonflags(args)[-1:] if w in DEST_LAST else args
        if any(SYSTEM_PATH.search(" " + a) for a in targets):
            return "write to a system path"

    # disks
    if w.startswith("mkfs"):
        return "disk tool"
    if w == "dd" and any(a.startswith("of=") for a in al):
        return "disk tool (dd of=)"
    if w == "nvme" and nonflags(al)[:1] and nonflags(al)[0] in ("format", "sanitize", "delete-ns", "create-ns",
                                                                  "attach-ns", "detach-ns", "fw-commit", "fw-download",
                                                                  "write", "write-zeroes", "set-feature", "reset"):
        return "disk tool"
    if w == "fsutil" and not (al[:1] == ["fsinfo"] or al[:2] == ["volume", "diskfree"]):
        return "disk tool"
    if w == "chkdsk" and any(a in ("/f", "/r", "/x", "/b") for a in al):
        return "disk repair"
    if w in ("vssadmin", "wbadmin") and any(a in ("delete", "resize") for a in al):
        return "shadow copy / backup deletion"
    if w == "wsl" and any(a in ("--unregister", "--shutdown", "--terminate", "-t", "--uninstall") for a in al):
        return "WSL distro shutdown/removal"
    if w == "zpool" and nonflags(al)[:1] not in (["status"], ["list"], ["iostat"], ["get"], ["history"]):
        return "disk tool"
    if w == "zfs" and nonflags(al)[:1] not in (["list"], ["get"]):
        return "disk tool"
    if w == "mdadm" and not any(a in ("--detail", "-d", "--examine", "-e", "--query", "-q") for a in al):
        return "disk tool"
    if w == "cryptsetup" and nonflags(al)[:1] not in (["status"], ["luksdump"], ["isluks"]):
        return "disk tool"

    # registry
    if w == "reg" and al[:1] and al[0] in ("delete", "add", "import", "restore", "load", "unload", "copy"):
        return "registry change"
    if w in ("regedit", "regini", "regedt32") and args:
        return "registry change"
    if w in REG_ITEM_CMDS and any(REG_PATH.match(a.split(":", 1)[1] if a.startswith("-") and ":" in a else
                                                 a.lstrip("-").split("=")[-1]) for a in args):
        return "registry change"
    if w in ("set-itemproperty", "sp", "new-itemproperty", "remove-itemproperty", "rp", "clear-itemproperty"):
        return "registry/property change"
    if w in ("new-psdrive", "ndr", "mount") and any("registry" in a for a in al):
        return "registry drive"
    if w in ("set-item", "si", "new-item", "ni", "remove-item", "ri", "clear-item") and any(
            a.lower().lstrip("-").split(":", 1)[-1].startswith("wsman:") or a.lower().startswith("wsman:") for a in args):
        return "WinRM settings"
    if w == "winrm" and nonflags(al)[:1] and nonflags(al)[0] in ("quickconfig", "qc", "set", "s", "create", "c",
                                                                  "delete", "d", "invoke", "i", "configsddl"):
        return "WinRM settings"
    if w == "cipher" and any(a.startswith(("/w", "/e", "/d", "/r", "/k", "/x", "/u")) for a in al):
        return "cipher wipe/encrypt"
    if "init.d" in toks[0].lower().replace("\\", "/") or w in ("invoke-rc.d", "rc-service"):
        if any(a in ("start", "stop", "restart", "reload", "force-reload", "force-stop") for a in al):
            return "service change"
    if w in ("get-item", "gi", "get-content", "gc", "cat", "type", "get-childitem", "gci", "dir", "ls") and any(
            a.lower().startswith("env:") and len(a) > 4 for a in args):
        return "reads a secret from the environment"

    # firewall, network, security, accounts, secrets
    if w == "netsh" and ("show" not in al or "exec" in al or "-f" in al) and any(
            a in ("set", "add", "delete", "reset", "import", "install", "uninstall", "advfirewall", "firewall",
                  "exec", "-f") for a in al):
        return "network/firewall change"
    if w == "ufw" and al[:1] != ["status"]:
        return "firewall"
    if re.fullmatch(r"ip6?tables(-nft|-legacy)?", w):
        reads = any(a in ("-L", "-S", "--list", "--list-rules") or re.fullmatch(r"-[nvx]*L[nvx]*", a) for a in args)
        if any(a in IPTABLES_MUTATE for a in args) or not reads:
            return "firewall"
    if re.fullmatch(r"ip6?tables(-nft|-legacy)?-restore", w) or w == "ebtables":
        return "firewall"
    if w == "nft" and nonflags(al)[:1] != ["list"]:
        return "firewall"
    if w == "firewall-cmd" and not all(a.startswith("--list") or a in ("--state", "--get-zones",
                                                                         "--get-active-zones") for a in al):
        return "firewall"
    if re.fullmatch(r"(new|set|remove|disable|enable|rename|copy)-netfirewall\w*", w):
        return "firewall"
    if w == "ip" and nonflags(al)[:1] and nonflags(al)[0] in ("link", "l", "addr", "address", "a", "route", "r",
                                                               "rule", "neigh", "tunnel") and any(
            a in ("set", "del", "delete", "flush", "add", "change", "replace", "down") for a in al):
        return "network change"
    if w in ("ifconfig", "ifdown", "ifup") and (w != "ifconfig" or any(a in ("down", "up") for a in al)):
        return "network change"
    if w == "nmcli" and any(a in ("down", "off", "delete", "modify", "disconnect") for a in al):
        return "network change"
    if w == "manage-bde" and al[:1] != ["-status"]:
        return "security settings"
    if w == "icacls" and any(re.match(r"^/(grant|deny|remove|reset|setowner|inheritance|setintegritylevel|restore)",
                                      a) for a in al):
        return "permissions"
    if w == "net" and al[:1]:
        if al[0] in ("stop", "start", "pause", "continue") and len(al) > 1:  # bare `net start` lists services
            return "service change"
        if al[0] in ("user", "localgroup", "group", "accounts") and len(al) > 1:
            return "accounts"
        if "/delete" in al or "/d" in al:
            return "share/connection delete"
    if w == "sysctl" and ("-w" in al or "--write" in al or any("=" in a for a in al)):
        return "kernel setting"
    if w == "tailscale" and nonflags(al)[:1] and nonflags(al)[0] not in TAILSCALE_SAFE:
        if not (nonflags(al)[0] in ("serve", "funnel") and nonflags(al)[1:2] == ["status"]):
            return "Tailscale change"
    if w == "cloudflared" and any(a in ("delete", "cleanup", "route", "install", "uninstall") for a in al):
        return "Cloudflare tunnel/service change"
    if w == "rundll32" and any("powrprof" in a or "lockworkstation" in a for a in al):
        return "shutdown/reboot"
    if w == "ssh-keygen" and not any(a == "-F" or a.startswith("-l") for a in args):
        return "credentials"
    if w == "ssh" and any("remotecommand" in a or a.startswith("-oremote") for a in al):
        return "ssh RemoteCommand option: write `ssh host '<cmd>'` so the guard can read it"
    if w == "gh" and (al[:2] == ["auth", "token"] or "--show-token" in al or ("-t" in al and "auth" in al)):
        return "prints a token"
    if w == "env" and not nonflags([a for a in args if "=" not in a]):
        return "prints the environment (secrets)"
    if w in ("set", "export", "declare", "typeset", "compgen") and (not args or any(a in ("-p", "-x", "-e")
                                                                                    for a in al)):
        return "prints the environment (secrets)"
    if w in ("get-childitem", "gci", "dir", "ls", "get-item", "gi", "get-content", "gc", "cat", "type") and any(
            a.rstrip("\\/").lower() in ("env:", "env:*") for a in args):
        return "prints the environment (secrets)"

    # services, processes and schedules
    if w == "systemctl" and any(a in SYSTEMCTL_MUTATE for a in nonflags(al)):
        return "service change (systemctl)"
    if w == "service" and any(a in ("start", "stop", "restart", "reload", "force-reload", "--full-restart")
                              for a in al):
        return "service change"
    if w == "loginctl" and any(a.startswith(("terminate", "kill", "poweroff", "reboot", "suspend", "hibernate"))
                               for a in al):
        return "session kill / shutdown"
    if w == "snap" and al[:1] and al[0] in ("stop", "restart", "disable", "remove", "revert"):
        return "service change"
    if w == "sc":
        verb = [a for a in al if not a.startswith("\\\\")][:1]  # sc \\server stop x
        if verb and verb[0] in ("stop", "start", "delete", "config", "create", "pause", "continue", "failure",
                                "failureflag", "sdset", "privs", "sidtype", "triggerinfo", "control", "description",
                                "managedaccount"):
            return "service change"
    if w == "schtasks" and any(a in ("/delete", "/change", "/end", "/create") for a in al):
        return "scheduled task change"
    if w == "wmic" and any(a in ("call", "delete", "set") for a in al):
        return "WMI change"
    if w == "kill" and not (al[:1] in (["-l"], ["-list"], ["-0"])):
        return "process kill"
    if w == "at" and args and al != ["-l"] and ("-f" in al or any(
            re.match(r"(?i)^(now|noon|midnight|teatime|tomorrow|\d)", a) for a in args)):
        return "schedule"
    if w == "init" and al[:1] and al[0] in ("0", "1", "6", "s"):
        return "shutdown/reboot"
    if w in ("apt", "apt-get", "aptitude") and any(a in ("remove", "purge", "autoremove", "autopurge") for a in al):
        return "uninstall"
    if w == "dpkg" and any(a in ("-r", "-P", "--remove", "--purge") for a in args):
        return "uninstall"
    if w in ("winget", "choco", "scoop", "pip", "pip3", "npm") and any(a in ("uninstall", "remove", "rm") for a in al):
        return "uninstall"

    # docker
    if w in ("docker", "podman", "docker-compose"):
        sub = docker_sub(args)
        if w == "docker-compose" or sub[:1] == ["compose"]:
            rest = sub[1:] if sub[:1] == ["compose"] else sub
            if any(a in COMPOSE_BAD for a in rest[:1]) or "--volumes" in al or ("-v" in al and "down" in rest):
                return "docker compose stop/remove/config (config prints .env values)"
        elif sub[:1] and sub[0] in DOCKER_BAD:
            return "docker %s" % sub[0]
        elif len(sub) > 1 and sub[1] in DOCKER_GROUP_BAD:
            return "docker %s %s" % (sub[0], sub[1])
        if sub[:1] == ["inspect"] or sub[:2] == ["container", "inspect"]:
            fmt = [args[k + 1] for k in range(len(args) - 1) if args[k] in ("-f", "--format")] + \
                  [a.split("=", 1)[1] for a in args if a.startswith("--format=")]
            has_fmt = any(a in ("-f", "--format") or a.startswith("--format=") for a in args)
            if not has_fmt or any(re.search(r"(?i)env|json \.\s*}}|{{\s*\.\s*}}|\.config\s*}}", f) for f in fmt):
                return "docker inspect prints container env (secrets): use --format without Env"

    if w == "git":
        r = git_rules(args)
        if r:
            return r

    # chmod/chown -R
    if w in ("chmod", "chown", "chgrp", "setfacl") and ("R" in sf or long_opt(args, "--recursive")):
        return "recursive chmod/chown"

    # databases
    if w == "pg_restore" and ("--clean" in al or "c" in sf):
        return "pg_restore --clean"

    # PowerShell encoded commands are opaque
    if w in ("powershell", "pwsh") and any(re.fullmatch(r"-e(n|nc|nco|ncod|ncode|ncoded|ncodedc\w*|c)?", a)
                                           for a in al):
        return "encoded PowerShell command (opaque)"

    return NEVER.get(w)


# --- patterns that refuse wherever they appear -------------------------------------------------------------------------

CODE_DELETE = re.compile(
    r"(?i)rmtree|rmsync|rmdirsync|\bfs\.(rm|rmdir)\s*\(|require\(\s*.fs.\s*\)\.rm(dir)?\s*\(|rm_rf|\brm_r\b|"
    r"remove_tree|::deletedirectory|directory\]::delete|os\.removedirs|removeall\s*\(|"
    r"\[\s*['\"](rm|del|rmdir|rd|shred)['\"]\s*,\s*['\"]-[a-z]*r|os\.system\s*\(|subprocess\.\w+\(\s*['\"]")
ANYWHERE = [
    (CODE_DELETE, "recursive delete or shell call in code"),
    (re.compile(r"(?i)\[(microsoft\.win32\.)?registry(key)?\]::|deletesubkey|deletevalue|\.setvalue\s*\("),
     "registry via .NET"),
    (re.compile(r"(?i)>\s*/dev/(sd|hd|vd|xvd|nvme|mmcblk|disk|dm-|md)\w*|of=/dev/(sd|hd|vd|xvd|nvme|mmcblk|disk|dm-|md)"),
     "write to a block device"),
    (re.compile(r"(?i)\b(drop\s+(database|table|schema|role|user|owned|extension|view|index|cluster)|"
                r"truncate\s+(table\s+)?(only\s+)?[\"\w.]+\s*(;|,|$|\bcascade\b|\brestart\b)|delete\s+from|"
                r"alter\s+(system|role|user|database)|alter\s+table\b[^;]*\bdrop\b)"), "database change"),
    (re.compile(r"(?i)frombase64string|base64\s+(-d|--decode|-D)\b"), "decoded command (opaque)"),
    (re.compile(r"(?i)\|\s*(sudo\s+)?(ba|z|da|k|fi)?sh\b|\|\s*(iex|invoke-expression|pwsh|powershell(\.exe)?)\b|"
                r"\|\s*ssh\b[^|;&\n]{0,300}?\s(sudo\s+)?(ba|z|da|k)?sh\b"), "something piped into a shell"),
    (re.compile(r"(?i)\|\s*(%|foreach-object)\s+(\{[^}]{0,400}\.)?(delete|kill|stop|terminate)\b|"
                r"\.(delete|kill|stop|terminate|reboot|shutdown|win32shutdown|win32shutdowntracker|uninstall|"
                r"setpowerstate|stopservice|startservice|changestartmode)\s*\(|"
                r"(foreach-object|%)\s*\{[^}]{0,400}\b(remove-item|ri|rm|del)\b"), "delete/stop through a method"),
    (re.compile(r"(?i)\brecurse\s*=\s*(\$?true|1)\b|psdefaultparametervalues"), "recursive delete by splatting/defaults"),
    (re.compile(r"(?i)(remove-item|\bri|\brm|\bdel|\berase|\brd|\brmdir)\b[^;\n|]{0,300}\(\s*(gci|get-childitem|ls|dir)"
                r"\b[^)]{0,300}\s-(r|s\b|depth)"), "recursive listing fed to a delete"),
    (re.compile(r"(?i)\[environment\]::getenvironmentvariables?\b|/proc/[\w*]+/environ|"
                r"\$(env:)?\{?\w*(token|secret|passw(or)?d|api_?key|access_?key|credential)\w*\}?"),
     "reads a secret from the environment"),
    (re.compile(r"(?i)disableallhooks"), "turns hooks off"),
    (re.compile(r"(?i)\binspect\b[^;|\n]{0,300}?(\.config\.env|\.env\b|\{\{\s*json\s+\.\s*\}\}|\{\{\s*\.\s*\}\}|"
                r"\.config\s*\}\})"), "docker inspect of the environment (secrets)"),
    (re.compile(r"(?i)>>?\s*['\"]?[^\s;|&'\"]*(/etc/|/proc/sysrq|/sys/|authorized_keys|sudoers|/var/spool/cron)"),
     "write to a system path"),
    (re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:"), "fork bomb"),
]

# The guard's own files and the settings that wire it: any command naming them must only read them
GUARD_FILES = re.compile(r"(?i)\.claude/+settings|tools/+guard(_core|_test)?\b|guard_core|guard_test")
READ_ONLY_WORDS = {"cat", "type", "get-content", "gc", "head", "tail", "less", "more", "grep", "egrep", "rg",
                   "findstr", "select-string", "sls", "wc", "ls", "dir", "stat", "get-item", "gi", "get-childitem", "gci",
                   "test-path", "file", "sha256sum", "md5sum", "get-filehash", "diff", "fc", "comp", "jq"}
GIT_READ = {"add", "diff", "log", "show", "status", "commit", "blame", "ls-files", "check-ignore"}

SECRET_PATH = re.compile(
    r"(^|[\\/'\"\s=:<])(id_(rsa|dsa|ecdsa|ed25519)(_sk)?(?!\.pub)\b|"
    r"[\w.-]+\.(pem|key|ppk|p12|pfx|kdbx)\b|[^\s'\"]*\.env(\.(?!example\b|sample\b|template\b)[\w.]+)?(?![\w.])|"
    r"rclone\.conf|\.pgpass|\.git-credentials|\.netrc|credentials\.json|\.credentials\.json|\.aws[\\/]credentials|"
    r"hosts\.yml|\.docker[\\/]config\.json|token\.json|db_password\b|bastion-ops[\\/]secrets|"
    r"backrest[\\/]+(config|rclone)|/run/secrets|/etc/g?shadow\b|ssh_host_\w+_key\b(?!\.pub)|"
    r"/proc/[\w*]+/environ)", re.I)
SECRET_NAMES = [".env", "id_rsa", "id_ed25519", "id_ecdsa", "id_dsa", "rclone.conf", ".pgpass", "db_password.txt",
                "db_password", ".git-credentials", ".netrc", ".credentials.json", "credentials.json", "secrets",
                "shadow", "config.json"]
SECRET_READERS = {"cat", "type", "get-content", "gc", "head", "tail", "less", "more", "strings", "xxd", "od", "base64",
                  "cp", "copy", "copy-item", "scp", "sed", "awk", "grep", "rg", "select-string", "sls", "findstr",
                  "tar", "zip", "7z", "compress-archive", "curl", "nano", "vi", "vim", "code", "notepad", "bat", "jq",
                  "python", "python3", "py", "node", "openssl", "age", "gpg"}
SECRET_OK_WORDS = {"ls", "dir", "stat", "test", "[", "test-path", "get-item", "gi", "get-childitem", "gci", "echo",
                   "printf", "write-output", "write-host"}
GIT_NAME_ONLY = {"check-ignore", "ls-files", "status", "rm"}


def secret_token(t, reader):
    if SECRET_PATH.search(" " + t):
        return True
    path = t.strip("'\"")
    base = re.split(r"[\\/]", path)[-1]
    if reader and any(c in base for c in "*?[") and not REG_PATH.match(path):  # a wildcard that could read a secret
        if base in ("*", "*.*"):  # a bare wildcard counts only where secrets live
            return bool(re.search(r"(?i)\.ssh|secrets|bench-register|backrest|\.aws|\.config[\\/]+(gh|rclone)", path))
        return any(fnmatch.fnmatchcase(n, base) for n in SECRET_NAMES)
    return False


def secret_reason(toks):
    w = word(toks[0])
    cands = toks if toks[0].startswith("<") else toks[1:]
    if w in SECRET_OK_WORDS and not toks[0].startswith("<"):
        return None
    if w == "git" and any(t.lower() in GIT_NAME_ONLY for t in toks[1:4]):
        return None
    if w == "find" and not any(t.lower() in ("-exec", "-execdir", "-ok", "-okdir") for t in toks):
        return None
    reader = w in SECRET_READERS or toks[0].startswith("<")
    for k, t in enumerate(cands):
        if w in ("ssh", "scp", "sftp", "rsync") and k > 0 and cands[k - 1] == "-i":
            continue  # the key handed to ssh is used, not printed
        if secret_token(t, reader):
            return "reads a secret file (%s): name it by path, never read it" % t
    return None


def guard_files_reason(cmd):
    """Any segment naming the guard or the settings must be a plain read (or git add/commit/diff ...)."""
    if not GUARD_FILES.search(re.sub(r"[\\/]+(\.[\\/]+)*", "/", cmd)):
        return None
    for stmt in statements(cmd):
        toks = qtokens(stmt)
        joined = re.sub(r"[\\/]+(\.[\\/]+)*", "/", " ".join(toks))
        if not toks or not GUARD_FILES.search(joined):
            continue
        w = word(toks[0])
        if w in READ_ONLY_WORDS:
            continue
        if w == "sed" and not any(a.startswith(("-i", "--in-place")) for a in toks[1:]):
            continue
        if w == "git" and next((t.lower() for t in toks[1:] if t.lower() in GIT_SUBS), "") in GIT_READ:
            continue
        if w in ("python", "python3", "py") and re.search(r"guard_test\.py$", joined) and \
                all(t in ("-I", "-B") or "guard_test" in t for t in toks[1:]):
            continue
        if w in ("python", "python3", "py") and re.search(r"(^|\s)(-I\s+)?tools/+secret_scan\.py\b", joined):
            continue  # the secret scan only reads the files it is given
        return "touches the guard or its settings: only the owner changes them"
    return None


# --- pipelines and scripts ---------------------------------------------------------------------------------------------

def pipeline_reason(cmd):
    """Stage-wise: a recursive listing piped into a delete; find -exec with any delete word."""
    for stmt in re.split(r"[;\n]|&&|\|\|", cmd):
        stages = [tokens(s.replace("'", " ").replace('"', " ")) for s in stmt.split("|")]
        for k, st in enumerate(stages):
            if not st:
                continue
            w = word(st[0])
            if w in LISTERS and (recursive(st[1:]) or any(a.lower() in ("-s", "/s") or a.lower().startswith("-depth")
                                                           for a in st[1:])):
                later = [t for s in stages[k + 1:] for t in s]
                if any(word(t) in RM_WORDS | {"delete"} for t in later):
                    return "recursive listing piped into a delete"
            if w == "find" and any(a.lower() in ("-exec", "-execdir", "-ok", "-okdir") for a in st) and \
                    re.search(r"(?i)(^|[\s'\"/])(rm|del|unlink|shred|rmdir|remove-item)(\s|$|['\"])", stmt):
                return "find -exec with a delete"
    return None


SCRIPT_EXT = re.compile(r"(?i)\.(sh|bash|zsh|ps1|psm1|bat|cmd|py)$")
INTERPRETERS = {"bash", "sh", "zsh", "dash", "ksh", "powershell", "pwsh", "python", "python3", "py", "node", "perl",
                "ruby", "source", "."}


def resolve(path, cwd):
    p = path.strip("'\"")
    if p.startswith("~"):
        p = os.path.expanduser(p)
    m = re.match(r"^/([a-zA-Z])/(.*)$", p)  # Git Bash /c/Users/...
    if m:
        p = "%s:/%s" % (m.group(1), m.group(2))
    return p if os.path.isabs(p) else os.path.join(cwd or os.getcwd(), p)


def script_paths(toks):
    """Script files this command runs: the command itself (`./x.sh`, `x.bat`), an interpreter's script argument
    (`bash x.sh`, `python x`, `pwsh -File x`), or a file redirected into it (`bash -s < x.sh`)."""
    out = []
    w = word(toks[0])
    first = toks[0].strip("'\"")
    if SCRIPT_EXT.search(first) or first.startswith(("./", ".\\")):
        out.append(first)
    for k, t in enumerate(toks[:12]):
        tt = t.strip("'\"")
        if tt.startswith("<") and len(tt) > 1 and not tt.startswith(("<(", "<<")):
            out.append(tt[1:])
        elif t == "<" and k + 1 < len(toks):
            out.append(toks[k + 1])
    args = toks[1:]
    al = [a.lower() for a in args]
    if w in ("powershell", "pwsh"):
        for k, a in enumerate(al):
            if a in ("-file", "-f") and k + 1 < len(args):
                out.append(args[k + 1])
    elif w in ("python", "python3", "py"):
        if not any(a in ("-c", "-m", "-") for a in al):
            j = 0
            while j < len(args) and args[j].startswith("-"):
                j += 2 if args[j] in ("-W", "-X") else 1
            out += args[j:j + 1]
    elif w in INTERPRETERS:
        if not any(a in ("-c", "-e", "-s", "-") for a in al):
            j = 0
            while j < len(args) and args[j].startswith("-"):
                j += 2 if args[j] in ("-o", "-O", "+O", "--rcfile", "--init-file") else 1
            out += args[j:j + 1]
    return [p for p in dict.fromkeys(out) if p and not p.startswith("$")]


def script_reason(toks, cwd, remote, strict=True):
    """strict: words from the quote-aware pass, where a path is whole, so an unreadable script is refused. The
    split-view pass (strict=False) only adds what the first can't see: scripts named inside quotes (bash -c "bash x")
    and remote ones."""
    for p in script_paths(toks):
        full = resolve(p, cwd)
        if remote and not (toks and "<" in " ".join(toks)):
            return "runs a script on the remote side (%s) that the guard can't read: pipe a local file instead" % p
        try:
            if os.path.getsize(full) > 200000:
                return "script too large to check (%s)" % p
            with open(full, encoding="utf-8", errors="replace") as f:
                body = f.read()
        except OSError:
            if not strict:
                continue
            return "runs a script the guard can't read (%s)" % p
        if remote and "\r" in body:
            return "script %s has CRLF line endings: bash on Linux breaks on them (convert to LF first)" % p
        if re.search(r"(?i)tools[\\/]+guard_test\.py$", full.replace("\\", "/")):
            continue  # the guard's own tests: protected from writes, full of destructive strings by design
        if full.lower().endswith(".py"):
            if CODE_DELETE.search(body):
                return "script %s: recursive delete or shell call in code" % p
            continue
        for line in normalise(body).splitlines():  # line by line: a script may be longer than MAX_LEN
            if line.lstrip().startswith("#"):
                continue  # comments don't run
            r = check(line, cwd, depth=1)
            if r:
                return "script %s: %s" % (p, r)
    return None


# --- the entry -------------------------------------------------------------------------------------------------------

def check(cmd, cwd=None, depth=0):
    if depth == 0:
        _t0[0] = time.monotonic()
    if not cmd or not cmd.strip():
        return None
    if len(cmd) > MAX_LEN:
        return "command too long to check (%d chars)" % len(cmd)
    try:
        return _check(cmd, cwd, depth)
    except Deadline:
        return "command too complex to check in time"


def _check(cmd, cwd, depth):
    cmd = normalise(cmd)
    r = guard_files_reason(cmd)
    if r:
        return r
    cmd = strip_literals(cmd)
    for rx, reason in ANYWHERE:
        tick()
        if rx.search(cmd):
            return reason
    r = pipeline_reason(cmd)
    if r:
        return r
    if re.search(r"\$\{|\$\(|`", cmd):  # a command word may be built at run time: r${X}m -rf, $(echo rm) -rf
        for seg in segments(cmd):
            i = next(iter(starts(seg)))[0]
            while i + 1 < len(seg) and re.match(r"^[$@][\w:.]+=?$", seg[i]) and seg[i + 1] in ("=", "+="):
                i += 2  # PowerShell assignment: $x = <command>
            toks = seg[i:] or seg
            fs = short_flags(toks[1:])
            if word(toks[0]) not in LISTERS | {"cp", "copy", "copy-item", "du", "scp", "rsync", "tree"} and (
                    (("r" in fs or "R" in fs) and "f" in fs) or (any(is_recurse_param(a) for a in toks[1:]) and
                                                                 any(a.lower().startswith("-force") for a in toks))):
                return "force+recursive flags on a command built at run time"
    remote = bool(re.search(r"(?i)(^|[^\w-])(ssh|wsl|docker|podman|kubectl)(?=\s)", cmd))
    for n, view in enumerate(views(cmd)):
        segs = [t for t in (tokens(s) for s in SEP.split(view)) if t]
        in_registry = any(word(t[0]) in ("cd", "sl", "set-location", "push-location", "pushd", "chdir") and
                          any(REG_PATH.match(a) for a in t[1:]) for t in segs)
        here = cwd
        for toks in segs:
            tick()
            if word(toks[0]) in ("cd", "set-location", "sl", "pushd", "chdir") and len(toks) > 1:
                here = resolve(toks[-1], here)
            for i, via_xargs in starts(toks):
                sub = toks[i:]
                if in_registry and word(sub[0]) in REG_ITEM_CMDS:
                    return "registry change (relative path after cd into the registry)"
                reason = check_at(sub, via_xargs) or secret_reason(sub)
                if not reason and depth == 0 and n == 1:  # A's quoted strings run no files; C has lost its \
                    reason = script_reason(sub, here, remote, strict=False)
                if reason:
                    return reason
    if depth == 0:  # scripts run by path, read from whole words: "C:\- Tools\x.ps1", tools\x.py
        here = cwd
        for stmt in statements(cmd):
            toks = qtokens(stmt)
            if not toks:
                continue
            if word(toks[0]) in ("cd", "set-location", "sl", "pushd", "chdir") and len(toks) > 1:
                here = resolve(toks[-1], here)
                continue
            for i, _ in starts(toks):
                r = script_reason(toks[i:], here, remote and "<" not in toks)
                if r:
                    return r
    return None
