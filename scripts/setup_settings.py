"""Ensure ~/.claude/settings.json has required configuration."""

import json
from pathlib import Path


def ensure_attribution(settings_path: Path):
    if settings_path.exists():
        data = json.loads(settings_path.read_text())
    else:
        data = {}

    if data.get("attribution", {}).get("commit", "MISSING") == "MISSING":
        data.setdefault("attribution", {})["commit"] = ""
        settings_path.write_text(json.dumps(data, indent=2))
        print(f"Set attribution.commit in {settings_path}")
    else:
        print(f"attribution.commit already set in {settings_path}")


if __name__ == "__main__":
    settings_path = Path.home() / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    ensure_attribution(settings_path)
