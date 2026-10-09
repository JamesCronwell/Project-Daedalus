# The Discord layout tool: how the owner uses it (BRIEF 05)

The server's structure (roles, categories, channels, role overwrites) lives in `discord/layout.toml`. A session edits
the file; **you** run `plan`, read it, then run `apply`. No session ever holds the token. The tool never deletes: it
flags extras, and a dropped role overwrite is neutralised (allow 0, deny 0), not removed. Schema: the docstring of
`tools/discord_layout.py`.

All commands run in your own PowerShell, in `C:\- Tools\- LLM\Daedalus`, by the full path
(`python -I "C:\- Tools\- LLM\Daedalus\tools\discord_layout.py" ...`).

## One-time: make the bot (about 10 minutes)
1. Discord Developer Portal (discord.com/developers/applications) > **New Application** > name it (e.g. `Layout Bot`).
2. **Bot** tab > **Reset Token** > copy the token straight into your password manager. Leave the three Privileged
   Gateway Intents off. Turn **Public Bot** off.
3. Store it for the tool: run `tools\discord-setpass.ps1` and paste the token when asked. It writes
   `%LOCALAPPDATA%\Daedalus\discord-token.dpapi` (readable only by you on this PC).
4. Copy the application's **Application ID** (General Information) and print the invite link (no secret in it):
   `python -I "C:\- Tools\- LLM\Daedalus\tools\discord_layout.py" invite --app-id <APPLICATION ID>`
   It asks for View Channels, Manage Channels, Manage Roles, Send Messages, Embed Links, Attach Files, Read Message
   History, Add Reactions, Mention Everyone, Manage Webhooks, Connect and Speak. Never Administrator, Manage Server,
   Kick or Ban.
5. Open the link and add the bot to the **test server**. In Server Settings > Roles, drag the bot's role **above every
   role you want it to edit** (it can only edit roles below its own).
6. Turn on Developer Mode (User Settings > Advanced), right-click the server's icon > **Copy Server ID**.

## On the test server
1. `... discord_layout.py import --guild <SERVER ID> --layout "C:\- Tools\- LLM\Daedalus\docs\discord\test-layout.toml"`
   (the `docs/discord` folder is gitignored; use it for the test server's layout).
2. `... plan --layout <that file>`: it should show no changes.
3. Tell a session what to change (a rename, a move, a new channel, a read-only overwrite, a new role). It edits the file
   and shows the diff. Then `plan` again and give the session the plan file to check, then
   `... apply "C:\- Tools\- LLM\Daedalus\docs\discord\plan-<time>.md" --layout <that file>`.
4. `plan` once more: it must show no changes. Also try a bit the bot can't set (say, Administrator on a role): the plan
   lists it under "Yours" and apply skips it.

## On the live server (Mojo Dojo Casa House)
The session writes the CHANGELOG entry first. Then: invite the bot, drag its role up, `import --guild <LIVE ID>` (to
`discord\layout.toml`), `check-template docs\discord\before-2026-10-09.template.json`, and `names` so you can confirm
no person's name sits in the file before it is committed.

## When something goes wrong
- **"REFUSED: the server changed"**: someone (you) changed the server after the plan. Run `plan` again.
- **"STOPPED"**: apply lists what it did and what failed. Run `plan` again; it shows what is left.
- **A leaked token**: Developer Portal > Bot > Reset Token, update the password manager, delete the `.dpapi` file, run
  `tools\discord-setpass.ps1` again.
- **Retire the bot**: kick it from the server, delete the application in the Portal, delete the `.dpapi` file.
