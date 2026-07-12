# Review Checklist

Use this checklist for deep reviews, readiness audits, or when the paper is
close to submission.

## Contribution And Positioning

- Is the central problem clear by the end of the introduction?
- Is the paper's contribution specific rather than a list of components?
- Does related work make the gap obvious without strawman comparisons?
- Is the claimed novelty believable for the target venue?
- Are limitations acknowledged without weakening the main claim unnecessarily?

## Related Work And Novelty Risk

- For high-risk reviews, was a recent-literature audit run instead of relying
  only on memory or the paper's current bibliography?
- Were direct and adjacent recent works searched with terminology variants,
  older names, acronyms, and neighboring task expressions?
- Are close works classified as direct competitor, claim limiter, table
  candidate, prose citation, background, or irrelevant?
- Does the paper avoid first/SOTA/only-new-benchmark language when adjacent work
  limits that claim?
- Are missing or ambiguous citations framed as reviewer risk with source
  coverage limits?

## Claims And Evidence

- Does every main claim point to a table, figure, experiment, theorem, dataset
  statistic, annotation audit, or citation?
- Are negative or mixed results framed honestly?
- Are appendix diagnostics used as diagnostics rather than main proof?
- Are deployment, robustness, calibration, generalization, or causality claims
  supported narrowly enough?

## Method And Protocol

- Is the task definition explicit?
- Are inputs, outputs, supervision, and inference-time information legal?
- Are train and evaluation protocols aligned?
- Are preprocessing, coordinate systems, prompts, model checkpoints, and
  conversion steps described enough to avoid ambiguity?
- Is there any hidden leakage from labels, future information, target actions,
  or evaluation artifacts?

## Experiments And Metrics

- Are baselines fair and clearly labeled?
- Are metrics defined with directionality and units?
- Are sample counts, splits, and checkpoint policies consistent?
- Are ablations tied to the main mechanism?
- Are confidence intervals, paired comparisons, or stratified analyses used
  when small deltas drive the conclusion?
- Are command/class imbalance and metric disagreement handled explicitly?

## Figures And Tables

- Can each figure/table be understood without reading long surrounding prose?
- Are captions concise and claim-aligned?
- Are colors, arrows, deltas, and highlights semantically consistent?
- Are table values traceable to artifacts?
- Are plot axes, units, legends, and labels consistent?
- Are PDF-rendered figures/tables unclipped and readable?

## Writing And Structure

- Does the abstract state problem, gap, contribution, and evidence clearly?
- Does each section have one job?
- Are terms and symbols introduced once and used consistently?
- Are paragraphs cohesive rather than run-log fragments?
- Are citations present for factual comparisons and related work claims?

## Reproducibility And Appendix

- Are released artifacts, review scope, and dataset terms stated precisely?
- Do appendix tables agree with main-paper numbers?
- Are qualitative examples representative and not overclaimed?
- Are draft markers, internal logs, and implementation notes removed from
  paper-facing text?
- Is the appendix useful as evidence and reproducibility support, not a hidden
  rebuttal?
