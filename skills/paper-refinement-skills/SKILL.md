---
name: paper-refinement-skills
description: Use when refining research-paper prose or section logic, including abstracts, introductions, related work, methods, captions, conclusions, and rebuttals. Improves clarity, concision, transitions, terminology, notation, and venue-appropriate style without inventing evidence.
license: MIT
---

# Paper Refinement Skills

## Overview

Use this skill when revising academic papers section by section. Preserve verified technical claims, keep terminology consistent, and adapt tone and density to the target venue.

## Workflow

1. Read the target sentence, paragraph, and immediate surrounding context before editing.
2. Identify whether the problem is structural or local: argument flow, scope, redundancy, terminology drift, or sentence quality.
3. Identify the paper story before polishing: dataset/benchmark, method, analysis, or system. Experiments should support that story, not read like a run log.
4. Freeze the claim hierarchy: one central paper claim first, with ablations,
   reliability studies, and diagnostics presented only as supporting evidence.
5. Revise conservatively: preserve verified claims, datasets, equations, and citations unless the user explicitly asks to change them.
6. When a passage is repeatedly misunderstood, fix the ambiguity at its source instead of only softening nearby claims.
7. When confusion comes from a category error, fix the category boundary before polishing the sentence. Separate dataset/protocol contents from diagnostic experiments, model design from evaluation controls, and baseline-conversion fairness from the paper's main contribution.
8. Check the revised passage against the rest of the paper for claim consistency, notation, references, figure/table links, and rendering risks.
9. After a figure or table changes, search nearby and later prose for stale
   terminology, old row names, obsolete panel structure, and implementation
   leakage. A consistent table has a matching body, caption, and local
   explanatory paragraph. If a new row is added to a delta-coded or
   reference-coded table, the prose must name the comparison reference and
   report movement in the same direction as the table cells.
10. Promote only reusable cross-paper heuristics into this skill. Keep paper-specific conventions outside the skill unless the user explicitly asks for a project-local note.

## Core Rules

- Prefer direct, claim-driven prose over long setup or component lists.
- Write manuscript content as the paper's author for reviewers. Insert only
  submission-ready prose, captions, equations, and table text. Keep advice to
  the user outside the manuscript; never insert author-facing instructions,
  editorial commentary, or internal status labels such as `TODO`, `TBD`, or
  `pending` into paper-facing text.
- Write for the paper reader, not for the experiment operator. Convert implementation steps, run bookkeeping, and parser mechanics into the smallest protocol statement needed for the claim, then move reproducibility details to appendix notes.
- Use section-aware disclosure. Main text should include only details that affect the scientific conclusion, fairness, validity, or reader interpretation. Checkpoints, runner names, guard logic, adapters, local paths, download failures, failed attempts, and engineering patches belong in Appendix or internal records by default.
- Do not sound anxious. Avoid stacking caveats in captions or result prose just because a reviewer might ask. If a detail does not change how the reader should interpret a result, move it out of the main narrative.
- Keep technical terms precise and consistent.
- Match the language to the section's altitude. Abstract, early Introduction, and Conclusion should use reader-facing claims and ordinary phrasing; reserve operator-facing protocol terms, conversion details, parser mechanics, and run-level bookkeeping for Experiments or Appendix.
- A coined or technical term carries a burden of proof. If an ordinary phrase says the same thing without losing precision, use the ordinary phrase, especially in the abstract and first-page motivation.
- Do not present ablations, controls, dry runs, parser diagnostics, conversion protocols, or resource gates as if they were core dataset or method components. State them as evaluation diagnostics, reproducibility details, or setup choices in the section where that role is clear.
- Do not leave internal implementation terms such as runner names, alias labels,
  old condition names, parser shorthand, or obsolete table logic in reader-facing
  prose unless they are necessary for reproducibility and placed in the right
  section.
- Use idiomatic, natural academic English: clear, human-sounding sentences; no awkward AI-like filler, inflated phrasing, rare words, or needless synonym swapping.
- Make prose clean and economical while preserving enough context for a reader to follow the logic.
- Do not use em dashes in paper prose; prefer full sentences, commas, semicolons, parentheses, or sentence splits.
- Use colons sparingly; avoid loose `claim: explanation` constructions when a cleaner full sentence is available.
- Match every claim to the paper's actual evidence. If a claim cannot be supported by the current experiments, citations, equations, or figures, weaken it, qualify it, or ask the user rather than inventing support.
- Avoid overclaiming, hidden guarantees, and wording that creates easy attack points. Prefer defensible formulations that state what the paper shows, under what setup, and with what scope.
- Do not fabricate references; if one is missing, use a visible placeholder instead of guessing.
- When a citation, related-work claim, reviewer-facing claim, or factual support is uncertain, use `$research-evidence` for a non-writing evidence check before strengthening or preserving the claim.
- Outside experimental sections, avoid adding concrete numbers unless they are already verified or required for correctness.
- Maintain symbol consistency and define symbols on first use.
- De-emphasize repeated secondary claims; keep them where they are needed for setup or reproducibility, not as a paper-wide slogan.
- Use one canonical name for each concept and metric. Collapse aliases that
  describe the same condition or ablation; remove a coined label when ordinary
  wording is equally precise.
- Define every non-standard metric before interpreting it. State what is
  measured, over which samples it is aggregated, its unit and direction, and
  the named reference for any delta.
- For planned but unfinished results, keep the accepted table structure and use
  `--` in unavailable cells. Remove unsupported result sentences and do not
  explain the internal completion state in the caption or manuscript prose.
- Do not treat adding numbers to a table as complete writing. First check the
  table contract: whether cells require deltas, reference labels, color
  semantics, confidence intervals, sample counts, or row-group notes. Then make
  the caption and result paragraph explain the same comparison.
- Treat baseline rows as normal method comparisons unless the qualification changes fairness, validity, or reproducibility. Disclose reproduction, conversion, checkpoint, or guard details in setup, captions, footnotes, or Appendix when they matter; do not make main-result prose sound like an incident report.
- Respect venue- or project-specific punctuation, notation, and equation conventions when they are supplied.

## Section Heuristics

- Abstract: compress to a problem-gap-method-result arc and avoid inventory-style method descriptions.
- Introduction: make the motivation concrete, isolate the gap early, and connect each paragraph to the paper's central bottleneck.
- Related Work: compare methods by limitation and relevance, not by laundry-list chronology.
- Method: define the setting first, then modules, then why each module is needed. Keep the task definition method-agnostic unless the subsection explicitly introduces the paper's instantiation.
- Experiments: distinguish setup, main results, ablations, and supplementary analysis. Keep fairness caveats factual and align every paragraph with its current table or figure.
- Dataset/benchmark papers: foreground why the dataset is needed, what annotation/evidence signal was difficult to obtain, and how experiments demonstrate the benchmark's value. Avoid letting baseline implementation details become the main story.
- Appendix: make supplementary sections reproducibility-oriented and calm; avoid turning them into hidden rebuttals.
- Captions and conclusion: prefer one clear takeaway per paragraph. Conclusions should usually close on the paper's broader claim, not on module inventory.

## References

- Read [references/refinement-guidelines.md](references/refinement-guidelines.md) before substantial revisions.
- Keep `SKILL.md` brief; put only reusable, cross-paper heuristics into the reference file.
