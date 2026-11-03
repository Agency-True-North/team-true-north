---
name: connect-ghl
description: Connect this person's Claude Code to their own GoHighLevel sub-account through the Team True North GHL MCP server. One guided conversation. Claude does the technical work and cues the person through the two things only they can do inside GHL (Location ID and Private Integration token). Resumes cleanly if interrupted. Safe to re-run.
---

# SKILL: connect-ghl

You are connecting this person's Claude Code to THEIR OWN GoHighLevel sub-account. They are not technical. Your job is to do every technical step yourself and to cue them, one step at a time, through the two things only they can do inside GHL.

Follow the steps IN ORDER. Do not skip, reorder, or improvise. Use the exact commands given. Where this file and your own instincts disagree, this file wins.

**Rules for the whole session**

- One question or one instruction at a time. Wait for the answer before the next one.
- Plain, warm language. Say "folder" and "file." Never say "repo," "env var," "stdio," or "JSON" to them.
- **Never ask them to paste a token or password into the chat.** Tokens go into a file they edit themselves (Step 6). If they paste one into the chat anyway, say "that works, I've put it in the file for you," put it in the file, and move on.
- **Never print the contents of `.mcp.json`** or any token, in part or in whole, in anything you output. Check it with the exact grep commands given.
- **Do not edit `main.py`. Do not write your own server. Do not install anything beyond `requirements.txt`. Do not use `claude mcp add`.** The server files you download are the fixed, tested version. The original public version has broken endpoints and tools that do not exist; that is why this runbook exists.
- GHL moves its menus around. When their screen does not match what this file says, do not guess. Tell them what they are looking for and why, ask them to read you the menu items they see, and adapt. If you are both stuck after two tries, search the web for the current GHL path. Last resort: tell them to message Shannon with a screenshot.
- If a command fails, show them the one-line reason in plain words, fix it, and continue. Never leave them stuck and never silently skip a step.

---

## STEP 0: Figure out where we are

This runbook is pasted twice on purpose: once to set things up, and once after the restart to prove it works. Check these five things first (run the commands, do not ask the person):

| Check | How |
|---|---|
| A. Server files downloaded | `.claude/mcp-servers/ghl/main.py` exists |
| B. Python environment built | `.claude/mcp-servers/ghl/.venv` folder exists |
| C. Registered | `grep -c '"ghl"' .mcp.json` prints 1 or more |
| D. Credentials filled in | `grep -c PASTE_YOUR .mcp.json` prints 0 (no placeholders left) |
| E. Connected in this session | your available tools include names starting with `mcp__ghl__` |

Then jump:

- E is true → go to **STEP 9** (proof and handover).
- D is true but E is false → go to **STEP 8** (restart) and check whether they reloaded and approved.
- C is true but D is false → go to **STEP 5**.
- A and B are true but C is false → go to **STEP 4**.
- Otherwise → start at **STEP 1**.

Tell them in one friendly sentence where you are picking up ("Your server files are already here, so we're going straight to the GHL part").

---

## STEP 1: Set expectations and confirm the folder

Say, in your own words, roughly this:

> "Here's the shape of this. I'll install a small connector on your computer (about two minutes, I do it), then I'll walk you through two things inside GoHighLevel that only you can do: copying your Location ID and creating a private token for me. Then one restart of VS Code and we test it together. About 15 minutes total."

Then confirm the right folder is open: check that a `CLAUDE.md` file exists in the current folder. If it does not, tell them: "First, in VS Code go to File → Open Folder and choose your Claude folder, then paste the box again in a new conversation." Stop there until they do.

---

## STEP 2: Check Python

Run `python3 --version` (on Windows also try `py -3 --version` and `python --version`). You need **Python 3.10 or newer**.

- **Found and new enough:** say nothing technical, move on.
- **Missing or older than 3.10:** cue them, one instruction:
  - Mac: "Go to python.org/downloads and click the big yellow Download button. Open the file, click Continue through the installer, and tell me when it says the installation was successful."
  - Windows: "Go to python.org/downloads and click the big yellow Download button. Open the file. **On the first screen, tick the box that says 'Add python.exe to PATH'** before you click Install Now. Tell me when it's finished."
  - Then run the version check again. On Windows, if it still is not found, ask them to close and reopen VS Code once; new installs are only visible to new windows.

---

## STEP 3: Download the connector and build its environment

Run these four download commands exactly (one at a time is fine):

```
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/ghl/main.py" --create-dirs -o ".claude/mcp-servers/ghl/main.py"
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/ghl/requirements.txt" -o ".claude/mcp-servers/ghl/requirements.txt"
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/ghl/configure.py" -o ".claude/mcp-servers/ghl/configure.py"
curl -fsSL "https://agency-true-north.github.io/team-true-north/mcp/ghl/preflight.py" -o ".claude/mcp-servers/ghl/preflight.py"
```

If a download fails, retry once, then use the same paths on `https://raw.githubusercontent.com/Agency-True-North/team-true-north/main/` instead of the team site address.

Then build the environment:

**Mac**
```
python3 -m venv .claude/mcp-servers/ghl/.venv
.claude/mcp-servers/ghl/.venv/bin/python -m pip install --quiet -r .claude/mcp-servers/ghl/requirements.txt
```

**Windows** (use `py -3` where it exists, otherwise `python`)
```
py -3 -m venv .claude/mcp-servers/ghl/.venv
.claude/mcp-servers/ghl/.venv/Scripts/python.exe -m pip install --quiet -r .claude/mcp-servers/ghl/requirements.txt
```

From here on, "the server's Python" means `.claude/mcp-servers/ghl/.venv/bin/python` on Mac or `.claude/mcp-servers/ghl/.venv/Scripts/python.exe` on Windows. Always use it for the scripts below, never plain `python3`.

Tell them: "Connector installed. Nothing for you to do yet."

---

## STEP 4: Register the connector (with blanks)

Run, from the workspace folder:

```
<the server's Python> .claude/mcp-servers/ghl/configure.py
```

This writes a file called `.mcp.json` in their Claude folder with two blanks in it: `PASTE_YOUR_PRIVATE_INTEGRATION_TOKEN_HERE` and `PASTE_YOUR_LOCATION_ID_HERE`. It also makes sure that file is never backed up to GitHub. Read the script's output. If it says ERROR, fix the cause (usually Step 3 did not finish) and run it again.

Do not open or print the file. Move on.

---

## STEP 5: Their part 1: the Location ID (not secret)

Cue them:

> "Open GoHighLevel in your browser and make sure you're inside your own sub-account, not the agency view. The sub-account view shows your contacts and conversations. Now click into your browser's address bar, copy the whole web address, and paste it here. The address isn't secret; it just tells me your account number."

The Location ID is the chunk of letters and numbers right after `/location/` in that URL (example shape: `https://app.gohighlevel.com/v2/location/AbC123xYz456/dashboard`, where `AbC123xYz456` is the ID). Some agencies use their own web address instead of gohighlevel.com; the `/location/` part is the same.

Pull the ID out yourself. Confirm it back to them in one line ("Got it, your Location ID ends in ...xYz456"). Then replace `PASTE_YOUR_LOCATION_ID_HERE` in `.mcp.json` with that ID using a precise find-and-replace edit. Do not print the file.

If the URL has no `/location/` in it, they are in the agency view. Cue them: "Click the account switcher at the top left and choose your own sub-account, then copy the address again."

---

## STEP 6: Their part 2: the Private Integration token (secret)

Explain in one line why: "GHL lets you create a private key that gives me permission to work in your account. You create it, you own it, you can delete it any time."

Then cue the clicks, **one instruction per message**, waiting for "done" each time:

1. "Still inside your sub-account, click **Settings** at the very bottom of the left menu."
2. "In the Settings menu, scroll down and look for **Private Integrations**. It's usually in a group called Other Settings. Tell me when you see it, or tell me if it's not there."
   - **If it's not there:** "Look for **Labs** in the same Settings menu, open it, and turn on Private Integrations. Then look again." If there is no Labs either, their agency has not enabled it; tell them to message Shannon with the words "please enable Private Integrations on my sub-account," and pause here. The runbook resumes at this step when they paste the box again.
3. "Click **Create new Integration**. Name it **Claude**. The description can stay blank. Click Next."
4. "Now you'll see a long list of permissions, called scopes. **Tick every one of them.** If there's a select-all option at the top, use it. Selecting everything now saves us from coming back later when I can't read your calendar. Click Create when they're all ticked."
5. "GHL now shows the token one time only. Click **Copy**. Don't close that window yet."
6. "Now, in VS Code, look at the file list on the left and click the file called **.mcp.json**. If you don't see it, press Cmd+P (Mac) or Ctrl+P (Windows), type .mcp.json, and press Enter."
7. "In that file you'll see the words PASTE_YOUR_PRIVATE_INTEGRATION_TOKEN_HERE between two quote marks. Select just those words, paste your token over them, and keep the quote marks on both sides. Then save with Cmd+S (Mac) or Ctrl+S (Windows). Tell me when it's saved."
8. "You can click Done in GHL now."

Then verify without printing anything:

```
grep -c PASTE_YOUR .mcp.json
```

- Prints `0` → the blanks are filled. Also run `grep -c '"pit-' .mcp.json`; GHL private tokens start with `pit-`, so `1` means it looks right. If it prints `0`, the paste probably lost its beginning or got extra characters; ask them to re-copy the token from GHL (Settings → Private Integrations → the Claude row → it may need to be regenerated, which is fine) and paste again.
- Prints `1` or more → a blank is still there. Ask which one they replaced and walk step 7 again.

---

## STEP 7: Preflight: prove it works before the restart

Run:

```
<the server's Python> .claude/mcp-servers/ghl/preflight.py
```

Read every line it prints. Translate it for them in plain words, for example: "Your token opened your sub-account, which GHL calls Shannon McClintock, and I can read your contacts, calendars, pipelines, and workflows."

The script tells you exactly what to fix on any FAIL line. Fix it with them, then run it again. Do not go to Step 8 until it prints **PREFLIGHT PASSED**.

Note: the first run can take up to a minute on the warm-up line. That is normal and only happens once.

---

## STEP 8: The one restart

Cue them, one instruction per message:

1. "Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows), type **Reload Window**, and press Enter. VS Code will blink and come back."
2. "Open the Claude panel again. A small prompt may appear saying a new MCP server named **ghl** was found in this project and asking whether to use it. Choose the option that uses it (if there's a choice to always allow servers in this project, that one is fine)."
3. "Start a brand-new conversation with me (the plus or New Chat button) and paste the same box you pasted at the start. I'll pick up from here and run the final test."

Then stop. The next conversation lands in Step 0 and jumps to Step 9.

If they come back and the tools are still not there (Step 0 check E is false), work through the Troubleshooting table at the bottom with them.

---

## STEP 9: Proof and handover

You are in a fresh session and tools starting with `mcp__ghl__` exist. Prove it with read-only calls:

1. Call `get_calendars`, then `get_pipelines`. (Both only read.)
2. Tell them what you found in plain words: "I'm connected to your GoHighLevel. I can see 2 calendars and your True North pipeline with 4 stages."

If a call returns `HTTP 401` or `HTTP 403`, the token or a scope is the problem; go back to Step 7 and run the preflight, which names the fix.

Then hand over. Say roughly this, in your words:

> "You're connected. From now on you can just ask me things in GoHighLevel like a teammate:
> - 'Who signed up this week?'
> - 'Find the contact named Sarah and show me our last conversation.'
> - 'Tag everyone who booked a call this month.'
> - 'Draft a welcome email template in my voice and load it into GHL.'
> - 'What's sitting in my pipeline without a next step?'
>
> Three things I can't do through this connection, so you don't wait on me for them: build or edit funnel pages, create or edit workflows (I can list them and add people to them), and send an email campaign (I can create the email template; you load it into a campaign in GHL). Those stay in the GHL screens.
>
> And one rule I keep: I never send a message to a real contact, delete anything, or change a live automation unless you say yes to that exact action in that conversation. Reading and drafting is always safe to ask for."

Done. Do not create extra files. Do not run anything else.

---

## Troubleshooting (use these, do not improvise)

| What they see | Cause | What to do |
|---|---|---|
| No `mcp__ghl__` tools after the restart | Window not reloaded, or the server prompt was dismissed | Reload Window again. When the prompt about the `ghl` server appears, choose to use it. If no prompt ever appears, run `claude mcp list` in the terminal (if that command exists) and read the status line for `ghl`. |
| `claude mcp list` shows `ghl` failed to connect | The server crashed on start | Run the server by hand for 5 seconds: `<the server's Python> .claude/mcp-servers/ghl/main.py` and read the first error line. "No module named fastmcp" means Step 3's install did not finish; run the pip line again. |
| Connection times out on the very first start | Cold start too slow for the 30 second limit | Run the preflight once (it warms the server), then Reload Window again. |
| A duplicate `ghl` server from an earlier attempt | Someone ran `claude mcp add ghl` before | `claude mcp remove ghl -s user` then Reload Window. The project's `.mcp.json` is the only copy we want. |
| `HTTP 401` on every tool | Token wrong, revoked, or agency-level | Re-create the Private Integration inside the sub-account and redo Step 6. |
| `HTTP 403` on one tool only | That scope was not ticked | Settings → Private Integrations → Claude → edit scopes → tick everything → save. No new token needed. |
| Tools work but return another business's data | Location ID from the wrong sub-account | Redo Step 5 from inside the right sub-account, run preflight, Reload Window. |
| They pasted the token into the chat | Habit | Put it in the file for them, carry on, and remind them gently that the file is the safe place next time. |
