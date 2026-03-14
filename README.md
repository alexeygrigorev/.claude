# Claude Dotfiles

Bootstrap and configure [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (and [OpenCode](https://opencode.ai/)) with shared skills, commands, aliases, and settings.

This repo serves as a single place to manage your AI coding assistant setup — clone it, run the installer, and get a consistent environment across machines.

## Install

Requires [git](https://git-scm.com/) and [uv](https://docs.astral.sh/uv/).

```bash
curl -sSL https://raw.githubusercontent.com/alexeygrigorev/.claude/main/setup.sh | bash
source ~/.bashrc
```

The installer will:

- Symlink `skills/` and `commands/` into `~/.claude` and `~/.config/opencode` (uses directory junctions on Windows)
- Add a `source` line to `~/.bashrc` pointing to this repo's `.bashrc` (with confirmation, idempotent)
- Configure `~/.claude/settings.json` — sets `attribution.commit` to empty string

Since `.bashrc` is sourced from the repo, pulling updates is enough to get new aliases and functions — no need to re-run the installer.

## Structure

```
.claude/
├── skills/            # Custom skills (auto-triggered by context)
├── commands/          # Slash commands (invoked manually)
├── scripts/           # Python setup scripts (run via uv)
├── .bashrc            # Shell aliases and functions
└── install.sh         # Installer
```

## Skills

Skills are automatically triggered by Claude Code when the context matches their description.

| Skill | Description |
|-------|-------------|
| `fetch-youtube` | Fetch YouTube video transcripts for analysis or summarization |

## Commands

Commands are invoked manually via `/command-name` in Claude Code.

| Command | Description |
|---------|-------------|
| `/create-github-repo` | Create a new GitHub repo with `gh` and push the current project |
| `/init-library` | Scaffold a new Python library with modern tooling (hatch, pyproject.toml) |
| `/release` | Release to PyPI and GitHub with version bumping and release notes |

## Bash Aliases

Available after sourcing `.bashrc`:

| Alias | Command |
|-------|---------|
| `c` | `claude` |
| `cc` | `claude -c` (continue last conversation) |
| `csp` | `claude --dangerously-skip-permissions` |
| `ccsp` | `claude -c --dangerously-skip-permissions` |

### Functions

- `claude_init` — Copy the shared `CLAUDE.md` template into the current directory to bootstrap a new project

## OpenCode Compatibility

The installer symlinks skills and commands into `~/.config/opencode` as well, so they work with both Claude Code and OpenCode out of the box.

## Adding New Skills and Commands

- Skills: create a folder in `skills/` with a `SKILL.md` frontmatter file and any supporting scripts
- Commands: add a markdown file to `commands/` with instructions for Claude to follow

Changes are picked up automatically — no re-install needed since the directories are symlinked.
