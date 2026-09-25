# dotfiles

Personal configuration files for macOS, Windows, and Linux machines.

The [Codex setup](codex/README.md) lives in `codex/`. Its portable config and
Consult roster are separate from Claude. `shared/` holds what both tools use:
the Humanizer skill, linked into both, and the GitHub account guard hook.

## Structure

```
dotfiles/
├── CLAUDE.md                    - rules for agents working in this repo
├── .claude-plugin/
│   └── marketplace.json         - Claude Code plugin marketplace for this repo
├── claude/
│   ├── CLAUDE.md                - global instructions for Claude Code and Codex
│   │                              (symlink ~/.claude/CLAUDE.md to this)
│   ├── settings.json            - baseline of ~/.claude/settings.json, without autoMode
│   ├── statusline.py            - status line: work/personal tree, context, rate limits,
│   │                              model, effort, ponytail mode, cost
│   ├── hooks/
│   │   ├── block-claude-attribution.py - PreToolUse hook: blocks commits/PRs with
│   │   │                          Claude attribution lines
│   │   └── direnv-env.sh        - SessionStart hook: loads direnv for each Bash command
│   └── plugins/
│       ├── consult/             - Claude Code plugin: /consult:2nd + /consult:panel
│       │                          (second opinions from independent models via OpenRouter)
│       └── handoff/             - Claude Code plugin: /handoff:handoff + SessionStart hook
│                                  (HANDOFF.md session resume memory for cold starts)
├── shared/
│   ├── hooks/
│   │   └── gh-account-guard.py  - PreToolUse hook for Claude Code and Codex: picks the
│   │                              GitHub account for bare `gh` commands
│   └── skills/
│       └── humanizer/           - Humanizer skill, linked into Claude Code and Codex
├── windows/
│   ├── vscode/
│   │   ├── settings.json          - VS Code preferences
│   │   ├── keybindings.json       - keyboard shortcuts
│   │   ├── extensions-local.txt   - extensions installed on Windows (Remote SSH, Remote WSL, etc.)
│   │   └── extensions-wsl.txt     - extensions installed inside WSL Ubuntu (Python stack, Claude Code, etc.)
│   └── scripts/
│       └── update-extensions.ps1 - updates extensions only if N days have passed since release
└── codex/
    ├── AGENTS.md                - link to shared claude/CLAUDE.md
    ├── config.toml              - portable settings; no model defaults
    ├── consult/                 - Codex roster and review runner
    ├── skills/                  - Consult and Handoff skills
    ├── hooks/                   - GitHub guard (symlink into shared/hooks/) and saved context
    ├── install.py               - repeatable setup with backups
    ├── check.py                 - offline installation checks
    └── README.md                - setup and ownership guide
```

## Claude Code plugins

This repo doubles as a Claude Code plugin marketplace:

```
/plugin marketplace add parthkulshreshtha/dotfiles
```

| Plugin | Install | What it does |
|---|---|---|
| `consult` | `/plugin install consult@parth-dotfiles` | `/consult:2nd` (one independent second opinion) and `/consult:panel` (a panel of independent model advisors), backed by OpenRouter. [Docs](claude/plugins/consult/README.md). |
| `handoff` | `/plugin install handoff@parth-dotfiles` | `/handoff:handoff` saves the session state to `HANDOFF.md`; a SessionStart hook injects it into the next session so cold starts resume with zero context. [Docs](claude/plugins/handoff/README.md). |

## How to use on a new Windows machine

1. Install VS Code (user scope, no admin needed):
   ```
   winget install --id Microsoft.VisualStudioCode --scope user --silent
   ```

2. Clone this repo:
   ```
   git clone git@github-personal:parthkulshreshtha/dotfiles.git
   ```

3. Copy `windows\vscode\settings.json` and `keybindings.json` into `%APPDATA%\Code\User\`.

4. Install the extensions. With a zero-day threshold the update script installs every
   extension in both lists, the WSL ones inside the `Ubuntu` distro:
   ```
   .\dotfiles\windows\scripts\update-extensions.ps1 -DaysThreshold 0
   ```

## How to use on a new macOS machine

For Codex, follow [the Codex installation guide](codex/README.md).
The steps below set up Claude Code.

1. Clone this repo to `~/personal/dotfiles`.

2. Link the global instructions:
   ```
   ln -s ~/personal/dotfiles/claude/CLAUDE.md ~/.claude/CLAUDE.md
   ```

3. Merge `claude/settings.json` into `~/.claude/settings.json`. It holds attribution,
   permission mode, model, hooks, status line, plugins, and UI preferences. Its paths are
   absolute and assume the repo is at `~/personal/dotfiles`, so change them if yours
   differs. Keep `autoMode` in the live file only: it names private work paths, so it
   never goes in this repo.

   The commands call `/opt/homebrew/bin/python3` by absolute path. Hooks and the status
   line run in a non-login shell, so Homebrew's `/opt/homebrew/bin` is not guaranteed to
   be on `PATH`. `/usr/bin/python3` works too; the Python scripts are stdlib-only.

4. After editing either file, check for drift. Run this from the repo root under zsh or bash:
   ```
   jq -S 'del(.autoMode)' ~/.claude/settings.json | diff - <(jq -S . claude/settings.json)
   ```
   No output means the live file matches the baseline.

5. Sanity-check the status line without launching Claude Code:
   ```
   echo '{"model":{"display_name":"Opus 5"},"cost":{"total_cost_usd":0.1}}' \
     | python3 claude/statusline.py
   ```
   Expect `no-tree │ Opus 5 │ $0.100`. The first segment reads `work` or `personal` when
   the session's directory is under `~/work` or `~/personal`. A `⚒` badge shows the
   ponytail mode while that plugin is on.

## Keeping Claude attribution out of commits (macOS)

Two parts, both in `claude/settings.json`. The setting stops Claude Code asking for the
lines; the hook blocks any commit or PR command that still carries them.

```json
"attribution": { "commit": "", "pr": "", "sessionUrl": false },
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "i=$(cat); case \"$i\" in *commit*|*gh*) printf %s \"$i\" | /opt/homebrew/bin/python3 /Users/<you>/personal/dotfiles/claude/hooks/block-claude-attribution.py ;; esac",
        "timeout": 10
      }]
    }
  ]
}
```

The `case` prefilter starts Python only when the hook input contains `commit` or `gh`.
Every command the hook blocks contains one of them.

Check the paths work. A wrong interpreter path does not block anything: it silently
disables the guard. Run this in a normal terminal, since inside Claude Code the live
hook blocks the test itself:

```
echo '{"tool_input":{"command":"git commit -m x -m \"Claude-Session: y\""}}' \
  | /opt/homebrew/bin/python3 claude/hooks/block-claude-attribution.py; echo "exit $?"
```

Expect a `Blocked:` line and `exit 2`. The hook reads only the command text, so messages
from files (`git commit -F`, `--body-file`) are not checked.

## GitHub account guard

`shared/hooks/gh-account-guard.py` routes bare `gh` commands to the account for their tree:
`~/.config/gh-personal` under `~/personal`, `~/.config/gh-work` under `~/work`. Outside
both trees it denies the call. Codex runs it through the `codex/hooks/gh-account-guard.py`
symlink. Claude Code runs it with `--claude`, which leaves the approval decision to Claude
Code's own permission checks. The entry in `claude/settings.json` runs:

```
i=$(cat); case "$i" in *gh*) printf %s "$i" | /opt/homebrew/bin/python3 /Users/<you>/personal/dotfiles/shared/hooks/gh-account-guard.py --claude ;; esac
```

See [the Codex guide](codex/README.md#github-guard) for the routing rules.

## direnv in Claude Code

Claude Code's Bash tool never runs direnv's prompt hook, so `.envrc` variables stay unset.
The SessionStart hook `claude/hooks/direnv-env.sh` adds one line to `$CLAUDE_ENV_FILE`,
which Claude Code runs before every Bash command. Each command then loads direnv for the
directory it starts in, so per-tree variables such as `AZURE_CONFIG_DIR`, `GH_CONFIG_DIR`,
and `HF_HOME` work inside Claude. A `cd` inside a command does not reload them.

```json
"SessionStart": [{"hooks": [{"type": "command", "command": "sh /Users/<you>/personal/dotfiles/claude/hooks/direnv-env.sh", "timeout": 5}]}]
```

The added line does nothing when direnv is not at `/opt/homebrew/bin/direnv`.
direnv loads only `.envrc` files you have approved with `direnv allow`.

## Updating extensions

Run it manually whenever you want to update. It only updates extensions released more
than N days ago (configured inside the script):

```
.\dotfiles\windows\scripts\update-extensions.ps1
```

## What goes where

| File | What to edit it for |
|---|---|
| `windows/vscode/settings.json` | Editor preferences, theme, font, language-specific settings |
| `windows/vscode/keybindings.json` | Custom keyboard shortcuts |
| `windows/vscode/extensions-local.txt` | Add/remove extensions for the Windows VS Code client |
| `windows/vscode/extensions-wsl.txt` | Add/remove extensions for the WSL Ubuntu VS Code server |
| `windows/scripts/update-extensions.ps1` | Change the day threshold (default: 7 days) |
| `claude/CLAUDE.md` | Global instructions for Claude Code and Codex |
| `claude/settings.json` | Portable Claude Code settings: hooks, status line, plugins; never `autoMode` |
| `claude/statusline.py` | Add/remove sections in the Claude Code status line |
| `claude/hooks/block-claude-attribution.py` | Change which attribution lines block a commit or PR |
| `claude/hooks/direnv-env.sh` | Change how Claude Code's Bash commands load direnv |
| `shared/hooks/gh-account-guard.py` | Change which GitHub account a `gh` command uses |
| `codex/config.toml` | Portable Codex settings and status-line segments; no model defaults |
| `codex/consult/advisors.toml` | Consult reviewer models, routes, and panels |

## Notes

- SSH config is NOT tracked here: it has too many machine-specific paths and server IPs.
  Keep a sanitized `ssh/config.example` if needed in future.
- Extension binaries are not tracked, only the ID lists in `extensions-local.txt` and
  `extensions-wsl.txt`. `update-extensions.ps1` installs them from the marketplace.
- The two status lines are wired up differently:
  - **Claude Code** runs `claude/statusline.py` straight out of this repo.
    `~/.claude/settings.json` points at it directly (`python3 /home/parth/dotfiles/...`
    under WSL, `/opt/homebrew/bin/python3 /Users/<you>/personal/dotfiles/...` on macOS).
    Editing the file here takes effect immediately, no copy step. The script is
    stdlib-only Python, so the same file runs under WSL and on macOS.
  - **Codex** has a portable baseline in `codex/config.toml`, verified against the live config.
    Merge it into `~/.codex/config.toml`, preserving machine-local trust and app settings.
    See [Codex setup](codex/README.md) for installation status.
