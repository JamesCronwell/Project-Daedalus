"""Render a Discord server template (GET /guilds/templates/<code>) as a category/channel/role tree.

    python -I tools/discord_tree.py docs/discord/before-2026-10-09.template.json

Read-only: it reads the saved JSON, nothing else. BRIEF 03.
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(sys.argv[1], encoding='utf-8'))
g = d['serialized_source_guild']
T = {0:'#',2:'voice',4:'CAT',5:'news',13:'stage',15:'forum',16:'media'}
P = {'ADMIN':0x8,'MANAGE_CH':0x10,'MANAGE_GUILD':0x20,'VIEW':0x400,'SEND':0x800,'MANAGE_MSG':0x2000,
     'MENTION_ALL':0x20000,'CONNECT':0x100000,'MANAGE_ROLES':0x10000000,'KICK':0x2,'BAN':0x4,'SEND_THREADS':0x4000000000}
roles = {r['id']: r for r in g['roles']}
def rname(i): return roles[i]['name'] if i in roles else f'?{i}'
def flags(v): v=int(v); return ','.join(k for k,b in P.items() if v & b) or '-'
def ow(c):
    out=[]
    for o in c.get('permission_overwrites') or []:
        a,dn = flags(o['allow']), flags(o['deny'])
        out.append(f"{rname(o['id'])}[+{a} -{dn}]")
    return '; '.join(out)
print(f"guild: verification={g['verification_level']} notif={g['default_message_notifications']} "
      f"filter={g['explicit_content_filter']} afk={g['afk_channel_id']} system_ch={g['system_channel_id']}")
chs = g['channels']
cats = sorted([c for c in chs if c['type']==4], key=lambda c:c['position'])
def kids(pid): return sorted([c for c in chs if c.get('parent_id')==pid and c['type']!=4], key=lambda c:(c['type'] in (2,13), c['position']))
for c in [None]+cats:
    pid = None if c is None else c['id']
    if c is None:
        k = kids(None)
        if not k: continue
        print('\n(no category)')
    else:
        print(f"\nCAT {c['name']}   {ow(c)}")
    for ch in kids(pid):
        extra = []
        if ch.get('topic'): extra.append('topic')
        if ch.get('nsfw'): extra.append('nsfw')
        if ch.get('rate_limit_per_user'): extra.append(f"slow={ch['rate_limit_per_user']}s")
        if ch.get('user_limit'): extra.append(f"limit={ch['user_limit']}")
        o = ow(ch)
        print(f"  {T.get(ch['type'],ch['type']):5} {ch['name']}{' ('+','.join(extra)+')' if extra else ''}{'   '+o if o else ''}")
print('\nROLES (top first): name | color | hoist | mentionable | notable perms')
for r in sorted(g['roles'], key=lambda r: -r['id']):
    perms = flags(r['permissions'])
    print(f"  {r['id']:>2} {r['name']} | #{r['color']:06x} | {'H' if r['hoist'] else '-'} | {'M' if r['mentionable'] else '-'} | "
          f"{'ADMIN' if int(r['permissions'])&0x8 else ','.join(x for x in perms.split(',') if x in ('MANAGE_CH','MANAGE_GUILD','MANAGE_ROLES','MANAGE_MSG','KICK','BAN','MENTION_ALL'))}")
