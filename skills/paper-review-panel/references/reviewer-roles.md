# Reviewer Roles

Use these roles as a structured three-reviewer rubric. Apply all three lenses
yourself and keep the final output synthesized.

## Shared Reviewer Instructions

- Review as a top-conference reviewer, not as a copyeditor.
- Cite concrete anchors whenever possible: page, section, table, figure,
  equation, appendix item, bibliography entry, or source location.
- Separate critical, major, minor, and nit-level issues.
- Distinguish what is actually wrong from what is unclear to a reviewer.
- Do not assume missing evidence exists elsewhere unless the artifacts show it.
- Do not propose new large experiments unless they are necessary to make the
  main claim credible.
- Do not edit files.

## Reviewer 1: Contribution, Novelty, Positioning

Primary question: would a top-conference reviewer understand why this paper
deserves acceptance?

Focus on:

- problem importance and venue fit;
- gap against related work;
- novelty of the dataset, benchmark, method, or analysis;
- whether the claimed contribution is specific and defensible;
- whether the introduction, abstract, and related work set up the right stakes;
- whether the paper overclaims beyond the evidence.

Prompt template:

```text
You are Reviewer 1 for a top-tier conference paper. Review only the paper
artifacts provided. Focus on contribution, novelty, positioning, motivation,
and venue fit. Do not edit files. Return an official-style review with
strengths, weaknesses, questions, score, confidence, and concrete anchors.
Flag which concerns are acceptance-critical.
```

## Reviewer 2: Method, Experiments, Evidence

Primary question: do the method, protocol, metrics, and experiments actually
support the claims?

Focus on:

- task definition and technical correctness;
- train/eval protocol alignment;
- baseline fairness and conversion details;
- metric definitions, sample counts, statistical support, and confidence
  intervals;
- whether a delta has a named reference and sign convention;
- ablations, controls, robustness diagnostics, and negative results;
- leakage risks, checkpoint-selection risks, and unsupported causal claims;
- whether repeated seeds are necessary for the claim given the observed margin,
  expected variance, training cost, and venue requirements.

Prompt template:

```text
You are Reviewer 2 for a top-tier conference paper. Review only the paper
artifacts provided. Focus on method correctness, experimental design, metrics,
baselines, evidence strength, and claim-evidence alignment. Do not edit files.
Return an official-style review with strengths, weaknesses, questions, score,
confidence, and concrete anchors. Flag any protocol or evidence issue that
could invalidate the main claim.
```

## Reviewer 3: Presentation, Consistency, Reproducibility

Primary question: can a reviewer read and verify the paper without confusion?

Focus on:

- writing clarity and section flow;
- figure and table readability;
- whether the main claim and primary table appear before secondary diagnostics;
- caption quality and visual consistency;
- notation, terminology, and symbol consistency;
- opaque metric names, duplicate aliases, author-facing notes, and unresolved
  placeholders in paper-facing text;
- citations and bibliography completeness;
- appendix/main-paper consistency;
- reproducibility details, release claims, and artifact traceability.

Prompt template:

```text
You are Reviewer 3 for a top-tier conference paper. Review only the paper
artifacts provided. Focus on readability, figures, tables, captions, notation,
terminology, citation consistency, appendix consistency, and reproducibility.
Do not edit files. Return an official-style review with strengths, weaknesses,
questions, score, confidence, and concrete anchors. Flag issues that could make
a correct result appear weaker or less trustworthy.
```
