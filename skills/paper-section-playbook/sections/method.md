# Method

Structural playbook for the Method section of a paper in CV / 3D perception / autonomous driving (CVPR / ICCV / ECCV / NeurIPS / CoRL).

For sentence-level polish, defer to `paper-refinement-skills`.

Sources: PHCP (arXiv:2509.09310), GenComm (arXiv:2510.19618), Where2comm (arXiv:2209.12836), HEAL (arXiv:2401.13964), DETR (arXiv:2005.12872), NeRF (arXiv:2003.08934), and BEVFormer (arXiv:2203.17270), plus `references/design-rationale.md`.

## Section skeleton (default)

The Method section follows this order:

1. **M1 — Opener + Problem formulation (hybrid).** A short opening paragraph that names the framework, references the main architecture figure (Fig. 2 or similar), and enumerates all submodules in one sentence. Follow immediately (or within the same subsection) with a **minimum-necessary** problem formulation: task-level inputs, outputs, agent setting, and the symbols needed by later subsections. Do not load every symbol here; subsection-internal symbols are defined inline at first use.
2. **M2 — Overall framework subsection.** A subsection (e.g., "Overall Framework" or "Framework Overview") that walks the reader through the pipeline as a block of equations tying the named submodules together (follow HEAL Eq. 1 / GenComm Eq. 2 block pattern). This subsection anchors every named submodule in a single forward pass.
3. **M3 … Mk — Submodule subsections.** One numbered subsection per major submodule. Each follows the three-paragraph structure defined in the next section.
4. **M_last — Training.** A dedicated subsection covering the total loss and training strategy. See "Training subsection" below for the one-subsection vs. two-subsection decision.

Exemplar anchors: Where2comm (Sec. 3 Problem Formulation → Sec. 4 with 4.1…4.6), HEAL (Sec. 3 prose formulation → Sec. 4 with 4.1–4.2 and embedded losses), GenComm (Sec. 3 formulation → 4.1 overview → 4.2 components → 4.3+4.4 training), BEVFormer (Sec. 3 opener → 3.1 overall → 3.2–3.5 components → 3.6 implementation).

## Minimum-necessary symbol list (M1 rule)

At the end of M1, the reader must know:

- How many agents / views / frames the method operates on.
- What each agent observes (sensor input) and produces (feature, detection, or ego-side output).
- The top-level operators that later appear in the pipeline equation (e.g., `enc`, `fuse`, `head`, or named Φ, Γ, etc.).
- The high-level optimization objective in one equation, if the paper reformulates the task (Where2comm, GenComm do this).

Do not yet introduce submodule-internal parameters, loss weights, or hyperparameters. They belong where they are used.

## Per-submodule paragraph structure (three-paragraph rule)

Each numbered submodule subsection follows this three-paragraph structure:

1. **P1 — Sub-problem statement.** State the specific sub-problem this module solves in 1–3 sentences. Tie it back to a limitation from the Introduction when possible. Do not begin with "We propose ..."; begin with the problem the reader already feels (e.g., "Features from heterogeneous encoders live in different spaces; directly fusing them degrades accuracy.").
2. **P2 — Input / output + operation.** Declare the input tensor, the output tensor, and the operation relating them. Introduce any submodule-internal symbols at first use. Prefer one to three numbered equations that are sufficient to specify the operation. The reader should be able to re-implement the submodule from this paragraph alone (up to architecture-level details deferred to Training).
3. **P3 — Design rationale.** Justify the specific choice made. Either refute an alternative ("we use additive fusion rather than multiplicative fusion, because …"), ground the choice in an observation ("feature-map visualization in Fig. N shows that channel and spatial attention dominate the domain gap, which motivates CBAM"), or cite a downstream experiment ("ablated in Sec. X"). A non-obvious design choice without rationale is a reviewer red flag.

Keep paragraph count consistent across submodules in the same paper. If one submodule needs pseudocode-style procedural description, extract it to the Appendix (see "Pseudocode policy") and keep the main-text paragraph structure uniform.

### When a submodule has 2–4 named internal components

Use **numbered subsection for the submodule itself** (e.g., 3.3 Spatial confidence-aware communication) and **bold inline sub-headings for its internal components**, following the Where2comm pattern:

```
### 3.3 Spatial confidence-aware communication

**Message packing.** <one to two paragraphs> ...

**Communication graph construction.** <one to two paragraphs> ...
```

Why hybrid: numbered subsections are navigable (reviewers can point to "Sec. 3.3"); bold inline headings keep component descriptions dense without subsubsection depth. Avoid nesting to subsubsection depth (3.3.1, 3.3.2) unless each internal component is itself multi-paragraph with its own equations and rationale.

Exemplar anchor: Where2comm Sec. 4.3 (arXiv:2209.12836).

### Overview-layer vs submodule-layer rhetoric

Bold-inline sub-headings are for the **submodule layer** only. At the **overview layer** (the paragraph that introduces a submodule's goal, constraints, and invariants before its component decomposition), prefer *derivational prose* over labeled announcements:

- ❌ `\textbf{Key design property.}` or `\textbf{Magic point:}` opening a micro-paragraph that states an invariant (e.g., identity initialization, equivariance, monotonicity). This reads as a ceremonial "look at our cleverness" flag.
- ❌ Three-stage signpost written as `Three stages: 1) ... 2) ... 3) ...` or with `(i)(ii)(iii)` enumeration.
- ❌ Deployment / setting constraints written as a bulleted or `(i)(ii)(iii)` list inside the overview paragraph.
- ✅ Let the invariant *emerge* as the conclusion of a stated constraint chain: "Because ..., a large ... would ... . We therefore require $\mathcal{P}_\theta$ to ...". The centered equation alone is sufficient visual anchor.
- ✅ If a stage summary is needed, use one compact sentence with commas or semicolons: "$\mathcal{P}_\theta$ proceeds through X, Y, and Z, with each stage built so that ...". If the surrounding prose already lists the stages, do not repeat the list; state only the functional division of labor.
- ✅ Weave constraints into prose with causal connectives ("while ...", "Because ...", "relying on neither ... nor ..."), not as a bulleted rationale dump.

Rationale: bold-inline headings at the overview layer compete with the submodule-layer bold-inline headings and visually "flatten" the two rhetorical tiers. The overview should establish *why* the decomposition is inevitable; the submodules should carry *what each piece does*. Decomposition belongs at the submodule layer, not the overview.

Rationale: preserve a visible hierarchy between the causal overview and the component-level implementation details; see `references/design-rationale.md`.

## Training subsection

Always a dedicated subsection (or pair of subsections) at the end of Method. Choose between one-subsection and two-subsection style based on training complexity:

**One-subsection style (default — follow Where2comm 4.6, BEVFormer 3.6).**

Use when: single-stage training, one total loss with a few terms, a handful of hyperparameters.

Content in order: total loss formula → per-term meaning → optimizer and learning-rate schedule → key hyperparameters (batch size, epochs, warm-up, weight decay) → any special training detail (curriculum, bandwidth sampling, data augmentation tied to the method).

**Two-subsection style (follow GenComm 4.3 + 4.4).**

Use when: multi-stage training (e.g., homogeneous pretrain → heterogeneous fine-tune, or teacher-student), multiple loss groups per stage, explicit per-stage hyperparameters.

Split into:
- "Training strategy" subsection: prose description of each stage, what is frozen / unfrozen, data used per stage.
- "Loss function" subsection: per-stage loss formulas, weighting, and loss-term definitions.

**Decision rule.** If the training description can be written in roughly one page with one main loss equation, use one subsection. If explaining the staging is itself a conceptual contribution or the loss splits into more than two per-stage formulas, use two.

**Mandatory contents regardless of style:**

- Total loss formula with every weight α, β, … defined.
- Per-term loss definitions (detection loss, regression loss, auxiliary loss) with the underlying form (focal / smooth-L1 / cross-entropy / MSE).
- Optimizer, learning rate, schedule, number of epochs, batch size.
- Anything that is non-standard for the venue (custom loss, custom sampler, staged schedule).

A reviewer must be able to estimate reproducibility from this subsection alone. Missing hyperparameters, missing per-term loss forms, or a total loss with undefined weights is a reviewer red flag.

## Pseudocode policy

Pseudocode / `\algorithm` blocks **do not appear in the main text**. Move them to the Appendix. Rationale: PHCP (arXiv:2509.09310) uses Algorithms 1 & 2 as the primary vehicle in Method, and the structure is characterized as loose; all other six exemplars use equations + prose.

If a procedural description is important enough that you want it visible, include it in the Appendix and reference it from the main text as "(Appendix A, Algorithm N)". In the main-text Method, describe the procedure with equations plus numbered prose steps (not `\begin{algorithmic}`).

## Figures in Method

- The main architecture figure (Fig. 2 or similar) is referenced in M1 (the opener). It should show all major submodules at a glance.
- Each submodule may reference a dedicated panel of the main figure, or a separate figure for its specific operation. Follow BEVFormer Fig. 2 (a) (b) (c) pattern, where each panel is re-referenced in its own submodule.
- Do not introduce a Method figure that is never referenced in its specific subsection; floating figures are a polish-pass cleanup item but originate in poor Method authoring.

## Notation discipline (cross-cutting rules)

The single largest class of reviewer complaints about Method writing is notation failure. Follow these rules without exception.

- **Define every symbol at its point of first use.** Inline in the same paragraph or immediately after the equation. Never introduce an undefined symbol — not in the figure caption, not in an equation, not in a pseudocode block.
- **Reuse symbols consistently across subsections.** Feature tensor `F_i` should remain `F_i` in every subsection that refers to it. Subscript / superscript conventions (agent index `i`, round `k`, time `t`) are fixed once and reused.
- **Preserve math styling conventions.** Parameter symbols, vectors, matrices, and random variables must keep the formatting established at first definition. Do not accidentally bold a scalar parameter or unbold a vector when rewriting prose around equations.
- **No symbol collision.** If `S` is the feature space in one paragraph, it cannot be the support set three paragraphs later. This was flagged as a red flag in PHCP (arXiv:2509.09310) where `𝒮` is overloaded.
- **Composite operators must be decomposed explicitly.** If `Γ_{j→i}(·)` bundles "transmit + spatial-transform + compress", name the sub-operations in the same paragraph where `Γ` is defined, even if you never use the sub-names later. Flagged in HEAL (arXiv:2401.13964) where `Γ` is used as a black box.
- **No silent symbol switch between Problem Formulation and pipeline equations.** If Sec. 3 defines the learnable network as `Φ_θ` in the optimization problem, the Sec. 4 pipeline equations must either (a) keep `Φ_θ`, or (b) include a one-line mapping "`Φ_θ = f_enc ∘ f_fuse ∘ f_head`" before introducing the function names. Flagged in GenComm (arXiv:2510.19618) where `Φ_θ` and `f_enc / f_gen / ...` are never bridged.
- **Do not re-define a symbol that was already defined earlier.** Refer back with "(Eq. N)" rather than restating the verbal definition.
- **Freeze-markers (stars, bars, tildes) are introduced once, in prose.** If `Φ*` means frozen, say so at first use and keep the convention.
- **Make non-trivial physical or topological location explicit in the equations themselves.** If an operator's *location* (which side of a network boundary it runs on, before/after a frozen block, on the sender vs receiver in a transmission setting, on a server vs a client) carries semantic weight, encode it in the formula via a directional subscript (e.g., `F_{i\to j}`, `g_\mathrm{server}`) or a one-line text convention placed immediately under the equation. Do not let the reader infer location only from the schematic figure: the equation must be self-contained when read in isolation. Whenever you introduce a `\to` / `\mapsto` / `\leftrightarrow` subscript for one such operator, also state in prose what the arrow's two sides denote (e.g., "sender → receiver", "source → target"), so the convention is locked at first use.

Run these checks at the notation-audit pass, before submission:

1. Walk every equation in order. For each symbol, confirm it is defined on or before this line.
2. For each named operator (`enc`, `Φ`, `Γ`, `f_gen`, …), confirm it is defined exactly once.
3. Search the Method for every symbol used in the Introduction's math (if any) and confirm they match.

## Claim–experiment alignment (cross-cutting rule, inherited from Introduction)

Every design choice described in Method must be traceable to a corresponding experimental validation:

- A submodule introduced with a design rationale must appear in an ablation table in Experiments. If the ablation does not exist, either add the ablation or soften the Method claim to "we adopt X following prior work" (no rationale claim, no ablation needed).
- A training-strategy claim (e.g., "two-stage training is necessary") must appear as a row in an ablation (with vs. without the second stage). Claiming necessity without the ablation is a reviewer red flag.
- A loss-weighting choice (α, β) that the paper emphasizes as important must appear in a sensitivity table.
- Named ablation variants must be defined at first use and in the relevant caption. If a variant changes the input prior, the noise process, the training corruption, or the inference schedule, state exactly which factor changes and which factors are held fixed.
- Any claim in Method that does not map to a table or figure in Experiments should be marked for deletion or softening.

Before submission, annotate each Method subsection with the table / figure / ablation that supports it. If a subsection has no supporting experiment, it is either under-validated or overclaimed.

## Self-review checklist (run before declaring a Method draft done)

- [ ] M1 opens with a concrete framework-name sentence and a Fig. 2 reference, not with a restatement of the Introduction.
- [ ] Minimum-necessary symbols are defined by end of M1: agent count, per-agent input, per-agent output, top-level operators, optimization objective (if reformulated).
- [ ] Problem formulation is task-level and method-agnostic; it does not assume paper-specific modules before those modules are introduced.
- [ ] Overview prose does not duplicate a stage list already stated nearby.
- [ ] Every submodule follows the three-paragraph structure (sub-problem → operation → rationale).
- [ ] Every non-obvious design choice has an explicit rationale paragraph tied to an experiment.
- [ ] Every submodule has a corresponding ablation or table in Experiments.
- [ ] Composite operators are decomposed inline at first use.
- [ ] No silent symbol switch between problem formulation and pipeline equations.
- [ ] No symbol collision anywhere in the Method.
- [ ] Math styling is consistent for parameters, vectors, matrices, and random variables.
- [ ] Every named component has one consistent name across all Method subsections and in the Introduction's contribution bullets.
- [ ] Any ablation variants named in Method are defined by the changed factor and the held-fixed factors.
- [ ] Training subsection contains total loss with defined weights, per-term loss forms, optimizer, schedule, epochs, batch size.
- [ ] No pseudocode in main text; Appendix Algorithm reference if needed.
- [ ] Main architecture figure is referenced from M1; sub-figures (if any) are referenced from the submodule that uses them.
- [ ] Every figure and table in Method is cited in prose at least once.
