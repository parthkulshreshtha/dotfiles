#!/usr/bin/env python3
"""Claude Code status line.

Claude Code pipes session JSON to stdin on each update. This prints one line:
home tree, context use, rate limits, model, effort, ponytail mode and cost.
A segment whose data is missing is left out. Standard library only.
"""
import json
import math
import os
import sys

# The badge and separator are not ASCII, so don't depend on the locale.
sys.stdout.reconfigure(encoding="utf-8")

def k(n):
    return f"{math.ceil(n / 1000)}k"

def colored(text, code):
    return f"\033[{code}m{text}\033[0m"

cyan   = lambda t: colored(t, "0;36")
yellow = lambda t: colored(t, "0;33")
green  = lambda t: colored(t, "0;32")
red    = lambda t: colored(t, "0;31")
dim    = lambda t: colored(t, "2")
orange = lambda t: colored(t, "38;5;172")

def home_tree(path):
    """Return "work" or "personal" if path is inside ~/work or ~/personal, else None.

    Symlinks are resolved on both sides, so a link into a tree counts as that tree.
    Relative or empty paths return None rather than resolving against this
    process's own directory.
    """
    if not isinstance(path, str) or not os.path.isabs(path):
        return None
    real = os.path.realpath(path)
    for name in ("work", "personal"):
        root = os.path.realpath(os.path.expanduser(f"~/{name}"))
        if os.path.commonpath([real, root]) == root:
            return name
    return None

def ponytail_badge():
    """Badge for the ponytail plugin's mode, or None when ponytail is off.

    The plugin writes its mode to $CLAUDE_CONFIG_DIR/.ponytail-active and
    deletes the file when turned off. The file is read defensively: symlinks
    are refused, only a few bytes are read, and only known modes are shown.
    """
    claude_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    flag = os.path.join(claude_dir, ".ponytail-active")
    if os.path.islink(flag) or not os.path.isfile(flag):
        return None
    try:
        with open(flag, encoding="utf-8") as f:
            mode = f.read(16).strip().lower()
    except (OSError, UnicodeDecodeError):
        return None
    # The modes the plugin writes. "off" or anything else shows nothing.
    if mode not in {"lite", "full", "ultra", "review"}:
        return None
    return orange("⚒ " if mode == "full" else f"⚒ :{mode.upper()}")

try:
    data = json.load(sys.stdin.buffer)
except ValueError:
    sys.exit(0)

parts = []

# Home tree of the session's current directory
ws = data.get("workspace") or {}
parts.append(home_tree(ws.get("current_dir") or data.get("cwd")) or dim("no-tree"))

# Context usage
ctx        = data.get("context_window") or {}
used_pct   = ctx.get("used_percentage")
total_tok  = ctx.get("total_input_tokens")
ctx_size   = ctx.get("context_window_size")

if used_pct is not None and total_tok is not None and ctx_size is not None:
    pct = round(used_pct)
    pct_colored = (red if pct >= 85 else yellow if pct >= 60 else green)(f"{pct}%")
    parts.append(f"ctx:{pct_colored} ({k(total_tok)}/{k(ctx_size)})")

# Rate limits: only sent for Claude.ai subscribers
rl      = data.get("rate_limits") or {}
five_hr = (rl.get("five_hour") or {}).get("used_percentage")
seven_d = (rl.get("seven_day")  or {}).get("used_percentage")
rate    = " ".join(filter(None, [
    f"session:{round(five_hr)}%" if five_hr is not None else None,
    f"7d:{round(seven_d)}%"      if seven_d is not None else None,
]))
if rate:
    parts.append(rate)

# Model name
model = (data.get("model") or {}).get("display_name") or "Unknown"
parts.append(cyan(model))

# Effort level: only sent for models that support it
effort = (data.get("effort") or {}).get("level")
if effort:
    parts.append(f"effort:{yellow(effort)}")

# Ponytail mode
badge = ponytail_badge()
if badge:
    parts.append(badge)

# Session cost
cost = (data.get("cost") or {}).get("total_cost_usd")
if cost is not None:
    parts.append(yellow(f"${cost:.3f}"))

print(dim(" │ ").join(parts), end="")
