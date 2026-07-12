# Experiments Section Playbook

Domain: CV, 3D perception, autonomous driving, and collaborative perception for CVPR, ICCV, ECCV, NeurIPS, and CoRL.

## Section skeleton (default order)

```
Experiments
├── E1. Experimental Setup
│   ├── Datasets
│   ├── Baselines (SOTA + representative prior works)
│   ├── Metrics
│   └── Implementation details
├── E2. Main Results  (quantitative comparison to SOTA)
├── E3. Ablation Studies  (per-component, satisfies reviewer expectation)
├── E4. Analysis / Robustness / Scalability  (per-hypothesis, 2-3 subsections)
├── E5. Qualitative Results  (1-2 figures in main text)
└── (Limitations is NOT placed here — it lives in Appendix only; see discipline note below.)
```

**Rule.** E1–E3 are non-negotiable. E4 subsection count = number of non-trivial hypotheses worth their own figure/table (typical: 2-3). E5 may be merged into E4 if space is tight.

**Limitations placement (default).** Put detailed limitations in a **dedicated Appendix section** unless the venue requires a main-text discussion. Avoid repeating the same material in Experiments and Conclusion. The Appendix section title is normally sufficient navigation; see the "Limitations — where it lives" block below.

## E1. Experimental Setup

**Default paragraph order.** Datasets → Baselines → Metrics → Implementation details. Reason: the reader should know *what* is tested, *against whom*, and *by what yardstick* before *how*.

**Datasets paragraph.** For each dataset: (a) one-line factual description (modality, scale, split used), (b) why this dataset is appropriate for the paper's claim. Do not copy dataset papers' motivation — cite and compress.

**Baselines paragraph.** Group baselines into 2-3 families (e.g., "early fusion", "intermediate fusion", "late fusion" for collaborative perception). Present main-table rows by normal method names first. State the chosen version, source, and any re-implementation or adaptation only where it affects fairness, validity, or reproducibility; **silent unfair re-implementations are a top reviewer red flag**, but overloading every row with checkpoint, guard, adapter, or failed-run caveats makes the table read like an incident report.

**Metrics paragraph.** Primary metric first (AP / IoU / NDS / PSNR …), secondary after. If using a non-standard metric, give a one-sentence definition and a reference. Do not invent a metric only to win a table.

**Implementation details paragraph.** Hardware, framework, optimizer + schedule, epochs, batch size, key hyperparameters. Must be sufficient to reproduce within ±1 point. If any hyperparameter was tuned per dataset, say so.

**E1 page-budget rule (push-to-appendix discipline).** Under tight page limits, default-push to Appendix:
- exhaustive dataset split numerics, frame counts, sensor specs, data-augmentation menus;
- per-baseline retraining recipes and config tables;
- secondary-metric definitions (keep only the primary metric in main);
- optimizer hyperparameter grids, schedule charts, framework versions, GPU model;
- plugin / submodule architecture details (channel widths, layer counts, init scheme), unless the value is itself a claim.

What stays in main E1 (compressed): dataset names + role (e.g., V2I / V2V), the encoder / model abbreviations used in main tables (with first-use expansion + axis convention), the canonical fusion / cooperation strategy compared, the primary metric name, and **one** pointer sentence ("Full implementation details are in Appendix~\ref{app:impl}."). Everything else: appendix.

If a few lines must be added to main E1, add only protocol details that prevent misinterpretation: what is transmitted, what remains local, how corruption or packet loss is sampled, how metrics are aggregated, and whether all methods share the same masks / seeds. Do not add new claims or hyperparameter minutiae just to fill space.

**Dataset / benchmark paper storytelling discipline.** When the paper's main
contribution is a dataset or benchmark, Experiments is not a chronological
record of runs. It is the evidence layer for the benchmark story: why the
dataset is needed, which annotation or evidence signal is hard to obtain, which
controls reveal the benchmark's diagnostic value, and how baselines demonstrate
that value. Keep runner details, parser mechanics, checkpoint bookkeeping, and
engineering caveats in appendix notes unless they are needed to understand the
main comparison. For planned-but-unfinished diagnostics, lay out the final table
structure with dash-valued metric cells, then fill metrics when accepted; do not
replace the table with prose promises.

**Protocol and diagnostic terminology lives here, not in the abstract.** Once E1
has defined the dataset, split, metric, and baseline conversion policy,
Experiments may use precise terms such as `converted external baselines`,
`shared validation protocol`, `evidence-control diagnostics`, and named control
conditions. Table captions or setup prose should carry this precision so the
abstract and early Introduction can stay reader-facing. Fairness/conversion
language must be explicit where rows are compared, but it should not leak into
the abstract as unexplained jargon.

**Baseline reporting rule.** Tables and main-result prose should treat a baseline
as a method being compared, not as an engineering story. Use the method name in
the row; put fairness and reproducibility details in setup prose, captions,
footnotes, or Appendix only when those details change how the result should be
interpreted. Avoid labels such as "converted", "guarded", or "reproduced" in the
row name unless the qualifier is essential to distinguish two reported variants.

**Diagnostic controls are analysis tools.** Interpret input controls, evidence
controls, parser diagnostics, and source-attribution scores as tests of what a
metric can or cannot certify. Do not imply that generated reasoning explains a
trajectory metric, or that a control result is itself a new dataset component,
unless the paper provides direct evidence for that stronger claim.

## E2. Main Results

**Default table layout.**
- **Default: one Table per dataset.** Easier to narrate per-dataset observations, easier for ablations to reference, and avoids the page-width trap.
- **Only collapse into a wide table when** (a) datasets ≤ 2, (b) metric count per dataset ≤ 2, (c) the combined `tabular` fits within `\linewidth` with readable 7pt font. Else revert to split.
- **Never** force a two-column table across the page just to "look impressive" — reviewers spot compression.

**Row organization.** Group by method family (not alphabetical). Put prior SOTA at the end of its group; put "Ours" as the last row with `\rowcolor{LightGray}` or bold. Single-column method names, keep venue+year in a separate column so alignment holds.

**Highlight policy.** Bold the best per column, underline the second. If "Ours" is not best on every column, do **not** cherry-pick bold — being second on one metric is credible, faking first is fatal.

**Prose that accompanies the table.** Three-move structure per table:
1. **Observation move** ("Table N shows Ours achieves X% AP, +Y% over the strongest baseline Z.")
2. **Explanation move** ("We attribute this to <mechanism>, consistent with our design in Sec. M.k.")
3. **Sanity move** ("Note the gain shrinks to Y'% on subset S, which we analyze in Sec. E4.k.")

The Sanity move is what separates believable papers from overclaiming ones. **Every main-table gain must be either explained or honestly bounded**.

**Seed variance.** Single-run is the default (domain has high compute cost). Report mean ± std over ≥3 seeds only when (a) margin vs SOTA < 1%, or (b) reviewers are likely to question variance. For NeurIPS checklist, declare honestly: "We report single-run results due to compute cost; the baseline was evaluated under identical conditions."

**Communication accounting.** For communication-sensitive papers, state what the reported payload means. Distinguish native communication cost from budget-matched comparison, and distinguish payload before corruption from retained payload after packet loss / dropping when both are discussed. A table that mixes these quantities without labeling is unfair even if the numbers are correct.

## E3. Ablation Studies (per-component)

**Purpose.** Satisfy the reviewer's mandatory check: each Method claim must map to an ablation row.

**Structure.** One main ablation Table (or a small cluster of 2-3 tied tables), with rows = component on/off combinations. Columns = primary metric on the chosen dataset (usually the main dataset, not all).

**Row composition.**
- Row 1: baseline (all components off, or the simplest variant).
- Middle rows: progressively add **one** component at a time.
- Last row: full model (all components on).

Do **not** mix per-component and per-hyperparameter ablations in the same table — split into separate small tables.

**Claim-alignment rule (hard).** For every numbered submodule in Method (M2 … M_{last-1}), there must be an ablation row where that submodule is off. If a component is not ablatable (architectural rewrite), say so explicitly and justify in one sentence.

**Variant-definition rule.** Before interpreting any ablation table, state the shared conditions and the varied factor. Define named variants in the table caption or surrounding prose. For example, if rows differ by whether they use an input prior, whether training injects noise, or how many inference steps are run, say which factor changes and which remains fixed.

**Prose pattern per ablation.**
- One sentence stating which component is ablated.
- One sentence reading the table: "Removing X drops AP by Y%, confirming <Method claim>."
- If the drop is small, do not hide it — instead, frame it: "Removing X yields only a 0.3% drop, indicating X is beneficial but not the dominant factor; the stronger contributor is Y."

Reviewers respect honesty on small gains; they penalize evasion.

## E4. Analysis / Robustness / Scalability (per-hypothesis)

**Purpose.** Answer the "would X hold under Y?" questions a skeptical reviewer will ask. Each subsection is a self-contained scientific question.

**Typical subsections for collaborative perception / 3D AD papers.**
- *Robustness to localization noise* — add Gaussian noise to poses, plot AP vs σ.
- *Scalability with number of agents* — vary N, plot AP and bandwidth vs N.
- *Generalization across datasets / domain gap* — train on A, test on B.
- *Communication–accuracy trade-off (Pareto)* — plot AP vs bandwidth.

**Paragraph structure per analysis subsection (3-sentence minimum).**
1. **Question**: "We ask whether <method property> holds under <stress condition>."
2. **Result**: "Fig. N shows <observation>: our method degrades by only X% while baseline Z degrades by Y%."
3. **Interpretation**: "This supports our Method claim that <mechanism> provides <property>, because <specific reason tied to design>."

**Efficiency / bandwidth plot.** Required **only when** the paper markets "efficient" / "low-bandwidth" / "real-time" — in which case a Pareto curve (accuracy vs cost) is non-negotiable. Otherwise, report efficiency as a single number in prose and tables: "Our model runs at T ms/frame on a single A100, using B MB upload per agent."

**Figure discipline.**
- Every plot has labeled axes with units.
- Every curve has a legible legend (no 5pt text).
- Error bars or shading only if genuinely computed — **fake shading is a known red flag**.
- Caption must be self-contained: what is plotted, what conclusion to draw.

## E5. Qualitative Results

**Default budget.** Keep 1–2 qualitative figures in the main text and move supporting views to the Appendix.

**Composition rule.** Each main-text figure must satisfy one of:
- **Failure-of-baseline vs success-of-ours**: two columns of the same scene showing baseline miss (missed detection / wrong geometry) and ours correct. This is the highest-value pattern.
- **Mechanism visualization**: showing what a specific Method component *does* (e.g., attention heatmap, confidence map, decoded communication message), paired with the corresponding equation or submodule citation.

**Banned patterns (CV community consensus).**
- "Gallery" grids of N×M scenes with no highlighted failure — readers can't find the claim.
- Qualitative figures without any baseline comparison — proves nothing.
- Cherry-picked scenes without disclosing selection criterion.

**Caption pattern.** "Qualitative comparison on <dataset>. Top: baseline <name> fails to <specific failure>. Bottom: ours correctly <specific success>, enabled by <Method component>. Additional examples in Appendix C."

## Limitations — default placement

Limitations is **not** a mandatory subsection inside Experiments. Prefer a dedicated Appendix section unless the venue requires main-text treatment.

**Default placement.** Put limitations in a **dedicated Appendix section** and let the Conclusion end on the paper's implication rather than a procedural pointer. Adapt this default to venue requirements.

**Critical: distinguish three kinds of Appendix content and do not merge them.**

| Category | Purpose | Title convention | What goes here |
|---|---|---|---|
| **Scope / extensions** | Bound the claim without framing positive evidence as weakness | `Experimental Scope and Extensions` | Untested extensions, deployment assumptions, and future directions that do not invalidate the reported evidence. |
| **Limitations** | Admit real weaknesses | `Extended Limitations and Failure Cases` | Scope assumptions that break, empirical failure regimes with measured drops, genuine ceilings (e.g., "teacher-bounded gain"). |
| **Robustness analysis** | Defend against a reviewer concern with a **positive** result | `Additional Robustness Analyses` (or combined with Design, see below) | Sample-order sensitivity with small std, noise/corruption robustness, seed variance — results that show stability. |
| **Design-justification analysis** | Defend a specific design choice with a targeted study | `Additional Robustness and Design Analyses` (combined) or its own section | Precision–recall curves showing a loss term doesn't create FPs; convergence curves; component interaction studies that were too specific for main ablation. |

**Do not file robustness or design-justification analyses under a Limitations title.** Doing so signals "these are my weaknesses" when they are in fact defensive evidence. Use `Experimental Scope and Extensions` when the content is mostly scope or future deployment conditions, and reserve `Extended Limitations and Failure Cases` for measured weaknesses. This error is common and will be flagged by careful reviewers.

**Content recipe for Limitations (3–4 sentences per item, 2–4 items total).**
1. **Scope limit** — a setting where the method is *not* designed to work ("We assume synchronized cameras; async input is out of scope.").
2. **Empirical weak spot** — a measured regime where performance degrades, citing a specific row/figure ("Table 3 row 5 shows a 3% drop under extreme occlusion.").
3. **Genuine ceiling** — a design-imposed upper bound on achievable quality (e.g., "teacher-bounded gain when ego encoder is weak").
4. **Optional: future-work hook** — one sentence on how the limitation could be addressed (not a promise).

**Banned phrasing.**
- "Our method has no limitations." — instant credibility loss.
- "Our method may not generalize to unseen domains." (vague) → replace with dataset name + measured drop.
- Over-disclaiming that undermines contributions ("Our method is not actually new"). Be honest, not self-defeating.

## Cross-cutting discipline

**Claim–evidence ledger.** Before submitting, build (mentally or on paper) a two-column map:

```
Intro contribution (i)  ─► Experiments evidence
  Insight sentence       ─► none needed (framing)
  Mechanism sentence     ─► Ablation row k (Table N)
  Gain sentence          ─► Main Table M, dataset D, metric X
```

Any contribution sentence with no right-hand-side entry is overclaiming. Any table with no left-hand-side owner is decoration.

**Table / figure caption style.** Self-contained: the caption states *what* is shown, *on which dataset*, and *what conclusion to read*. A reader who scans only captions should still understand the paper's empirical story.

**Numbers in prose.** Always report numbers when claiming gains in text. Round consistently (one decimal for AP/IoU; two for mAP when small; integer ms for latency). Match the precision in the table.

**Cross-reference hygiene.** Every Table/Figure must be cited in prose before it appears, and cited at least once more in the section that analyzes it. Orphan tables are a reviewer smell.

**Single-mention appendix discipline.** Each appendix section should be referenced from the main paper **at most once**. When the same appendix is pointed to from a Method paragraph, a table caption, a Main-Results paragraph, and an Ablation paragraph, the duplication signals that the author was anxious rather than confident. Pick the *single most claim-bound location* (the place where dropping the pointer would leave the strongest unanswered "where is this analyzed?" question) and delete the other pointers. Captions and prose should not both point to the same appendix. Reverse-completeness (every appendix is referenced from somewhere) is a soft target, not a hard rule — an appendix reachable only via the appendix index/TOC is acceptable if its title carries the claim.

**Cross-section terminology lock.** Pick **one** canonical noun for each architectural concept (e.g., "fusion module" — not "fusion backbone" / "fusion strategy" / "aggregation module" used interchangeably) and lock it across abstract, intro, related work, method, captions, experiments, and conclusion. A single grep at submission time to enforce one canonical form per concept catches the most common consistency failure. Names of compared methods (`F-Cooper`, `V2X-ViT`, `HEAL`) must use the exact spelling and casing of the originating paper, identically in table cells and in surrounding prose.

**High-level-to-technical consistency.** If the abstract uses a simple phrase
such as "same evaluation setting", Experiments should define the precise version
of that phrase, e.g., common split, horizon, coordinate convention, metric, or
conversion rule. The paper may use precise terms in Experiments, but each term
must map back to a high-level claim rather than becoming a standalone slogan.

**No temporal adverb between two parallel comparison settings.** When two settings are juxtaposed (with-vs-without, prior-vs-ours, before-vs-after), avoid "subsequently / eventually / then" connecting them in prose: such adverbs imply a time order that the comparison does not actually have, and reviewers read it as a process narrative rather than a controlled comparison. Use parallel verbs ("Without the plugin every pair drops below ego; with the plugin every pair recovers...") or a single sentence with a contrastive conjunction.

**Emphasis-once rule for coined terms.** A coined term (e.g., a named gap, a named property, a named regime) is italicized with `\emph{}` exactly once — at its first formal definition site, which is normally the Introduction. Subsequent appearances in Method / Experiments / Conclusion use plain text. Re-italicizing the same term in §3.1 or in the Conclusion is a re-definition signal that contradicts the Intro definition; pick one definition site and downgrade all later occurrences to the plain term.

## Self-review checklist (run before submission)

- [ ] E1 ordering is Datasets → Baselines → Metrics → Implementation.
- [ ] Every baseline's source / config is cited where needed; re-implementation or adaptation details are disclosed without turning main rows into engineering caveats.
- [ ] Main table uses per-dataset split unless the collapse conditions are met.
- [ ] "Ours" row is highlighted; bolding reflects actual best, not cherry-picked.
- [ ] Each Method submodule has at least one ablation row (or an explicit justification why not ablatable).
- [ ] Named ablation variants are defined by the changed factor and held-fixed factors before interpretation.
- [ ] Technical fairness/conversion terms are defined in setup or captions, not introduced first in the abstract.
- [ ] Diagnostic controls are interpreted as analysis tools and are not described as dataset or method components.
- [ ] Generated reasoning is not used as a proxy explanation for trajectory metrics unless that causal link is directly tested.
- [ ] Communication cost, if reported, clearly separates native budget, budget-matched comparison, pre-corruption payload, and retained payload where relevant.
- [ ] Each Analysis subsection has a question → result → interpretation structure.
- [ ] Qualitative figure count ≤ 2 in main text; each shows a clear claim-aligned contrast.
- [ ] Scope / limitations discussion exists in a dedicated Appendix section (not in Experiments, not in Conclusion, no Conclusion pointer); real limitation items include concrete measured weak spots when available.
- [ ] Appendix Limitations section contains **only** real limitations; robustness analyses and design-justification analyses live in a separate `Additional Robustness and Design Analyses` section.
- [ ] All figures have labeled axes, legible legends, self-contained captions.
- [ ] NeurIPS/CoRL reproducibility checklist answered honestly, not optimistically.

## Exemplar anchors

- **Where2comm** (NeurIPS 2022): per-dataset main tables + robustness-to-pose-error + communication–accuracy Pareto. Gold standard for collaborative perception Experiments structure.
- **HEAL** (ICLR 2024): heterogeneous setting; strong ablation design over communication modalities.
- **BEVFormer** (ECCV 2022): clean per-dataset tables, strong Analysis section for temporal fusion ablation.
- **DETR** (ECCV 2020): minimal qualitative-figure strategy; all the argument is in ablations.
- **NeRF** (ECCV 2020): 3-row claim-evidence ledger (single quantitative table + qualitative focus) — exception, not rule.
- **SAM** (arXiv 2304.02643): Experiments-as-story; useful only as a counter-anchor for papers that *are* benchmarks themselves.

## Rhetorical templates (fill-in skeletons)

These are reusable sentence skeletons distilled from typical CVPR/ICCV/NeurIPS 3D-perception and collaborative-perception papers (Where2comm, HEAL, BEVFormer, DETR, V2X-ViT, CoBEVT). Use them as starting points; adapt vocabulary, don't invent new cues.

### E1 — Setup paragraph openers

- **Datasets.**
  - "We evaluate on {dataset A} \cite{...} and {dataset B} \cite{...}, which are the standard benchmarks for {task}."
  - "{Dataset} contains {N} {samples / sequences / scenes} collected from {source}; we adopt the official train/val/test split."
  - "To further assess {property}, we additionally report results on {dataset C}."
- **Baselines.**
  - "We compare against {N} representative methods spanning {family 1}, {family 2}, and {family 3}. For fairness, we re-train {method X} with its official config under our setting."
  - "All baseline numbers are reproduced using the authors' released checkpoints unless otherwise noted."
- **Metrics.**
  - "Following standard practice \cite{...}, we report {metric 1} and {metric 2}; higher is better."
  - "We additionally measure {efficiency metric} to quantify the communication / compute cost."
- **Implementation details.**
  - "We train for {E} epochs with AdamW, initial learning rate {lr}, batch size {B}, on {N}× {GPU}. All hyperparameters are shared across datasets unless stated otherwise."

### E2 — Main results (3-move pattern)

1. **Observation move.**
   - "Tab. {N} reports the comparison on {dataset}. Our method achieves {X}% {metric}, outperforming the strongest prior work {Z} \cite{...} by {Y}% absolute."
   - "As shown in Tab. {N}, {ours} sets a new state of the art on all {k} metrics of {dataset}."
2. **Explanation move.**
   - "We attribute this gain to {mechanism}, which addresses the {limitation} of {baseline family}, as designed in Sec.~\ref{sec:method.k}."
   - "The improvement is consistent with our motivation in Sec.~\ref{sec:intro}: {short restatement of insight}."
3. **Sanity / bounded-claim move.**
   - "The margin shrinks to {Y'}% on {subset / harder condition}, which we analyze in Sec.~\ref{sec:analysis.k}."
   - "On {metric}, our method is on par with {Z}, indicating that the gain primarily comes from {specific axis}."

### E3 — Ablation descriptions

- **Opener for the ablation subsection.**
  - "We study the contribution of each component of {model} on {dataset}; results are summarized in Tab.~\ref{tab:ablation}."
- **Per-row description.**
  - "Removing {component X} drops {metric} by {Y}% ({before} → {after}), confirming that {claim tied to Sec. M.k}."
  - "Replacing {component X} with {simpler alternative} reduces {metric} by {Y}%, indicating that {design rationale} is essential."
- **Small-gain framing (use when drop is < 1%).**
  - "Disabling {X} yields only a {Y}% drop; {X} is beneficial but not the dominant factor, with {Y'} contributing most of the improvement."
- **Hyperparameter ablation table.**
  - "Tab.~\ref{tab:hp} sweeps {hyperparameter}. Performance peaks at {value}, beyond which {explanation}; we use this value in all other experiments."

### E4 — Analysis subsection openers

- **Robustness.**
  - "We assess robustness to {perturbation} by adding {noise model} with std $\sigma$. Fig.~\ref{fig:robust} shows that our method degrades by only {X}% at $\sigma = {s}$, while {baseline} degrades by {Y}%, supporting our claim that {mechanism} provides {property}."
- **Scalability.**
  - "We vary the {number of agents / resolution / sequence length} from {a} to {b}. Fig.~\ref{fig:scale} shows that {metric} scales {linearly / gracefully / ...}, with {observation}."
- **Communication–accuracy trade-off (for bandwidth-sensitive papers).**
  - "Fig.~\ref{fig:pareto} plots accuracy against communication cost. Our method dominates the Pareto frontier, achieving {X}% {metric} at {Z} MB, matching {baseline}'s accuracy with {k}× less bandwidth."
- **Cross-domain / generalization.**
  - "We train on {A} and evaluate on {B} without fine-tuning. Tab.~\ref{tab:cross} shows a drop of {X}%, smaller than {baseline}'s {Y}%, suggesting better cross-domain behavior."

### E5 — Qualitative figure captions

- "Qualitative comparison on {dataset}. {Baseline} \textbf{fails to} {specific failure mode} (top), while ours \textbf{correctly} {specific success} (bottom), enabled by {Method component, with section ref}. More examples in Appendix~\ref{app:qual}."
- "Visualization of {intermediate signal} produced by {component}. Brighter regions correspond to {semantic}. This confirms that {component} learns to focus on {expected behavior}."

### E6 — Limitations

- "Our method has the following limitations. First, {scope limit, e.g., assumed sensor configuration}. Second, as shown in Tab.~\ref{tab:main} row {k} / Fig.~\ref{fig:X}, performance degrades by {Y}% under {regime}, which we attribute to {honest cause}. Addressing {one of these} is left to future work."

### Style do-s and don't-s

- **Do** use "Tab." / "Fig." / "Sec." consistently (or the full word consistently) — pick one and stick with it.
- **Do** prefer present tense for descriptions of our method ("Our method achieves..."), past tense only for the experimental procedure ("We trained for ...").
- **Don't** write "significantly" without a defined test; in this domain it reads as filler or, worse, misleading.
- **Don't** chain more than two "we" clauses in one sentence — breaks rhythm and reads as a changelog.
- **Don't** use "as can be seen" / "it is worth noting" — these are pure filler, reviewers skim past them.
