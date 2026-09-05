# Artifact contract

## Workspace

```text
<project>/
├── project.yaml
├── seed.md
├── sources/
│   ├── raw/
│   └── index.yaml
├── wiki/
│   ├── overview.md
│   ├── synthesis.md
│   ├── sources/
│   ├── concepts/
│   ├── entities/
│   ├── comparisons/
│   ├── notes/
│   └── open-questions.md
├── guideline.md
├── critique.md
├── output/
└── log.md
```

Do not add page categories until repeated projects demonstrate a retrieval need.

## Project manifest

Keep `project.yaml` simple enough for the standard-library scripts to parse:

```yaml
schema_version: 1
id: example-project
title: Example project
mode: writing
status: seed
created: 2026-07-31
seed_sha256:
source_roots:
  - /absolute/read-only/path
target_repo:
```

Valid modes are `writing` and `building`. Valid states are `seed`, `scoped`, `researching`, `distilled`, `critiqued`, `ready`, `rendered`, `implemented`, and `verified`.

State transitions are forward-only except `researching ↔ distilled` and `distilled ↔ critiqued`, which allow iteration. Advancing from `critiqued` to `ready` requires a distilled guideline, a completed critique, and a passing lint run. It does not require a separate approval action. Research does not permit publication or target-repository edits.

Leave `seed_sha256` empty while drafting the seed. Freeze it before research with `scripts/freeze_seed.py`; subsequent lint runs fail if `seed.md` changes.

## Source index

Use a top-level `sources:` list in `sources/index.yaml`:

```yaml
schema_version: 1
sources:
  - id: stable-kebab-id
    title: Human-readable title
    type: article
    locator: https://example.com/source
    captured: 2026-07-31
    published: 2026-07-01
    authority: primary
    summary: One retrieval-oriented sentence.
    page: wiki/sources/stable-kebab-id.md
    raw:
    relevance: 0.90
    status: selected
```

Allowed `authority` values: `primary`, `secondary`, `personal`, `unknown`. Allowed `status` values: `candidate`, `selected`, `rejected`, `stale`.

Use stable IDs. Never silently reuse an ID for a different source. A URL may remain the raw locator when copying would violate access or copyright constraints.

## Provenance markers

Prefix substantive bullets in derived pages with one marker:

- `[FACT source-id]` — paraphrase supported by the named source.
- `[QUOTE source-id]` — short direct quotation within copyright limits.
- `[HUMAN]` — the user's view, experience, or decision.
- `[INFERENCE source-id,...]` — agent synthesis that is not stated directly.
- `[OPEN]` — unresolved question, conflict, or weakly supported claim.

Use multiple source IDs when a synthesis depends on multiple sources. Never turn an inference into a fact during later rewriting.

## Source page

Each `wiki/sources/<id>.md` contains:

1. title and source locator;
2. retrieval-oriented summary;
3. important claims with provenance markers;
4. limitations or possible bias;
5. links to relevant derivative pages;
6. access and publication dates when known.

Summaries help retrieval; they do not replace evidence. Read raw material when exact wording, technical details, or disputed claims matter.

## Append-only log

Append one line per material operation:

```text
2026-07-31T14:30:00+02:00 | research | selected source-id | reason
```

Do not rewrite historical entries. Correct mistakes with a new entry.

## Context budget

Retrieve in this order:

1. manifest, seed, and index metadata;
2. overview or relevant summaries;
3. focused derivatives;
4. raw sources.

Prefer the smallest set that can answer the question. Record why a new source or page materially changes the project.
