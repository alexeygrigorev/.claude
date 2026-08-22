"""Configure the 'zodex' profile: Codex routed to Z.AI under ~/.zodex.

The profile config is the default ``~/.codex/config.toml`` with only
routing-related keys overridden, so settings you enable/disable in the main
Codex config propagate here. Re-run with ``--sync-config`` (or relaunch
`zodex`, which does it automatically) after editing the default config.
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


ZODEX_PROXY_PORT = 18765
ZAI_CODING_CHAT_URL = "https://api.z.ai/api/coding/paas/v4/chat/completions"
ZAI_API_KEY_URL = "https://z.ai/manage-apikey/apikey-list"


def zodex_overrides(model_catalog_path: Path) -> dict:
    """Routing-only overrides layered on top of the default Codex config."""
    return {
        "model": "glm-5.3",
        "model_provider": "codex-proxy",
        "model_catalog_json": str(model_catalog_path),
        "model_context_window": 1000000,
        "disable_response_storage": True,
        "personality": "pragmatic",
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
            "codex-proxy": {
                "name": "Z.AI via local codex-proxy",
                "base_url": f"http://127.0.0.1:{ZODEX_PROXY_PORT}/v1",
                "wire_api": "responses",
                "requires_openai_auth": False,
            }
        },
    }


def write_profile_config(model_catalog_path: Path) -> Path:
    """Regenerate ~/.zodex/config.toml from the default Codex config."""
    text, _base = build_profile_toml(
        zodex_overrides(model_catalog_path),
        profile_name="zodex",
        sync_command="scripts/setup_zodex.py --sync-config",
        # The base config's reasoning effort may be invalid for the routed
        # model catalog; let per-model defaults apply instead.
        drop_keys=("model_reasoning_effort",),
    )
    config_path = Path.home() / ".zodex" / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(text)
    return config_path


MODEL_CATALOG_JSON = """{
  "models": [
    {
      "slug": "glm-5.2",
      "display_name": "GLM-5.2",
      "description": "Z.AI GLM coding model routed through local codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "none", "description": "Disable explicit thinking budget" },
        { "effort": "medium", "description": "Balanced reasoning" },
        { "effort": "high", "description": "More reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 50,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": false,
      "default_reasoning_summary": "none",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 1000000,
      "max_context_window": 1000000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text", "image"],
      "supports_search_tool": true,
      "use_responses_lite": false
    },
    {
      "slug": "glm-5.3",
      "display_name": "GLM-5.3",
      "description": "Z.AI GLM coding model routed through local codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "max",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
        { "effort": "high", "description": "Enhanced reasoning for coding tasks" },
        { "effort": "max", "description": "Deep reasoning for complex tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 60,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": false,
      "default_reasoning_summary": "none",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 1000000,
      "max_context_window": 1000000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": true,
      "use_responses_lite": false
    },
    {
      "slug": "glm-5-turbo",
      "display_name": "GLM-5-Turbo",
      "description": "Z.AI faster GLM model routed through local codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "medium",
      "supported_reasoning_levels": [
        { "effort": "none", "description": "Disable explicit thinking budget" },
        { "effort": "medium", "description": "Balanced reasoning" },
        { "effort": "high", "description": "More reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 51,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": false,
      "default_reasoning_summary": "none",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 1000000,
      "max_context_window": 1000000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text", "image"],
      "supports_search_tool": true,
      "use_responses_lite": false
    }
  ]
}
"""


PROXY_CONFIG_JSON = f"""{{
  "server": {{
    "host": "127.0.0.1",
    "port": {ZODEX_PROXY_PORT},
    "log_level": "INFO"
  }},
  "zai": {{
    "api_url": "{ZAI_CODING_CHAT_URL}",
    "models": []
  }},
  "models": {{
    "served": []
  }},
  "routing": {{
    "model_routes": {{
      "*": ["proxy:glm-5.2"],
      "glm-5.2": [
        {{
          "type": "physical",
          "model": "glm-5.2",
          "reasoning": {{ "effort": "high" }}
        }}
      ],
      "glm-5-turbo": [
        {{
          "type": "physical",
          "model": "glm-5-turbo",
          "reasoning": {{ "effort": "medium" }}
        }}
      ],
      "compact-default": [
        {{
          "type": "physical",
          "model": "glm-5-turbo",
          "reasoning": {{ "effort": "none" }}
        }}
      ]
    }}
  }},
  "health": {{
    "auth_failure_immediate_unhealthy": true,
    "failure_threshold": 3,
    "cooldown_seconds": 60
  }},
  "access": {{
    "require_key": false,
    "keys": []
  }},
  "auto_compaction": {{
    "enabled": true,
    "max_attempts_per_request": 1,
    "tail_items_to_keep": 8
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
    "preferred_targets": ["compact-default"]
  }},
  "retry": {{
    "enabled": true,
    "max_attempts": 5,
    "initial_delay_ms": 1000,
    "max_delay_ms": 60000,
    "backoff_multiplier": 2.0
  }}
}}
"""

ZAI_MODELS_URL = ZAI_CODING_CHAT_URL.removesuffix("/chat/completions") + "/models"


def extract_model_messages() -> str:
    """Extract model_messages from the real ~/.codex model catalog.

    Codex registers apply_patch and other built-in tools only when the model
    catalog entry contains a ``model_messages.instructions_template``. The real
    Codex catalog (populated by ``codex debug models``) has this, but we must
    copy it into the Z.AI catalog so Codex treats GLM models the same way.

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
            "Error: 'codex' not found. The zodex profile requires the real "
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
            "catalog (~/.codex). The zodex profile needs the "
            "instructions_template from a real Codex model so apply_patch and "
            "other built-in tools are registered. Make sure Codex is logged in "
            "and has fetched its model catalog (run 'codex' interactively once)."
        )

    return json.dumps(model_messages)


def discover_zai_models(api_key: str) -> list[str]:
    """Return model slugs from the account-scoped Z.AI models endpoint."""
    request = Request(ZAI_MODELS_URL, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except (HTTPError, TimeoutError, URLError, json.JSONDecodeError) as exc:
        print(f"Warning: could not discover Z.AI models ({exc}); using the built-in catalog.")
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


def augment_catalog(catalog: dict, discovered_models: list[str]) -> None:
    """Add API models that Codex does not know while preserving existing entries."""
    models = catalog.setdefault("models", [])
    existing = {model["slug"] for model in models}
    template = next((model for model in models if model.get("slug") == "glm-5.2"), models[0])

    for priority, slug in enumerate(discovered_models, start=100):
        if not slug or slug in existing:
            continue
        model = json.loads(json.dumps(template))
        model.update(
            {
                "slug": slug,
                "display_name": slug.upper(),
                "description": "Z.AI model discovered from the account models endpoint.",
                "default_reasoning_level": "high",
                "supported_reasoning_levels": [
                    {"effort": "low", "description": "Lightweight reasoning"},
                    {"effort": "medium", "description": "Balanced reasoning"},
                    {"effort": "high", "description": "More reasoning for coding tasks"},
                ],
                "priority": priority,
                "input_modalities": ["text"],
            }
        )
        models.append(model)
        existing.add(slug)


def read_zlaude_key() -> str:
    settings_path = Path.home() / ".zlaude" / "settings.json"
    if not settings_path.exists():
        return ""
    try:
        data = json.loads(settings_path.read_text())
    except json.JSONDecodeError:
        return ""
    env = data.get("env", {})
    if not isinstance(env, dict):
        return ""
    key = env.get("ANTHROPIC_AUTH_TOKEN", "")
    return key.strip() if isinstance(key, str) else ""


def prompt_api_key(reuse_zlaude_key: bool) -> str:
    zlaude_key = read_zlaude_key()
    if reuse_zlaude_key and zlaude_key:
        return zlaude_key

    if zlaude_key:
        answer = input("  Reuse Z.AI key from ~/.zlaude/settings.json? [Y/n]: ").strip().lower()
        if answer in {"", "y", "yes"}:
            return zlaude_key

    print(f"  Get a Z.AI API key at: {ZAI_API_KEY_URL}")
    key = getpass.getpass("  Enter your Z.AI API key: ").strip()
    if not key:
        print("Error: no Z.AI API key provided. Aborting; no changes made.")
        sys.exit(1)
    return key


def write_private_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    os.chmod(path, 0o600)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reuse-zlaude-key",
        action="store_true",
        help="reuse ~/.zlaude/settings.json's Z.AI key without prompting",
    )
    parser.add_argument(
        "--sync-config",
        action="store_true",
        help="only regenerate config.toml from the default Codex config; "
        "no prompts and no API key needed",
    )
    args = parser.parse_args()

    zodex_dir = Path.home() / ".zodex"
    zodex_dir.mkdir(parents=True, exist_ok=True)

    env_path = zodex_dir / "zai.env"
    proxy_config_path = zodex_dir / "codex-proxy" / "config.json"
    model_catalog_path = zodex_dir / "model-catalogs" / "zai.json"

    if args.sync_config:
        config_path = write_profile_config(model_catalog_path)
        print(f"  Synced {config_path} from the default Codex config")
        return

    api_key = prompt_api_key(args.reuse_zlaude_key)

    model_messages_json = extract_model_messages()

    config_path = write_profile_config(model_catalog_path)
    write_private_file(env_path, f"ZAI_API_KEY={shlex.quote(api_key)}\n")
    proxy_config_path.parent.mkdir(parents=True, exist_ok=True)
    proxy_config_path.write_text(PROXY_CONFIG_JSON)
    model_catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(MODEL_CATALOG_JSON)
    augment_catalog(catalog, discover_zai_models(api_key))
    for model in catalog.get("models", []):
        model["model_messages"] = json.loads(model_messages_json)
    model_catalog_path.write_text(json.dumps(catalog, indent=2))

    print(f"  Configured zodex profile at {zodex_dir}")


if __name__ == "__main__":
    main()
