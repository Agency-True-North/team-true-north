#!/usr/bin/env python3
"""
configure.py for the GoHighLevel connection (Team True North).

Registers the GHL MCP server in the workspace's .mcp.json with placeholder
credentials, so the person can paste their token into the FILE instead of
the chat. Safe to run again: values already filled in are kept.

Run it from the workspace root (the folder that holds CLAUDE.md):
    <venv python> .claude/mcp-servers/ghl/configure.py
"""
import json
import os
import sys
from pathlib import Path

SERVER_NAME = "ghl"
TOKEN_PLACEHOLDER = "PASTE_YOUR_PRIVATE_INTEGRATION_TOKEN_HERE"
LOCATION_PLACEHOLDER = "PASTE_YOUR_LOCATION_ID_HERE"
GITIGNORE_LINES = [
    ".mcp.json",
    ".claude/mcp-servers/*/.venv/",
    ".claude/mcp-servers/*/.token.json",
    ".claude/mcp-servers/*/__pycache__/",
]


def venv_python(server_dir: Path) -> Path:
    if os.name == "nt":
        return server_dir / ".venv" / "Scripts" / "python.exe"
    return server_dir / ".venv" / "bin" / "python"


def main() -> int:
    server_dir = Path(__file__).resolve().parent
    workspace = Path.cwd().resolve()
    config_path = workspace / ".mcp.json"

    if not (workspace / "CLAUDE.md").exists():
        print("WARNING: no CLAUDE.md in this folder. Make sure you ran this from the")
        print(f"workspace root. Current folder: {workspace}")
        print("If this is wrong, press Ctrl+C now and re-run from the Claude folder.")

    py = venv_python(server_dir)
    if not py.exists():
        print(f"ERROR: the server's Python environment is missing at {py}")
        print("Create the virtual environment and install requirements first (runbook Step 3).")
        return 1

    existing = {}
    if config_path.exists():
        try:
            existing = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup = config_path.with_suffix(".json.broken")
            config_path.rename(backup)
            print(f"WARNING: .mcp.json was not valid JSON. Moved it to {backup.name} and starting fresh.")
            existing = {}
    servers = existing.setdefault("mcpServers", {})
    old_env = servers.get(SERVER_NAME, {}).get("env", {}) if isinstance(servers.get(SERVER_NAME), dict) else {}

    def keep(key: str, placeholder: str) -> str:
        value = (old_env.get(key) or "").strip()
        return value if value and value != placeholder else placeholder

    servers[SERVER_NAME] = {
        "command": str(py),
        "args": [str(server_dir / "main.py")],
        "env": {
            "GHL_PRIVATE_TOKEN": keep("GHL_PRIVATE_TOKEN", TOKEN_PLACEHOLDER),
            "GHL_LOCATION_ID": keep("GHL_LOCATION_ID", LOCATION_PLACEHOLDER),
        },
    }
    config_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")

    gitignore = workspace / ".gitignore"
    current = gitignore.read_text(encoding="utf-8").splitlines() if gitignore.exists() else []
    missing = [line for line in GITIGNORE_LINES if line not in current]
    if missing:
        with gitignore.open("a", encoding="utf-8") as fh:
            if current and current[-1].strip():
                fh.write("\n")
            fh.write("# Claude connections: never back these up online\n")
            fh.write("\n".join(missing) + "\n")

    env = servers[SERVER_NAME]["env"]
    needs = [k for k, v in env.items() if v in (TOKEN_PLACEHOLDER, LOCATION_PLACEHOLDER)]
    print(f"OK: wrote {config_path}")
    print(f"OK: server command points at {py}")
    if needs:
        print("STILL NEEDED in .mcp.json: " + ", ".join(needs))
    else:
        print("OK: both GHL values are filled in. Next: run preflight.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
