# dotfiles

Personal configuration files for Windows and Linux machines.

## Structure

```
dotfiles/
├── windows/
│   ├── vscode/
│   │   ├── settings.json          - VS Code preferences
│   │   ├── keybindings.json       - keyboard shortcuts
│   │   ├── extensions-local.txt   - extensions installed on Windows (Remote SSH, GitLens, etc.)
│   │   ├── extensions-wsl.txt     - extensions installed inside WSL Ubuntu (Python stack, Claude Code, etc.)
│   │   └── snippets/              - custom code snippets (if any)
│   ├── claude/
│   │   └── statusline-command.py - Claude Code status line script (model, ctx%, cost, rate limits)
│   └── scripts/
│       ├── setup.ps1            - run once on a new Windows machine to apply all configs
│       └── update-extensions.ps1 - updates extensions only if N days have passed since release
└── linux/
    └── codex/
        └── config.toml          - Codex CLI config (model, status line, plugins)
```

## How to use on a new Windows machine

1. Install VS Code (user scope, no admin needed):
   ```
   winget install --id Microsoft.VisualStudioCode --scope user --silent
   ```

2. Clone this repo:
   ```
   git clone git@github-personal:parthkulshreshtha/dotfiles.git
   ```

3. Run setup (copies settings, installs extensions):
   ```
   .\dotfiles\windows\scripts\setup.ps1
   ```

## Updating extensions

Run manually whenever you want to update — only updates extensions released more than N days ago (configured inside the script):

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
| `windows/scripts/setup.ps1` | Change where files get copied, add new tools to install |
| `windows/scripts/update-extensions.ps1` | Change the day threshold (default: 7 days) |
| `windows/claude/statusline-command.py` | Add/remove sections in the Claude Code status line |
| `linux/codex/config.toml` | Codex model/reasoning effort, `[tui] status_line` segments, feature flags, plugins |

## Notes

- SSH config is NOT tracked here — too many machine-specific paths and server IPs.
  Keep a sanitized `ssh/config.example` if needed in future.
- Extension binaries are not tracked — only the ID lists in `extensions-local.txt` and `extensions-wsl.txt`.
  The setup script installs them fresh from the marketplace.
- The two status lines are wired up differently:
  - **Claude Code** runs its script straight out of this repo — `~/.claude/settings.json` points at
    `python3 /home/parth/dotfiles/windows/claude/statusline-command.py`. Editing the file here takes
    effect immediately, no copy step.
  - **Codex** only reads `~/.codex/config.toml`, so `linux/codex/config.toml` is a reference copy.
    Copy it into place on a new machine, then re-add the `[projects."/path"] trust_level` entries —
    those are stripped here because they grant trusted execution on machine-specific paths.
- `windows/claude/` is a historical location; that script actually runs under WSL. New Linux-side
  configs go in `linux/`.
