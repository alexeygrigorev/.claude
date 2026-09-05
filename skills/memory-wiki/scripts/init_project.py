#!/usr/bin/env python3
"""Initialize a project-scoped memory wiki without overwriting existing work."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import date, datetime
from pathlib import Path


DIRECTORIES = (
    "sources/raw",
    "wiki/sources",
    "wiki/concepts",
    "wiki/entities",
    "wiki/comparisons",
    "wiki/notes",
    "output",
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-project"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(content, encoding="utf-8")


def writing_seed(title: str) -> str:
    return f"""# {title}

## Intended reader

<!-- Who is this for? -->

## Desired change

<!-- What should the reader understand, feel, or do afterward? -->

## Core claim

<!-- State what you currently believe before research. -->

## Brain dump

<!-- Add rough thoughts, experiences, questions, and tentative order. -->

## Must use

<!-- Personal material or known-good sources. -->

## Must avoid

<!-- Claims, sources, tones, or directions that do not belong. -->

## Constraints

<!-- Form, length, deadline, publication, and voice constraints. -->
"""


def building_seed(title: str) -> str:
    return f"""# {title}

## Problem

<!-- Describe the current pain and who experiences it. -->

## Desired behavior

<!-- Describe the observable outcome. -->

## Acceptance criteria

- [ ] Replace with a verifiable criterion.

## Constraints

<!-- Compatibility, security, performance, migration, and operational constraints. -->

## Current understanding

<!-- Suspected components, prior decisions, and unknowns. -->

## Comparison sources

<!-- Repositories, standards, papers, or documentation worth researching. -->

## Non-goals

<!-- State what this project intentionally will not solve. -->
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--mode", choices=("writing", "building"), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--id", dest="project_id")
    parser.add_argument("--seed-file", type=Path)
    parser.add_argument("--source-root", action="append", default=[])
    parser.add_argument("--target-repo", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()

    if project_dir.exists() and any(project_dir.iterdir()):
        print(f"error: {project_dir} is not empty", file=sys.stderr)
        return 2
    if args.seed_file and not args.seed_file.is_file():
        print(f"error: seed file does not exist: {args.seed_file}", file=sys.stderr)
        return 2

    project_dir.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES:
        (project_dir / directory).mkdir(parents=True, exist_ok=True)

    seed_path = project_dir / "seed.md"
    if args.seed_file:
        shutil.copyfile(args.seed_file, seed_path)
        seed_hash = sha256(seed_path)
        status = "scoped"
    else:
        seed = writing_seed(args.title) if args.mode == "writing" else building_seed(args.title)
        write_new(seed_path, seed)
        seed_hash = ""
        status = "seed"

    roots = "\n".join(f"  - {yaml_string(str(Path(root).expanduser().resolve()))}" for root in args.source_root)
    if not roots:
        roots = "  []"
    target_repo = str(Path(args.target_repo).expanduser().resolve()) if args.target_repo else ""
    manifest = f"""schema_version: 1
id: {slugify(args.project_id or args.title)}
title: {yaml_string(args.title)}
mode: {args.mode}
status: {status}
created: {date.today().isoformat()}
seed_sha256: {seed_hash}
source_roots:
{roots}
target_repo: {yaml_string(target_repo)}
"""
    write_new(project_dir / "project.yaml", manifest)
    write_new(project_dir / "sources/index.yaml", "schema_version: 1\nsources: []\n")
    write_new(
        project_dir / "wiki/overview.md",
        "# Overview\n\n- [OPEN] Summarize the project landscape after selecting sources.\n",
    )
    write_new(
        project_dir / "wiki/synthesis.md",
        "# Synthesis\n\n- [OPEN] Record the current thesis, evidence, and dissent.\n",
    )
    write_new(
        project_dir / "wiki/open-questions.md",
        "# Open questions\n\n- [OPEN] Replace with the first material research question.\n",
    )
    write_new(
        project_dir / "guideline.md",
        "# Guideline\n\nStatus: not distilled\n\nResearch must be distilled here before execution.\n",
    )
    write_new(
        project_dir / "critique.md",
        "# Critique\n\n## Reflection\n\nNot run.\n\n## Decision review\n\nNot run.\n\n## Accepted risks\n\nNone.\n",
    )
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    write_new(project_dir / "log.md", f"# Log\n\n{timestamp} | init | created {args.mode} project | {status}\n")

    print(project_dir)
    if not seed_hash:
        print("next: edit seed.md, then run freeze_seed.py", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
