#!/bin/bash
# Install Claude dotfiles

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
YES_FLAG=""

if [[ "${1:-}" == "--yes" ]]; then
    YES_FLAG="--yes"
fi

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

# Install CLI wrappers to ~/bin
mkdir -p "$HOME/bin"
for wrapper in "$REPO_DIR/bin/"*; do
    name="$(basename "$wrapper")"
    cp "$wrapper" "$HOME/bin/$name"
    chmod +x "$HOME/bin/$name"
    echo "Installed wrapper: ~/bin/$name"
done

# Ensure ~/bin is early in PATH (before /usr/bin)
if ! echo "$PATH" | tr ':' '\n' | grep -qx "$HOME/bin"; then
    echo "WARNING: ~/bin is not in your PATH."
    echo "Add this to your ~/.bashrc or ~/.profile:"
    echo '  export PATH="$HOME/bin:$PATH"'
elif [[ "$(command -v gh)" != "$HOME/bin/gh" ]]; then
    echo "WARNING: ~/bin/gh is not taking priority. Another gh comes first in PATH."
    echo "Make sure ~/bin is early in PATH:"
    echo '  export PATH="$HOME/bin:$PATH"'
fi

# Setup bashrc source line and settings.json
uv run --no-project python "$REPO_DIR/scripts/setup_bashrc.py" $YES_FLAG
uv run --no-project python "$REPO_DIR/scripts/setup_settings.py"

echo "Installation complete. Run 'source ~/.bashrc' to apply changes."
