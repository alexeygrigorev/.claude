"""Shared logic: build isolated Codex profile configs from the default one.

Both routed profiles (zodex -> Z.AI, godex -> OpenCode Go) want the user's
main ``~/.codex/config.toml`` as their base, with only routing-related keys
overridden. That way anything the user enables/disables in the default Codex
config propagates to the routed profiles instead of being silently reset by a
static template.
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path


BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def load_base_config() -> tuple[dict, Path]:
    """Parse the default Codex config; empty dict when missing/unreadable."""
    base_path = Path.home() / ".codex" / "config.toml"
    if base_path.exists():
        try:
            return tomllib.loads(base_path.read_text()), base_path
        except tomllib.TOMLDecodeError as exc:
            print(
                f"Warning: cannot parse {base_path} ({exc}); "
                "generating profile without a base.",
                file=sys.stderr,
            )
    return {}, base_path


def deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge `overrides` into a copy of `base` (overrides win)."""
    merged = dict(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def format_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):  # bool is a subclass of int; handled above
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value)
    raise TypeError(f"unsupported scalar type: {type(value).__name__}")


def _key(key: str) -> str:
    return key if BARE_KEY_RE.fullmatch(key) else json.dumps(key)


def _classify(node: dict) -> tuple[list, list, list]:
    scalars: list = []
    sub_tables: list = []
    table_arrays: list = []

    for key, value in node.items():
        if isinstance(value, dict):
            if value:  # skip empty tables entirely
                sub_tables.append((key, value))
        elif (
            isinstance(value, list)
            and value
            and all(isinstance(item, dict) for item in value)
        ):
            table_arrays.append((key, value))
        else:
            scalars.append((key, value))

    return scalars, sub_tables, table_arrays


def _emit_table(lines: list[str], prefix: tuple[str, ...], node: dict) -> None:
    scalars, sub_tables, table_arrays = _classify(node)

    # Emit the header only when the table owns scalar content; pure containers
    # are implied by their children's dotted headers ([a.b] needs no [a]).
    if prefix and scalars:
        lines.append("")
        lines.append("[" + ".".join(_key(part) for part in prefix) + "]")

    for key, value in scalars:
        lines.append(f"{_key(key)} = {_format_inline(value)}")

    for key, child in sub_tables:
        _emit_table(lines, (*prefix, key), child)

    for key, items in table_arrays:
        for item in items:
            lines.append("")
            lines.append(
                "[[" + ".".join(_key(part) for part in (*prefix, key)) + "]]"
            )
            inner_scalars, _, _ = _classify(item)
            for ikey, ivalue in inner_scalars:
                lines.append(f"{_key(ikey)} = {_format_inline(ivalue)}")


def _format_inline(value: object) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_format_inline(item) for item in value) + "]"
    return format_value(value)


def dump_toml(document: dict) -> str:
    lines: list[str] = []
    _emit_table(lines, (), document)
    return "\n".join(lines).rstrip() + "\n"


def build_profile_toml(
    overrides: dict,
    *,
    profile_name: str,
    sync_command: str,
    drop_keys: tuple[str, ...] = (),
) -> tuple[str, Path]:
    """Return (toml_text, base_path) for a routed profile.

    Base is the live ``~/.codex/config.toml``; only ``overrides`` (deeply
    merged) differ. Keys named in ``drop_keys`` are removed afterwards — used
    for defaults like ``model_reasoning_effort`` that may be invalid for the
    routed profile's model catalog and should fall back to per-model defaults.
    """
    base, base_path = load_base_config()
    document = deep_merge(base, overrides)
    for key in drop_keys:
        document.pop(key, None)

    header = (
        f"# AUTO-GENERATED {profile_name} profile — do not edit by hand.\n"
        f"# Base: {base_path} (merged at generation time; re-run\n"
        f"# `{sync_command}` after changing the default Codex config).\n"
    )
    return header + dump_toml(document), base_path
