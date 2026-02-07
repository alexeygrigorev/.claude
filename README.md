# Claude Dotfiles

This directory contains symlinks and configuration for Claude Code CLI.

## Symlinks

Create symlinks from this repo to `~/.claude`:

```bash
cd ~/git/.claude
ln -sf "$(pwd)/skills" ~/.claude/skills
ln -sf "$(pwd)/commands" ~/.claude/commands
```

## Structure

- `skills/` - Custom skills for Claude Code
- `commands/` - Custom commands for Claude Code
- `.bashrc` - Claude-related aliases and functions

## Bash Integration

To add Claude aliases and functions to your shell:

```bash
cat .bashrc >> ~/.bashrc && source ~/.bashrc
```

Or use the install command:

```bash
./install.sh
```
