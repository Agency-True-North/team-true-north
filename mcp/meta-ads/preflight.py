#!/usr/bin/env python3
"""
preflight.py for the Meta Ads connection (Team True North).

Proves the credentials in .mcp.json work against the live Meta API BEFORE
the restart: token valid, right permissions, ad account reachable. If the
token is a short-lived user token it is exchanged for a long-lived one and
saved to .token.json (the server keeps that fresh from then on). Also warms
up the server so its first real start is fast. Never prints secrets.

Run from the workspace root with the server's own Python:
    <venv python> .claude/mcp-servers/meta-ads/preflight.py
Optional: --config PATH   (defaults to ./.mcp.json)
          --server NAME   (defaults to meta-ads)
"""
import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("ERROR: run this with the server's own Python (the one inside .venv), not the system Python.")
    sys.exit(1)

PLACEHOLDERS = {"PASTE_YOUR_APP_ID_HERE", "PASTE_YOUR_APP_SECRET_HERE", "PASTE_YOUR_ACCESS_TOKEN_HERE"}
NEEDED_SCOPES = ["ads_read", "ads_management"]
NICE_SCOPES = ["business_management", "pages_show_list"]
ACCOUNT_STATUS = {1: "active", 2: "disabled", 3: "unsettled", 7: "pending risk review",
                  8: "pending settlement", 9: "in grace period", 100: "pending closure",
                  101: "closed", 201: "any active", 202: "any closed"}


def clean(value: str, label: str) -> str:
    raw = value or ""
    fixed = raw.strip().strip('"').strip("'").strip()
    if not fixed or fixed in PLACEHOLDERS:
        print(f"FAIL: {label} is still the placeholder (or empty) in .mcp.json.")
        print("      Open .mcp.json in VS Code, replace the placeholder, save, then run me again.")
        sys.exit(1)
    if fixed != raw:
        print(f"NOTE: {label} had extra spaces or quotes around it. Tidy that in .mcp.json so the server sees it clean.")
    return fixed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".mcp.json")
    ap.add_argument("--server", default="meta-ads")
    args = ap.parse_args()
    config_path = Path(args.config).expanduser()
    if not config_path.exists():
        print(f"FAIL: {config_path} not found. Run this from the workspace root after configure.py.")
        return 1
    data = json.loads(config_path.read_text(encoding="utf-8"))
    server = data.get("mcpServers", {}).get(args.server)
    if not server:
        print(f"FAIL: no '{args.server}' entry in {config_path}. Run configure.py first.")
        return 1
    env = server.get("env", {})
    app_id = clean(env.get("META_APP_ID"), "META_APP_ID")
    app_secret = clean(env.get("META_APP_SECRET"), "META_APP_SECRET")
    seed_token = clean(env.get("META_ACCESS_TOKEN"), "META_ACCESS_TOKEN")
    if not app_id.isdigit():
        print("FAIL: META_APP_ID should be a long number (from App settings > Basic). Check it in .mcp.json.")
        return 1

    cmd = Path(server.get("command", ""))
    print(f"{'OK' if cmd.exists() else 'FAIL'}: server Python at {cmd}")
    if not cmd.exists():
        print("      The .venv is missing. Redo the virtual environment step, then configure.py again.")
        return 1

    # Load the real server code with these credentials so its own token logic runs
    os.environ["META_APP_ID"] = app_id
    os.environ["META_APP_SECRET"] = app_secret
    os.environ["META_ACCESS_TOKEN"] = seed_token
    server_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(server_dir))
    t0 = time.time()
    try:
        import main
    except Exception as e:
        print(f"FAIL: the server code did not load: {e}")
        print("      Re-download main.py and reinstall requirements.txt, then run me again.")
        return 1
    secs = time.time() - t0
    print(f"OK: server warm-up finished in {secs:.0f}s" + (" (first run is slow; next start is fast)" if secs > 5 else ""))

    problems = 0
    base = main.BASE_URL

    # 1. Exchange a short-lived token for a long-lived one if possible (no-op for system user tokens)
    try:
        asyncio.run(main._maybe_refresh())
    except Exception as e:
        print(f"NOTE: token exchange step skipped ({e})")
    token = main._token()

    # 2. Inspect the token with the app's own credentials
    try:
        r = httpx.get(f"{base}/debug_token", params={"input_token": token,
                                                      "access_token": f"{app_id}|{app_secret}"}, timeout=30)
    except httpx.RequestError as e:
        print(f"FAIL: could not reach Meta: {e}. Check the internet connection and run me again.")
        return 1
    info = r.json().get("data", {}) if r.status_code < 400 else {}
    if r.status_code >= 400 or not info:
        err = r.json().get("error", {}).get("message", r.text[:200])
        print(f"FAIL: Meta rejected the App ID / App Secret pair: {err}")
        print("      Re-copy both from developers.facebook.com > your app > App settings > Basic (click Show on the secret).")
        return 1
    if not info.get("is_valid"):
        print(f"FAIL: the access token is not valid: {info.get('error', {}).get('message', 'expired or revoked')}")
        print("      Generate a fresh token (runbook Step 6) and paste it into .mcp.json again.")
        return 1
    ttype = info.get("type", "?")
    expires = info.get("expires_at", 0)
    if not expires:
        print(f"OK: token is valid ({ttype}) and never expires")
    else:
        days = round((expires - time.time()) / 86400)
        print(f"OK: token is valid ({ttype}), expires in {days} days; the server renews it every week while it is used")
        if days < 2:
            print("NOTE: that is a short-lived token and the exchange did not stick. Check the App Secret, then run me again.")
    scopes = info.get("scopes", [])
    missing = [s for s in NEEDED_SCOPES if s not in scopes]
    if missing:
        print(f"FAIL: token is missing required permissions: {', '.join(missing)}")
        print("      Generate the token again and tick ads_read AND ads_management.")
        problems += 1
    else:
        print(f"OK: permissions include {', '.join(NEEDED_SCOPES)}")
    nice_missing = [s for s in NICE_SCOPES if s not in scopes]
    if nice_missing:
        print(f"NOTE: optional permissions not present: {', '.join(nice_missing)} (page lookups may be limited)")

    # 3. Can this token see an ad account?
    try:
        r = httpx.get(f"{base}/me/adaccounts", params={"fields": "id,name,account_status",
                                                        "access_token": token}, timeout=30)
        accounts = r.json().get("data", []) if r.status_code < 400 else None
    except httpx.RequestError as e:
        print(f"FAIL: could not reach Meta for ad accounts: {e}")
        return 1
    if accounts is None:
        print(f"FAIL: ad account lookup failed: {r.json().get('error', {}).get('message', r.text[:200])}")
        problems += 1
    elif not accounts:
        print("FAIL: the token works but no ad account is attached to it.")
        print("      System user: Business Settings > Users > System users > Assign assets > Ad accounts > tick yours > Full control.")
        print("      Personal token: make sure you generated it while logged in as a user with access to the ad account.")
        problems += 1
    else:
        for a in accounts[:10]:
            status = ACCOUNT_STATUS.get(a.get("account_status"), str(a.get("account_status")))
            print(f"OK: ad account \"{a.get('name')}\" ({a.get('id')}) is {status}")
        if len(accounts) > 10:
            print(f"    ...and {len(accounts) - 10} more")

    print()
    if problems == 0:
        print("PREFLIGHT PASSED. Next: reload the VS Code window (Command Palette > Developer: Reload Window),")
        print("approve the project MCP server when asked, start a NEW conversation, and paste the box again.")
        return 0
    print("PREFLIGHT FAILED. Fix the FAIL lines above, save .mcp.json, and run me again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
