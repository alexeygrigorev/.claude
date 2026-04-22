---
name: init-library
description: Initialize a new Python library with modern tooling, packaging, tests, and optional CLI support. Use when the user wants to scaffold a new Python package.
allowed-tools: Bash(uv *), Bash(git *), Bash(make *), Bash(mkdir *), Bash(touch *), Bash(ls *)
---

# Init Library

Initialize a new Python library with modern tooling.

## Ask the User

Before starting, ask:

1. Library name
2. Short description
3. Runtime dependencies
4. Whether the package should install a CLI executable

## Target Structure

```text
<library_name>/
├── <library_name>/
│   ├── __init__.py
│   ├── cli.py
│   └── __version__.py
├── tests/
│   └── __init__.py
├── .github/
│   └── workflows/
│       └── test.yml
├── Makefile
├── pyproject.toml
├── README.md
├── .gitignore
├── .python-version
└── uv.lock
```

## Build Configuration

Use this `pyproject.toml` shape:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "<library_name>"
description = "<description>"
readme = "README.md"
license = {text = "WTFPL"}
requires-python = ">=3.10"
dynamic = ["version"]

dependencies = [
    # Add runtime dependencies here
]

authors = [
    {name = "<your-name>", email = "<your-email>"}
]

[dependency-groups]
dev = [
    "hatch",
    "pytest",
    "pytest-cov",
    "ruff",
]

[tool.hatch.build.targets.wheel]
packages = ["<library_name>"]

[tool.hatch.version]
path = "<library_name>/__version__.py"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

If the package should expose a CLI, add:

```toml
[project.scripts]
<library_name> = "<library_name>.cli:main"
```

## Default Files

`__version__.py`:

```python
__version__ = "0.0.1"
```

`cli.py` template when a CLI is requested:

```python
import argparse


def main():
    parser = argparse.ArgumentParser(description="<description>")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    print("Hello from <library_name>!")


if __name__ == "__main__":
    main()
```

`Makefile`:

```makefile
.PHONY: test setup shell coverage publish-build publish-test publish publish-clean

test:
	uv run pytest

setup:
	uv sync --dev

shell:
	uv shell

coverage:
	uv run pytest --cov=<library_name> --cov-report=term-missing

publish-build:
	uv run hatch build

publish-test:
	uv run hatch publish --repo test

publish:
	uv run hatch publish

publish-clean:
	rm -r dist/
```

`.python-version`:

```text
3.13
```

## After Creating Files

Run:

```bash
uv sync --dev
```

Then verify the scaffold with at least one basic test run path, and keep the generated project consistent with the user's answers.
