---
name: rebuttal-response-skills
description: Use when drafting, revising, compressing, planning, or stress-testing rebuttals and author responses for AI, vision, robotics, or autonomous-driving venues. Enforces complete issue coverage, concise reviewer-specific strategy, verified evidence, no fabrication, and no overpromising.
license: MIT
---

# Rebuttal Response Skills

## Core Goal
Produce a safe, concise, evidence-grounded author response that improves acceptance probability without overclaiming, fabricating, or wasting space.

## Non-Negotiable Gates
1. **Provenance gate**: every factual claim must map to one source: paper text, appendix/supplement, code, log/result file, user-confirmed result, or explicitly marked future work.
2. **Commitment gate**: every promise must be either already done, explicitly approved by the user, or framed as future work / limitation.
3. **Coverage gate**: every reviewer concern must end in one of: answered, answered with narrow concession, deferred intentionally, or needs user input.
4. **Tone gate**: no defensive phrasing, no "the reviewer asks/notes" unless needed for disambiguation; answer the concern directly.
5. **Limit gate**: respect page / character / per-reviewer limits. If over limit, compress by removing explanation before removing evidence.
6. **External-evidence gate**: when a response depends on a citation, related-work claim, or reference authenticity that is not already verified in the paper artifacts, use `$research-evidence` before drafting the visible claim.

## Workflow

### 1. Normalize Inputs
Collect:
- venue and exact format rule: one shared response vs per-reviewer threads; page/word/character limit; PDF vs text-only; anonymity.
- raw reviews, reviewer IDs, scores, confidence, stance.
- paper source, supplement, key tables, logs, and existing ablations.
- user-approved new experiments and results.

### 2. Build an Issue Board
For each concern, record:
- reviewer ID and raw anchor quote.
- issue type: clarity, assumption, novelty, mechanism, ablation, baseline, statistics, efficiency, reproducibility, limitation, writing.
- severity: critical / major / minor.
- reviewer priority: pivotal if the reviewer is borderline/negative and the concern is addressable.
- response mode:
  - `direct_clarification`: reviewer missed or misunderstood existing content.
  - `appendix_pointer`: answer mostly exists in appendix/supplement.
  - `grounded_evidence`: use a table, metric, equation, code fact, or log.
  - `narrow_concession`: reviewer is locally right; preserve the main claim.
  - `structural_distinction`: show why the method is not reducible to a generic baseline.
  - `future_work_boundary`: outside scope, not claimed, but reasonable extension.

### 3. Strategy Before Drafting
- Decide structure: reviewer-wise when reviewers are distinct; issue-wise only when many concerns overlap.
- Allocate space by decision impact, not by number of comments.
- Lead with shared positives only if they support the acceptance case; keep opener short.
- Prioritize the concerns that can flip a borderline reviewer.
- For each pivotal concern, identify the minimum sufficient evidence: one number, one table, one equation, or one code fact.

### 4. Draft Pattern
Default per-issue pattern:
1. **Direct answer** in the first sentence.
2. **Evidence** in 1-3 sentences, with exact appendix/table/figure pointers when content already exists.
3. **Implication**: what this resolves or what will be clarified in revision.

Preferred style:
- Use concise declarative sentences.
- Point to appendix/supplement instead of re-explaining long derivations.
- Use numbers only when they directly answer the concern.
- Avoid vague thanks before every issue.
- Avoid repeating the reviewer's wording unless needed to map a concern.
- Do not write "The reviewer asks..." or "The reviewer notes..." by default.

### 5. Evidence and Experiment Triage
Run or report a new experiment only if it is:
- directly requested or clearly decision-relevant;
- cheap enough for rebuttal time;
- interpretable under current training/eval protocol;
- not a new major contribution.

If evidence already exists:
- cite the exact appendix/table/figure/section.
- reproduce only the smallest table needed for readability.
- explain less; reviewers can inspect the referenced evidence.

If evidence is external:
- use `$research-evidence` for a focused check.
- report only verified or likely-supported claims in the visible rebuttal.
- mark unsupported or ambiguous literature claims as needs-user-input instead of improvising.

If an experiment is pending:
- do not include it as a result.
- keep a source comment/TODO separate from the visible rebuttal.
- if mentioning future work, frame as limitation, not promise.

### 6. Compression Rules
When over limit, cut in this order:
1. repeated gratitude and setup;
2. restating reviewer questions;
3. long interpretation of obvious tables;
4. implementation details already in appendix;
5. secondary metrics;
6. weak future-work statements.

Keep:
- direct answers to pivotal concerns;
- one strong numerical anchor per empirical concern;
- narrow concessions that avoid overclaiming;
- explicit pointers to appendix/supplement evidence;
- all reviewer concerns covered at least minimally.

### 7. Stress Test Checklist
Before finalizing, ask:
- Is any reviewer concern missing?
- Is any claim unsupported by paper/code/result logs?
- Is any promise not approved by the user?
- Could any sentence sound defensive or dismissive?
- Is any result vulnerable to train/test mismatch or cherry-picking?
- Is the main acceptance case clear to the area chair?
- Does the response remain anonymous and free of external links if required?

### 8. Follow-Up Rounds
For new reviewer comments:
- write a delta reply only, not a full rewrite.
- link each new comment to an existing issue or create a new issue.
- escalate technically, not rhetorically.
- concede if the reviewer is correct.
- if a reviewer is immovable and no new evidence exists, answer once and stop arguing.

## Collaborative Perception Defaults
For autonomous-driving collaborative perception papers:
- Prefer mechanism + ablation + robustness evidence over broad claims.
- Treat density / confidence / uncertainty terminology carefully; define operational meaning.
- Separate communication payload from measured latency.
- Separate local feature denoising from collaborative fusion with A/B/C diagnostics when possible.
- For modality extension questions, distinguish module generality from current supervision source.
- For distance / small-object concerns, report stratified AP if available; do not overclaim outside benchmark classes.

## Benchmark / Dataset Rebuttal Defaults
For dataset, benchmark, or reference-baseline papers:
- Keep protocol boundaries explicit. Do not mix native metrics and unified-protocol metrics in the same main comparison table unless each row is clearly labeled; call bridge baselines bridge baselines.
- Separate the dataset contribution, benchmark protocol, and reference baseline. Do not oversell a simple reference model as the main methodological contribution.
- Separate language reasoning supervision from structured prediction outputs. Do not claim raw chain-of-thought, explanations, or rationales generate final actions unless the model actually uses them as the prediction source.
- Treat mixed or negative ablations as scope evidence or appendix analysis unless they directly support the main claim. State the narrow interpretation before the implication.
- For annotation-quality concerns, answer with provenance, audit gates, human-review scope, sample counts, and failure-repair policy. Avoid vague phrases such as "we manually checked" without describing what was checked.
