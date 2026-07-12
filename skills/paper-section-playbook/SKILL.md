---
name: paper-section-playbook
description: Use when planning, drafting, or restructuring the Abstract, Introduction, Related Work, Method, Experiments, or Conclusion of a computer-vision, 3D-perception, or autonomous-driving paper. Provides section- and paragraph-level methodology; use paper-refinement-skills for sentence-level polish.
license: MIT
---

# Paper Section Playbook

## Scope and complement

This skill answers **"how should this section be structured and what should each paragraph do?"** for papers in CV, 3D perception, and autonomous driving venues (CVPR / ICCV / ECCV / NeurIPS / CoRL).

For sentence-level prose polish (word choice, punctuation, terminology consistency, em-dash rules, etc.), defer to `paper-refinement-skills` instead. Both skills may be active at once; this one operates at the section and paragraph level, the other at the sentence level.

## When to load this skill

- The user is planning or restructuring a paper section, not just polishing prose.
- The user asks "how do I write the Intro / Method / Experiments / etc."
- The user is rebutting a reviewer comment about section structure, motivation, or framing.
- The user wants exemplar-based guidance ("how do top papers do X").

## Routing

1. Identify which section the user is working on.
2. Read the matching file under `sections/` for the structural playbook (paragraph functions, decision tree, common reviewer red flags).
3. If the user is choosing between writing styles, consult `decision-trees/paper-type-router.md` to identify their paper type (new method / new task / new analysis / system / dataset), then apply the corresponding branch in the section file.
4. For Related Work, method motivation, experiment framing, or exemplar-based guidance, use `$research-evidence` when citation support or top-venue precedent is uncertain. Prefer CVPR, ICCV, ECCV, ICLR, NeurIPS/NIPS, and ICML before secondary autonomous-driving or robotics venues unless the topic requires them.
5. Use the worked skeletons and templates in the relevant section file when the user wants concrete patterns.
6. After drafting, run the section file's self-review checklist and `checklists/reviewer-redflags.md` for the relevant section.

## Authoring principle

Section files combine patterns from cited, high-impact exemplar papers with the
generalized principles in `references/design-rationale.md`. Treat exemplars as
evidence, not authority. Keep a rule only when it has a traceable source or a
clear rationale with stated conditions.

Do not invent generic writing advice. If a rule has no source, it does not belong here.

## Section files

- `sections/abstract.md` — authored
- `sections/introduction.md` — authored
- `sections/related-work.md` — authored
- `sections/method.md` — authored
- `sections/experiments.md` — authored
- `sections/conclusion.md` — authored

(Files appear as the corresponding section is elicited and ratified by the user.)

## Post-use feedback loop (meta-rule)

**This skill is a working hypothesis, not a fixed rulebook.** After each real paper application:

1. Record where a recommendation failed, drew justified pushback, or conflicted with venue or paper constraints.
2. If a rule produced a bad recommendation in context, do not silently follow it next time. Either:
   - **Narrow** the rule (add the condition under which it applies), or
   - **Flip** the rule's default (if the user's corrected choice is the better general default), or
   - **Remove** the rule (if it was over-generalized guidance).
3. Update `references/design-rationale.md` only when the lesson is generalizable; do not preserve private conversations, project identifiers, or dated interaction logs.
4. User-originating preferences always outrank inferred rules from exemplars.

Signals to watch for:
- "Why did you put X in Y?" → the placement rule is probably over-normative.
- "I don't need to follow this, I'll do Z instead." → the default may be wrong for this user's venue/style.
- "This feels defensive / redundant / apologetic." → the rule is adding ceremony, not substance.

When in doubt, ask the user to ratify the update before applying it to the skill file.

## Cross-skill handoff

After this skill produces a section draft or restructuring plan, hand off to `paper-refinement-skills` for sentence-level polish. Do not duplicate prose-polish rules here.
For substantial edits, also check that section-level claims still match the paper's tables, figures, citations, notation, and rendered cross-references.
