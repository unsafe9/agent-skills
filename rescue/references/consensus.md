# Consensus mode

Gather independent perspectives from all three backends, then synthesize a single
conclusion. Treat the request as the question or proposal to evaluate.

## Roster

Three perspectives run in parallel on the same question but in isolation — no
perspective sees another's response. Isolation prevents anchoring and forces genuine
diversity.

One of the three is the **host backend** — the system this skill runs under. Its
perspective runs natively: a subagent is already a fresh, independent instance of that
system, so it reasons directly with no CLI call. The other two are reached through
their CLIs.

- **Host backend** (`claude` on a Claude Code host, `codex` on a Codex host, `gemini`
  on a Gemini/Antigravity host) — a subagent reasoning natively; no CLI.
- **Each non-host backend** — a subagent forwarding to that backend's CLI per
  `{{SKILL_DIR}}/references/codex.md`, `gemini.md`, or `claude.md`.

All three are analysts, not implementers: their prompts tell them to investigate and
report only. They run in default mode — read code, search, run checks — but make no
edits. Each is a one-off fresh pass, so the CLI forwarders run **ephemeral** per their
reference's no-persist default (`claude --no-session-persistence`, `codex --ephemeral`;
`agy` has no such flag) — consensus never leaves resumable analyst sessions behind.

## Step 1 — Formulate the question

Turn the request into a clear, self-contained question or proposal. Beyond the
conversation context every spawn carries (see SKILL.md, "Context to carry"), consensus
has one addition: if the request references files or code, read the relevant content
first and embed it in the prompt — each analyst sees only what you put in the prompt.

## Step 2 — Assign stances

Each perspective gets a different stance to force adversarial analysis; without
stances, perspectives converge. Distribute so at least one argues **for** and at least
one argues **against**. With three perspectives, the third is **neutral**.

| Stance | Directive |
|---|---|
| **for** | Advocate for the proposal; build the strongest case. Still flag genuinely fatal flaws — rigorous optimism, not blind promotion. |
| **against** | Challenge the proposal; find weaknesses, risks, better alternatives. Still acknowledge genuinely strong points — rigorous scrutiny, not sabotage. |
| **neutral** | Weigh evidence proportionally. If evidence strongly favors one side, say so — accurate representation, not artificial balance. |

## Step 3 — Spawn all three in parallel

Launch all three perspectives in the same turn through the available
subagent/delegation facility, then wait for every response before synthesizing. Give
the native (host) perspective a strong, frontier-tier model — it does the real
reasoning — and the CLI forwarders a cheaper tier, since the CLI does their reasoning.

**Native (host) perspective** — spawn a subagent and give it the analyst prompt
directly:

```
You are an independent analyst. Investigate and report only; do not edit files.
<analyst prompt below>
```

**Each non-host perspective** — spawn a subagent that forwards to that backend's CLI,
pointing at the matching reference (`codex.md` for Codex, `gemini.md` for Gemini,
`claude.md` when Claude is not the host):

```
Read {{SKILL_DIR}}/references/<backend>.md and follow it to forward this analyst
request to <Backend>. Act only as the thin forwarder; return the CLI's stdout verbatim.

<analyst prompt below>
```

The analyst prompt itself carries the "investigate and report only; do not edit
files" instruction, so the forwarders need no read-only flag — the backends run in
default mode and make no changes.

### Analyst prompt template

Each perspective gets the stance directive plus this structured-output contract:

```
You are one of several independent analysts evaluating the same question. Your
response will be synthesized with other perspectives. Investigate and report only;
do not edit files.

## Stance
{stance_directive}

## Question
{question_with_full_context}

## Response Format
Respond in exactly this structure:

### Verdict
One sentence: your overall assessment.

### Analysis
Evaluate across these dimensions (skip any that are irrelevant):
1. Technical feasibility
2. Implementation complexity and risks
3. Alternatives and trade-offs
4. Long-term implications (maintenance, scalability, evolution)

### Confidence
X/10 — brief justification and what uncertainties remain.

### Key Takeaways
3-5 bullets: the most critical insights, risks, or recommendations.
```

## Step 4 — Synthesize

After **all** perspectives respond, synthesize into one conclusion. Do not
concatenate — compare, contrast, and adjudicate. Attribute points by backing system:
**Claude**, **Codex**, **Gemini**.

#### Agreement
Points where perspectives converge despite different stances. Convergence from
adversarial analysis is a strong signal — highlight with high confidence.

#### Disagreement
For each divergence: state both positions and their assigned stances; separate
stance-driven arguments from genuine analytical differences; adjudicate which is
stronger given the user's context, and why.

#### Confidence
Report each perspective's confidence score side by side. Large gaps are informative —
a 3/10 on an "against" stance suggests the proposal is strong.

#### Consensus Conclusion
A clear, actionable recommendation integrating the strongest arguments — not a
compromise, but the best answer that survives adversarial scrutiny. If perspectives
agree despite opposing stances, say so directly. If they fundamentally disagree beyond
their stances, explain the trade-off and give your own reasoned recommendation.

## Step 5 — Present

Show the synthesis directly, concisely formatted — not a wall of text. Do not show raw
perspective responses unless the user asks.

If a backend's CLI is unavailable, proceed with the remaining perspectives and note
which one was skipped.
