# Claude Dotfiles

Configuration, skills, and setup scripts for Claude Code CLI.

## Install

```bash
cd ~/git/.claude
./install.sh
source ~/.bashrc
```

This will:
- Create symlinks/junctions for `skills/` and `commands/` in `~/.claude` and `~/.config/opencode`
- Add a `source` line to `~/.bashrc` (with confirmation)
- Set `attribution.commit` in `~/.claude/settings.json`

## Structure

- `skills/` - Custom skills for Claude Code
- `commands/` - Custom commands for Claude Code
- `scripts/` - Python setup scripts (run via `uv run python`)
- `.bashrc` - Claude-related aliases and functions

## Bash Aliases

| Alias | Command |
|-------|---------|
| `c` | `claude` |
| `cc` | `claude -c` |
| `csp` | `claude --dangerously-skip-permissions` |
| `ccsp` | `claude -c --dangerously-skip-permissions` |
| `claude_init` | Copy `CLAUDE.md` template to current directory |
