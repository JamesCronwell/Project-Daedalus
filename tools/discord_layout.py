"""Discord layout as code (BRIEF 05): import, check-template, names, plan, apply, invite.

    python -I tools/discord_layout.py import --guild ID [--layout discord/layout.toml] [--force]
    python -I tools/discord_layout.py check-template docs/discord/before-2026-10-09.template.json [--layout ...]
    python -I tools/discord_layout.py names [--layout ...]
    python -I tools/discord_layout.py plan [--layout ...]            writes docs/discord/plan-<UTC>.md
    python -I tools/discord_layout.py apply docs/discord/plan-<UTC>.md [--layout ...]
    python -I tools/discord_layout.py invite --app-id ID             prints the bot's invite URL (no secret)

The OWNER runs import, plan and apply. A session never holds the token: it is read here, from the DPAPI file that
tools/discord-setpass.ps1 writes (%LOCALAPPDATA%\\Daedalus\\discord-token.dpapi), and goes nowhere but the
Authorization header. Python standard library only.

What the tool manages: STRUCTURE only: roles (name, colour, hoist, mentionable, permissions, order), categories and
channels (type, name, parent, topic, nsfw, slowmode, user limit, order) and ROLE permission overwrites. It never
touches who holds a role, messages, bots, webhooks, follows, server settings or MEMBER overwrites (they are counted in
the plan, never changed). It never deletes: the API client refuses DELETE outright. Things on the server that the
layout doesn't list are "extras", reported and left alone. A role overwrite the layout doesn't set is neutralised
(allow 0, deny 0), not deleted, and a neutral overwrite counts as no overwrite.

THE LAYOUT FILE (TOML, schema version 1)

    version = 1
    guild_id = "123"                  # a snowflake, as a string (ids are not secrets)
    guild_name = "..."                # information only

    [[role]]                          # listed top (highest) first; the @everyone role (key "everyone") is last
    key = "bots"                      # stable name, unique among roles: what the file refers to
    id = "456"                        # the Discord id; empty or absent = create it (apply writes the id back)
    name = "Bots"
    color = 0                         # integer RGB
    hoist = false
    mentionable = false
    managed = false                   # true: made by an integration; shown, never edited
    permissions = ["VIEW_CHANNEL"]    # names (BIT_n for a bit this tool has no name for)

    [[channel]]                       # file order = sibling order; categories and their children
    key = "general"                   # unique among channels and categories
    id = "789"
    type = "text"                     # text voice category news stage forum media
    name = "general"
    parent = "mess-hall"              # the category's key; absent for categories and uncategorised channels
    topic = ""                        # text, news, forum and media
    nsfw = false
    slowmode = 0                      # seconds
    user_limit = 0                    # voice and stage

    [[channel.overwrite]]             # ROLE overwrites only, belongs to the [[channel]] above it
    role = "everyone"                 # a role key
    allow = []
    deny = ["SEND_MESSAGES"]

A rename keeps the key and the id, so history, webhooks and follows stay. A change to the bits the bot doesn't hold
(Administrator, Manage Server, Kick, Ban, and in a given channel whatever the bot can't do there) shows in the plan
as "yours" and is skipped by apply, which carries on with the rest.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
import tomllib
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone

API_BASE = "https://discord.com/api/v10"
USER_AGENT = "DiscordBot (https://github.com/JamesCronwell/Project-Daedalus, 1)"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LAYOUT = os.path.join(REPO, "discord", "layout.toml")
PLAN_DIR = os.path.join(REPO, "docs", "discord")
ALL_BITS = (1 << 64) - 1

PERM_NAMES = {
    0: "CREATE_INSTANT_INVITE", 1: "KICK_MEMBERS", 2: "BAN_MEMBERS", 3: "ADMINISTRATOR", 4: "MANAGE_CHANNELS",
    5: "MANAGE_GUILD", 6: "ADD_REACTIONS", 7: "VIEW_AUDIT_LOG", 8: "PRIORITY_SPEAKER", 9: "STREAM",
    10: "VIEW_CHANNEL", 11: "SEND_MESSAGES", 12: "SEND_TTS_MESSAGES", 13: "MANAGE_MESSAGES", 14: "EMBED_LINKS",
    15: "ATTACH_FILES", 16: "READ_MESSAGE_HISTORY", 17: "MENTION_EVERYONE", 18: "USE_EXTERNAL_EMOJIS",
    19: "VIEW_GUILD_INSIGHTS", 20: "CONNECT", 21: "SPEAK", 22: "MUTE_MEMBERS", 23: "DEAFEN_MEMBERS",
    24: "MOVE_MEMBERS", 25: "USE_VAD", 26: "CHANGE_NICKNAME", 27: "MANAGE_NICKNAMES", 28: "MANAGE_ROLES",
    29: "MANAGE_WEBHOOKS", 30: "MANAGE_GUILD_EXPRESSIONS", 31: "USE_APPLICATION_COMMANDS", 32: "REQUEST_TO_SPEAK",
    33: "MANAGE_EVENTS", 34: "MANAGE_THREADS", 35: "CREATE_PUBLIC_THREADS", 36: "CREATE_PRIVATE_THREADS",
    37: "USE_EXTERNAL_STICKERS", 38: "SEND_MESSAGES_IN_THREADS", 39: "USE_EMBEDDED_ACTIVITIES",
    40: "MODERATE_MEMBERS", 41: "VIEW_CREATOR_MONETIZATION_ANALYTICS", 42: "USE_SOUNDBOARD",
    43: "CREATE_GUILD_EXPRESSIONS", 44: "CREATE_EVENTS", 45: "USE_EXTERNAL_SOUNDS", 46: "SEND_VOICE_MESSAGES",
    49: "SEND_POLLS", 50: "USE_EXTERNAL_APPS",
}
BIT_BY_NAME = {n: 1 << b for b, n in PERM_NAMES.items()}


def perm_names(v):
    return [PERM_NAMES.get(b, f"BIT_{b}") for b in range(64) if (v >> b) & 1]


def perm_bits(names):
    v = 0
    for n in names:
        if n in BIT_BY_NAME:
            v |= BIT_BY_NAME[n]
        elif re.fullmatch(r"BIT_\d{1,2}", n) and int(n[4:]) < 64:
            v |= 1 << int(n[4:])
        else:
            raise LayoutError(f"unknown permission name {n!r}")
    return v


def _b(*names):
    return sum(BIT_BY_NAME[n] for n in names)


ADMIN = BIT_BY_NAME["ADMINISTRATOR"]
VIEW = BIT_BY_NAME["VIEW_CHANNEL"]
MANAGE_CHANNELS = BIT_BY_NAME["MANAGE_CHANNELS"]
MANAGE_ROLES = BIT_BY_NAME["MANAGE_ROLES"]
# The bot's permission set (owner's yes, 2026-10-09; BRIEF 05 note 3). Never Administrator, Manage Server, Kick, Ban.
BOT_PERMS = _b("VIEW_CHANNEL", "MANAGE_CHANNELS", "MANAGE_ROLES", "SEND_MESSAGES", "EMBED_LINKS", "ATTACH_FILES",
               "READ_MESSAGE_HISTORY", "ADD_REACTIONS", "MENTION_EVERYONE", "MANAGE_WEBHOOKS", "CONNECT", "SPEAK")

CH_TYPES = {"text": 0, "voice": 2, "category": 4, "news": 5, "stage": 13, "forum": 15, "media": 16}
CH_TYPE_NAMES = {v: k for k, v in CH_TYPES.items()}
TOPIC_TYPES = {0, 5, 15, 16}
LIMIT_TYPES = {2, 13}


class LayoutError(Exception):
    pass


class DiscordError(Exception):
    def __init__(self, status, method, path, message):
        super().__init__(f"{method} {path} -> {status}: {message}")
        self.status = status


# ---------------------------------------------------------------- the layout file

def _q(s):
    out = ['"']
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif ord(ch) < 0x20 or ord(ch) == 0x7F:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _arr(names):
    if len(names) <= 3:
        return "[" + ", ".join(_q(n) for n in names) + "]"
    return "[\n" + "".join(f"    {_q(n)},\n" for n in names) + "]"


def dump_layout(layout):
    L = ["# Discord layout (BRIEF 05). Edit it, then the owner runs plan and apply. See tools/discord_layout.py.",
         "version = 1", f"guild_id = {_q(layout['guild_id'])}"]
    if layout.get("guild_name"):
        L.append(f"guild_name = {_q(layout['guild_name'])}")
    for r in layout["roles"]:
        L += ["", "[[role]]", f"key = {_q(r['key'])}", f"id = {_q(r.get('id') or '')}", f"name = {_q(r['name'])}",
              f"color = {int(r['color'])}", f"hoist = {'true' if r['hoist'] else 'false'}",
              f"mentionable = {'true' if r['mentionable'] else 'false'}"]
        if r.get("managed"):
            L.append("managed = true")
        L.append(f"permissions = {_arr(perm_names(r['permissions']))}")
    for c in layout["channels"]:
        L += ["", "[[channel]]", f"key = {_q(c['key'])}", f"id = {_q(c.get('id') or '')}", f"type = {_q(c['type'])}",
              f"name = {_q(c['name'])}"]
        if c.get("parent"):
            L.append(f"parent = {_q(c['parent'])}")
        if c.get("topic"):
            L.append(f"topic = {_q(c['topic'])}")
        if c.get("nsfw"):
            L.append("nsfw = true")
        if c.get("slowmode"):
            L.append(f"slowmode = {int(c['slowmode'])}")
        if c.get("user_limit"):
            L.append(f"user_limit = {int(c['user_limit'])}")
        for o in c.get("overwrites", []):
            L += ["", "[[channel.overwrite]]", f"role = {_q(o['role'])}", f"allow = {_arr(perm_names(o['allow']))}",
                  f"deny = {_arr(perm_names(o['deny']))}"]
    return "\n".join(L) + "\n"


def _need(d, field, typ, where):
    if field not in d or not isinstance(d[field], typ) or (typ is int and isinstance(d[field], bool)):
        raise LayoutError(f"{where}: {field!r} missing or not a {typ.__name__}")
    return d[field]


def _check_unknown(d, allowed, where):
    extra = set(d) - set(allowed)
    if extra:
        raise LayoutError(f"{where}: unknown field(s) {sorted(extra)}")


def _digits(s, where):
    if s and not re.fullmatch(r"\d{1,25}", s):
        raise LayoutError(f"{where}: id {s!r} is not a snowflake")
    return s


def load_layout(text):
    try:
        d = tomllib.loads(text)
    except tomllib.TOMLDecodeError as e:
        raise LayoutError(f"not valid TOML: {e}")
    _check_unknown(d, {"version", "guild_id", "guild_name", "role", "channel"}, "top level")
    if d.get("version") != 1:
        raise LayoutError("version must be 1")
    gid = _digits(_need(d, "guild_id", str, "top level"), "guild_id")
    if not gid:
        raise LayoutError("guild_id is empty")
    roles, chans = [], []
    rkeys, ckeys = set(), set()
    for i, r in enumerate(d.get("role", [])):
        w = f"role #{i + 1}"
        _check_unknown(r, {"key", "id", "name", "color", "hoist", "mentionable", "managed", "permissions"}, w)
        key = _need(r, "key", str, w)
        w = f"role {key!r}"
        if key in rkeys:
            raise LayoutError(f"{w}: duplicate key")
        rkeys.add(key)
        rid = _digits(r.get("id", ""), w)
        if key == "everyone":
            rid = rid or gid
            if rid != gid:
                raise LayoutError(f"{w}: the everyone role's id is the guild id")
        roles.append({"key": key, "id": rid, "name": _need(r, "name", str, w), "color": r.get("color", 0),
                      "hoist": bool(r.get("hoist", False)), "mentionable": bool(r.get("mentionable", False)),
                      "managed": bool(r.get("managed", False)),
                      "permissions": perm_bits(_need(r, "permissions", list, w))})
        if not isinstance(roles[-1]["color"], int):
            raise LayoutError(f"{w}: color must be an integer")
    if "everyone" not in rkeys:
        raise LayoutError("the everyone role (key \"everyone\") is missing")
    if roles[-1]["key"] != "everyone":
        raise LayoutError("the everyone role must be the last [[role]]")
    for i, c in enumerate(d.get("channel", [])):
        w = f"channel #{i + 1}"
        _check_unknown(c, {"key", "id", "type", "name", "parent", "topic", "nsfw", "slowmode", "user_limit",
                           "overwrite"}, w)
        key = _need(c, "key", str, w)
        w = f"channel {key!r}"
        if key in ckeys:
            raise LayoutError(f"{w}: duplicate key")
        ckeys.add(key)
        typ = _need(c, "type", str, w)
        if typ not in CH_TYPES:
            raise LayoutError(f"{w}: type {typ!r} is not one of {sorted(CH_TYPES)}")
        ows = []
        for o in c.get("overwrite", []):
            _check_unknown(o, {"role", "allow", "deny"}, w + " overwrite")
            a, dn = perm_bits(_need(o, "allow", list, w)), perm_bits(_need(o, "deny", list, w))
            if a & dn:
                raise LayoutError(f"{w}: overwrite for {o.get('role')!r} allows and denies {perm_names(a & dn)}")
            ows.append({"role": _need(o, "role", str, w), "allow": a, "deny": dn})
        chans.append({"key": key, "id": _digits(c.get("id", ""), w), "type": typ, "name": _need(c, "name", str, w),
                      "parent": c.get("parent", ""), "topic": c.get("topic", ""), "nsfw": bool(c.get("nsfw", False)),
                      "slowmode": c.get("slowmode", 0), "user_limit": c.get("user_limit", 0), "overwrites": ows})
    cats = {c["key"] for c in chans if c["type"] == "category"}
    for c in chans:
        w = f"channel {c['key']!r}"
        if c["parent"] and (c["parent"] not in cats or c["type"] == "category"):
            raise LayoutError(f"{w}: parent {c['parent']!r} is not a category (or this is a category)")
        for o in c["overwrites"]:
            if o["role"] not in rkeys:
                raise LayoutError(f"{w}: overwrite for unknown role key {o['role']!r}")
        if len({o["role"] for o in c["overwrites"]}) != len(c["overwrites"]):
            raise LayoutError(f"{w}: two overwrites for one role")
    return {"guild_id": gid, "guild_name": d.get("guild_name", ""), "roles": roles, "channels": chans}


def set_id_in_text(text, kind, key, new_id):
    """Write `id = "<new_id>"` into the [[role]] / [[channel]] block whose key is `key`, keeping every other byte."""
    lines = text.split("\n")
    table = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("["):
            table = s
            continue
        if table == f"[[{kind}]]" and re.fullmatch(r'key\s*=\s*"' + re.escape(key) + r'"', s):
            new = f'id = "{new_id}"'
            j = i + 1
            while j < len(lines) and lines[j].strip() != "" and not lines[j].strip().startswith("["):
                if re.match(r"\s*id\s*=", lines[j]):
                    lines[j] = new
                    return "\n".join(lines)
                j += 1
            lines.insert(i + 1, new)
            return "\n".join(lines)
    raise LayoutError(f"no [[{kind}]] with key {key!r} to write the id into")


# ---------------------------------------------------------------- the API

def default_token_path():
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Daedalus", "discord-token.dpapi")


def _dpapi_unprotect(blob):
    import ctypes
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    buf = ctypes.create_string_buffer(blob, len(blob))
    inb = Blob(len(blob), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))
    out = Blob()
    crypt32, kernel32 = ctypes.windll.crypt32, ctypes.windll.kernel32
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    if not crypt32.CryptUnprotectData(ctypes.byref(inb), None, None, None, None, 0, ctypes.byref(out)):
        raise OSError("the token file could not be decrypted (a different Windows user or PC?)")
    try:
        return ctypes.string_at(out.pbData, out.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(out.pbData, ctypes.c_void_p))


def read_token(path=None):
    path = path or default_token_path()
    if not os.path.exists(path):
        raise OSError(f"no token file at {path}: run tools\\discord-setpass.ps1 first")
    with open(path, "r", encoding="ascii") as f:
        blob = bytes.fromhex(f.read().strip())
    data = _dpapi_unprotect(blob)
    for enc in ("utf-16-le", "utf-8"):
        try:
            t = data.decode(enc).strip()
        except UnicodeDecodeError:
            continue
        if t and t.isascii() and t.isprintable():
            return t
    raise OSError("the token file decrypted to something that is not a token")


def _urllib_transport(method, url, headers, data):
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


class Api:
    """Minimal Discord REST client. The token only ever goes into the Authorization header."""

    def __init__(self, token, transport=None, sleep=time.sleep):
        self._token = token
        self._transport = transport or _urllib_transport
        self._sleep = sleep

    def request(self, method, path, body=None):
        if method == "DELETE":
            raise DiscordError(0, method, path, "this tool never deletes")
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Authorization": "Bot " + self._token, "User-Agent": USER_AGENT,
                   "Content-Type": "application/json"}
        for attempt in range(6):
            status, hdrs, raw = self._transport(method, API_BASE + path, headers, data)
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else None
            except ValueError:
                payload = None
            if status == 429 and attempt < 5:
                wait = (payload or {}).get("retry_after") or {k.lower(): v for k, v in hdrs.items()}.get(
                    "retry-after") or 1
                self._sleep(float(wait) + 0.1)
                continue
            if status >= 400:
                msg = (payload or {}).get("message") if isinstance(payload, dict) else None
                code = (payload or {}).get("code") if isinstance(payload, dict) else None
                raise DiscordError(status, method, path, f"{msg or 'error'} (code {code})")
            return payload
        raise DiscordError(429, method, path, "still rate limited after retries")


# ---------------------------------------------------------------- the live server

def _slug(name, fallback):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or fallback


def _norm_role(r):
    return {"id": r["id"], "name": r["name"], "color": r.get("color", 0), "hoist": bool(r.get("hoist")),
            "mentionable": bool(r.get("mentionable")), "permissions": int(r["permissions"]),
            "position": r.get("position", 0), "managed": bool(r.get("managed"))}


def _norm_channel(c):
    return {"id": c["id"], "type": c["type"], "name": c["name"], "position": c.get("position", 0),
            "parent_id": c.get("parent_id"), "topic": c.get("topic") or "", "nsfw": bool(c.get("nsfw")),
            "slowmode": c.get("rate_limit_per_user") or 0, "user_limit": c.get("user_limit") or 0,
            "ows": [{"id": o["id"], "type": o["type"], "allow": int(o["allow"]), "deny": int(o["deny"])}
                    for o in c.get("permission_overwrites") or []]}


class Live:
    def __init__(self, guild_id, roles, channels, bot_id, bot_role_ids):
        self.guild_id, self.roles, self.channels = guild_id, roles, channels
        self.bot_id, self.bot_role_ids = bot_id, bot_role_ids

    @classmethod
    def fetch(cls, api, guild_id):
        bot = api.request("GET", "/users/@me")["id"]
        member = api.request("GET", f"/guilds/{guild_id}/members/{bot}")
        roles = {r["id"]: _norm_role(r) for r in api.request("GET", f"/guilds/{guild_id}/roles")}
        chans = {c["id"]: _norm_channel(c) for c in api.request("GET", f"/guilds/{guild_id}/channels")}
        return cls(guild_id, roles, chans, bot, list(member.get("roles", [])))

    def base_perms(self):
        p = self.roles[self.guild_id]["permissions"]
        for r in self.bot_role_ids:
            p |= self.roles[r]["permissions"]
        return ALL_BITS if p & ADMIN else p

    def bot_top(self):
        return max([self.roles[r]["position"] for r in self.bot_role_ids if r in self.roles] + [0])

    def effective(self, ch):
        """The bot's permissions in a channel: the standard base + overwrites order."""
        base = self.base_perms()
        if base == ALL_BITS:
            return ALL_BITS
        ows = {(o["type"], o["id"]): o for o in ch["ows"]}
        p = base
        o = ows.get((0, self.guild_id))
        if o:
            p = (p & ~o["deny"]) | o["allow"]
        a = d = 0
        for r in self.bot_role_ids:
            o = ows.get((0, r))
            if o:
                a |= o["allow"]
                d |= o["deny"]
        p = (p & ~d) | a
        o = ows.get((1, self.bot_id))
        if o:
            p = (p & ~o["deny"]) | o["allow"]
        return p

    def fingerprint(self):
        data = {"bot": self.bot_id, "bot_roles": sorted(self.bot_role_ids),
                "roles": [self.roles[k] for k in sorted(self.roles)],
                "channels": [dict(self.channels[k], ows=sorted(self.channels[k]["ows"], key=lambda o: (o["type"], o["id"])))
                             for k in sorted(self.channels)]}
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def sibling_order(live, parent_id):
    return sorted((c for c in live.channels.values() if c["parent_id"] == parent_id),
                  key=lambda c: (c["position"], int(c["id"])))


def refill(current, managed):
    """`current` with the managed entries' slots refilled in the managed order; everything else stays put."""
    managed = [m for m in managed if m in current]
    ms, it = set(managed), iter(managed)
    return [next(it) if x in ms else x for x in current]


# ---------------------------------------------------------------- import / check-template / names

def import_layout(live, guild_name=""):
    warnings = []
    roles = sorted(live.roles.values(), key=lambda r: -r["position"])
    keys, used = {}, set()

    def unique(base):
        k, n = base, 2
        while k in used:
            k, n = f"{base}-{n}", n + 1
        used.add(k)
        return k

    role_out = []
    used.add("everyone")
    for r in roles:
        if r["id"] == live.guild_id:
            continue
        keys[r["id"]] = unique(_slug(r["name"], "role-" + r["id"][-4:]))
        role_out.append({"key": keys[r["id"]], "id": r["id"], "name": r["name"], "color": r["color"],
                         "hoist": r["hoist"], "mentionable": r["mentionable"], "managed": r["managed"],
                         "permissions": r["permissions"]})
    ev = live.roles[live.guild_id]
    keys[live.guild_id] = "everyone"
    role_out.append({"key": "everyone", "id": ev["id"], "name": ev["name"], "color": 0, "hoist": False,
                     "mentionable": False, "managed": False, "permissions": ev["permissions"]})
    order_of_roles = [r["key"] for r in role_out]
    members_ows = 0
    ckeys, used = {}, set()
    chan_out = []

    def add(c, parent_key):
        nonlocal members_ows
        if c["type"] not in CH_TYPE_NAMES:
            warnings.append(f"skipped #{c['name']}: channel type {c['type']} is not supported")
            return None
        key = unique(_slug(c["name"], "channel-" + c["id"][-4:]))
        ckeys[c["id"]] = key
        ows = []
        for o in c["ows"]:
            if o["type"] != 0:
                members_ows += 1
                continue
            if o["id"] not in keys:
                warnings.append(f"skipped an overwrite on #{c['name']} for an unknown role id")
                continue
            if o["allow"] or o["deny"]:
                ows.append({"role": keys[o["id"]], "allow": o["allow"], "deny": o["deny"]})
        ows.sort(key=lambda o: order_of_roles.index(o["role"]))
        chan_out.append({"key": key, "id": c["id"], "type": CH_TYPE_NAMES[c["type"]], "name": c["name"],
                         "parent": parent_key,
                         "topic": c["topic"] if c["type"] in TOPIC_TYPES else "", "nsfw": c["nsfw"],
                         "slowmode": c["slowmode"], "user_limit": c["user_limit"] if c["type"] in LIMIT_TYPES else 0,
                         "overwrites": ows})
        return key

    for c in sibling_order(live, None):
        k = add(c, "")
        if k and c["type"] == 4:
            for ch in sibling_order(live, c["id"]):
                add(ch, k)
    for c in live.channels.values():
        if c["parent_id"] and c["parent_id"] not in live.channels:
            warnings.append(f"skipped #{c['name']}: its category is missing")
    return {"guild_id": live.guild_id, "guild_name": guild_name, "roles": role_out, "channels": chan_out}, \
        warnings, members_ows


def check_template(layout, tpl):
    g = tpl["serialized_source_guild"]
    diffs = []
    t_roles = [r["name"] for r in sorted((r for r in g["roles"] if r["id"] != 0), key=lambda r: -r["id"])]
    l_roles = [r["name"] for r in layout["roles"] if r["key"] != "everyone" and not r["managed"]]
    diffs += _compare_lists("role", t_roles, l_roles)
    tc = {c["id"]: c for c in g["channels"]}

    def tkids(pid):
        return sorted((c for c in g["channels"] if c.get("parent_id") == pid), key=lambda c: c["position"])

    t_top = [(c["name"], CH_TYPE_NAMES.get(c["type"], str(c["type"]))) for c in tkids(None)]
    l_top = [(c["name"], c["type"]) for c in layout["channels"] if not c["parent"]]
    diffs += _compare_lists("top-level channel/category", t_top, l_top)
    cats_l = {c["name"]: c for c in layout["channels"] if c["type"] == "category"}
    byk = {c["key"]: c for c in layout["channels"]}
    for cat in (tc[i] for i in tc if tc[i]["type"] == 4):
        kids_t = [(c["name"], CH_TYPE_NAMES.get(c["type"], str(c["type"]))) for c in tkids(cat["id"])]
        lc = cats_l.get(cat["name"])
        if not lc:
            continue
        kids_l = [(c["name"], c["type"]) for c in layout["channels"] if c["parent"] and byk[c["parent"]] is lc]
        diffs += _compare_lists(f"channel in category {cat['name']!r}", kids_t, kids_l)
    return diffs


def _compare_lists(what, tpl, lay):
    from collections import Counter
    out = []
    ct, cl = Counter(tpl), Counter(lay)
    for x in (ct - cl):
        out.append(f"missing in the layout: {what} {x!r}")
    for x in (cl - ct):
        out.append(f"extra in the layout: {what} {x!r}")
    common_t = [x for x in tpl if x in cl and x in ct]
    common_l = [x for x in lay if x in cl and x in ct]
    if common_t != common_l:
        out.append(f"order differs for {what}s: template {common_t!r} vs layout {common_l!r}")
    return out


# ---------------------------------------------------------------- plan

def _bits_txt(add, remove):
    parts = []
    if add:
        parts.append("add " + ", ".join(perm_names(add)))
    if remove:
        parts.append("remove " + ", ".join(perm_names(remove)))
    return "; ".join(parts)


def make_plan(layout, live, now=None):
    g = live.guild_id
    if layout["guild_id"] != g:
        raise LayoutError("the layout is for another server than the one the plan reads")
    roles_L, chans_L = layout["roles"], layout["channels"]
    rid = {r["key"]: r["id"] or None for r in roles_L}
    cid = {c["key"]: c["id"] or None for c in chans_L}
    for r in roles_L:
        if r["id"] and r["id"] not in live.roles:
            raise LayoutError(f"role {r['key']!r}: id {r['id']} is not on the server; clear its id to create it anew")
    for c in chans_L:
        if c["id"] and c["id"] not in live.channels:
            raise LayoutError(f"channel {c['key']!r}: id {c['id']} is not on the server; clear its id to create it anew")
    if len({i for i in list(rid.values()) if i}) != len([i for i in rid.values() if i]) or \
            len({i for i in cid.values() if i}) != len([i for i in cid.values() if i]):
        raise LayoutError("two entries share one id")
    base = live.base_perms()
    bot_top = live.bot_top()
    mask_g = base & BOT_PERMS
    can_roles = bool(base & MANAGE_ROLES)
    can_chan_g = bool(base & MANAGE_CHANNELS)
    actions, yours, extras = [], [], []

    # ---- roles
    for r in roles_L:
        if r["id"]:
            lr = live.roles[r["id"]]
            label = f'role "{lr["name"]}"'
            everyone = r["id"] == g
            reason = None
            if not everyone and lr["managed"]:
                reason = "made by an integration"
            elif not everyone and lr["position"] >= bot_top:
                reason = "at or above the bot's role"
            elif not can_roles:
                reason = "the bot lacks Manage Roles"
            ch = {}
            if not everyone:
                for f in ("name", "color", "hoist", "mentionable"):
                    if lr[f] != r[f]:
                        ch[f] = r[f]
            lp, wp = lr["permissions"], r["permissions"]
            if reason:
                if ch or lp != wp:
                    yours.append(f"{label}: {reason}; left as it is (" + ", ".join(
                        sorted(ch) + (["permissions"] if lp != wp else [])) + " differ)")
                continue
            target = (lp & ~mask_g) | (wp & mask_g)
            if target != lp:
                ch["permissions"] = target
            ybits = (wp ^ lp) & ~mask_g
            if ybits:
                yours.append(f"{label}: permissions the bot can't set: "
                             + _bits_txt(wp & ybits, lp & ybits))
            if ch:
                actions.append({"kind": "role.edit", "key": r["key"], "id": r["id"], "changes": {
                    k: (str(v) if k == "permissions" else v) for k, v in ch.items()},
                    "summary": f'edit {label}: ' + ", ".join(
                        (f"name -> {r['name']!r}" if k == "name" else
                         f"permissions ({_bits_txt(target & ~lp, lp & ~target)})" if k == "permissions" else
                         f"{k} -> {v}") for k, v in ch.items())})
        else:
            if not can_roles:
                yours.append(f'role "{r["name"]}" to create: the bot lacks Manage Roles')
                continue
            wp = r["permissions"]
            if wp & ~mask_g:
                yours.append(f'new role "{r["name"]}": permissions the bot can\'t set (left off): '
                             + ", ".join(perm_names(wp & ~mask_g)))
            actions.append({"kind": "role.create", "key": r["key"], "name": r["name"], "color": r["color"],
                            "hoist": r["hoist"], "mentionable": r["mentionable"],
                            "permissions": str(wp & mask_g), "summary": f'create role "{r["name"]}"'})
    # role order
    if can_roles:
        elig = sorted((x for x in live.roles.values() if x["id"] != g and x["position"] < bot_top),
                      key=lambda x: -x["position"])
        by_id = {r["id"]: r["key"] for r in roles_L if r["id"]}
        creates = [r["key"] for r in roles_L if not r["id"]]
        current = [x["id"] for x in elig] + ["new:" + k for k in creates]
        elig_ids = {x["id"] for x in elig}
        managed_tok = [(r["id"] if r["id"] else "new:" + r["key"]) for r in roles_L
                       if r["key"] != "everyone" and (not r["id"] or r["id"] in elig_ids)]
        if refill(current, managed_tok) != current:
            actions.append({"kind": "role.reorder", "order": [by_id.get(t, t[4:]) for t in managed_tok],
                            "summary": "reorder roles: " + ", ".join(
                                live.roles[t]["name"] if t in live.roles else t[4:] for t in managed_tok
                                if t in current)})
    # ---- channels
    cat_ids = {c["key"]: c["id"] or None for c in chans_L if c["type"] == "category"}
    for c in chans_L:
        pkey = c["parent"] or None
        want_parent = cat_ids[pkey] if pkey else None
        if not c["id"]:
            ok = True
            if pkey and want_parent:
                ok = bool(live.effective(live.channels[want_parent]) & MANAGE_CHANNELS)
            elif not pkey:
                ok = can_chan_g
            if not ok:
                yours.append(f'channel "{c["name"]}" to create: the bot lacks Manage Channels there')
                continue
            m = (live.effective(live.channels[want_parent]) & BOT_PERMS) if want_parent else mask_g
            ows = []
            for o in c["overwrites"]:
                if (o["allow"] | o["deny"]) & ~m:
                    yours.append(f'new channel "{c["name"]}": overwrite bits the bot can\'t set (left off): '
                                 + ", ".join(perm_names((o["allow"] | o["deny"]) & ~m)))
                a, d = o["allow"] & m, o["deny"] & m
                if a or d:
                    ows.append({"role": o["role"], "allow": str(a), "deny": str(d)})
            actions.append({"kind": "channel.create", "key": c["key"], "type": CH_TYPES[c["type"]], "name": c["name"],
                            "parent": pkey, "topic": c["topic"], "nsfw": c["nsfw"], "slowmode": c["slowmode"],
                            "user_limit": c["user_limit"], "overwrites": ows,
                            "summary": f'create {c["type"]} "{c["name"]}"'
                                       + (f' in "{_cname(chans_L, pkey)}"' if pkey else "")
                                       + (f" with {len(ows)} overwrite(s)" if ows else "")})
            continue
        lc = live.channels[c["id"]]
        label = f'#{lc["name"]}'
        if CH_TYPES[c["type"]] != lc["type"]:
            yours.append(f"{label}: the layout says type {c['type']} but a channel's type can't be changed")
            continue
        eff = live.effective(lc)
        can_edit = bool(eff & MANAGE_CHANNELS) and bool(eff & VIEW)
        ch = {}
        if lc["name"] != c["name"]:
            ch["name"] = c["name"]
        if lc["type"] in TOPIC_TYPES and lc["topic"] != c["topic"]:
            ch["topic"] = c["topic"]
        if lc["type"] != 4 and lc["nsfw"] != c["nsfw"]:
            ch["nsfw"] = c["nsfw"]
        if lc["type"] != 4 and lc["slowmode"] != c["slowmode"]:
            ch["rate_limit_per_user"] = c["slowmode"]
        if lc["type"] in LIMIT_TYPES and lc["user_limit"] != c["user_limit"]:
            ch["user_limit"] = c["user_limit"]
        moved = (lc["parent_id"] or None) != (want_parent if (want_parent or not pkey) else "new:" + pkey)
        ow_acts, ow_yours = _overwrite_diffs(c, lc, layout, live, eff, rid)
        if not can_edit and (ch or moved or ow_acts or ow_yours):
            yours.append(f"{label}: the bot can't see or manage this channel; left as it is")
            continue
        if ch:
            actions.append({"kind": "channel.edit", "key": c["key"], "id": c["id"], "changes": ch,
                            "summary": f"edit {label}: " + ", ".join(
                                f"name -> {v!r}" if k == "name" else k for k, v in ch.items())})
        if moved:
            ok = True
            if want_parent:
                ok = bool(live.effective(live.channels[want_parent]) & MANAGE_CHANNELS)
            if ok:
                actions.append({"kind": "channel.move", "key": c["key"], "id": c["id"], "parent": pkey,
                                "summary": f'move {label} to "{_cname(chans_L, pkey) if pkey else "(top level)"}"'})
            else:
                yours.append(f"{label}: the bot can't manage the category it should move to")
        if ow_acts and not (eff & MANAGE_ROLES):
            yours.append(f"{label}: the bot lacks Manage Roles there; its overwrite changes are yours")
        else:
            actions += ow_acts
        yours += ow_yours
    # channel order
    if can_chan_g:
        tops = [None] + [k for k in (c["key"] for c in chans_L if c["type"] == "category")]
        for pk in tops:
            pid = cat_ids[pk] if pk else None
            kids = [c for c in chans_L if (c["parent"] or None) == pk]
            leaving = {c["id"] for c in chans_L if c["id"] and (c["parent"] or None) != pk}
            current = [x["id"] for x in sibling_order(live, pid) if x["id"] not in leaving] if pid or pk is None else []
            toks = [(c["id"] if c["id"] else "new:" + c["key"]) for c in kids]
            arrivals = [t for t in toks if t not in current]
            current = current + arrivals
            if not current:
                continue
            if arrivals or refill(current, toks) != current:
                actions.append({"kind": "channel.reorder", "parent": pk,
                                "order": [c["key"] for c in kids],
                                "summary": "reorder " + (f'"{_cname(chans_L, pk)}"' if pk else "the top level")
                                           + ": " + ", ".join(c["name"] for c in kids)})
    # ---- extras and unmanaged
    laid_roles = {r["id"] for r in roles_L if r["id"]}
    laid_chans = {c["id"] for c in chans_L if c["id"]}
    for r in sorted(live.roles.values(), key=lambda x: -x["position"]):
        if r["id"] not in laid_roles:
            extras.append(f'role "{r["name"]}" (not in the layout; left alone)')
    for c in sorted(live.channels.values(), key=lambda x: (x["parent_id"] or "", x["position"])):
        if c["id"] not in laid_chans:
            extras.append(f'{CH_TYPE_NAMES.get(c["type"], c["type"])} "{c["name"]}" (not in the layout; left alone)')
    mem = sum(1 for c in live.channels.values() for o in c["ows"] if o["type"] == 1)
    memc = sum(1 for c in live.channels.values() if any(o["type"] == 1 for o in c["ows"]))
    order = {"role.create": 0, "role.edit": 1, "role.reorder": 2, "channel.create": 3, "channel.edit": 4,
             "channel.move": 5, "channel.overwrite": 6, "channel.reorder": 7}
    # categories are created before their children
    actions.sort(key=lambda a: (order[a["kind"]], 0 if a.get("type") == 4 else 1))
    return {"version": 1, "created": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "guild_id": g, "fingerprint": live.fingerprint(), "actions": actions, "yours": yours, "extras": extras,
            "member_overwrites": mem, "member_overwrite_channels": memc}


def _cname(chans_L, key):
    return next((c["name"] for c in chans_L if c["key"] == key), key)


def _overwrite_diffs(c, lc, layout, live, eff, rid):
    mask = eff & BOT_PERMS
    want = {o["role"]: (o["allow"], o["deny"]) for o in c["overwrites"]}
    liv = {o["id"]: (o["allow"], o["deny"]) for o in lc["ows"] if o["type"] == 0}
    acts, yours = [], []
    for r in layout["roles"]:
        w = want.get(r["key"], (0, 0))
        l = liv.get(r["id"], (0, 0)) if r["id"] else (0, 0)
        if w == l:
            continue
        ta, td = (l[0] & ~mask) | (w[0] & mask), (l[1] & ~mask) | (w[1] & mask)
        y = ((w[0] ^ l[0]) | (w[1] ^ l[1])) & ~mask
        if y:
            yours.append(f'#{lc["name"]} overwrite for role "{r["name"]}": bits the bot can\'t set: '
                         + ", ".join(perm_names(y)))
        if (ta, td) != l:
            acts.append({"kind": "channel.overwrite", "key": c["key"], "id": c["id"], "role": r["key"],
                         "allow": str(ta), "deny": str(td),
                         "summary": f'#{lc["name"]}: overwrite for "{r["name"]}" '
                                    f'allow [{", ".join(perm_names(ta)) or "-"}] deny [{", ".join(perm_names(td)) or "-"}]'})
    return acts, yours


MARK = "<!-- apply reads the JSON block below; do not edit it -->"


def render_plan(plan):
    L = [f"# Discord plan {plan['created']}", "",
         f"Server {plan['guild_id']}. {len(plan['actions'])} change(s), {len(plan['yours'])} for you, "
         f"{len(plan['extras'])} extra(s) left alone.", "", "## Changes apply will make", ""]
    L += [f"{i}. {a['summary']}" for i, a in enumerate(plan["actions"], 1)] or ["(none: the server matches the layout)"]
    L += ["", "## Yours (apply skips these; do them by hand or leave them)", ""]
    L += [f"- {y}" for y in plan["yours"]] or ["(none)"]
    L += ["", "## Extras (on the server, not in the layout; never deleted)", ""]
    L += [f"- {e}" for e in plan["extras"]] or ["(none)"]
    L += ["", "## Unmanaged", "",
          f"{plan['member_overwrites']} member overwrite(s) on {plan['member_overwrite_channels']} channel(s): "
          "not in the layout, not touched.", "", "## Machine part", "", MARK, "```json",
          json.dumps(plan, indent=1, sort_keys=True), "```", ""]
    return "\n".join(L)


def parse_plan(text):
    i = text.find(MARK)
    if i < 0:
        raise LayoutError("not a plan file (no machine part)")
    m = re.search(r"```json\n(.*?)\n```", text[i:], re.S)
    if not m:
        raise LayoutError("the plan's JSON block is missing")
    plan = json.loads(m.group(1))
    if plan.get("version") != 1:
        raise LayoutError("unknown plan version")
    return plan


# ---------------------------------------------------------------- apply

def apply_plan(api, plan, layout_path, log=print):
    """Re-reads the server, refuses a stale plan, then makes the plan's actions one at a time, stopping at the first
    error. Returns 0 (done), 1 (stopped on an error), 2 (refused as stale)."""
    g = plan["guild_id"]
    live = Live.fetch(api, g)
    if live.fingerprint() != plan["fingerprint"]:
        log("REFUSED: the server changed since this plan was made. Run plan again.")
        return 2
    if not plan["actions"]:
        log("Nothing to do.")
        return 0
    with open(layout_path, "r", encoding="utf-8") as f:
        text = f.read()
    layout = load_layout(text)
    rmap = {r["key"]: r["id"] or None for r in layout["roles"]}
    cmap = {c["key"]: c["id"] or None for c in layout["channels"]}
    done = []

    def fail(msg):
        log(f"STOPPED: {msg}")
        log(f"Done before the stop ({len(done)}):")
        for d in done:
            log("  - " + d)
        log("Run plan again before anything else.")
        return 1

    def write_id(kind, key, new_id):
        nonlocal text
        text = set_id_in_text(text, kind, key, new_id)
        with open(layout_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    for a in plan["actions"]:
        try:
            k = a["kind"]
            if k == "role.create":
                r = api.request("POST", f"/guilds/{g}/roles", {
                    "name": a["name"], "color": a["color"], "hoist": a["hoist"], "mentionable": a["mentionable"],
                    "permissions": a["permissions"]})
                rmap[a["key"]] = r["id"]
                write_id("role", a["key"], r["id"])
            elif k == "role.edit":
                api.request("PATCH", f"/guilds/{g}/roles/{a['id']}", a["changes"])
            elif k == "role.reorder":
                _apply_role_order(api, g, a, rmap)
            elif k == "channel.create":
                body = {"name": a["name"], "type": a["type"], "nsfw": a["nsfw"],
                        "permission_overwrites": [{"id": _need_id(rmap, o["role"]), "type": 0, "allow": o["allow"],
                                                   "deny": o["deny"]} for o in a["overwrites"]]}
                if a["type"] in TOPIC_TYPES and a["topic"]:
                    body["topic"] = a["topic"]
                if a["type"] != 4 and a["slowmode"]:
                    body["rate_limit_per_user"] = a["slowmode"]
                if a["type"] in LIMIT_TYPES and a["user_limit"]:
                    body["user_limit"] = a["user_limit"]
                if a["parent"]:
                    body["parent_id"] = _need_id(cmap, a["parent"])
                c = api.request("POST", f"/guilds/{g}/channels", body)
                cmap[a["key"]] = c["id"]
                write_id("channel", a["key"], c["id"])
            elif k == "channel.edit":
                api.request("PATCH", f"/channels/{a['id']}", a["changes"])
            elif k == "channel.move":
                api.request("PATCH", f"/channels/{a['id']}", {"parent_id": _need_id(cmap, a["parent"]) if a["parent"] else None})
            elif k == "channel.overwrite":
                cid = a["id"] or _need_id(cmap, a["key"])
                api.request("PUT", f"/channels/{cid}/permissions/{_need_id(rmap, a['role'])}",
                            {"type": 0, "allow": a["allow"], "deny": a["deny"]})
            elif k == "channel.reorder":
                _apply_channel_order(api, g, a, cmap)
            else:
                return fail(f"unknown action kind {k!r}")
        except (DiscordError, LayoutError, KeyError, OSError) as e:
            return fail(f"{a.get('summary', a.get('kind'))}: {e}")
        done.append(a["summary"])
        log("ok: " + a["summary"])
    log(f"Done: {len(done)} change(s). Run plan again: it should show none.")
    return 0


def _need_id(m, key):
    if not m.get(key):
        raise LayoutError(f"no id known for key {key!r}")
    return m[key]


def _apply_role_order(api, g, a, rmap):
    live = Live.fetch(api, g)
    top = live.bot_top()
    elig = sorted((x for x in live.roles.values() if x["id"] != g and x["position"] < top), key=lambda x: -x["position"])
    current = [x["id"] for x in elig]
    managed = [rmap[k] for k in a["order"] if rmap.get(k)]
    new = refill(current, managed)
    slots = [x["position"] for x in elig]
    body = [{"id": rid, "position": pos} for rid, pos in zip(new, slots) if live.roles[rid]["position"] != pos]
    if body:
        api.request("PATCH", f"/guilds/{g}/roles", body)


def _apply_channel_order(api, g, a, cmap):
    live = Live.fetch(api, g)
    pid = cmap[a["parent"]] if a["parent"] else None
    current = [x["id"] for x in sibling_order(live, pid)]
    managed = [cmap[k] for k in a["order"] if cmap.get(k)]
    new = refill(current, managed)
    body = [{"id": cid, "position": i} for i, cid in enumerate(new) if live.channels[cid]["position"] != i]
    if body:
        api.request("PATCH", f"/guilds/{g}/channels", body)


# ---------------------------------------------------------------- command line

def _api():
    return Api(read_token())


def cmd_import(a):
    if os.path.exists(a.layout) and not a.force:
        print(f"{a.layout} exists: pass --force to overwrite it", file=sys.stderr)
        return 1
    api = _api()
    live = Live.fetch(api, a.guild)
    name = (api.request("GET", f"/guilds/{a.guild}") or {}).get("name", "")
    layout, warnings, members = import_layout(live, name)
    os.makedirs(os.path.dirname(os.path.abspath(a.layout)), exist_ok=True)
    with open(a.layout, "w", encoding="utf-8", newline="\n") as f:
        f.write(dump_layout(layout))
    print(f"wrote {a.layout}: {len(layout['roles'])} role(s), {len(layout['channels'])} channel(s)/categories; "
          f"{members} member overwrite(s) left out")
    for w in warnings:
        print("warning: " + w)
    return 0


def cmd_check_template(a):
    with open(a.layout, encoding="utf-8") as f:
        layout = load_layout(f.read())
    with open(a.template, encoding="utf-8") as f:
        tpl = json.load(f)
    diffs = check_template(layout, tpl)
    for d in diffs:
        print(d)
    print("MATCH: the layout equals the template by name and position" if not diffs
          else f"{len(diffs)} difference(s) listed above")
    return 0 if not diffs else 1


def cmd_names(a):
    with open(a.layout, encoding="utf-8") as f:
        layout = load_layout(f.read())
    print("ROLES")
    for r in layout["roles"]:
        print("  " + r["name"])
    print("CHANNELS AND CATEGORIES")
    for c in layout["channels"]:
        print(("  " if not c["parent"] else "      ") + c["name"] + (f"   [{c['topic']}]" if c["topic"] else ""))
    return 0


def cmd_plan(a):
    with open(a.layout, encoding="utf-8") as f:
        layout = load_layout(f.read())
    live = Live.fetch(_api(), layout["guild_id"])
    plan = make_plan(layout, live)
    os.makedirs(a.out_dir, exist_ok=True)
    path = os.path.join(a.out_dir, "plan-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".md")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_plan(plan))
    print(f"wrote {path}: {len(plan['actions'])} change(s), {len(plan['yours'])} yours, {len(plan['extras'])} extra(s)")
    return 0


def cmd_apply(a):
    with open(a.plan, encoding="utf-8") as f:
        plan = parse_plan(f.read())
    return apply_plan(_api(), plan, a.layout)


def cmd_invite(a):
    print(f"https://discord.com/oauth2/authorize?client_id={a.app_id}&scope=bot&permissions={BOT_PERMS}")
    return 0


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("import")
    s.add_argument("--guild", required=True)
    s.add_argument("--layout", default=DEFAULT_LAYOUT)
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_import)
    s = sub.add_parser("check-template")
    s.add_argument("template")
    s.add_argument("--layout", default=DEFAULT_LAYOUT)
    s.set_defaults(fn=cmd_check_template)
    s = sub.add_parser("names")
    s.add_argument("--layout", default=DEFAULT_LAYOUT)
    s.set_defaults(fn=cmd_names)
    s = sub.add_parser("plan")
    s.add_argument("--layout", default=DEFAULT_LAYOUT)
    s.add_argument("--out-dir", default=PLAN_DIR)
    s.set_defaults(fn=cmd_plan)
    s = sub.add_parser("apply")
    s.add_argument("plan")
    s.add_argument("--layout", default=DEFAULT_LAYOUT)
    s.set_defaults(fn=cmd_apply)
    s = sub.add_parser("invite")
    s.add_argument("--app-id", required=True)
    s.set_defaults(fn=cmd_invite)
    a = p.parse_args(argv)
    try:
        return a.fn(a)
    except (LayoutError, DiscordError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
