"""PreToolUse hook: block destructive commands unless explicitly confirmed."""

import json
import sys

# Each entry: (pattern to match, human-readable description)
DESTRUCTIVE_PATTERNS = [
    ("gh repo delete", "GitHub repo deletion"),
    ("rm -rf /", "recursive delete from root"),
    ("DROP DATABASE", "database deletion"),
    ("DROP TABLE", "table deletion"),
    ("git push --force", "force push"),
    ("git push -f", "force push"),
    ("terraform apply", "Terraform apply"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return

    command = data.get("tool_input", {}).get("command", "")

    for pattern, description in DESTRUCTIVE_PATTERNS:
        if pattern in command:
            json.dump(
                {
                    "decision": "block",
                    "reason": f"Blocked: {description} detected (`{pattern}`). If you really want to do this, explicitly confirm.",
                },
                sys.stdout,
            )
            return


if __name__ == "__main__":
    main()
