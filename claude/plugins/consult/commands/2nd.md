---
description: Get one independent second opinion from a named advisor.
argument-hint: "<seat> <what you want checked>  (seats: consult --list)"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/consult:*), Bash(mktemp:*), Read, Agent
---

Get a second opinion on: **$ARGUMENTS**

The first word is the seat. If no seat is named, pick one and say which in a clause:

| Seat | Use it for | Live search |
|---|---|---|
| `sol` | hardest reasoning, red team | yes |
| `grok` | is the premise even right — cheapest frontier seat | yes |
| `gemini` | second-order effects, big context | yes |
| `fable` | does this answer what was actually asked (subagent, free) | own tools |
| `kimi` | writing, tone, how it lands | no |
| `codex` | code only | yes |
| `glm` / `deepseek` | cheap correctness check | no |

Optional `--lens <name>` overrides the seat's default job. Lenses: `red-team`,
`blast-radius`, `contrarian`, `conformance`, `prose`, `correctness`, `strategy`.

Seats marked yes search the web on their own initiative, and only when the question
turns on a current fact — verified: they cite nothing on a pure-logic artifact. So a
version-sensitive question should go to one of those, not to `glm`/`deepseek`/`kimi`,
which answer from training data. `--no-web` forces every seat offline; it saves a few
cents only on calls that would have searched.
`${CLAUDE_PLUGIN_ROOT}/bin/consult --list` shows which is which.

## Run it

Write the artifact to `mktemp /tmp/consult-XXXXXX.md` — self-contained, no
conversation history, and without my argument for why it is right. Then:

```
${CLAUDE_PLUGIN_ROOT}/bin/consult --seat <seat> --question "<question>" --artifact <file>
```

For the `fable` seat the script returns a directive instead of a verdict; spawn an
Agent with `model: fable`, `run_in_background: false`, and require the same shape.

**If `consult` exits 3, every API key is out of credit.** Stop — do not retry and do
not answer as though a second opinion had been obtained. Say plainly that the
OpenRouter credit is exhausted, show the exit-3 message, and offer a Claude subagent
instead (billed to the Claude session, not OpenRouter). `consult --check-keys` shows
what each key has left, and warns when two keys share one account — same account
means same balance, so such a key is not a spare.

## Then respond

Show the verdict inline, verbatim. Then in three lines or fewer: what I accept, what
I reject and why, what I am doing about it. One round — no re-consulting the same
seat on the same question.

If the advisor is confidently wrong because it lacks context I have, say so directly.
A second opinion is input, not a verdict I have to defer to.

Live search reduces stale answers, it does not end them, and a seat can cite a source
it then misreads. Keep checking load-bearing factual claims yourself — the `Read:`
list under a verdict shows what it actually looked at, and an empty list on an online
seat means nothing either way (Google returns no citations even when it searched).
