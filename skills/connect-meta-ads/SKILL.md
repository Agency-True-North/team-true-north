---
name: connect-meta-ads
description: Connect this person's Claude Code to their own Meta (Facebook and Instagram) ad account through the Team True North Meta Ads MCP server. One guided conversation. Claude does the technical work and cues the person through the three things only they can do inside Meta (create the app, copy its ID and secret, generate a token). Resumes cleanly if interrupted. Safe to re-run.
---

# SKILL: connect-meta-ads

You are connecting this person's Claude Code to THEIR OWN Meta ad account. They are not technical and Meta's screens are confusing even for people who are. Your job is to do every technical step yourself and to cue them, one click at a time, through the parts only they can do.

Follow the steps IN ORDER. Do not skip, reorder, or improvise. Use the exact commands given. Where this file and your own instincts disagree, this file wins.

**Rules for the whole session**

- One question or one instruction at a time. Wait for the answer before the next one.
- Plain, warm language. Say "folder" and "file." Never say "repo," "env var," "OAuth," "scope," or "JSON" to them. Say "permission" instead of "scope."
- **Never ask them to paste the App Secret or the access token into the chat.** Those go into a file they edit themselves (Steps 5 and 6). The App ID is not secret; it can go in the chat. If they paste a secret into the chat anyway, say "that works, I've put it in the file for you," put it in the file, and move on.
- **Never print the contents of `.mcp.json`, `.token.json`, or any token or secret**, in part or in whole. Check them only with the exact grep commands given.
- **Do not edit `main.py`. Do not write your own server. Do not install anything beyond `requirements.txt`. Do not use `claude mcp add`.** The server you download is the tested version with self-renewing tokens, retries, and plain-English errors.
- Meta renames menus constantly. When their screen does not match this file, do not guess. Tell them what they are looking for and why, ask them to read you the options they see, and adapt. If you are both stuck after two tries, search the web for the current path. Last resort: tell them to message Shannon with a screenshot.
- If a command fails, show them the one-line reason in plain words, fix it, and continue. Never leave them stuck and never silently skip a step.

---

## STEP 0: Figure out where we are

This runbook is pasted twice on purpose: once to set things up, and once after the restart to prove it works. Check these five things first (run the commands, do not ask the person):

| Check | How |
|---|---|
| A. Server files downloaded | `.claude/mcp-servers/meta-ads/main.py` exists |
| B. Python environment built | `.claude/mcp-servers/meta-ads/.venv` folder exists |
| C. Registered | `grep -c '"meta-ads"' .mcp.json` prints 1 or more |
| D. Credentials filled in | `grep -c PASTE_YOUR_A .mcp.json` prints 0 (no Meta placeholders left) |
| E. Connected in this session | your available tools include names starting with `mcp__meta-ads__` |

Then jump:

- E is true → go to **STEP 9** (proof and handover).
- D is true but E is false → go to **STEP 8** (restart) and check whether they reloaded and approved.
- C is true but D is false → go to **STEP 4** (their part begins there).
- A and B are true but C is false → go to **STEP 3b** (register).
- Otherwise → start at **STEP 1**.

Tell them in one friendly sentence where you are picking up.

---

## STEP 1: Set expectations and confirm the folder

Say, in your own words, roughly this:

> "Here's the shape of this. I'll install a small connector on your computer (two minutes, I do it). Then I'll walk you through three things inside Meta that only you can do: creating a tiny 'app' that gives me a door into your ad account, copying its ID and secret, and generating a key that never expires. Then one restart of VS Code and we test it together. Meta's screens are the slow part; budget 25 minutes."

Then ask one question:

> "Do you run your ads from a Meta Business Portfolio (the business.facebook.com side), with your ad account inside it?"

- **Yes:** continue.
- **No or not sure:** the team's **Meta Ads Setup Guide** builds the Business Portfolio, ad account, and pixel. Tell them to finish sections 02 and 03 of that guide first, then paste this box again. Pause here.

Then confirm the right folder is open: check that a `CLAUDE.md` file exists in the current folder. If not, tell them: "In VS Code go to File → Open Folder and choose your Claude folder, then paste the box again in a new conversation." Stop until they do.

---

## STEP 2: Check Python

Run `python3 --version` (on Windows also try `py -3 --version` and `python --version`). You need **Python 3.10 or newer**.

- **Found and new enough:** move on silently.
- **Missing or older than 3.10:** cue them:
  - Mac: "Go to python.org/downloads and click the big yellow Download button. Open the file, click Continue through the installer, and tell me when it says the installation was successful."
  - Windows: "Go to python.org/downloads and click the big yellow Download button. Open the file. **On the first screen, tick 'Add python.exe to PATH'** before you click Install Now. Tell me when it's finished."
  - Re-run the version check. On Windows, if it still is not found, ask them to close and reopen VS Code once.

---

## STEP 3: Download the connector and build its environment

Run these four download commands exactly:

```
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/meta-ads/main.py" --create-dirs -o ".claude/mcp-servers/meta-ads/main.py"
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/meta-ads/requirements.txt" -o ".claude/mcp-servers/meta-ads/requirements.txt"
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/meta-ads/configure.py" -o ".claude/mcp-servers/meta-ads/configure.py"
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/meta-ads/preflight.py" -o ".claude/mcp-servers/meta-ads/preflight.py"
```

If a download fails, retry once, then use the same paths on `https://raw.githubusercontent.com/Agency-True-North/team-true-north/main/` instead.

Build the environment:

**Mac**
```
python3 -m venv .claude/mcp-servers/meta-ads/.venv
.claude/mcp-servers/meta-ads/.venv/bin/python -m pip install --quiet -r .claude/mcp-servers/meta-ads/requirements.txt
```

**Windows** (use `py -3` where it exists, otherwise `python`)
```
py -3 -m venv .claude/mcp-servers/meta-ads/.venv
.claude/mcp-servers/meta-ads/.venv/Scripts/python.exe -m pip install --quiet -r .claude/mcp-servers/meta-ads/requirements.txt
```

From here on, "the server's Python" means `.claude/mcp-servers/meta-ads/.venv/bin/python` on Mac or `.claude/mcp-servers/meta-ads/.venv/Scripts/python.exe` on Windows. Always use it for the scripts below.

### STEP 3b: Register the connector (with blanks)

```
<the server's Python> .claude/mcp-servers/meta-ads/configure.py
```

This writes `.mcp.json` in their Claude folder with three blanks: `PASTE_YOUR_APP_ID_HERE`, `PASTE_YOUR_APP_SECRET_HERE`, `PASTE_YOUR_ACCESS_TOKEN_HERE`. It also makes sure that file is never backed up online. If the GHL connector was set up earlier, it is kept; this adds alongside it. If the script says ERROR, fix the cause (usually Step 3 did not finish) and run it again.

Tell them: "Connector installed. Now the Meta part, one click at a time."

---

## STEP 4: Their part 1: create the Meta app

Explain in one line why: "Meta only lets software into an ad account through an 'app.' Yours will be private, just a door with your name on it. Nobody else ever sees it."

Cue the clicks, **one instruction per message**, waiting for "done" each time:

1. "In your browser go to **developers.facebook.com** and log in with the Facebook account that owns your ads. If it's your first time there, it may ask you to register as a developer: accept the terms and confirm your email or phone. Tell me when you're on the developer site."
2. "At the top right click **My Apps**, then the green **Create App** button."
3. "Meta now asks about a use case. Look for an option that mentions **Marketing API** or **managing ads** (recent wording: 'Create & manage ads with Marketing API'). Pick it and click Next. If you only see broad categories, choose **Other**, then **Business**, then Next. Read me the options if neither fits."
4. "Name the app **Claude Ads** (add your first name if you like). Make sure the contact email is yours. If it asks for a **Business portfolio**, choose yours. Then click **Create app**. It may ask for your Facebook password."
5. "You should now be looking at your app's dashboard. Tell me what you see at the top."

**Do not** let them click anything about "Go live," "App Review," or "Publish." A private app in development mode is exactly right: it can work on their own ad accounts without any review.

---

## STEP 5: Their part 2: the App ID (not secret) and App Secret (secret)

1. "In the left menu of your app, click **App settings**, then **Basic**."
2. "At the top you'll see **App ID**: a long number. Copy it and paste it here. That one isn't secret."
   - Replace `PASTE_YOUR_APP_ID_HERE` in `.mcp.json` with it using a precise find-and-replace edit. Do not print the file.
3. "Next to **App secret** click **Show**. It may ask for your password. Then click into the secret and copy it."
4. "Now, in VS Code, click the file called **.mcp.json** in the file list on the left (or press Cmd+P on Mac / Ctrl+P on Windows, type .mcp.json, Enter)."
5. "Find the words PASTE_YOUR_APP_SECRET_HERE between two quote marks. Select just those words, paste the secret over them, keep the quote marks, and save with Cmd+S or Ctrl+S. Tell me when it's saved."

Verify silently with `grep -c PASTE_YOUR_APP_SECRET_HERE .mcp.json` (want `0`).

---

## STEP 6: Their part 3: the access token

Explain in one line: "Last piece. Meta needs a key that proves you gave me permission. We'll make one that never expires so you never do this again."

**Path A (preferred): a System User token.** One instruction per message:

1. "Go to **business.facebook.com/settings**. This is Business Settings for your portfolio. If it asks which business, pick the one with your ad account."
2. "In the left menu under **Users**, click **System users**. Click **Add**."
3. "Name it **Claude**, set the role to **Admin**, and click **Create system user**. Accept any terms it shows."
4. "Click on your new Claude system user. Click **Assign assets**. Choose **Apps** on the left, tick **Claude Ads**, turn on full control (it may be called Manage app), and Save."
5. "Click **Assign assets** again. Choose **Ad accounts**, tick your ad account, turn on full control (Manage ad account), and Save."
6. "Click **Assign assets** once more. Choose **Pages**, tick your business page, turn on full control, and Save. This lets me see which page your ads run from."
7. "Now click **Generate new token**. Choose the app **Claude Ads**. For **Token expiration** choose **Never**. Tell me if Never isn't offered."
8. "In the permissions list tick these five: **ads_management**, **ads_read**, **business_management**, **pages_show_list**, **pages_read_engagement**. Then click **Generate token**."
9. "Meta shows the token one time only. Click **Copy**."
10. "In VS Code, in the .mcp.json file, find PASTE_YOUR_ACCESS_TOKEN_HERE between two quote marks. Select just those words, paste the token over them, keep the quote marks, and save. Tell me when it's saved."

If "Never" is not offered, Meta wants the business verified first. Take **Path B** instead; it works for a long time and renews itself.

**Path B (fallback): a personal token that the connector renews.**

1. "Go to **developers.facebook.com/tools/explorer**. This is Meta's Graph API Explorer."
2. "On the right, under **Meta App**, choose **Claude Ads**. Under **User or Page**, choose **User Token**."
3. "Under **Permissions**, click Add a permission and add these: **ads_read**, **ads_management**, **business_management**, **pages_show_list**. Then click **Generate Access Token**, and click Continue as yourself in the pop-up."
4. "Copy the token that appears in the Access Token box."
5. Same paste as Path A step 10.

A Path B token lasts about two hours on its own; the preflight in Step 7 trades it for a two-month one, and the server renews that every week as long as it gets used. It dies only if they change their Facebook password or go two months without using it. The "Renewing a token later" note at the bottom covers that.

Verify silently with `grep -c PASTE_YOUR_A .mcp.json` (want `0`).

---

## STEP 7: Preflight: prove it works before the restart

Run:

```
<the server's Python> .claude/mcp-servers/meta-ads/preflight.py
```

Read every line. Translate for them in plain words, for example: "Your key is valid and never expires, it has the ad permissions, and I can see your ad account 'TTN Ads,' which is active."

The script says exactly what to fix on any FAIL line. Fix it with them and run again. Do not go to Step 8 until it prints **PREFLIGHT PASSED**.

Notes:
- The warm-up line can take up to a minute on the first run. Normal, once only.
- If the token line says it expires in about 60 days, that is Path B working as designed.
- If the ad account line says "disabled" or "unsettled," the connection is fine; the ad account itself needs attention in Ads Manager (payment or policy). Say so plainly.

---

## STEP 8: The one restart

One instruction per message:

1. "Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows), type **Reload Window**, and press Enter."
2. "Open the Claude panel again. A small prompt may appear saying a new MCP server named **meta-ads** was found in this project. Choose the option that uses it."
3. "Start a brand-new conversation with me and paste the same box you pasted at the start. I'll run the final test."

Then stop. The next conversation lands in Step 0 and jumps to Step 9.

---

## STEP 9: Proof and handover

You are in a fresh session and tools starting with `mcp__meta-ads__` exist. Prove it with read-only calls:

1. Call `check_connection`. Read the result: token valid, days left or never, permissions, ad accounts reachable.
2. Call `get_ad_accounts`. Note each account's name and its `act_` number; you will need that number for every campaign question later.
3. Tell them in plain words: "I'm connected to your Meta ad account 'TTN Ads.' Your key never expires and I can read and manage campaigns there."

If `check_connection` reports the token invalid, go back to Step 7; the preflight names the fix.

Then hand over. Say roughly this, in your words:

> "You're connected. Things you can ask me now:
> - 'How did my ads do this week? Spend, leads, cost per lead.'
> - 'Which ad set is winning and which one is wasting money?'
> - 'Show me the campaigns I have paused.'
> - 'Draft three new primary texts for the ad that's working.'
> - 'Walk me through launching a new ad set inside my existing campaign.'
>
> Two rules I keep, because this is real money:
> - Reading and analyzing is always safe to ask for. I never create, edit, pause, launch, or change a budget unless you say yes to that exact action in that conversation, and I'll state the dollar amount back to you before I touch a budget.
> - When we do build, we stay inside your existing campaign and add ad sets to it, with budgets set at the ad set level. Restarting campaigns resets what Meta has learned about your audience."

Done. Do not create extra files. Do not run anything else.

---

## Renewing a token later (only if it ever dies)

Path A tokens do not die. A Path B token dies after a password change or two months unused. Symptom: every Meta tool answers "AUTH FAILED (code 190)." Fix: generate a new token (Path A or B above), have them paste it over the old one in `.mcp.json`, delete the file `.claude/mcp-servers/meta-ads/.token.json`, run the preflight, Reload Window. Never paste the token in chat.

---

## Troubleshooting (use these, do not improvise)

| What they see | Cause | What to do |
|---|---|---|
| No `mcp__meta-ads__` tools after the restart | Window not reloaded, or the server prompt was dismissed | Reload Window again and choose to use the `meta-ads` server when prompted. If no prompt appears, run `claude mcp list` (if that command exists) and read the status for `meta-ads`. |
| `claude mcp list` says `meta-ads` failed to connect | Crashed on start, or cold start too slow | Run the preflight once (it warms the server and shows any error), then Reload Window again. "No module named fastmcp" means Step 3's install did not finish; run the pip line again. |
| Preflight: "Meta rejected the App ID / App Secret pair" | One of them copied wrong | App settings → Basic. Re-copy both. The secret needs Show clicked first. |
| Preflight: token missing ads_management or ads_read | Permissions not ticked when generating | Generate the token again with all five ticked (Path A step 8). |
| Preflight: "no ad account is attached" | System user never got the ad account assigned | Path A step 5. Then run preflight again; no new token needed. |
| Ad account shows "disabled" | Meta restricted the ad account itself | Not a connection problem. Open Ads Manager and follow Meta's notice (usually payment or policy). |
| `AUTH FAILED (code 190)` weeks later | Path B token died (password change or unused 60 days) | "Renewing a token later" above. |
| A duplicate `metaads` or `meta-ads` server from an earlier attempt | Someone ran `claude mcp add` before | `claude mcp remove <name> -s user` then Reload Window. The project's `.mcp.json` is the only copy we want. |
| They pasted the secret or token into the chat | Habit | Put it in the file for them, carry on, and remind them gently that the file is the safe place next time. |
