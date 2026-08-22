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
        "model": "gpt-5.6-luna",
        "model_provider": "go-codex-proxy",
        "model_catalog_json": str(model_catalog_path),
        "model_context_window": 272000,
        "disable_response_storage": True,
        "suppress_unstable_features_warning": True,
        "model_providers": {
            "go-codex-proxy": {
                "name": "OpenCode Go via local go-codex-proxy",
                "base_url": f"http://127.0.0.1:{GODEX_PROXY_PORT}/v1",
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


MODEL_CATALOG_JSON = """{
  "models": [
    {
      "slug": "gpt-5.6-luna",
      "display_name": "GPT-5.6 Luna",
      "description": "OpenCode Go Responses-native model passed through go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "medium",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
        { "effort": "medium", "description": "Balanced reasoning" },
        { "effort": "high", "description": "More reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 100,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": true,
      "default_reasoning_summary": "auto",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 272000,
      "max_context_window": 272000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text", "image"],
      "supports_search_tool": true,
      "use_responses_lite": false
    },
    {
      "slug": "grok-4.5",
      "display_name": "Grok 4.5",
      "description": "OpenCode Go Responses-native model passed through go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
        { "effort": "high", "description": "Enhanced reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 99,
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
      "context_window": 256000,
      "max_context_window": 256000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text", "image"],
      "supports_search_tool": true,
      "use_responses_lite": false
    },
    {
      "slug": "glm-5.3",
      "display_name": "GLM-5.3",
      "description": "OpenCode Go GLM model converted to chat completions by go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "none", "description": "Disable explicit thinking" },
        { "effort": "high", "description": "Enhanced reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 90,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": true,
      "default_reasoning_summary": "auto",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 200000,
      "max_context_window": 200000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": false,
      "use_responses_lite": false
    },
    {
      "slug": "glm-5.2",
      "display_name": "GLM-5.2",
      "description": "OpenCode Go GLM model converted to chat completions by go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "none", "description": "Disable explicit thinking" },
        { "effort": "medium", "description": "Balanced reasoning" },
        { "effort": "high", "description": "More reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 89,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": true,
      "default_reasoning_summary": "auto",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 200000,
      "max_context_window": 200000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text", "image"],
      "supports_search_tool": false,
      "use_responses_lite": false
    },
    {
      "slug": "kimi-k3",
      "display_name": "Kimi K3",
      "description": "OpenCode Go Kimi model converted to chat completions by go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
        { "effort": "high", "description": "Enhanced reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 80,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": true,
      "default_reasoning_summary": "auto",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 256000,
      "max_context_window": 256000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": false,
      "use_responses_lite": false
    },
    {
      "slug": "deepseek-v4-flash",
      "display_name": "DeepSeek V4 Flash",
      "description": "OpenCode Go DeepSeek model converted to chat completions by go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
        { "effort": "high", "description": "Enhanced reasoning for coding tasks" }
      ],
      "shell_type": "shell_command",
      "visibility": "list",
      "supported_in_api": true,
      "priority": 70,
      "additional_speed_tiers": [],
      "service_tiers": [],
      "availability_nux": null,
      "upgrade": null,
      "supports_reasoning_summaries": true,
      "default_reasoning_summary": "auto",
      "support_verbosity": false,
      "default_verbosity": "medium",
      "apply_patch_tool_type": "freeform",
      "web_search_tool_type": "text_and_image",
      "truncation_policy": { "mode": "tokens", "limit": 10000 },
      "supports_parallel_tool_calls": true,
      "supports_image_detail_original": true,
      "context_window": 128000,
      "max_context_window": 128000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": false,
      "use_responses_lite": false
    },
    {
      "slug": "minimax-m3",
      "display_name": "MiniMax M3",
      "description": "OpenCode Go MiniMax model converted to Anthropic messages by go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "high",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
        { "effort": "high", "description": "Enhanced reasoning for coding tasks" }
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
      "context_window": 200000,
      "max_context_window": 200000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": false,
      "use_responses_lite": false
    },
    {
      "slug": "qwen3.7-plus",
      "display_name": "Qwen3.7 Plus",
      "description": "OpenCode Go Qwen model converted to Anthropic messages by go-codex-proxy.",
      "base_instructions": "You are Codex, a coding agent. Be concise, precise, and useful.",
      "default_reasoning_level": "medium",
      "supported_reasoning_levels": [
        { "effort": "low", "description": "Lightweight reasoning" },
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
      "context_window": 256000,
      "max_context_window": 256000,
      "effective_context_window_percent": 95,
      "experimental_supported_tools": [],
      "input_modalities": ["text"],
      "supports_search_tool": false,
      "use_responses_lite": false
    }
  ]
}
"""


PROXY_CONFIG_JSON = f"""{{
  "server": {{
    "host": "127.0.0.1",
    "port": {GODEX_PROXY_PORT},
    "log_level": "INFO"
  }},
  "upstream": {{
    "base_url": "{GO_BASE_URL}",
    "api_key_env": "OPENCODE_GO_API_KEY",
    "api_key": null
  }},
  "anthropic": {{
    "default_max_tokens": 16384
  }},
  "routing": {{
    "model_routes": {{}}
  }},
  "models": {{
    "served": []
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
        print(f"Warning: could not discover OpenCode Go models ({exc}); using the built-in catalog.")
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

    for priority, slug in enumerate(discovered_models, start=200):
        if not slug or slug in existing:
            continue
        model = json.loads(json.dumps(template))
        model.update(
            {
                "slug": slug,
                "display_name": slug.upper(),
                "description": "OpenCode Go model discovered from the account models endpoint.",
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
    catalog = json.loads(MODEL_CATALOG_JSON)
    augment_catalog(catalog, discover_go_models(api_key))
    for model in catalog.get("models", []):
        model["model_messages"] = json.loads(model_messages_json)
    model_catalog_path.write_text(json.dumps(catalog, indent=2))

    print(f"  Configured godex profile at {godex_dir}")


if __name__ == "__main__":
    main()
