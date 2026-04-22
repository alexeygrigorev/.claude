#!/bin/bash
# One-line installer for Claude Dotfiles
# Usage: curl -sSL https://raw.githubusercontent.com/alexeygrigorev/.claude/main/installer.sh | bash

set -e

REPO_URL="https://github.com/alexeygrigorev/.claude.git"
INSTALL_DIR="$HOME/git/.claude"
YES_FLAG=""

if [ "${1:-}" = "--yes" ]; then
    YES_FLAG="--yes"
fi

# Check for git
if ! command -v git &>/dev/null; then
    echo "Error: git is required but not installed."
    exit 1
fi

# Check for uv
if ! command -v uv &>/dev/null; then
    echo "Error: uv is required. Install it first: https://docs.astral.sh/uv/"
    exit 1
fi

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation..."
    git -C "$INSTALL_DIR" pull --rebase
else
    echo "Cloning claude dotfiles..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
fi

# Run configure
cd "$INSTALL_DIR"
./configure.sh $YES_FLAG

echo ""
echo "Run 'source ~/.bashrc' or restart your shell to apply changes."
