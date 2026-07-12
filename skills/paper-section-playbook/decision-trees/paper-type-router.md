# Paper Type Router

Use this tree to decide which Introduction variant (in `sections/introduction.md`) applies.

## Step 1 — What is the primary contribution?

- **A new method that improves performance on an existing task** (most collab-perception papers, BEVFormer, DETR for detection).
- **A new task / new problem setting** (HEAL defines "open heterogeneous collab perception"; SAM defines "promptable segmentation").
- **A new representation** (NeRF; Gaussian Splatting).
- **A new dataset / benchmark** paired with baselines.
- **A new system / foundation model** spanning task + model + data (SAM).
- **A new analysis / insight** that reinterprets existing work.

## Step 2 — Pick the Intro variant

| Contribution type | Variant | Rationale |
|---|---|---|
| New method (single axis) in CV / 3D / AD | **A — Limitation-driven new-question** (default) | Matches PHCP, GenComm, Where2comm, HEAL. |
| New method with two orthogonal mechanisms | **B — Two-motivation parallel** | Matches BEVFormer (spatial + temporal). |
| New task (novel setting) | **A**, but name the new setting explicitly in P2 and coin a handle for it (HEAL: "open heterogeneous"). |
| New dataset | **A**, but add a 4th contribution bullet naming the dataset; keep quantified experimental bullet last. |
| New representation | Out of scope default — consider Variant C (NeRF-style, compressed methodological). Ask the user before drafting; do not auto-apply. |
| New foundation-model / system | Out of scope default — consider Variant D (SAM-style, analogy-scaffolded with pillar sub-paragraphs). Ask the user before drafting. |
| Removal-of-components pitch | Consider Variant E (DETR-style running-prose contributions). Requires a very crisp "what we no longer need" story. Ask the user. |

## Step 3 — Sanity checks

- If two "axes" collapse to one mechanism with two properties, use A, not B.
- If the "new task" is a minor re-parameterization of an existing setting, use A and skip the task-coining move; reviewers punish inflated task-novelty claims.
- If the paper has both a new method and a new dataset, lead with the one that is more defensible under review; the weaker of the two goes into P5 and the 4th contribution bullet.
