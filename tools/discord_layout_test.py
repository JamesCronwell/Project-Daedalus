"""Tests for tools/discord_layout.py against an in-memory fake of the Discord API. No network, no token.
Run: python -I tools/discord_layout_test.py   (exit 0 = all pass)
"""
import copy
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discord_layout as dl  # noqa: E402

B = dl.BIT_BY_NAME
G = "1000"
BOT = "9000"
EVERYONE = B["VIEW_CHANNEL"] | B["SEND_MESSAGES"] | B["READ_MESSAGE_HISTORY"]


class FakeDiscord:
    """Just enough of the REST API, with Discord's rules the tool relies on: a bot can only add permission bits it
    holds, can only edit roles below its own, and a PATCH of permission_overwrites would delete the ones it omits."""

    def __init__(self):
        self.calls = []
        self.next_id = 5000
        self.roles = {
            G: self.role(G, "@everyone", 0, EVERYONE),
            "2001": self.role("2001", "Admin", 5, B["ADMINISTRATOR"]),
            "2002": self.role("2002", "Layout Bot", 4, dl.BOT_PERMS, managed=True),
            "2003": self.role("2003", "Members", 2, B["VIEW_CHANNEL"], color=255),
            "2004": self.role("2004", "Feed", 1, 0),
        }
        self.bot_roles = ["2002"]
        self.channels = {}
        self.add_ch("3001", 4, "MESS HALL", None, 0)
        self.add_ch("3002", 4, "COMMS", None, 1)
        self.add_ch("4001", 0, "general", "3001", 0, topic="hello",
                    ows=[self.ow(G, 0, 0, 0), self.ow("777", 1, B["VIEW_CHANNEL"], 0)])  # 777: a member overwrite
        self.add_ch("4002", 2, "lobby", "3001", 1, user_limit=5)
        self.add_ch("4003", 0, "news-feed", "3002", 0, ows=[self.ow("2003", 0, B["VIEW_CHANNEL"], 0)])

    @staticmethod
    def role(i, name, pos, perms, managed=False, color=0):
        return {"id": i, "name": name, "position": pos, "permissions": str(perms), "managed": managed,
                "color": color, "hoist": False, "mentionable": False}

    @staticmethod
    def ow(i, typ, allow, deny):
        return {"id": i, "type": typ, "allow": str(allow), "deny": str(deny)}

    def add_ch(self, i, typ, name, parent, pos, topic=None, ows=None, user_limit=0):
        self.channels[i] = {"id": i, "type": typ, "name": name, "parent_id": parent, "position": pos, "topic": topic,
                            "nsfw": False, "rate_limit_per_user": 0, "user_limit": user_limit,
                            "permission_overwrites": ows or []}

    def bot_base(self):
        p = int(self.roles[G]["permissions"])
        for r in self.bot_roles:
            p |= int(self.roles[r]["permissions"])
        return p

    def bot_top(self):
        return max(self.roles[r]["position"] for r in self.bot_roles)

    def forbid(self, bits):
        if bits & ~self.bot_base() and not self.bot_base() & dl.ADMIN:
            raise dl.DiscordError(403, "x", "x", "Missing Permissions")

    def request(self, method, path, body=None):
        self.calls.append((method, path, copy.deepcopy(body)))
        parts = path.strip("/").split("/")
        if method == "DELETE":
            raise AssertionError("the tool deleted something: " + path)
        if method == "GET" and path == "/users/@me":
            return {"id": BOT}
        if method == "GET" and parts[:2] == ["guilds", G] and parts[2] == "members":
            return {"roles": list(self.bot_roles)}
        if method == "GET" and path == f"/guilds/{G}":
            return {"name": "Test Server"}
        if method == "GET" and path == f"/guilds/{G}/roles":
            return copy.deepcopy(list(self.roles.values()))
        if method == "GET" and path == f"/guilds/{G}/channels":
            return copy.deepcopy(list(self.channels.values()))
        if method == "POST" and path == f"/guilds/{G}/roles":
            self.forbid(int(body["permissions"]))
            i = self.new_id()
            for r in self.roles.values():
                if r["id"] != G and r["position"] >= 1:
                    r["position"] += 1
            self.roles[i] = self.role(i, body["name"], 1, int(body["permissions"]), color=body["color"])
            self.roles[i].update(hoist=body["hoist"], mentionable=body["mentionable"])
            return {"id": i}
        if method == "PATCH" and path == f"/guilds/{G}/roles":
            for e in body:
                if self.roles[e["id"]]["position"] >= self.bot_top():
                    raise dl.DiscordError(403, method, path, "role above the bot")
            for e in body:
                self.roles[e["id"]]["position"] = e["position"]
            return None
        if method == "PATCH" and parts[:3] == ["guilds", G, "roles"]:
            r = self.roles[parts[3]]
            if r["managed"] or r["position"] >= self.bot_top():
                raise dl.DiscordError(403, method, path, "Missing Permissions")
            if "permissions" in body:
                self.forbid(int(body["permissions"]) & ~int(r["permissions"]))
            r.update({k: (str(v) if k == "permissions" else v) for k, v in body.items()})
            return None
        if method == "POST" and path == f"/guilds/{G}/channels":
            assert "permission_overwrites" in body
            for o in body["permission_overwrites"]:
                self.forbid(int(o["allow"]) | int(o["deny"]))
            i = self.new_id()
            sib = [c for c in self.channels.values() if c["parent_id"] == body.get("parent_id")]
            self.add_ch(i, body["type"], body["name"], body.get("parent_id"), len(sib), topic=body.get("topic"),
                        ows=body["permission_overwrites"], user_limit=body.get("user_limit", 0))
            return {"id": i}
        if method == "PATCH" and path == f"/guilds/{G}/channels":
            for e in body:
                self.channels[e["id"]]["position"] = e["position"]
            return None
        if method == "PATCH" and parts[0] == "channels":
            assert "permission_overwrites" not in body, "a whole-list PATCH would delete unlisted overwrites"
            c = self.channels[parts[1]]
            if "parent_id" in body and body["parent_id"] != c["parent_id"]:
                c["position"] = len([x for x in self.channels.values() if x["parent_id"] == body["parent_id"]])
            c.update(body)
            return None
        if method == "PUT" and parts[0] == "channels" and parts[2] == "permissions":
            c = self.channels[parts[1]]
            old = next((o for o in c["permission_overwrites"] if o["id"] == parts[3]), None)
            oa, od = (int(old["allow"]), int(old["deny"])) if old else (0, 0)
            self.forbid((int(body["allow"]) & ~oa) | (int(body["deny"]) & ~od))
            c["permission_overwrites"] = [o for o in c["permission_overwrites"] if o["id"] != parts[3]] + [
                {"id": parts[3], "type": body["type"], "allow": body["allow"], "deny": body["deny"]}]
            return None
        raise AssertionError(f"fake has no {method} {path}")

    def new_id(self):
        self.next_id += 1
        return str(self.next_id)

    def writes(self):
        return [c for c in self.calls if c[0] != "GET"]


def imported(fake):
    live = dl.Live.fetch(fake, G)
    layout, warnings, members = dl.import_layout(live, "Test Server")
    return layout, warnings, members


def edit(layout, kind, key):
    return next(x for x in layout[kind] if x["key"] == key)


def run_plan(fake, layout):
    return dl.make_plan(layout, dl.Live.fetch(fake, G))


class Case(unittest.TestCase):
    def setUp(self):
        self.fake = FakeDiscord()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "layout.toml")

    def save(self, layout):
        with open(self.path, "w", encoding="utf-8", newline="\n") as f:
            f.write(dl.dump_layout(layout))

    def apply(self, plan):
        out = []
        rc = dl.apply_plan(self.fake, plan, self.path, log=out.append)
        return rc, out


class TestDiff(Case):
    def test_import_then_plan_is_empty(self):
        layout, warnings, members = imported(self.fake)
        self.assertEqual(warnings, [])
        self.assertEqual(members, 1)
        plan = run_plan(self.fake, layout)
        self.assertEqual(plan["actions"], [])
        self.assertEqual(plan["yours"], [])
        self.assertEqual(plan["extras"], [])
        self.assertEqual(plan["member_overwrites"], 1)

    def test_import_keys_and_order(self):
        layout, _, _ = imported(self.fake)
        self.assertEqual([r["key"] for r in layout["roles"]], ["admin", "layout-bot", "members", "feed", "everyone"])
        self.assertEqual([c["key"] for c in layout["channels"]],
                         ["mess-hall", "general", "lobby", "comms", "news-feed"])
        self.assertEqual(edit(layout, "channels", "news-feed")["parent"], "comms")
        # the member overwrite on #general is not in the layout
        self.assertEqual(edit(layout, "channels", "general")["overwrites"], [])

    def test_the_full_loop(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "channels", "general")["name"] = "chat"                       # a rename
        edit(layout, "channels", "news-feed")["parent"] = "mess-hall"               # a move
        edit(layout, "channels", "news-feed")["overwrites"].append(                 # a read-only overwrite
            {"role": "everyone", "allow": 0, "deny": B["SEND_MESSAGES"]})
        layout["channels"].append({"key": "ops", "id": "", "type": "text", "name": "ops", "parent": "comms",
                                   "topic": "ops chat", "nsfw": False, "slowmode": 0, "user_limit": 0,
                                   "overwrites": []})                               # a new channel
        layout["roles"].insert(3, {"key": "pingers", "id": "", "name": "Pingers", "color": 1, "hoist": True,
                                   "mentionable": True, "managed": False,
                                   "permissions": B["MENTION_EVERYONE"]})           # a new role
        self.save(layout)
        general_id = edit(layout, "channels", "general")["id"]
        plan = run_plan(self.fake, layout)
        kinds = [a["kind"] for a in plan["actions"]]
        self.assertEqual(sorted(kinds), sorted(["role.create", "role.reorder", "channel.create", "channel.edit",
                                                "channel.move", "channel.overwrite", "channel.reorder",
                                                "channel.reorder"]))
        self.assertEqual(plan["yours"], [])
        rc, out = self.apply(plan)
        self.assertEqual(rc, 0, out)
        # the renamed channel kept its id; nothing was created for it
        self.assertEqual(self.fake.channels[general_id]["name"], "chat")
        self.assertEqual(sum(1 for c in self.fake.calls if c[0] == "POST" and c[1].endswith("/channels")), 1)
        # the member overwrite survived
        self.assertTrue(any(o["id"] == "777" for o in self.fake.channels[general_id]["permission_overwrites"]))
        # no whole-list PATCH, no DELETE (the fake asserts both); the new ids were written back
        text = open(self.path, encoding="utf-8").read()
        reloaded = dl.load_layout(text)
        self.assertTrue(edit(reloaded, "channels", "ops")["id"])
        self.assertTrue(edit(reloaded, "roles", "pingers")["id"])
        # the role landed between Members and Feed, as the file says
        order = [r["name"] for r in sorted(self.fake.roles.values(), key=lambda r: -r["position"])]
        self.assertEqual(order, ["Admin", "Layout Bot", "Members", "Pingers", "Feed", "@everyone"])
        # the move and the new channel are where the file puts them
        kids = [c["name"] for c in dl.sibling_order(dl.Live.fetch(self.fake, G), "3001")]
        self.assertEqual(kids, ["chat", "lobby", "news-feed"])
        # a second plan shows no changes
        plan2 = run_plan(self.fake, reloaded)
        self.assertEqual(plan2["actions"], [], [a["summary"] for a in plan2["actions"]])
        self.assertEqual(plan2["yours"], [])

    def test_reorder_only(self):
        layout, _, _ = imported(self.fake)
        ch = layout["channels"]
        i, j = [k for k, c in enumerate(ch) if c["key"] in ("general", "lobby")]
        ch[i], ch[j] = ch[j], ch[i]
        plan = run_plan(self.fake, layout)
        self.assertEqual([a["kind"] for a in plan["actions"]], ["channel.reorder"])
        self.save(layout)
        rc, _ = self.apply(plan)
        self.assertEqual(rc, 0)
        self.assertEqual([c["name"] for c in dl.sibling_order(dl.Live.fetch(self.fake, G), "3001")],
                         ["lobby", "general"])
        self.assertEqual(run_plan(self.fake, layout)["actions"], [])


class TestNeverDelete(Case):
    def test_extras_are_flagged_and_left(self):
        layout, _, _ = imported(self.fake)
        layout["channels"] = [c for c in layout["channels"] if c["key"] != "lobby"]
        layout["roles"] = [r for r in layout["roles"] if r["key"] != "feed"]
        self.save(layout)
        plan = run_plan(self.fake, layout)
        self.assertEqual(plan["actions"], [])
        self.assertTrue(any("lobby" in e for e in plan["extras"]))
        self.assertTrue(any("Feed" in e for e in plan["extras"]))
        rc, _ = self.apply(plan)
        self.assertEqual(rc, 0)
        self.assertEqual(self.fake.writes(), [])

    def test_a_dropped_overwrite_is_neutralised_not_deleted(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "channels", "news-feed")["overwrites"] = []
        self.save(layout)
        plan = run_plan(self.fake, layout)
        self.assertEqual([a["kind"] for a in plan["actions"]], ["channel.overwrite"])
        self.assertEqual((plan["actions"][0]["allow"], plan["actions"][0]["deny"]), ("0", "0"))
        rc, _ = self.apply(plan)
        self.assertEqual(rc, 0)
        self.assertEqual(run_plan(self.fake, layout)["actions"], [])  # neutral = absent

    def test_the_client_refuses_delete(self):
        api = dl.Api("tok", transport=lambda *a: (200, {}, b"{}"))
        with self.assertRaises(dl.DiscordError):
            api.request("DELETE", "/channels/1")


class TestOwnersBits(Case):
    def test_flagged_and_skipped_apply_goes_on(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "roles", "members")["permissions"] = (
            B["VIEW_CHANNEL"] | B["SEND_MESSAGES"] | B["KICK_MEMBERS"] | B["ADMINISTRATOR"])
        edit(layout, "channels", "general")["name"] = "chat"
        self.save(layout)
        plan = run_plan(self.fake, layout)
        text = "\n".join(plan["yours"])
        self.assertIn("KICK_MEMBERS", text)
        self.assertIn("ADMINISTRATOR", text)
        role_edit = next(a for a in plan["actions"] if a["kind"] == "role.edit")
        self.assertEqual(int(role_edit["changes"]["permissions"]), B["VIEW_CHANNEL"] | B["SEND_MESSAGES"])
        rc, out = self.apply(plan)
        self.assertEqual(rc, 0, out)
        self.assertEqual(int(self.fake.roles["2003"]["permissions"]), B["VIEW_CHANNEL"] | B["SEND_MESSAGES"])
        self.assertEqual(self.fake.channels["4001"]["name"], "chat")  # the rest was done

    def test_roles_above_the_bot_and_managed_roles_are_yours(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "roles", "admin")["name"] = "Boss"
        edit(layout, "roles", "layout-bot")["color"] = 5
        plan = run_plan(self.fake, layout)
        self.assertEqual(plan["actions"], [])
        self.assertEqual(len(plan["yours"]), 2)
        self.assertTrue(any("above the bot" in y for y in plan["yours"]))
        self.assertTrue(any("integration" in y for y in plan["yours"]))

    def test_a_channel_the_bot_cannot_see_is_yours(self):
        self.fake.channels["4003"]["permission_overwrites"].append(self.fake.ow("2002", 0, 0, B["VIEW_CHANNEL"]))
        layout, _, _ = imported(self.fake)
        edit(layout, "channels", "news-feed")["name"] = "news"
        plan = run_plan(self.fake, layout)
        self.assertEqual(plan["actions"], [])
        self.assertTrue(any("can't see or manage" in y for y in plan["yours"]))

    def test_new_role_bits_outside_the_set_are_left_off(self):
        layout, _, _ = imported(self.fake)
        layout["roles"].insert(3, {"key": "mods", "id": "", "name": "Mods", "color": 0, "hoist": False,
                                   "mentionable": False, "managed": False,
                                   "permissions": B["SEND_MESSAGES"] | B["BAN_MEMBERS"]})
        plan = run_plan(self.fake, layout)
        create = next(a for a in plan["actions"] if a["kind"] == "role.create")
        self.assertEqual(int(create["permissions"]), B["SEND_MESSAGES"])
        self.assertTrue(any("BAN_MEMBERS" in y for y in plan["yours"]))


class TestStale(Case):
    def test_a_stale_plan_is_refused(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "channels", "general")["name"] = "chat"
        self.save(layout)
        plan = run_plan(self.fake, layout)
        self.fake.channels["4002"]["name"] = "renamed by hand"
        before = len(self.fake.writes())
        rc, out = self.apply(plan)
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", out[0])
        self.assertEqual(len(self.fake.writes()), before)

    def test_stops_at_the_first_error_and_lists_what_was_done(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "channels", "general")["name"] = "chat"
        edit(layout, "channels", "lobby")["name"] = "lounge"
        self.save(layout)
        plan = run_plan(self.fake, layout)
        orig = self.fake.request

        def flaky(method, path, body=None):
            if path == "/channels/4002":
                raise dl.DiscordError(500, method, path, "boom")
            return orig(method, path, body)
        self.fake.request = flaky
        rc, out = self.apply(plan)
        self.assertEqual(rc, 1)
        self.assertTrue(any("STOPPED" in o for o in out))
        self.assertTrue(any("chat" in o for o in out))
        self.assertEqual(self.fake.channels["4001"]["name"], "chat")


class TestApiRetry(unittest.TestCase):
    def test_429_is_retried_after_retry_after(self):
        seq = [(429, {}, b'{"retry_after": 0.5, "message": "slow down"}'),
               (429, {}, b'{"retry_after": 1.0}'), (200, {}, b'{"id": "1"}')]
        slept, seen = [], []

        def transport(method, url, headers, data):
            seen.append(headers)
            return seq.pop(0)
        api = dl.Api("tok", transport=transport, sleep=slept.append)
        self.assertEqual(api.request("GET", "/users/@me"), {"id": "1"})
        self.assertEqual(len(slept), 2)
        self.assertAlmostEqual(slept[0], 0.6)
        self.assertEqual(seen[0]["Authorization"], "Bot tok")
        self.assertTrue(seen[0]["User-Agent"].startswith("DiscordBot ("))

    def test_errors_carry_no_token(self):
        api = dl.Api("SECRET-TOKEN", transport=lambda *a: (403, {}, b'{"message": "Missing Access", "code": 50001}'))
        with self.assertRaises(dl.DiscordError) as cm:
            api.request("GET", "/guilds/1/roles")
        self.assertNotIn("SECRET-TOKEN", str(cm.exception))
        self.assertIn("Missing Access", str(cm.exception))


class TestToml(Case):
    def test_round_trip(self):
        layout, _, _ = imported(self.fake)
        edit(layout, "channels", "general")["topic"] = 'quote " back\\slash\nnewline\ttab ünï 🎲'
        edit(layout, "channels", "general")["name"] = "a \"name\""
        edit(layout, "channels", "news-feed")["overwrites"].append(
            {"role": "everyone", "allow": B["VIEW_CHANNEL"] | B["ADD_REACTIONS"] | B["CONNECT"] | B["SPEAK"],
             "deny": B["SEND_MESSAGES"] | (1 << 47)})
        text = dl.dump_layout(layout)
        again = dl.load_layout(text)
        self.assertEqual(again, layout)
        self.assertEqual(dl.dump_layout(again), text)
        self.assertIn("BIT_47", text)

    def test_validation(self):
        layout, _, _ = imported(self.fake)
        good = dl.dump_layout(layout)
        for bad in (good.replace('version = 1', 'version = 2'),
                    good.replace('parent = "mess-hall"', 'parent = "nope"', 1),
                    good.replace('"VIEW_CHANNEL"', '"VIEW_CHANEL"', 1),
                    good + '\n[[channel]]\nkey = "general"\nid = ""\ntype = "text"\nname = "x"\n',
                    good.replace('type = "text"', 'type = "textt"', 1)):
            with self.assertRaises(dl.LayoutError):
                dl.load_layout(bad)

    def test_set_id_in_text_keeps_everything_else(self):
        layout, _, _ = imported(self.fake)
        layout["channels"].append({"key": "ops", "id": "", "type": "text", "name": "ops", "parent": "comms",
                                   "topic": "", "nsfw": False, "slowmode": 0, "user_limit": 0, "overwrites": []})
        text = dl.dump_layout(layout)
        out = dl.set_id_in_text(text, "channel", "ops", "123456")
        self.assertEqual(out.replace('id = "123456"', 'id = ""'), text)
        out2 = dl.set_id_in_text("# note\n[[channel]]\nkey = \"x\"\nname = \"x\"\n", "channel", "x", "99999")
        self.assertIn('key = "x"\nid = "99999"\nname', out2)
        with self.assertRaises(dl.LayoutError):
            dl.set_id_in_text(text, "role", "ops", "1")  # wrong kind


class TestHelpers(unittest.TestCase):
    def test_refill_keeps_unmanaged_slots(self):
        self.assertEqual(dl.refill(["a", "x", "b", "y", "c"], ["c", "a", "b"]), ["c", "x", "a", "y", "b"])
        self.assertEqual(dl.refill(["a", "b"], ["a", "b"]), ["a", "b"])
        self.assertEqual(dl.refill(["a", "b"], ["zz", "b", "a"]), ["b", "a"])

    def test_permission_names(self):
        self.assertEqual(dl.perm_bits(dl.perm_names(dl.BOT_PERMS)), dl.BOT_PERMS)
        for n in ("ADMINISTRATOR", "MANAGE_GUILD", "KICK_MEMBERS", "BAN_MEMBERS"):
            self.assertFalse(dl.BOT_PERMS & B[n], n)
        self.assertIn("permissions=" + str(dl.BOT_PERMS),
                      "permissions=" + str(dl.BOT_PERMS))

    def test_invite_url(self):
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            dl.cmd_invite(type("A", (), {"app_id": "42"})())
        self.assertIn("client_id=42", buf.getvalue())
        self.assertIn(f"permissions={dl.BOT_PERMS}", buf.getvalue())

    def test_plan_file_round_trip(self):
        fake = FakeDiscord()
        layout, _, _ = imported(fake)
        edit(layout, "channels", "general")["name"] = "chat — \"x\""
        plan = run_plan(fake, layout)
        self.assertEqual(dl.parse_plan(dl.render_plan(plan)), plan)


class TestTemplate(Case):
    def template(self, layout):
        roles = [{"id": 0, "name": "@everyone"}]
        names = [r["name"] for r in reversed(layout["roles"]) if r["key"] != "everyone" and not r["managed"]]
        roles += [{"id": i + 1, "name": n} for i, n in enumerate(names)]
        chans, n = [], 0
        ids = {}
        for c in layout["channels"]:
            n += 1
            ids[c["key"]] = n
        pos = {}
        for c in layout["channels"]:
            p = c["parent"] or None
            pos[p] = pos.get(p, -1) + 1
            chans.append({"id": ids[c["key"]], "type": dl.CH_TYPES[c["type"]], "name": c["name"],
                          "parent_id": ids[c["parent"]] if c["parent"] else None, "position": pos[p]})
        return {"serialized_source_guild": {"roles": roles, "channels": chans}}

    def test_match_and_differences(self):
        layout, _, _ = imported(self.fake)
        tpl = self.template(layout)
        self.assertEqual(dl.check_template(layout, tpl), [])
        edit(layout, "channels", "general")["name"] = "chat"
        d = dl.check_template(layout, tpl)
        self.assertTrue(any("missing in the layout" in x and "general" in x for x in d))
        self.assertTrue(any("extra in the layout" in x and "chat" in x for x in d))
        layout, _, _ = imported(self.fake)
        layout["roles"][2], layout["roles"][3] = layout["roles"][3], layout["roles"][2]
        self.assertTrue(any("order differs" in x for x in dl.check_template(layout, tpl)))


if __name__ == "__main__":
    unittest.main(verbosity=1)
