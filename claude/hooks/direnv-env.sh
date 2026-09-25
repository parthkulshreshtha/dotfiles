#!/bin/sh
# SessionStart hook. Claude Code's Bash tool never runs direnv's prompt hook, so .envrc
# variables stay unset. Claude runs $CLAUDE_ENV_FILE before every Bash command, so the
# line added here loads direnv for the directory each command starts in.
[ -n "$CLAUDE_ENV_FILE" ] || exit 0
line='[ -x /opt/homebrew/bin/direnv ] && eval "$(/opt/homebrew/bin/direnv export zsh 2>/dev/null)"'
grep -qxF "$line" "$CLAUDE_ENV_FILE" 2>/dev/null || printf '%s\n' "$line" >> "$CLAUDE_ENV_FILE"
