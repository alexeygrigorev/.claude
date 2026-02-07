# Claude Code CLI aliases and functions

alias c="claude"
alias cc="claude -c"
alias csp="claude --dangerously-skip-permissions"
alias ccsp="claude -c --dangerously-skip-permissions"

claude_init() {
  local src="${CLAUDE_DOTFILES_DIR:-$HOME/git/.claude}/CLAUDE.md"
  local dest="$PWD/CLAUDE.md"

  if [[ -e "$dest" ]]; then
    echo "CLAUDE.md already exists in this directory. Nothing done."
    return 0
  fi

  cp "$src" "$dest" || return 1
  echo "Init successful: CLAUDE.md created."
}
