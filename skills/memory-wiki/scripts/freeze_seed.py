#!/usr/bin/env python3
"""Freeze a completed seed by recording its checksum in the project manifest."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from datetime import datetime
from pathlib import Path


PLACEHOLDERS = ("<!--", "Replace with a verifiable criterion.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()
    root = args.project_dir.resolve()
    manifest_path = root / "project.yaml"
    seed_path = root / "seed.md"

    if not manifest_path.is_file() or not seed_path.is_file():
        print("error: project.yaml and seed.md are required", file=sys.stderr)
        return 2

    seed = seed_path.read_text(encoding="utf-8")
    if any(marker in seed for marker in PLACEHOLDERS):
        print("error: seed still contains template placeholders", file=sys.stderr)
        return 2

    manifest = manifest_path.read_text(encoding="utf-8")
    hash_match = re.search(r"(?m)^seed_sha256:[ \t]*(.*)$", manifest)
    if not hash_match:
        print("error: project.yaml has no seed_sha256 field", file=sys.stderr)
        return 2
    if hash_match.group(1).strip():
        print("error: seed is already frozen", file=sys.stderr)
        return 2

    digest = hashlib.sha256(seed_path.read_bytes()).hexdigest()
    manifest = re.sub(r"(?m)^seed_sha256:[ \t]*$", f"seed_sha256: {digest}", manifest)
    manifest = re.sub(r"(?m)^status:[ \t]*seed[ \t]*$", "status: scoped", manifest)
    manifest_path.write_text(manifest, encoding="utf-8")

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with (root / "log.md").open("a", encoding="utf-8") as log:
        log.write(f"{timestamp} | scope | froze seed | sha256:{digest}\n")

    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
