# handoff — session resume memory for Claude Code

One command, one file. When you're about to leave, clear, or the context is
getting out of hand, run:

```
/handoff:handoff
```

Claude overwrites `HANDOFF.md` at the project root with the live state of the
work — then you can safely `/clear` or close. The next session starts cold and
picks up where you left off: a SessionStart hook injects `HANDOFF.md` plus a
git reality check automatically. That covers another machine or a teammate too,
if you commit and pull the file — see Tips.

## Install

```
/plugin marketplace add parthkulshreshtha/dotfiles
/plugin install handoff@parth-dotfiles
```

No dependencies. Works in any project; needs nothing but a POSIX shell for the
hook (macOS, Linux, WSL).

## How it works

**Saving** — `/handoff:handoff` rewrites `HANDOFF.md` from scratch with five
fixed sections. Claude will usually run it on its own when you say you're
leaving or clearing — but typing the command yourself is the reliable path.

| Section | Contents |
|---|---|
| **Now** | one paragraph: what the project is, what is mid-flight |
| **Just finished** | 2–5 bullets, this session's completed work only |
| **Next step** | the first concrete action a cold session can take, zero questions |
| **Watch out** | live traps only — gotchas that will bite the next session |
| **Waiting on user** | pending decisions, each with what it unblocks |

Hard rules baked into the command: overwrite, never append (history lives in
git); ≤80 lines, aim for 40; written for a stranger — exact paths, runnable
commands, no session shorthand.

**Resuming** — the SessionStart hook (it fires on every session start,
resumes included) looks for `HANDOFF.md` in the directory the session started
in, then at the git toplevel:

- Found, and its first line starts with `# HANDOFF` → injects the file (capped
  at 120 lines), plus a computed reality check (branch, `git status` with an
  honest "N more" count when truncated, last 5 commits) with the instruction to
  trust the computed state over the file if they disagree.
- Not found → the hook stays completely silent. Projects opt in simply by
  having a `HANDOFF.md`, which the first `/handoff:handoff` run creates.
- A pre-existing, unrelated file named `HANDOFF.md` is ignored (it won't start
  with `# HANDOFF`) and this plugin will not touch it uninvited.

## Why not just rely on memory / compaction?

Compaction summarizes a conversation; it doesn't survive `/clear`, machine
switches, or weeks away. A handoff file is deliberate: it records the *state of
the work* (not the chat), it's version-controlled with the code, and it costs
one short file read at session start instead of a long summarized context.

## Tips

- The command saves the file but never commits it — that's your call, and there
  are two sane modes. **Solo / cross-machine:** commit it with your work
  (`docs: update handoff`) so other machines resume from it. **Shared branches:**
  a mutable per-session file invites merge conflicts and stale state from
  whoever saved last — consider adding `HANDOFF.md` to `.gitignore` and keeping
  it local-only.
- Durable project facts (conventions, long-lived gotchas) belong in `CLAUDE.md`
  or your project docs, not in `HANDOFF.md` — the command keeps at most a
  one-line pointer. The file describes *now*, nothing else.
- Works fine outside git repos too; the reality check just shows nothing.

## Files

```
handoff/
├── .claude-plugin/plugin.json   # plugin manifest
├── commands/handoff.md          # /handoff:handoff
├── hooks/hooks.json             # SessionStart: inject HANDOFF.md + git reality check
└── README.md
```
