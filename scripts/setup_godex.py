"""Configure the 'godex' profile: Codex routed to OpenCode Go under ~/.godex.

The profile config is the default ``~/.codex/config.toml`` with only
routing-related keys overridden, so settings you enable/disable in the main
Codex config propagate here. Re-run with ``--sync-config`` (or relaunch
`godex`, which does it automatically) after editing the default config.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _codex_profile_merge import build_profile_toml


GODEX_PROXY_PORT = 18766
GO_BASE_URL = "https://opencode.ai/zen/go/v1"
GO_MODELS_URL = GO_BASE_URL + "/models"
GO_AUTH_URL = "https://opencode.ai/auth"


def godex_overrides(model_catalog_path: Path) -> dict:
    """Routing-only overrides layered on top of the default Codex config."""
    return {
        "model": "muse-spark-1.3-contributor",
        "model_provider": "go-codex-proxy",
        "model_catalog_json": str(model_catalog_path),
        "model_context_window": 272000,
        "disable_response_storage": True,
        "suppress_unstable_features_warning": True,
        # Subagent support requires multi-agent v2 regardless of the base
        # config; everything else under [features] still inherits from it.
        "features": {
            "multi_agent_v2": {
                "enabled": True,
                "max_concurrent_threads_per_session": 16,
            }
        },
        "model_providers": {
            "go-codex-proxy": {
                "name": "OpenCode Go via local codex-proxy",
                "base_url": f"http://127.0.0.1:{GODEX_PROXY_PORT}/go/v1",
                "wire_api": "responses",
                "requires_openai_auth": False,
            }
        },
    }


def write_profile_config(model_catalog_path: Path) -> Path:
    """Regenerate ~/.godex/config.toml from the default Codex config."""
    text, _base = build_profile_toml(
        godex_overrides(model_catalog_path),
        profile_name="godex",
        sync_command="scripts/setup_godex.py --sync-config",
        # The base config's reasoning effort may be invalid for the routed
        # model catalog; let per-model defaults apply instead.
        drop_keys=("model_reasoning_effort",),
    )
    config_path = Path.home() / ".godex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(text)
    return config_path


# One generic entry per discovered model. The proxy owns all wire-format
# knowledge; the Codex catalog carries no per-model hardcoding, so models the
# upstream retires simply disappear from the picker.
CATALOG_TEMPLATE = {
    "display_name": "",
    "description": "OpenCode Go model routed through the local proxy.",
    "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
    "default_reasoning_level": "high",
    "supported_reasoning_levels": [
        {"effort": "none", "description": "Disable explicit thinking budget"},
        {"effort": "low", "description": "Lightweight reasoning"},
        {"effort": "medium", "description": "Balanced reasoning"},
        {"effort": "high", "description": "More reasoning for coding tasks"},
    ],
    "shell_type": "shell_command",
    "visibility": "list",
    "supported_in_api": True,
    "priority": 0,
    "additional_speed_tiers": [],
    "service_tiers": [],
    "availability_nux": None,
    "upgrade": None,
    "supports_reasoning_summaries": False,
    "default_reasoning_summary": "none",
    "support_verbosity": False,
    "default_verbosity": "medium",
    "apply_patch_tool_type": "freeform",
    "web_search_tool_type": "text_and_image",
    "truncation_policy": {"mode": "tokens", "limit": 10000},
    "supports_parallel_tool_calls": True,
    "supports_image_detail_original": True,
    "context_window": 200000,
    "max_context_window": 200000,
    "effective_context_window_percent": 95,
    "experimental_supported_tools": [],
    "input_modalities": ["text"],
    "supports_search_tool": True,
    "use_responses_lite": False,
}


def build_catalog(discovered_models: list[str]) -> dict:
    """Build the Codex model catalog purely from the live Go model list."""
    models = []
    for priority, slug in enumerate(discovered_models, start=100):
        entry = json.loads(json.dumps(CATALOG_TEMPLATE))
        entry.update({"slug": slug, "display_name": slug, "priority": priority})
        models.append(entry)
    return {"models": models}


PROXY_CONFIG_JSON = f"""{{
  "server": {{
    "host": "127.0.0.1",
    "port": {GODEX_PROXY_PORT}
  }},
  "models": {{
    "served": []
  }},
  "routing": {{
    "model_routes": {{}}
  }},
  "accounts": [],
  "access": {{
    "require_key": false,
    "keys": []
  }},
  "reasoning": {{
    "default_effort": "high",
    "effort_levels": {{
      "none": {{ "budget": 0, "level": "LOW" }},
      "medium": {{ "budget": 16384, "level": "MEDIUM" }},
      "high": {{ "budget": 32768, "level": "HIGH" }}
    }}
  }},
  "timeouts": {{
    "connect_seconds": 10,
    "read_seconds": 600
  }},
  "compaction": {{
    "temperature": 0.1,
    "preferred_targets": []
  }},
  "retry": {{
    "enabled": true,
    "max_attempts": 5,
    "initial_delay_ms": 1000,
    "max_delay_ms": 60000,
    "backoff_multiplier": 2.0
  }},
  "providers": {{
    "go": {{
      "base_url": "{GO_BASE_URL}",
      "api_key_env": "OPENCODE_GO_API_KEY",
      "api_key": null
    }}
  }}
}}
"""


def extract_model_messages() -> str:
    """Extract model_messages from the real ~/.codex model catalog.

    Codex registers apply_patch and other built-in tools only when the model
    catalog entry contains a ``model_messages.instructions_template``. The real
    Codex catalog (populated by ``codex debug models``) has this, but we must
    copy it into the OpenCode Go catalog so Codex treats routed models the
    same way.

    Returns a JSON string suitable for embedding as the ``model_messages`` value.
    Aborts with a clear error if the catalog is unavailable.
    """
    codex_home = str(Path.home() / ".codex")
    try:
        result = subprocess.run(
            ["codex", "debug", "models"],
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "CODEX_HOME": codex_home},
        )
    except FileNotFoundError:
        sys.exit(
            "Error: 'codex' not found. The godex profile requires the real "
            "Codex CLI to be installed so its model catalog (including "
            "instructions_template for apply_patch) can be extracted."
        )
    if result.returncode != 0:
        sys.exit(
            f"Error: 'codex debug models' failed (exit {result.returncode}).\n"
            f"stderr: {result.stderr.strip()}"
        )
    try:
        catalog = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: could not parse 'codex debug models' output as JSON: {exc}")

    # Find a model that has model_messages (prefer gpt-5.5, then any)
    models = catalog.get("models", [])
    model_messages = None
    for model in models:
        if model.get("slug") == "gpt-5.5" and model.get("model_messages"):
            model_messages = model["model_messages"]
            break
    if model_messages is None:
        for model in models:
            if model.get("model_messages"):
                model_messages = model["model_messages"]
                break

    if model_messages is None:
        sys.exit(
            "Error: no model with 'model_messages' found in the real Codex "
            "catalog (~/.codex). The godex profile needs the "
            "instructions_template from a real Codex model so apply_patch and "
            "other built-in tools are registered. Make sure Codex is logged in "
            "and has fetched its model catalog (run 'codex' interactively once)."
        )

    return json.dumps(model_messages)


def discover_go_models(api_key: str) -> list[str]:
    """Return model slugs from the OpenCode Go models endpoint."""
    request = Request(
        GO_MODELS_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            # Cloudflare rejects requests without a browser-ish user agent.
            "User-Agent": "godex-setup/0.1 (curl-compatible)",
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (HTTPError, TimeoutError, URLError, json.JSONDecodeError) as exc:
        print(f"Warning: could not discover OpenCode Go models ({exc}); leaving the catalog empty.")
        return []

    models = payload.get("data", [])
    if not isinstance(models, list):
        return []
    return [
        model_id
        for model in models
        if isinstance(model, dict)
        and isinstance(model.get("id"), str)
        and (model_id := model["id"].strip())
    ]


def prompt_api_key() -> str:
    print(f"  Subscribe to OpenCode Go and copy your API key at: {GO_AUTH_URL}")
    key = getpass.getpass("  Enter your OpenCode Go API key: ").strip()
    if not key:
        print("Error: no OpenCode Go API key provided. Aborting; no changes made.")
        sys.exit(1)
    return key


def write_private_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    os.chmod(path, 0o600)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--key",
        help="OpenCode Go API key (omit to prompt interactively)",
    )
    parser.add_argument(
        "--sync-config",
        action="store_true",
        help="only regenerate config.toml from the default Codex config; "
        "no prompts and no API key needed",
    )
    args = parser.parse_args()

    godex_dir = Path.home() / ".godex"
    godex_dir.mkdir(parents=True, exist_ok=True)

    env_path = godex_dir / "go.env"
    proxy_config_path = godex_dir / "go-codex-proxy" / "config.json"
    model_catalog_path = godex_dir / "model-catalogs" / "opencode-go.json"

    if args.sync_config:
        config_path = write_profile_config(model_catalog_path)
        print(f"  Synced {config_path} from the default Codex config")
        return

    api_key = args.key or prompt_api_key()

    model_messages_json = extract_model_messages()

    config_path = write_profile_config(model_catalog_path)
    write_private_file(env_path, f"GO_API_KEY={shlex.quote(api_key)}\n")
    proxy_config_path.parent.mkdir(parents=True, exist_ok=True)
    proxy_config_path.write_text(PROXY_CONFIG_JSON)
    model_catalog_path.parent.mkdir(parents=True, exist_ok=True)
    discovered = discover_go_models(api_key)
    if not discovered:
        sys.exit(
            "Error: could not discover OpenCode Go models; the catalog is "
            "discovery-only (no built-in fallback). Check network/API key."
        )
    catalog = build_catalog(discovered)
    for model in catalog.get("models", []):
        model["model_messages"] = json.loads(model_messages_json)
    model_catalog_path.write_text(json.dumps(catalog, indent=2))

    print(f"  Configured godex profile at {godex_dir}")


if __name__ == "__main__":
    main()
