#!/bin/bash
# Install Claude dotfiles to ~/.bashrc

REPO_DIR="$(pwd)"

# Create symlinks
ln -sf "$REPO_DIR/skills" ~/.claude/skills
ln -sf "$REPO_DIR/commands" ~/.claude/commands

# Set repo path in ~/.bashrc
if ! grep -q "CLAUDE_DOTFILES_DIR" ~/.bashrc; then
  echo "" >> ~/.bashrc
  echo "# Claude dotfiles location" >> ~/.bashrc
  echo "export CLAUDE_DOTFILES_DIR=\"$REPO_DIR\"" >> ~/.bashrc
fi

# Append .bashrc content to ~/.bashrc if not already present
if ! grep -q "Claude Code CLI aliases" ~/.bashrc; then
  cat .bashrc >> ~/.bashrc
  echo "Added Claude aliases to ~/.bashrc"
else
  echo "Claude aliases already present in ~/.bashrc"
fi

echo "Installation complete. Run 'source ~/.bashrc' to apply changes."
