---
name: rebuttal-response-skills
description: Use when drafting, revising, compressing, planning, or stress-testing rebuttals and author responses in PDF or OpenReview Markdown. Requires exact review text, preserves reviewer order, and grounds each answer in verified paper or experiment evidence.
license: MIT
---

# Rebuttal Response Skills

## Core Goal

Write a direct, reviewer-specific author response that is easy to verify and
hard to misread. Keep evidence discipline strict internally. Do not turn that
discipline into a visible stream of disclaimers, limitations, or defensive
scope statements.

## Required Inputs

Do not draft from a paraphrase of the review.

1. Obtain the exact review text, including all available questions, weaknesses,
   scores, confidence ratings, and score-raising conditions. A supplied file or
   attachment containing the full text counts. If the user provides only a
   summary, ask only for the complete review first. Do not send a long intake
   checklist. After receiving it, discover local artifacts before asking for
   anything else.
2. Read the submitted paper and supplement, preferably the submitted PDF as the
   reviewer saw it. Use newer source files only to locate content or when the
   user explicitly identifies them as the submission.
3. Determine the official response format: shared or per-reviewer, PDF or
   portal text, page or character limit, anonymity rules, Markdown/LaTeX
   support, and whether links or attachments are allowed. Verify current
   official venue instructions when the venue is known and the rules were not
   supplied.
4. Collect only evidence that can be traced to the submission, appendix, code,
   accepted result artifacts, verified literature, or an explicit
   user-confirmed value.

## Select the Output Mode

Ask the user when the mode is genuinely ambiguous. Official venue rules
override all defaults.

### OpenReview Markdown

- Use one response per reviewer when the platform provides separate threads.
- Include reviewer ID, score, and confidence in the title when they are
  available, useful, and allowed by the platform.
- Count the complete visible response, including headings, tables, spaces, and
  Markdown, under the platform's stated rule.
- Use GFM tables for dense numerical comparisons and supported LaTeX
  delimiters for formulas.
- Check table alignment, paired math delimiters, headings, bold text, and links
  before submission.

### PDF Author Response

- Use the official template and exact page limit. One page is common, not
  universal.
- Preserve reviewer order within the shared document while allocating more
  space to decision-critical concerns.
- Compile the final source, render every page, and inspect page count, font
  size, overflow, clipping, table readability, and references.
- Do not solve overflow by making the response unreasonably small or dense.

## Map the Review Before Drafting

Read the review sentence by sentence. For each substantive point, record its
reviewer, source section, original position, premise, explicit request,
available evidence, and proposed answer.

- Preserve the visible order of the review. Meta-review priorities may change
  emphasis, but not the question sequence.
- Match labels to the source: `Q1` for Questions and `W1` for standalone
  Weaknesses. Use `S1` only when a factual premise in Strengths needs explicit
  correction and cannot be handled cleanly in the opening or a related
  question. Do not replace source-matched labels with generic labels such as
  `C1`.
- If a weakness and a question ask the same thing, answer once under the
  explicit question at its original position. Keep the duplicate mapping
  internal.
- If two explicit questions overlap but contain distinct requests, keep both
  headings. Answer the shared part once, then use the later heading only for
  the remaining request.
- Treat a declarative score-raising condition in the Questions section as the
  next `Q` item.
- Keep a separate concern map for each reviewer. Reuse a shared experiment only
  when it directly answers both reviewers; do not import one reviewer's
  requested baselines, limitations, or side issues into another response.
- Ensure every substantive point is answered, intentionally combined with a
  duplicate, or held for one necessary user decision.

## Draft Each Response

Assume the reviewer may not remember the paper in detail. Start with at most
two or three short sentences that restore only the method concept needed to
understand the answers.

For each issue:

1. Use a short heading that faithfully restates the concern.
2. Give the direct answer in the first sentence.
3. Provide the minimum explanation, evidence, formula, or experiment needed.
4. End with the concrete implication for that concern.

Writing rules:

- Prefer short declarative sentences and familiar technical words.
- Write in the authors' voice for the reviewer, not as notes to the user.
- Match the reviewer's tone. Use a cooperative tone for exploratory questions
  and a calm, factual, AC-readable tone for skeptical or low-score reviews.
- Do not criticize the reviewer or speculate about their expertise.
- Avoid repeated gratitude, long question restatements, generic transition
  sentences, and AI-sounding summaries.
- Use compact tables when prose would force the reviewer to track many values.
  Define the protocol, comparison point, unit, and direction. Bold the best
  relevant result. Do not add redundant gain rows when the best values are
  already clear.
- Report mixed or negative results honestly, then explain their narrow
  implication without hiding them or turning them into a broader claim.

## Stay on the Asked Question

- Do not volunteer unrelated limitations, missing modalities, extra tasks,
  baselines, experiments, or deployment gaps.
- Do not habitually write "we only claim", "we do not claim", or long scope
  boundaries. Use a boundary only when it corrects a material misreading,
  separates measured evidence from an estimate, or prevents an actual
  overclaim.
- Do not repeat a limitation already acknowledged by the reviewer unless it is
  part of the question being answered.
- For a request that is infeasible during rebuttal, first answer the technical
  point with current evidence or reasoning. Explain the missing protocol or
  resource in one concise sentence. Add a future-work commitment only after the
  user approves it.
- Never promise a new experiment, dataset, release, revision, or result merely
  to make the response sound complete.

## Evidence Discipline

Maintain an internal claim-to-source map even when it is not shown to the
reviewer.

- Separate submitted evidence, new rebuttal evidence, analytical derivations,
  dataset statistics, architectural reasoning, and future work.
- Trace every number to the submitted PDF, a table/CSV/log, or an explicit
  user-confirmed final value. Record user-confirmed values as such internally.
- Do not present pending runs, placeholders, expected trends, or partial
  outputs as results.
- State formulas and analytical estimates with their assumptions. Do not call
  them measured latency, accuracy, scalability, or network behavior.
- Use `$research-evidence` when a response depends on external literature,
  dataset facts, novelty positioning, or citation authenticity. Do not invent
  citations. Follow venue rules on links and normal citations.
- Add a new experiment only when it directly answers the review, fits the
  rebuttal window, uses an interpretable protocol, and does not create a new
  paper contribution.

## Resolve High-Impact Decisions

Use `$grill-me` behavior for ambiguous reviewer requests, experiment choices,
conflicting evidence, response-scope tradeoffs, or future commitments.

- Inspect the paper, review, code, logs, and official rules before asking.
- Ask one high-impact question at a time and provide a recommended answer.
- Use a reasonable documented default for non-critical choices.
- Do not make this skill dependent on Plan Mode.

## Independent Reviewer and AC Audit

For a high-stakes final response, use independent subagents when available.

1. Give each reviewer agent only the exact review, submitted paper, applicable
   venue rules, and that reviewer's response.
2. Do not provide the intended answer, prior critique, or suspected weakness.
3. Ask the agent to identify missed or reordered concerns, evasive answers,
   unsupported claims, unclear concepts, contradictions, and format violations.
4. Give an AC agent the meta-review, all reviews, and all responses only after
   the reviewer-specific audits.
5. Revise substantive problems. Do not expand the rebuttal for minor stylistic
   preferences.

If subagents are unavailable, apply the same audit yourself.

## Final Three-Pass Check

1. **Coverage and order**: every concern is mapped once, headings match the
   review, duplicates are merged, and reviewer-specific issues remain isolated.
2. **Evidence and logic**: every number and factual claim has provenance;
   comparisons are fair; estimates are labeled; no unapproved commitment,
   contradiction, or logical gap remains.
3. **Language and rendering**: sentences are direct and natural; repetition is
   removed; Markdown/LaTeX or the compiled PDF renders correctly; the exact
   character or page limit is satisfied with margin.

For a follow-up reviewer comment, write only the needed delta response. Do not
restart the full rebuttal unless the new comment changes the response strategy.

## Technical Rebuttal Defaults

- Separate communication payload from compute latency and measured network
  latency.
- Separate architecture-level scaling from measured multi-agent accuracy,
  runtime, congestion, or dataset coverage.
- Keep native and unified-protocol baselines clearly labeled.
- Use mechanism, control, and ablation evidence to explain why a method works;
  do not assign a full gain to one component when several factors change.
- Treat dataset counts and protocol audits as context, not performance evidence.
