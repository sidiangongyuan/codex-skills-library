# Local S0-S5 Workflow

Use this reference when the user asks for a staged framework-figure planning
session or when the figure is important enough to need a source-faithful prompt
contract.

## S0 Paper Foundation

Goal: understand what the paper actually supports before designing anything.

Collect:

- source files or text excerpts
- target contribution claim
- modules, data types, training/inference split, losses, variables, and symbols
- evidence anchors for arrows, dependencies, and evaluation claims
- known ambiguity, missing source, or unsupported visual risks

Output a compact risk register. If the core method is underspecified, stop and
ask for the missing source.

## S1 Figure Strategy

Goal: decide what the first glance should teach.

Define:

- figure role and reader question
- primary module hierarchy
- semantic graph: entities and relationships
- visual render graph: layout regions, ordering, grouping, and connectors
- visible text contract: exact labels allowed in the figure
- caption/prose handoff: details that should not be inside the image
- style family: publication schematic, clean line art, minimal flat diagram, or
  user-specified surface style

Output candidate directions or prompt packages, but do not generate images
unless explicitly requested.

## S2 Sketch Exploration

Goal: explore diverse layouts without changing the paper semantics.

Default local behavior is text-only: propose candidate directions such as
pipeline-left-to-right, hierarchical module stack, data/model/control split,
agent loop, or uncertainty/diagnostic panel.

Generate images only if the user explicitly asks. Smoke-test artifacts or toy
outputs created for validation must be deleted after the test unless the user
asked to keep them.

## S3 Direction Select

Goal: choose or combine directions based on evidence and user preference.

Review each candidate for:

- source fidelity
- first-glance clarity
- connector correctness
- symbol consistency
- text density
- whether visual details belong in caption/prose instead

Record what to preserve, remove, simplify, or repair.

## S4 Formal Candidate Brief

Goal: turn the selected direction into a handoff-ready figure specification.

Include:

- final candidate matrix
- exact module labels and connector labels
- must-include and must-exclude lists
- allowed symbols, colors, and line styles
- prompt package or manual-redraw brief
- residual risks and required user confirmations

## S5 Candidate Image

Goal: optionally generate final candidate images.

Only run this stage when the user explicitly asks for image generation and the
source-faithful contract is ready. After S5, stop. The human owns candidate
selection, manual editing, caption finalization, and paper placement.

## Compact Output Format

For most user requests, do not expose all internals. Return:

- figure role
- reader question
- source-backed core modules
- semantic flow
- visible text contract
- style recommendation
- candidate directions
- risks
- next action
