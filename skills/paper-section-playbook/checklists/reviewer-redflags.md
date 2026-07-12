# Reviewer Red Flags — Introduction

Patterns that frequently draw reviewer objections, distilled from analysis of PHCP, GenComm, Where2comm, HEAL, DETR, NeRF, SAM, BEVFormer. Each flag is traceable to a specific observed risk.

## Overclaim patterns

- **Unqualified "first" claim.** "We are the first to X" without a scope qualifier (setting, fidelity, data regime). Reviewers will find prior-art counter-examples from adjacent fields. Fix: bound the claim ("first under open heterogeneous setting", "first at photorealistic real-scene fidelity").
- **Headline number vs. weak baseline.** Quoting a large improvement (e.g., "30% over direct collaboration") when the baseline is not the SOTA at matched budget. Fix: either quote vs. SOTA or relabel the comparison explicitly.
- **Benefit claim without matching experiment.** Listing "efficient communication", "privacy-preserving", "scalable" as contributions when no corresponding plot, table, or threat model appears in Experiments. Fix: either add the experiment or remove the claim.
- **Structural / ethical claim without a test.** "Preserves privacy", "ensures fairness", "is safe" must have an empirical test or an explicit scope disclaimer. Structural arguments alone do not survive review.
- **Contribution phrased as "we solve X".** Invites reviewers to look for failure cases. Use "we propose / show / design / introduce".

## Structural weaknesses

- **P1 is generic ("AI is important, autonomous driving matters")** without pointing at the specific sub-problem. The first paragraph should already be narrower than the title.
- **Prior-work paragraph lists methods without grouping them.** A laundry list of names is not a taxonomy. Group into 2–3 named categories and state the shared limitation.
- **Rhetorical question is generic** ("How can we do better?"). Must contain the operational verb of the paper's reformulation.
- **Contribution bullets are noun-phrases with no verb-of-claim.** Ambiguous what the paper is asserting. Noun-phrase bullets are acceptable only in the NeRF/representation-paper variant.
- **Fig. 1 is a method block diagram with no baseline.** Reader cannot see what is new.
- **No scope or limitation discussion anywhere.** A draft that reads as universally valid invites reviewers to find the gap. Place honest scope discussion where it fits best; do not force it into the Intro if it reads defensive.
- **Intro claims not mapped to specific tables.** When every claim cannot be pointed to a table or figure by number, the paper is likely overclaiming somewhere.

## Terminology drift

- **Component named under different aliases across paragraphs.** "Prior BEV map", "dense prior", "initialization" used interchangeably. Pick one name in P4 and keep it throughout the paper.
- **Contribution bullets use different terms than Method / Experiments sections.** Cross-section consistency is a reviewer tell; terminology drift signals the paper was written in pieces without unifying pass.
- **Architectural-noun drift across sections.** "Fusion module" in Method, "fusion backbone" in §5.4 caption, "fusion strategy" in Conclusion, "aggregation module" in §3.1 — all referring to the same block. Pick one canonical noun for each architectural concept and grep-enforce it across abstract, intro, related work, method, captions, experiments, and conclusion.
- **Compared-method names mismatched between table and prose.** A table row says `F-Cooper` but the paragraph that analyzes it writes `Fcooper` (or vice versa). Use the exact spelling and casing from the originating paper, identically in cells and prose.
- **Coined term re-italicized at every recurrence.** A term defined with `\emph{}` in Intro should appear in plain text everywhere afterwards. Re-italicizing the same term in §3.1 / Method / Conclusion reads as a re-definition and signals an unmerged draft. Italicize once, at the first formal definition site.
- **Coined term replaces a simple phrase without adding precision.** If "same evaluation setting" or "controlled diagnostics" says exactly what the reader needs, do not invent a stiffer label for the abstract or first-page motivation. Coined terms are useful only when they reduce ambiguity after being defined.
- **Technical/protocol term appears before it is explained.** A term such as `protocol-matched`, `conversion protocol`, `parser diagnostic`, or a runner/control label in the Abstract creates friction before the setup has given it meaning. Use ordinary language early; define the technical term in Experiments or Appendix.
- **Baseline caveat overload in front matter or table rows.** A main result row that reads like "official-checkpoint / converted / guarded / pending / adapter" makes the paper sound anxious and hides the comparison axis. Put necessary reproducibility detail in setup, captions, footnotes, or Appendix.

## Padding and self-defeating prose

- **Filler sentences in the abstract.** Sentences of the form "This problem remains a big challenge in practice" / "Such a setting is widely needed" carry no verifiable claim and waste a slot. Either fold the urgency into the gap sentence or delete.
- **Decoration words in the gap sentence.** "Urgently needed", "critically important", "extremely challenging" — drop. The gap is sharper without modifiers.
- **Temporal adverb between two parallel comparison settings.** "Without the plugin, performance drops; the plugin *subsequently* recovers it." The two settings are parallel, not sequential — "subsequently / eventually / then" implies a process that does not exist. Use parallel verbs or a contrastive conjunction.
- **Casual evidence connector in the abstract.** "And it achieves..." reads informal and exposes a splice between contribution and evidence. Use a direct evidence sentence with dataset, metric, and comparison target.
- **Abstract reads like a run log or protocol note.** Validation counts, split bookkeeping, conversion details, parser mechanics, resource gates, and control-condition inventories belong in Experiments or Appendix unless they are the central result.
- **Caption reads like a run log.** Captions should explain the comparison, control, or diagnostic role. They should not preserve runner names, failed attempts, local paths, checkpoint download notes, or implementation history unless needed to interpret the table.

## Cross-paper hygiene

- **Same appendix referenced multiple times from main text.** When `Appendix~\ref{app:analyses}` is cited from Method, table caption, Main Results, and Ablation simultaneously, the duplication signals anxiety. Pick the single most claim-bound location and delete the rest. Captions and prose should not both point to the same appendix.
- **Punctuation inside `\emph{}` for parallel headers.** `In \emph{Training.} Prior work ...` / `In \emph{Deployment.} Prior work ...` — the period inside the emphasis is a header artifact left over from a `\paragraph{}` rewrite; the sentence is now grammatically broken. Move the punctuation outside: `In \emph{Training}, prior work ...`.

---

# Reviewer Red Flags — Method

Observed patterns that frequently draw reviewer objections in CV / 3D / AD Method sections.

## Notation failures

- **Silent symbol switch.** Problem formulation introduces abstract symbols (`Ψ_θ'`, `Φ_θ`) that are never re-used in the pipeline equations, which instead use function names (`f_enc`, `f_fuse`, …). Bridge with a one-line mapping at the switch point. Flagged in GenComm (arXiv:2510.19618).
- **Symbol collision.** The same glyph is overloaded with two meanings in the same Method section (e.g., `S` as feature space and as support set). Use distinct symbols or typefaces. Flagged in PHCP (arXiv:2509.09310).
- **Undefined-at-first-use.** A symbol first appears inside an equation or algorithm without a prose definition in the same paragraph. Flagged in PHCP (`ℋᵢ` introduced only inside Algorithm 1).
- **Composite-operator black box.** A composite operator `Γ_{j→i}(·)` bundles multiple sub-operations (transmit + spatial-transform + compress) but is never decomposed into named sub-components. Reviewers cannot tell whether the compression / transformation is trivial or substantive. Flagged in HEAL (arXiv:2401.13964).
- **Inconsistent name for the same component.** Calling the same module "prior BEV map", "dense prior", and "initialization" across sections. Pick one name at first use and reuse it.
- **Ablation label undefined at first use.** A row name such as "prior-only", "zero-prior", "no-noise", or "lite" is used without saying what factor is changed and what is held fixed. Reviewers should not need code or private context to decode a table row.
- **Math styling drift.** A scalar parameter becomes bold, a vector loses boldface, or a random variable changes typeface after a prose rewrite. This is often introduced during editing and is easy to catch with a rendered math pass.
- **Compound abbreviation introduced without expanding both sides and without locking the arrow's semantic axis.** A pairing like `A→B`, `X-Y`, `src↔tgt`, or `T1/T2` is used in a caption or table without first stating (a) what `A` and `B` stand for in full, and (b) what the connector encodes (e.g., "ego→neighbor", "source→target", "encoder→decoder", "modality at train→modality at test"). The reader has to guess from context whether the arrow encodes a directional dependency, a substitution, a transformation, or a pairing. First-use rule: in the very first table caption, figure caption, or sentence that uses the compound, write the expansion and the axis once, then use the short form everywhere else.
- **Equation hides where the operation runs.** When an operator's *physical or topological location* matters for the paper's claim — which side of a transmission boundary it runs on, before vs. after a frozen module, on the sender vs. the receiver, on a server vs. a client — the equation should encode that location via a directional subscript (`F_{i\to j}`, `g_\mathrm{server}`) or via a one-line text convention placed immediately under the equation. A schematic figure is not a substitute: an equation must be self-contained when read in isolation. Particularly important when the contribution is *where* a module is placed rather than *what* it computes.
- **Defensive hedge that opens a door the paper does not need.** When introducing a new symbol or stage, do not append a one-line "we assume X is lossless / ideal / noise-free / negligible / unchanged" unless the paper actually studies the non-ideal version. Such hedges name a concern (channel noise, compression loss, drift, latency) the paper otherwise never engages, and reviewers read them as either a missing experiment ("you said you'd defer to Sec. X — where is it?") or an unforced concession ("you admit a simplification; quantify its cost"). The clean fix is to introduce the symbol *operationally* (what it stands for, where it comes from) without a hedge: the absence of a hedge implicitly says "this paper studies the version where that effect is not the variable of interest". Add the hedge only if there is a paired experiment, ablation, or scope statement in Experiments / Limitations that the hedge points to.

## Structural weaknesses

- **Opener restates the Introduction.** M1 should frame the method by naming the framework and pointing at Fig. 2, not rehearse the limitations of prior work. Prior-work criticism belongs in Introduction and Related Work.
- **Submodule without design rationale.** A non-obvious design choice (diffusion vs. VAE; deformable vs. vanilla attention; CBAM vs. MLP adapter) is introduced without justification. Either add a rationale paragraph tied to an ablation, or soften to "following X [cite]" to remove the novelty claim.
- **Submodule with rationale but no ablation.** The paper claims design X is necessary, but Experiments do not ablate X. Either add the ablation or soften the Method claim.
- **Pseudocode as primary carrier of method description.** Algorithms 1, 2, 3 replacing equations. Moves the method out of mathematical form and into implementation form; often reads as loose. Push pseudocode to Appendix.
- **Training recipe too thin to reproduce.** Few-shot or specialized settings that omit adapter parameter count, seed protocol, per-stage optimizer, or data sampling details. Any element a reimplementor would guess differently from the paper needs to be pinned down.
- **Loss with undefined weights.** Total loss `ℒ = L_det + α L_feat + β L_cons` where α, β are never assigned or explained. Either give values or say "tuned on validation" with the search range.

## Claim-alignment failures

- **Design claim without ablation.** Method says "we use two-stage training to avoid X"; Experiments has no with/without-second-stage row.
- **Efficiency claim without measurement.** Method says "efficient communication"; Experiments has no bandwidth-accuracy plot.
- **Generalization claim without held-out test.** Method says the method generalizes across sensor types / agent types; Experiments only tests one configuration.
- **Necessity claim from a single run.** Method says component Y is necessary based on one number; Experiments lacks a seed-variance or multi-setting confirmation.

## Figure hygiene

- **Main figure has components not described in any subsection.** If Fig. 2 has a box labeled "refinement head" that never appears in Method prose, the reader assumes the paper is hiding something.
- **Figure referenced only in the opener.** Each sub-panel of a multi-panel figure should be re-referenced by the subsection that uses it. If not, either merge panels or re-reference.
- **Method figure with no in-text `\ref{}`.** Every figure or table must be cited in prose at least once.

---

# Reviewer Red Flags — Experiments

## Setup / fairness

- **Silent re-implementation of baselines.** If a baseline is re-trained instead of using the official checkpoint, and the config is not disclosed, reviewers assume unfair comparison.
- **Missing obvious baseline.** Omitting the SOTA method of the previous year in the same venue is a near-auto-rejection.
- **Dataset split mismatch.** Using a non-standard train/val split without justification invalidates all numbers.
- **Metric invention.** Reporting on a new metric while dropping the community-standard one — reviewers assume gaming.
- **Communication accounting mismatch.** A table mixes native communication cost, budget-matched cost, pre-corruption payload, and post-corruption retained payload without labeling which quantity is reported.

## Main results

- **Bolding the wrong cell.** Bolding "Ours" when a baseline is higher by 0.1 — instant trust loss.
- **Missing a column where ours loses.** Reviewers notice omitted metrics; honest loss is better than hidden loss.
- **Margin-shrinking under zoom.** Gains of 0.2 AP reported as "significant" without std or subset analysis.
- **Cherry-picked dataset.** Reporting only on datasets where the method wins, with no note about others.

## Ablation

- **Missing ablation for a claimed component.** If Method introduces component X but no row switches X off, the claim is unsubstantiated.
- **Mega-table mixing component ablation with hyperparameter sweeps.** Reviewers can't read it.
- **Ablation on a different dataset than main results.** Forces the reader to trust a cross-dataset transfer they shouldn't.
- **"Full model" row not matching Main Results number.** Numbers must match exactly; a mismatch of 0.1 signals a different seed / config and invalidates the table.
- **Variant names not defined before interpretation.** The prose explains a row's behavior before telling the reader whether the row removes a prior, removes noise conditioning, changes inference steps, or changes training corruption.
- **Table body changed but caption/prose stayed old.** Duplicate rows removed, panels merged, or labels renamed without updating the caption and nearby interpretation. This creates a consistency bug even when the numbers are correct.

## Analysis / figures

- **Efficiency claim without Pareto plot** for papers marketing efficiency — see E4 rule.
- **Fake error bars / shading.** If you didn't run multiple seeds, don't draw error bars. This is noticed.
- **Axes without units or labels.** Immediate flag.
- **Log-scale axis without disclosure.** Reviewers suspect manipulation.
- **Diagnostic figure treated as causal proof.** A diagnostic plot can show metric behavior, distribution shift, or decoupling. It cannot prove a mechanism unless the experiment directly tests that causal link.

## Qualitative

- **Gallery without claim.** N×M grid with no highlighted failure — no information value.
- **No baseline in qualitative figure.** Ours looking good proves nothing.
- **Undisclosed cherry-picking.** "Representative examples" without selection criterion → reviewer treats as cherry-picked.

## Limitations / honesty

- **Absent Limitations section.** In NeurIPS/CoRL this violates the checklist; in CVPR/ICCV it signals immaturity.
- **Performative limitations** ("Our method is slower than real-time by 0.1ms") — transparent evasion; list the *real* weakness (poor cross-domain, needs calibration, etc.).
- **Scope text framed as a severe weakness.** If the content is mostly an untested extension or deployment assumption, use a scope / extensions title rather than making a reviewer-facing "failure" section out of it.
- **Overclaim in Conclusion contradicting Experiments.** Reviewers re-read Conclusion after Experiments; any contradiction is devastating.
- **Robustness or design-justification analyses filed under a Limitations title** (e.g., putting a *positive* sample-order-stability result under "Extended Limitations"). This frames positive evidence as weakness. Use separate Appendix titles: `Extended Limitations and Failure Cases` vs `Additional Robustness and Design Analyses`.

## Cross-section

- **Intro contribution (iii) has no corresponding table row** — see Claim–evidence ledger.
- **Method submodule M.k has no ablation row** — ditto.
- **Experiments section exceeds page budget, pushing real content into the Appendix** — weakens credibility. (Limitations itself in Appendix is fine per user-locked policy; what weakens credibility is moving *main results* or *core ablations* out.)

---

# Reviewer Red Flags — Related Work

## Structural

- **Missing Related Work section.** Extremely rare but fatal; reviewers interpret as ignorance or evasion.
- **Related Work pushed to end of paper.** Only acceptable for specific NeurIPS/DETR-style papers; risky at CVPR/ICCV.
- **Chronological walkthrough without lineage.** Reads as a lit-review homework, not research positioning.
- **Themes with no shared limitation.** Exposes that the author didn't analyze the landscape.
- **One theme, one giant paragraph.** Hard to scan; reviewers will skip.

## Coverage

- **Missing the most cited paper of the lineage.** Instant competence flag.
- **Missing the last-year same-venue paper addressing the same problem.** Reviewers check this deliberately.
- **Baseline in Experiments not cited in Related Work.** Internal inconsistency; looks sloppy.
- **Concurrent work ignored.** If a preprint from the past 3 months on the same topic exists and is not mentioned, reviewers (often the authors of that preprint) take offense.
- **Over-citing lab's own prior work.** More than ~15% self-citation density raises eyebrows.

## Content

- **Paragraph-per-paper walkthrough.** "Paper X does A. Paper Y does B. Paper Z does C." Reviewers read it as padding.
- **Describing a prior paper's full method.** Out of scope; belongs in that paper, not yours.
- **Vague critique** ("existing methods have limitations", "these approaches are not sufficient"). Must be specific and tied to an assumption or failure mode.
- **Critique that doesn't connect to your contribution.** If you critique axis X but your method doesn't address X, the critique is irrelevant and reviewers will call it out.
- **Positioning sentence inflated into a contribution restatement.** Keep it to one sentence; save the details for Method.

## Tone

- **Dismissive language** ("these methods are naive / limited / fail completely"). Reviewers of those works are your reviewers — stay neutral.
- **Over-praising** ("the seminal work \cite{X} brilliantly shows..."). Unnecessary; just state what the work does.
- **Tense inconsistency** mixing past and present for the same lineage — jarring to read.

## Cross-section

- **Duplicating Intro.** If Related Work's opening is the same 3 sentences as Intro's "existing work" paragraph, it reads as copy-paste.
- **Contradicting Experiments.** If Related Work says "X is the current SOTA" but Experiments compares against a different SOTA Y, readers distrust both claims. Keep them aligned.

---

# Reviewer Red Flags — Abstract

## Structural

- **Longer than 200 words or shorter than 100.** Too long = didn't prioritize; too short = didn't substantiate.
- **Split into 2+ paragraphs in CVPR/ICCV/ECCV submission.** Violates venue norm.
- **Missing a named method** (no "we propose X"). Harder to remember and cite.
- **Banned opener** ("In recent years...", "With the development of...", "Deep learning has revolutionized...").
- **Method abstract ends without concrete evidence.** Abstracts must deliver evidence, not aspiration. Method papers usually end with a number-backed claim; evaluation or reliability papers may end with the broader lesson if the preceding sentence carries the key evidence.
- **Forcing a table-like final sentence when the paper's point is a lesson.** For evaluation or reliability papers, a final broader lesson is acceptable if the preceding sentence already carries the key quantitative evidence. Do not force a table-like ending when it weakens the story.

## Content

- **Qualitative-only results** ("significantly outperforms"). Current reviewer expectation is 1-2 concrete numbers.
- **Numbers don't match Intro / Main Table / Conclusion.** Even a 0.1% mismatch kills trust.
- **Vague mechanism.** "We propose a novel framework..." without naming the 2–3 components is unevaluable.
- **More than 3 components listed.** Reader forgets everything after the third.
- **Diagnostic control written as a dataset component.** Controls, perturbations, parser warnings, and audit checks are evaluation tools unless the paper explicitly defines them as benchmark schema. Do not list them alongside annotations or released targets in an abstract component sentence.
- **Fairness/conversion jargon in the abstract.** Phrases like `protocol-matched evaluation` can be correct in Experiments but stiff and unclear in Abstract. Use a reader-facing phrase such as "under the same evaluation setting" unless the technical term is itself the contribution.
- **Mechanism phrasing is too implementation-shaped.** "Four-part reasoning diagnostics" may be precise in a dataset section; "evidence reasoning" is often enough in the Abstract if the part count is not the claim.
- **Generated reasoning implied to explain trajectory quality.** Unless the paper directly tests a causal link, do not imply that CoT/rationale text explains FDE, trajectory quality, or action correctness. Treat it as a diagnostic or supervision signal with the stated scope.
- **Claims first / novel / only without evidence.** Reviewers cross-check and push back.
- **Copy-pasted first sentence from Introduction.** Reviewer notices; reads as laziness.

## Tone

- **Future tense** ("we will show that..."). Use present.
- **Passive voice for your own contribution** ("a method is proposed"). Use active.
- **Filler phrases** ("it is well known that", "as mentioned", "as can be seen"). Cut.
- **Contractions** ("can't", "won't", "it's"). Formal register only.

## Consistency

- **Method name in Abstract ≠ method name in Intro / Method.** Pick one and stick with it throughout.
- **Dataset name mismatch.** "{Dataset-A}" vs "{Dataset A}" vs "{DatasetA}" — normalize spelling and casing across the paper.
- **Metric name drift.** "AP@0.5" vs "[email protected]" vs "AP" — be consistent; decide in the abstract and follow through.

---

# Reviewer Red Flags — Conclusion

## Structural

- **Missing Conclusion** in a CVPR/ICCV/ECCV submission. Nearly always bad.
- **Conclusion longer than ¼ page** in two-column. Signals inability to prioritize.
- **Multi-paragraph Conclusion** without a reason. Single paragraph is the norm.

## Content

- **Pure recap of Abstract.** No added value, no implication. A reviewer's common complaint.
- **Identical sentences to Abstract.** Not just overlap — literal copy. Flags laziness.
- **New concept / method introduced in Conclusion.** Never acceptable.
- **New term or taxonomy introduced in Conclusion.** Even if the concept is not a method, defining a fresh name in Conclusion reads like the paper changed after Experiments. Reuse established terms in their simplest form.
- **Component inventory instead of lesson.** A conclusion sentence that re-lists dataset fields, modules, controls, and diagnostics is a weak ending. State what those elements let the paper show.
- **Diagnostic-number dump.** Repeating several small control rates or parser scores in Conclusion reads like a table caption. Keep at most one anchor number unless the conclusion's main lesson depends on the numeric contrast.
- **Heavy re-citation** (>2 citations). Belongs in Related Work.
- **Overclaim** ("we revolutionize / first / universal / always"). Cross-checked against Experiments.
- **Contradiction with Experiments** (Experiments show failure regime, Conclusion claims universality). Biggest trust-destroyer.
- **Vague future work as wishlist** without any substantive anchor. Signals lack of direction.
- **Emotional closer** ("we hope this inspires future research"). Weak; end with a grounded sentence.

## Consistency

- **Anchor number mismatch** with Abstract / Intro / main Table. Even 0.1% drift kills trust.
- **Method name drift**: differently capitalized or typeset from the rest of the paper.
- **Implication not supported by any ablation or analysis** in Experiments. Reviewers trace it.

## Limitations linkage

- **Limitations never mentioned anywhere** — not in Appendix at all. NeurIPS/CoRL checklist violation.
- **Limitations duplicated across Conclusion and Appendix**, each a little different. Per user-locked policy, Appendix only — no Conclusion content, no Conclusion pointer.
- **Conclusion pointer-references Appendix Limitations.** Per user-locked policy, do not do this; the Appendix title is the signpost.
- **Mixed content under a Limitations title** — e.g., a robustness analysis with a positive result filed under `Extended Limitations`. Separate Appendix titles by category (see Limitations / honesty block above).
