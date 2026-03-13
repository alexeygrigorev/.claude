#!/bin/bash
# Install Claude dotfiles

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create symlinks for ~/.claude and ~/.config/opencode
TARGETS=(~/.claude ~/.config/opencode)

for TARGET_DIR in "${TARGETS[@]}"; do
    mkdir -p "$TARGET_DIR"

    if [[ "$OS" == "Windows_NT" ]]; then
        echo "Creating directory junctions in $TARGET_DIR on Windows..."
        WIN_REPO=$(cygpath -w "$REPO_DIR")
        WIN_TARGET=$(cygpath -w "$TARGET_DIR")

        rm -rf "$TARGET_DIR/skills" "$TARGET_DIR/commands"

        cmd.exe //c "mklink /J ${WIN_TARGET}\\skills ${WIN_REPO}\\skills" 2>/dev/null
        cmd.exe //c "mklink /J ${WIN_TARGET}\\commands ${WIN_REPO}\\commands" 2>/dev/null
    else
        echo "Creating symlinks in $TARGET_DIR..."
        ln -sf "$REPO_DIR/skills" "$TARGET_DIR/skills"
        ln -sf "$REPO_DIR/commands" "$TARGET_DIR/commands"
    fi
done

# Setup bashrc source line and settings.json
uv run python "$REPO_DIR/scripts/setup_bashrc.py"
uv run python "$REPO_DIR/scripts/setup_settings.py"

echo "Installation complete. Run 'source ~/.bashrc' to apply changes."
