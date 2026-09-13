#!/usr/bin/env python3
"""PreToolUse(Bash) guard: block commits and PRs that carry Claude attribution.

The `attribution` setting and CLAUDE.md already ask Claude Code not to add these
lines. This is the backstop for when the model adds them anyway.

It reads the command text only, so it is best-effort: a message taken from a file
(`git commit -F`, `--body-file`) or built at run time is not seen.

Exit 2 cancels the tool call and shows stderr to the model, which can retry clean.
Messages name the kind of line matched, never the command text. Unreadable input
also exits 2, so a malformed call fails closed instead of slipping through.
"""
import json
import re
import sys

# A commit or PR command. `[^\n;&|]*` lets `git -C dir commit` match without
# reaching across into a separate command.
PUBLISH = re.compile(r"\bgit\b[^\n;&|]*\bcommit\b|\bgh\s+pr\s+(?:create|edit)\b")

ATTRIBUTION = [
    ("Co-Authored-By Claude trailer", re.compile(r"co-authored-by:[^\n]*\b(?:claude|anthropic)\b", re.I)),
    ("Claude-Session trailer", re.compile(r"claude-session:", re.I)),
    ("claude.ai session URL", re.compile(r"claude\.ai/code/session_", re.I)),
    ("Generated with Claude Code footer", re.compile(r"generated with \[?claude code", re.I)),
]


def find_attribution(command):
    """Return the label of the first attribution line in a publish command, else None."""
    if not PUBLISH.search(command):
        return None
    return next((label for label, pattern in ATTRIBUTION if pattern.search(command)), None)


def main():
    try:
        label = find_attribution(json.load(sys.stdin)["tool_input"]["command"])
    except Exception as exc:
        print(f"attribution guard: unreadable hook input ({type(exc).__name__}); command blocked", file=sys.stderr)
        return 2
    if label:
        print(f"Blocked: {label} in a commit or PR command. Remove all Claude attribution lines and retry.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
