---
description: Convene a panel of independent model advisors, then decide.
argument-hint: "[code|decision|writing|cheap|max] <what you want reviewed>"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/consult:*), Bash(mktemp:*), Bash(git rev-parse:*), Write, Read, Edit, Agent
---

Convene an advisory panel on: **$ARGUMENTS**

## 1. Pick the panel

If the first word of the arguments is `code`, `decision`, `writing`, `cheap`, or
`max`, that is the panel and the rest is the question. Otherwise choose one and
say which you chose in a single clause:

- `code` — implementation, diffs, architecture of a change
- `decision` — should we do X, which approach, business/career/strategy calls
- `writing` — posts, docs, comms, anything judged on how it reads
- `cheap` — quick sanity check, ~2 cents
- `max` — irreversible: migrations, auth, public API, anything expensive to undo

`code`, `decision` and `max` seats search the web themselves, and only when the
question actually turns on a current fact. In `cheap` only `grok` can search, so
do not rely on that panel for a version, a price, or whether a project is still
maintained. `--no-web` forces any panel offline, which only saves money on calls
that would have searched anyway.

## 2. Build the artifact

Write what the panel should judge to a temp file via `mktemp /tmp/consult-XXXXXX.md`.

The artifact is **self-contained**. The advisors cannot see this conversation, and
that is deliberate — it is what stops them anchoring on my framing. So include the
plan, diff, or text in full, plus whatever context is needed to judge it, and state
the constraints that are already fixed. Do not include my reasoning for why it is
right; that biases the panel toward agreeing.

## 3. Run the panel

Issue the `consult` call and the Claude subagent **in the same message** so they run
concurrently:

```
${CLAUDE_PLUGIN_ROOT}/bin/consult --panel <name> --question "<question>" --artifact <file>
```

The `fable` seat is never called by the script — it appears in the output as
`NOT CALLED BY SCRIPT`. Its lens is known up front (`prose` on the `writing`
panel, `conformance` everywhere else), so do not wait for the script: spawn an
Agent with `model: fable`, `run_in_background: false`, giving it the same
artifact and that lens, and requiring it to answer in the same shape:
verdict (AGREE / AGREE_WITH_CHANGES / DISAGREE), at most 3 issues with severity and
evidence, a concrete alternative if it disagrees, and what would change its mind.
If `model: fable` is not available on this plan or Claude Code version, spawn the
subagent with the session's default model instead and say so in the output.

Show all panel output inline, verbatim. Do not summarise away an advisor's reasoning.

**If `consult` exits 3, every API key is out of credit.** Stop — do not retry, do not
try a smaller panel, do not quietly fall back to answering as if a panel had run.
Tell the user plainly that the panel cannot run because the OpenRouter credit is
exhausted, show the exit-3 message (it lists which keys failed and why), and offer
to continue with a Claude subagent review instead, which bills to the Claude session
rather than OpenRouter. `consult --check-keys` shows what is left on each key.

Note when diagnosing: keys on the **same** OpenRouter account share one balance, so a
second key from that account is not a spare. `--check-keys` warns when it sees this.

## 4. Decide — this is the part that matters

One round. There is no round two. If the panel does not converge, that means the
question was underspecified, not that more opinions are needed. Say so and reframe
the question instead of re-running.

After the verdicts, output exactly these four things:

**Agreed** — what every advisor converged on. State it as settled and act on it.

**Split** — where they disagreed. For each split: my call, why, and what evidence
would flip me. I make the call. I do not hand three opinions back and ask what you
think.

**Overruled** — advisor findings I am rejecting, and why. An advisor that lacks
repo context can be confidently wrong; say so plainly rather than deferring.

**Out of scope** — real but unrelated findings. Logged, not fixed now.

Escalate to the user only when the split is a genuine judgment call with material,
hard-to-reverse cost. Style, naming, and taste I resolve myself.

If an advisor claims something about the codebase I cannot verify from context, say
plainly that the claim is unverified — and check it in the repo myself if it is
load-bearing.

Live search cuts stale answers, it does not eliminate them: an advisor can cite a
page and still misread it, and an online seat showing no `Read:` list may have
searched anyway (Google returns no citations). So keep verifying load-bearing facts
independently, and when a whole objection rests on an outdated premise, say that and
overrule the objection rather than working around it.

## 5. Log the decision

Append to `~/.claude/decisions/<repo-name>.md` (create the directory if absent; use
`_general.md` when not in a git repo). Get the name from
`basename $(git rev-parse --show-toplevel)`.

**Never write the decision log inside the repo.** Panels cover career, business and
strategy questions as well as code, and those records must not be committable or
pushable from a work repo. The log stays private and outside version control while
still being per-project.

```markdown
## <YYYY-MM-DD> — <question in one line>
- **Panel:** <name> (<seats>)
- **Verdicts:** <tally>
- **Decision:** <what we're doing>
- **Because:** <the one reason that decided it>
- **Dissent overruled:** <what we rejected, or "none">
- **Revisit if:** <the signal that would reopen this>
```

This is what stops the same question being re-litigated in three weeks. Keep each
entry under six lines.
