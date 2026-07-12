# Design Rationale

This reference records reusable writing principles behind the section
playbooks. It intentionally excludes private conversations, project-specific
details, dated interaction logs, and personal preferences. Published exemplars
and venue requirements remain the primary evidence; these principles explain
how to generalize them without turning one paper's structure into a universal
rule.

## Evidence and adaptation

- Treat exemplar papers as patterns to test, not templates to copy.
- Scope every rule by paper type, venue, page budget, and available evidence.
- Prefer the venue's current requirements over a local default.
- When a recommendation fails in practice, narrow, replace, or remove it rather
  than adding an exception without rationale.

## Layered disclosure

- Abstract, early Introduction, and Conclusion carry the scientific question,
  contribution, headline evidence, and implication.
- Method and Experiments introduce precise mechanisms, comparison settings,
  controls, and diagnostics when the reader needs them.
- Appendix material carries reproduction details, extended diagnostics,
  conversion procedures, parser behavior, and implementation bookkeeping.
- Move a detail upward only when it changes the main claim, fairness, validity,
  or reproducibility judgment.

This keeps front matter readable without hiding information that affects the
paper's credibility.

## Claim and evidence alignment

- Map every contribution claim to a table, figure, ablation, or verified
  analysis before finalizing the Introduction.
- Do not present an untested benefit as a contribution.
- Keep diagnostic correlations distinct from causal conclusions unless the
  experiment directly tests the mechanism.
- Qualify novelty and "first" claims by the exact setting they cover.

## Story-first experiments

- Organize experiments around the questions needed to support the paper's
  argument, not the chronological order in which runs completed.
- Present baselines by their recognizable method names in main comparisons;
  disclose conversion, guard, adapter, and checkpoint details where they affect
  fairness or reproducibility.
- Define the comparison axis before designing a figure or table. Remove panels,
  controls, and annotations that do not help that comparison.
- It is acceptable to establish the table structure before all values exist,
  but placeholders must never be mistaken for results.

## Method exposition

- Start from the constraint or invariant that makes a design choice necessary,
  then introduce the mechanism that satisfies it.
- Keep the overview causal and reader-facing; reserve dense component headings,
  equations, and procedural detail for the submodule layer.
- Use stable names and notation across Introduction, Method, figures, tables,
  and ablations.
- Explain where non-trivial operators act when sender/receiver, server/client,
  or pre/post-module location changes the meaning.

## Section altitude and terminology

- Prefer plain reader-facing terms before the formal setup defines technical
  labels.
- Introduce each coined term once, justify why it is needed, and reuse it
  consistently.
- Keep datasets, protocols, model components, evaluation controls, and fairness
  procedures as distinct concept categories.
- Avoid ceremonial labels, invented taxonomy, and implementation history that
  does not help the scientific argument.

## Consistency pass

After changing a figure, table, or central claim, update its caption, nearby
prose, cross-references, and later interpretation in the same pass. Check that
the abstract, contribution bullets, method terminology, experiment labels, and
conclusion still describe the same evidence boundary.
