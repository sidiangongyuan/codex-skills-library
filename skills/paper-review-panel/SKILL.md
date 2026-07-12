---
name: paper-review-panel
description: Use when conducting a mock top-conference review, reviewer-panel audit, readiness assessment, or accept/reject risk analysis for a research paper. Synthesizes reviewer-style concerns for venues such as CVPR, ICCV, ECCV, ICLR, NeurIPS, and AAAI without editing the manuscript.
license: MIT
---

# Paper Review Panel

## Core Rule

Review by default. Do not edit the paper, mutate LaTeX, change figures, rerun
experiments, or patch files unless the user separately asks for implementation.
The output is an official-review-style synthesis plus compact revision
priorities.

## Workflow

1. Ground the review in artifacts.
   - Prefer the compiled PDF first when available; inspect layout, figures,
     tables, appendix, and references as a reviewer would see them.
   - Read the source text, bibliography, figure/table sources, logs, or result
     artifacts only as needed to verify claims and locate concrete anchors.
   - Use `$research-evidence` for citation/reference sanity checks or literature
     positioning when a review finding depends on external evidence.
   - For novelty, related-work, score-prediction, reviewer-risk,
     rebuttal-readiness, or final-submission reviews, run a recent-literature
     audit through `$research-evidence` before finalizing novelty or acceptance
     risk. Do not require this extra pass for casual local or prose-only reviews
     unless novelty or missing citations are part of the ask.
   - If only a section is provided, label the result as a partial review and do
     not score the full paper as if all sections were available.

2. Choose solo or panel mode.
   - Spawn subagents only when the user explicitly asks for subagents, a
     reviewer panel, multiple reviewers, or parallel review.
   - If subagents are not explicitly authorized, perform a solo review using
     the same three-reviewer rubric.
   - When panel mode is authorized, read `references/subagent-panel.md` and
     launch three independent read-only reviewer agents.

3. Use the three-reviewer lens.
   - Reviewer 1: contribution, novelty, positioning, motivation, venue fit.
   - Reviewer 2: method, technical correctness, experiments, metrics, evidence.
   - Reviewer 3: writing, figures, tables, consistency, reproducibility,
     appendix, reviewer readability.
   - Read `references/reviewer-roles.md` for detailed role prompts.

4. Synthesize rather than concatenate.
   - Do not paste raw subagent reviews by default.
   - Judge each concern independently: valid issue, clarity-induced
     misunderstanding, unsupported or incorrect reviewer claim, or optional
     polish.
   - Preserve concrete anchors such as section, page, table, figure, equation,
     appendix item, or source location whenever available.

5. Report in official-review style.
   - Use English by default.
   - Use venue-aware scoring when the venue is known. If unknown, use
     `Overall score 1-10` and `Confidence 1-5`.
   - End with score, confidence, acceptance risk, and compact revision
     priorities.
   - Read `references/output-format.md` before drafting the final synthesis.

## Review Standards

- Treat unsupported claims, weak baselines, missing ablations, protocol leakage,
  metric ambiguity, and inconsistent appendix/main-paper numbers as high-risk
  issues.
- For dataset and benchmark papers, separate dataset contribution, protocol
  validity, reference baseline strength, and evidence that the benchmark tests
  the claimed capability.
- For method papers, separate novelty, technical correctness, implementation
  plausibility, ablation quality, and comparison fairness.
- Do not fabricate citations or assume experiments exist. If evidence is
  missing, mark the concern as a risk or requested evidence.
- For high-risk novelty or readiness judgments, do not rely on memory or the
  paper's current bibliography alone. Use `$research-evidence` to test direct
  and adjacent recent work, terminology variants, and source-coverage limits.
- If a novelty, related-work, or citation-authenticity concern remains
  uncertain after checking, report the uncertainty as reviewer risk rather than
  treating the concern as proven.
- Read `references/review-checklist.md` for the full audit checklist.

## Reference Routing

- Read `references/subagent-panel.md` only for explicit subagent/panel requests.
- Read `references/reviewer-roles.md` for role-specific prompts and solo-review
  lenses.
- Read `references/output-format.md` before writing the final review.
- Read `references/review-checklist.md` for deep or high-stakes readiness
  audits.
