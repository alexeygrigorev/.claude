#!/bin/bash
# Install Claude dotfiles to ~/.bashrc

REPO_DIR="$(pwd)"

# Create symlinks
if [[ "$OS" == "Windows_NT" ]]; then
    # Windows - use mklink for directory junctions
    echo "Creating directory junctions on Windows..."
    WIN_REPO=$(cygpath -w "$REPO_DIR")

    # Remove existing directories/junctions if they exist
    rm -rf ~/.claude/skills ~/.claude/commands

    cmd.exe //c "mklink /J %USERPROFILE%\\.claude\\skills ${WIN_REPO}\\skills" 2>/dev/null
    cmd.exe //c "mklink /J %USERPROFILE%\\.claude\\commands ${WIN_REPO}\\commands" 2>/dev/null
else
    # Unix/macOS - use regular symlinks
    echo "Creating symlinks on Unix/macOS..."
    ln -sf "$REPO_DIR/skills" ~/.claude/skills
    ln -sf "$REPO_DIR/commands" ~/.claude/commands
fi

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
