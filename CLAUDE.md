# Working in this repo

- This repo is public. Never commit tokens, keys, work repo or dataset names, or `autoMode` settings.
- `claude/settings.json` is the baseline without `autoMode`. The live file is `~/.claude/settings.json`.
  Check drift with the `jq` command in `README.md`.
- `claude/CLAUDE.md` holds the global instructions for Claude Code and Codex (`codex/AGENTS.md` links to it).
- Hook scripts and `claude/statusline.py` run straight from this checkout. A broken edit breaks live sessions at once.
- Plugins run from a cached copy, not this checkout. After editing one, bump its version, run
  `claude plugin update <name>@parth-dotfiles`, and restart. The update copies the working tree, uncommitted edits included.
- Run `python3 codex/check.py` after changing `codex/`, `shared/hooks/`, or the consult plugin. It must print `PASS`.
