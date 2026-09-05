#!/usr/bin/env python3
"""Lint a memory-wiki project using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_PATHS = (
    "project.yaml",
    "seed.md",
    "sources/raw",
    "sources/index.yaml",
    "wiki/overview.md",
    "wiki/synthesis.md",
    "wiki/sources",
    "wiki/concepts",
    "wiki/entities",
    "wiki/comparisons",
    "wiki/notes",
    "wiki/open-questions.md",
    "guideline.md",
    "critique.md",
    "output",
    "log.md",
)
MODES = {"writing", "building"}
STATUSES = {
    "seed",
    "scoped",
    "researching",
    "distilled",
    "critiqued",
    "ready",
    "approved",
    "rendered",
    "implemented",
    "verified",
}
AUTHORITIES = {"primary", "secondary", "personal", "unknown"}
SOURCE_STATUSES = {"candidate", "selected", "rejected", "stale"}
MARKER = re.compile(r"^- \[(?:FACT [^]]+|QUOTE [^]]+|HUMAN|INFERENCE [^]]+|OPEN)\]")
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def scalar(value: str) -> str:
    value = value.strip()
    if value.startswith(('"', "'")):
        try:
            return str(json.loads(value))
        except json.JSONDecodeError:
            return value.strip("'\"")
    return value


def flat_yaml(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^([a-z0-9_]+):\s*(.*)$", line)
        if match:
            values[match.group(1)] = scalar(match.group(2))
    return values


def index_sources(path: Path, report: Report) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    if not re.search(r"(?m)^schema_version:\s*1\s*$", text):
        report.error("sources/index.yaml: schema_version must be 1")
    if not re.search(r"(?m)^sources:", text):
        report.error("sources/index.yaml: missing sources list")
        return []

    sources: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        start = re.match(r"^  - ([a-z_]+):\s*(.*)$", line)
        item = re.match(r"^    ([a-z_]+):\s*(.*)$", line)
        if start:
            if current:
                sources.append(current)
            current = {start.group(1): scalar(start.group(2)), "_line": str(number)}
        elif item and current is not None:
            current[item.group(1)] = scalar(item.group(2))
    if current:
        sources.append(current)
    return sources


def check_source_index(root: Path, report: Report) -> None:
    sources = index_sources(root / "sources/index.yaml", report)
    required = {"id", "title", "type", "locator", "authority", "summary", "page", "status"}
    seen: set[str] = set()
    for source in sources:
        label = source.get("id") or f"line {source['_line']}"
        missing = sorted(key for key in required if not source.get(key))
        if missing:
            report.error(f"source {label}: missing {', '.join(missing)}")
        source_id = source.get("id", "")
        if source_id in seen:
            report.error(f"source {source_id}: duplicate id")
        seen.add(source_id)
        if source.get("authority") and source["authority"] not in AUTHORITIES:
            report.error(f"source {label}: invalid authority {source['authority']}")
        if source.get("status") and source["status"] not in SOURCE_STATUSES:
            report.error(f"source {label}: invalid status {source['status']}")
        page = source.get("page")
        if source.get("status") == "selected" and page and not (root / page).is_file():
            report.error(f"source {label}: selected page does not exist: {page}")


def check_markdown(root: Path, report: Report) -> None:
    wiki = root / "wiki"
    for path in wiki.rglob("*.md"):
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            if line.startswith("- ") and not MARKER.match(line) and not line.startswith("- [ ]"):
                report.warn(f"{relative}:{number}: substantive bullet lacks provenance marker")
        for target in MARKDOWN_LINK.findall(text):
            clean = target.split("#", 1)[0]
            if not clean or re.match(r"^(?:https?://|mailto:)", clean):
                continue
            if not (path.parent / clean).resolve().exists():
                report.error(f"{relative}: broken local link: {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()
    root = args.project_dir.resolve()
    report = Report()

    if not root.is_dir():
        print(f"error: project directory does not exist: {root}", file=sys.stderr)
        return 2

    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            report.error(f"missing required path: {relative}")
    if report.errors:
        return emit(report)

    manifest = flat_yaml(root / "project.yaml")
    for key in ("schema_version", "id", "title", "mode", "status", "created", "seed_sha256"):
        if key not in manifest:
            report.error(f"project.yaml: missing {key}")
    if manifest.get("schema_version") != "1":
        report.error("project.yaml: schema_version must be 1")
    if manifest.get("mode") not in MODES:
        report.error(f"project.yaml: invalid mode {manifest.get('mode', '')}")
    if manifest.get("status") not in STATUSES:
        report.error(f"project.yaml: invalid status {manifest.get('status', '')}")
    if manifest.get("mode") == "building" and not manifest.get("target_repo"):
        report.warn("project.yaml: building project has no target_repo")

    expected_hash = manifest.get("seed_sha256", "")
    actual_hash = hashlib.sha256((root / "seed.md").read_bytes()).hexdigest()
    if expected_hash and expected_hash != actual_hash:
        report.error("seed.md changed after it was frozen")
    if manifest.get("status") != "seed" and not expected_hash:
        report.error("project.yaml: non-seed project must freeze seed_sha256")
    if not expected_hash:
        report.warn("seed.md is not frozen")

    check_source_index(root, report)
    check_markdown(root, report)

    if manifest.get("status") in {"ready", "approved", "rendered", "implemented", "verified"}:
        guideline = (root / "guideline.md").read_text(encoding="utf-8")
        if "Status: not distilled" in guideline:
            report.error("execution-ready project still has an undistilled guideline")

    return emit(report)


def emit(report: Report) -> int:
    for message in report.errors:
        print(f"ERROR: {message}")
    for message in report.warnings:
        print(f"WARN: {message}")
    print(f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
