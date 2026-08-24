---
description: Use when the user says they are leaving, clearing the session, or logging off, when they say the context is getting too long or about to compact, when they type /handoff, or when a meaningful chunk of work just finished and HANDOFF.md no longer matches reality.
argument-hint: "(no arguments — reads the session and git state)"
allowed-tools: Read, Write, Bash(git status:*), Bash(git log:*), Bash(git rev-parse:*), Bash(git diff:*)
---

# Handoff

Overwrite `HANDOFF.md` at the project root — the git toplevel, or the directory the
session started in when not in a git repo — so the next session starts cold with zero
context from the user. Replace the entire file every time — never append, never keep
old entries. History lives in git, not in this file.

If no `HANDOFF.md` exists yet, this run creates it — from then on the plugin's
SessionStart hook injects it into every new session in this project automatically.

## Gather (under a minute)

- The **current `HANDOFF.md`**, if any — carry forward any "Watch out" or
  "Waiting on user" item that is still true; everything else from the old file dies here.
- `git status --short` and `git log --oneline -5` — what is committed vs pending.
  (Not a git repo? Skip these; the file still works.)
- This conversation — what changed, what was decided, what broke.

## Write exactly these five sections, in this order

Title the file `# HANDOFF — <name>` where `<name>` is the repo directory
(`basename $(git rev-parse --show-toplevel)`, or the working directory's name).
Keep that exact title form — the SessionStart hook only injects files whose first
line starts with `# HANDOFF`, so an unrelated file with this name stays untouched.
Section bodies below describe what to write — they are not literal text.

```markdown
# HANDOFF — <name>

*(Overwrite this file, never append. Keep ≤80 lines.)*

## Now
One short paragraph: what this project is in one clause, and what is mid-flight
this moment. A cold reader gets oriented from this paragraph alone.

## Just finished
2–5 bullets covering this session's completed work only (commit subjects welcome).
This is not a history — older work is already in git.

## Next step
The first concrete action a fresh session can take, specific enough to start with
zero questions: file paths, the command to run, the doc to write. If every next
action is blocked, say so and name the blocking item from "Waiting on user".

## Watch out
Only traps that are still live and will bite the next session (a gotcha found
today, a half-done rename, a flaky dependency). Drop entries that no longer apply.

## Waiting on user
Pending decisions or approvals carried forward until resolved, each with what it
unblocks. Write "Nothing." if none.
```

## Rules

- **≤80 lines total; aim for 40.** If over, cut "Just finished" bullets first, then
  compress "Watch out". Shorter is better — the next session reads this before
  anything else.
- Write for a stranger: no session shorthand, no "as discussed", no pronouns without
  referents. Every path and command exact and runnable.
- A gotcha that will outlive the next few sessions belongs in the project's own docs
  (`CLAUDE.md`, a notes file — wherever this project keeps durable facts); "Watch out"
  keeps at most a one-line pointer while it still affects the immediate next step.
- This command saves the file; it does not commit. Whether `HANDOFF.md` gets
  committed, and when, is the user's call (trade-offs in the plugin README) — do not
  run git add/commit here unless the user asks.
- Finish by telling the user, in one line, that the handoff is saved and it is safe
  to clear or close the session.
