#!/bin/bash
# Install Claude dotfiles to ~/.bashrc

REPO_DIR="$(pwd)"

# Create symlinks for ~/.claude and ~/.config/opencode
TARGETS=(~/.claude ~/.config/opencode)

for TARGET_DIR in "${TARGETS[@]}"; do
    # Create target directory if it doesn't exist
    mkdir -p "$TARGET_DIR"

    if [[ "$OS" == "Windows_NT" ]]; then
        # Windows - use mklink for directory junctions
        echo "Creating directory junctions in $TARGET_DIR on Windows..."
        WIN_REPO=$(cygpath -w "$REPO_DIR")
        WIN_TARGET=$(cygpath -w "$TARGET_DIR")

        # Remove existing directories/junctions if they exist
        rm -rf "$TARGET_DIR/skills" "$TARGET_DIR/commands"

        cmd.exe //c "mklink /J ${WIN_TARGET}\\skills ${WIN_REPO}\\skills" 2>/dev/null
        cmd.exe //c "mklink /J ${WIN_TARGET}\\commands ${WIN_REPO}\\commands" 2>/dev/null
    else
        # Unix/macOS - use regular symlinks
        echo "Creating symlinks in $TARGET_DIR..."
        ln -sf "$REPO_DIR/skills" "$TARGET_DIR/skills"
        ln -sf "$REPO_DIR/commands" "$TARGET_DIR/commands"
    fi
done

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
