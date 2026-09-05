#!/usr/bin/env python3
"""Advance a memory-wiki project through guarded workflow states."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


TRANSITIONS = {
    "scoped": {"researching"},
    "researching": {"distilled"},
    "distilled": {"researching", "critiqued"},
    "critiqued": {"distilled", "ready"},
    "ready": {"distilled", "rendered", "implemented"},
    # Preserve forward progress for projects created before `ready` replaced
    # the explicit approval state.
    "approved": {"rendered", "implemented"},
    "rendered": {"verified"},
    "implemented": {"verified"},
}


def field(manifest: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:[ \t]*(.*)$", manifest)
    return match.group(1).strip().strip('"') if match else ""


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("new_status")
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    root = args.project_dir.resolve()
    manifest_path = root / "project.yaml"
    if not manifest_path.is_file():
        return fail("project.yaml does not exist")

    manifest = manifest_path.read_text(encoding="utf-8")
    current = field(manifest, "status")
    mode = field(manifest, "mode")
    if args.new_status not in TRANSITIONS.get(current, set()):
        return fail(f"invalid transition: {current} -> {args.new_status}")
    if args.new_status == "rendered" and mode != "writing":
        return fail("only writing projects can become rendered")
    if args.new_status == "implemented" and mode != "building":
        return fail("only building projects can become implemented")

    if args.new_status == "ready":
        guideline = (root / "guideline.md").read_text(encoding="utf-8")
        critique = (root / "critique.md").read_text(encoding="utf-8")
        if "Status: not distilled" in guideline:
            return fail("guideline.md has not been distilled")
        if "Not run." in critique:
            return fail("reflection and decision review must be completed")
        lint = subprocess.run(
            [sys.executable, str(Path(__file__).with_name("lint_project.py")), str(root)],
            check=False,
        )
        if lint.returncode:
            return fail("lint must pass before execution")

    updated = re.sub(
        rf"(?m)^status:[ \t]*{re.escape(current)}[ \t]*$",
        f"status: {args.new_status}",
        manifest,
        count=1,
    )
    if updated == manifest:
        return fail("could not update project status")
    manifest_path.write_text(updated, encoding="utf-8")

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with (root / "log.md").open("a", encoding="utf-8") as log:
        log.write(f"{timestamp} | state | {current} -> {args.new_status} | {args.reason}\n")
    print(f"{current} -> {args.new_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
