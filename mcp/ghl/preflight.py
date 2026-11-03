#!/usr/bin/env python3
"""
preflight.py for the GoHighLevel connection (Team True North).

Proves the credentials in .mcp.json work against the live GHL API BEFORE the
restart, so nobody restarts into a broken connection. Also warms up the
server so its first real start is fast. Never prints the token.

Run from the workspace root with the server's own Python:
    <venv python> .claude/mcp-servers/ghl/preflight.py
Optional: --config PATH   (defaults to ./.mcp.json)
"""
import argparse
import json
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("ERROR: run this with the server's own Python (the one inside .venv), not the system Python.")
    sys.exit(1)

SERVER_NAME = "ghl"
BASE = "https://services.leadconnectorhq.com"
PLACEHOLDERS = {"PASTE_YOUR_PRIVATE_INTEGRATION_TOKEN_HERE", "PASTE_YOUR_LOCATION_ID_HERE"}


def load_env(config_path: Path) -> dict:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    server = data.get("mcpServers", {}).get(SERVER_NAME)
    if not server:
        print(f"FAIL: no '{SERVER_NAME}' entry in {config_path}. Run configure.py first.")
        sys.exit(1)
    return server.get("env", {}), server


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


def call(path: str, token: str, params: dict | None = None) -> tuple[int, dict | str]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) TTN-preflight",
    }
    try:
        r = httpx.get(f"{BASE}{path}", headers=headers, params=params or {}, timeout=30)
    except httpx.RequestError as e:
        return 0, f"network error: {e}"
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, r.text[:200]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=".mcp.json")
    args = ap.parse_args()
    config_path = Path(args.config).expanduser()
    if not config_path.exists():
        print(f"FAIL: {config_path} not found. Run this from the workspace root after configure.py.")
        return 1

    env, server = load_env(config_path)
    token = clean(env.get("GHL_PRIVATE_TOKEN"), "GHL_PRIVATE_TOKEN")
    loc = clean(env.get("GHL_LOCATION_ID"), "GHL_LOCATION_ID")

    cmd = Path(server.get("command", ""))
    print(f"{'OK' if cmd.exists() else 'FAIL'}: server Python at {cmd}")
    if not cmd.exists():
        print("      The .venv is missing. Redo the virtual environment step, then configure.py again.")
        return 1

    problems = 0

    # 1. Does this token open this sub-account?
    status, body = call(f"/locations/{loc}", token)
    if status == 200 and isinstance(body, dict):
        name = body.get("location", {}).get("name", "(name not returned)")
        print(f"OK: connected to sub-account \"{name}\" (Location ID ends in ...{loc[-4:]})")
    elif status == 401:
        print("FAIL: GHL rejected the token (401). It was copied wrong, or it was created at the agency level")
        print("      instead of inside the sub-account. Make a fresh Private Integration INSIDE the sub-account and paste again.")
        problems += 1
    elif status == 403:
        print("FAIL: the token works but cannot open this Location ID (403). Either the token belongs to a different")
        print("      sub-account, or the 'locations' read scope was not selected. Easiest fix: recreate the Private")
        print("      Integration with ALL scopes selected, inside the same sub-account as the Location ID.")
        problems += 1
    elif status == 404:
        print("FAIL: GHL has no sub-account with that Location ID (404). Re-copy the ID from the browser address bar")
        print("      while inside the sub-account: the part right after /location/ in the URL.")
        problems += 1
    elif status == 0:
        print(f"FAIL: could not reach GHL. {body}")
        print("      Check the internet connection and run me again.")
        return 1
    else:
        print(f"FAIL: unexpected answer from GHL (HTTP {status}): {str(body)[:200]}")
        problems += 1

    # 2. Scope spot-checks (each one maps to a scope the person ticks in GHL)
    checks = [
        ("Contacts", f"/contacts/", {"locationId": loc, "limit": 1}),
        ("Pipelines", f"/opportunities/pipelines", {"locationId": loc}),
        ("Calendars", f"/calendars/", {"locationId": loc}),
        ("Workflows", f"/workflows/", {"locationId": loc}),
        ("Tags", f"/locations/{loc}/tags", None),
        ("Email templates", f"/emails/builder", {"locationId": loc, "limit": 1}),
    ]
    missing = []
    for label, path, params in checks:
        s, _ = call(path, token, params)
        if s == 200:
            print(f"OK: {label} readable")
        elif s in (401, 403):
            print(f"MISSING SCOPE: {label} (HTTP {s})")
            missing.append(label)
        else:
            print(f"NOTE: {label} returned HTTP {s} (not a credentials problem; moving on)")
    if missing:
        print("      Fix: GHL sub-account > Settings > Private Integrations > your integration > edit scopes,")
        print("      tick everything, save. The same token keeps working after a scope edit.")

    # 3. Warm up the server so the first real start is quick
    server_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(server_dir))
    t0 = time.time()
    try:
        import main  # noqa: F401
        secs = time.time() - t0
        print(f"OK: server warm-up finished in {secs:.0f}s" + (" (first run is slow; next start is fast)" if secs > 5 else ""))
    except Exception as e:  # pragma: no cover
        print(f"FAIL: the server code did not load: {e}")
        print("      Re-download main.py and reinstall requirements.txt, then run me again.")
        problems += 1

    print()
    if problems == 0:
        print("PREFLIGHT PASSED. Next: reload the VS Code window (Command Palette > Developer: Reload Window),")
        print("approve the project MCP server when asked, start a NEW conversation, and paste the box again.")
        return 0
    print("PREFLIGHT FAILED. Fix the FAIL lines above, save .mcp.json, and run me again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
