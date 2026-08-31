# Global conventions

## Error messages and logs

- Never put data values in error messages or logs — they may be sensitive and logs travel.
  Identify the problem with metadata only: type names, table/column/field names, counts.

## Git commits

- Do NOT add `Co-Authored-By: Claude ...` trailers to commit messages.
- Do NOT add `Claude-Session:` links or any other Claude Code metadata to commit messages.
- Do NOT add "Generated with Claude Code" footers to commit messages or PR bodies.
- Commit messages describe the change only.

## Code comments and docstrings

- Committed code never references planning artifacts: plan steps (`P3`), decision
  notes (`decision 0001`, `DECISIONS.md`), handoffs, build-order steps, ticket
  briefs in `notes/`, or anything else that lives outside the repo's committed
  files. Other people and their agents read the code without those files.
- If the referenced reasoning matters to the next reader, inline it in one or two
  sentences. If it is bookkeeping ("step 2 of the plan"), drop it.
- Test for every comment: does it still make sense to a stranger with only the
  committed repo? If not, rewrite or delete it.
- References to committed artifacts are fine: ticket IDs, migration numbers,
  files in `docs/`.

## How to write replies to me

- Use short, direct sentences. Aim for under 20 words. Split long sentences in two.
- One idea per sentence. Prefer active voice. Passive is fine when the actor is
  unknown or unimportant.
- Use plain everyday words in prose. Prefer short bullet lists over long paragraphs.
- These rules apply to prose only. Code, commands, file paths, flags, identifiers,
  API names, and error text stay verbatim in backticks. Never paraphrase or simplify
  those.
- Gloss a jargon term in parentheses on first mention, and only when I likely do not
  know it. A few words is enough. Do not gloss common tool or language terms, and do
  not repeat a gloss.
- No filler, no preamble, no restating my question.
- When you are unsure or have not verified something, say so plainly in one short
  sentence. Never state a guess as a fact. A caveat is not filler.
- These are defaults. Follow any task-specific format or exact-output request instead.

## Referring to plans, handoffs, and past decisions

Assume I remember nothing from a prior session, and that I read your replies with
no plan file open.

### Never make a bare reference

Every mention of earlier work carries three things inline: the ID, a restatement
in plain words, and where it lives.

- Bad: "Next is step 3." / "As we decided earlier." / "Per the handoff."
- Good: "Next is `P3` — add retry to `fetchUser()` (`PLAN.md:24`)."
- Good: "Per `D2` — SQLite over Postgres, because deploys are single-node
  (`DECISIONS.md`)."

If you cannot name both an ID and a file, say you are going from memory of this
chat, and quote the exact sentence you mean.

### Stable IDs

- Plan steps: `P1`, `P2`, ... Assigned once. Never renumbered. Finished steps stay
  in the file, marked `[x]`. New steps take the next free number even if they
  belong in the middle. Split a step as `P4a`, `P4b`.
- Decisions: `D1`, `D2`, ... in `DECISIONS.md`, one line each:
  `D3 (2026-08-31) — <what> because <why>. Affects P5, P6.`
- Open questions: `Q1`, `Q2`, ... When one resolves, it becomes a `D` and keeps a
  pointer back: `Q2 → D5`.

### Orientation line

Start the first reply of a new session, and the first reply after a compact, with
one line and nothing before it:

`Plan: PLAN.md · Done: P1–P4 · Now: P5 (wire up cache) · Blocked: Q2`

If there is no plan file, say that in the line.

### Echo before you act

When I say "go ahead", "do that", or "yes", restate what I just approved in one
line before you touch anything. I may have lost the thread.

### Restate options when you ask me something

When you ask me to decide, put the options and the trade-off in that same message.
Never rely on me remembering options from earlier.

### Closing a step

Say `P5 done — <what changed>, <files>.` Update the plan file in the same turn.
The file must never disagree with what you told me.
