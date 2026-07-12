# Abstract Section Playbook

Domain: CV, 3D perception, autonomous driving, and collaborative perception for CVPR, ICCV, ECCV, NeurIPS, and CoRL.

## Default format

- **Single paragraph**, 150–200 words. Never split into two paragraphs for CVPR/ICCV/ECCV. (NeurIPS/ICLR occasionally allow 2 paragraphs — still prefer 1.)
- **Contains concrete evidence.** At least 1–2 concrete numbers (e.g., "+3.2% AP on Dataset-A", "2× less bandwidth") — qualitative-only claims ("significantly outperforms") are now penalized. Method papers should usually end with a number-backed claim; evaluation, reliability, and benchmark papers may end with the broader lesson if the preceding sentence already carries the key evidence.
- **Self-contained.** Reader decides whether to open the PDF based on the abstract alone; no cliffhangers, no "see Fig. 1".

## Structural slots

An abstract delivers **five slots in order**. Every sentence should be mapping to one slot; if you cannot tag a sentence to a slot, it is filler.

```
[Slot 1] Context          (optional, 0–1 sentence)
[Slot 2] Problem / gap     (1 sentence, required)
[Slot 3] Proposal          (1 sentence, required — names the method)
[Slot 4] Mechanism         (1–3 sentences — what are the key components and why they work)
[Slot 5] Evidence          (1–2 sentences — datasets, metrics, numbers)
```

Target distribution: ~1 sentence (or 0) for Slot 1, 1 each for Slots 2, 3, 5, and 1–3 for Slot 4. Aim for **6–8 sentences total**.

## Opening strategy (paper-type adaptive)

**Decision rule.** The opener depends on what the paper contributes most.

- **If the paper proposes a new problem or new setting** (e.g., a new task, a new benchmark, a new assumption relaxation): open with **1 sentence of context + 1 sentence of problem** (Slots 1 + 2). The context sentence establishes that the problem is meaningful to the community.
  - Template: "{Domain / task} increasingly relies on {capability}, yet existing {axis} assume {assumption} and fail when {breakdown}."
- **If the paper proposes a new method for an established problem** (most CVPR/ICCV collaborative-perception / 3D-detection papers): **skip Slot 1, open directly with the problem (Slot 2)**. Reviewers already know the field; wasting 1 sentence on background costs word budget.
  - Template: "{Task} under {challenging condition} remains challenging because {specific reason tied to Method}."
- **If the paper is observation-driven** (a non-trivial insight motivates the design): open with the observation.
  - Template: "We observe that {insight}; this motivates {approach}."

**Banned openers.**
- "In recent years, {topic} has attracted increasing attention." — textbook filler.
- "With the development of {topic}, ..." — same.
- "Deep learning has revolutionized {topic}." — instant credibility loss.

## Slot-by-slot templates

**Slot 2 — Problem / gap.**
- "However, existing {family} approaches rely on {assumption}, which breaks down when {condition}."
- "{Task} remains challenging because {specific cause}, leading to {observable symptom in metric}."

**Slot 3 — Proposal.** One sentence naming the method and its one-clause key idea.
- "We propose {METHOD}, a {one-word category, e.g., framework / architecture / training strategy} that {key insight / mechanism}."
- "To address this, we introduce {METHOD}, which {one-clause mechanism}."

**Slot 4 — Mechanism (1–3 sentences).** Describe 2–3 design components at the "what / why" level, not equations. Explain how the components relate; do not present an inventory of module names.
- "Specifically, {METHOD} {component A operation} to {component A purpose}. Additionally, {component B operation} {component B purpose}."
- "At the core of {METHOD} is {central idea}, which {why it works}."
- **Never** list more than 3 components in Slot 4. Reader can't retain more from an abstract.

**Component sentence for benchmark / evaluation papers.** List only reader-facing data or protocol surfaces: labels, QA targets, reasoning annotations, action references, splits, or evaluation tasks. Do **not** list ablations, controls, parser warnings, baseline conversion rules, dry-run gates, or resource constraints as if they were dataset components. If controls are central to the paper, name them in the result/diagnostic sentence as evaluation diagnostics, not in the dataset inventory.

**Slot 5 — Evidence.** Dataset names + 1–2 numbers + comparison target.
- "Experiments on {dataset A} and {dataset B} show that {METHOD} achieves {X}% {metric}, outperforming the state of the art by {Y}% while using {Z}× less {cost}."
- "On {dataset}, {METHOD} improves {metric} from {before} to {after} (+{delta}), setting a new state of the art."

For reliability or evaluation papers, Slot 5 can be evidence + lesson: first state the main quantitative result, then state what the controlled diagnostic shows. Keep the diagnostic phrasing high-level unless the control itself is the central result.

## Number discipline

- **1–2 numbers minimum**, 3 maximum. More than 3 numbers turns the abstract into a table dump and the reader remembers none.
- Prefer **relative gain + named dataset + named metric**: "+3.2% AP on Dataset-A" beats "achieves 68.4% AP".
- If you report an efficiency number, prefer **relative** over absolute: "2× less bandwidth" beats "8.4 MB per frame".
- **Consistency**: the number in the abstract **must exactly match** the final main-table number — no rounding disagreements, no "as of writing" drift. Reviewers cross-check.
- **Named baseline optional**: "+3.2% over HEAL" is strongest; "+3.2% over the state of the art" is acceptable; "significant improvement" is not.
- If robustness or efficiency is protocol-specific, state the scope inside the evidence sentence (e.g., "under the stated packet-loss protocol" or "at matched payload"). Do not let a narrow experiment read as a universal claim.

## Front-matter compression rule

The abstract is not the place for run-level or operator-level detail. Default-exclude:

- validation-frame counts, split bookkeeping, and sample-filter counts;
- fairness/conversion terms such as `protocol-matched` unless the phrase is immediately understandable without a setup section;
- checkpoint initialization, official-checkpoint status, runner names, guard/adapter details, local paths, download failures, failed attempts, and engineering patches;
- parser mechanics, diagnostic implementation details, resource gates, dry runs, and artifact paths;
- inventories of control conditions, unless those controls are the paper's main empirical finding.

The abstract is not a lab notebook, reproduction note, or baseline incident report. If a detail is needed only to reproduce the run, not to understand the paper's claim, it belongs later.

Use ordinary phrasing until precision is needed. For example, "under the same evaluation setting" is usually better in the abstract than "under protocol-matched evaluation"; "controlled diagnostics" is usually better than a full list of control names.

## Coordination with Introduction

Abstract and Introduction share DNA but not text.

- **Abstract = compressed Introduction.** Every abstract sentence should have a counterpart in the Intro (problem sentence ↔ Intro ¶2; mechanism sentences ↔ Intro ¶3; gain sentence ↔ Intro ¶5 contribution (iii)).
- **But no copy-paste.** If the abstract and Intro first sentence are identical, reviewers flag it as lazy. Reword.
- **Method name introduction.** Abstract should introduce the method name (e.g., "we propose PHCP") before Intro does; Intro can then use the name freely from ¶3.
- **Numbers must match across Abstract / Intro / Main Table / Conclusion.** A single-digit drift kills credibility.

## Style do-s and don't-s

- **Do** write in present tense throughout ("we propose", "experiments show"), not future ("we will show") or past ("we proposed").
- **Do** use active voice for your own contributions ("we propose", not "a method is proposed").
- **Do** name the method (e.g., PHCP, GenComm, Where2comm). An unnamed method is harder to cite and remember.
- **Don't** use contractions ("can't", "won't"). CVPR/ICCV abstracts are formal.
- **Don't** open with "In this paper" — implicit; wastes a slot.
- **Don't** begin the evidence sentence with "And it ..." or any casual connector. Use one clean evidence sentence with dataset, metric, and comparison target.
- **Don't** end with "We hope this work inspires future research" — weak finish; end with either the paper's strongest number-backed claim or, for evaluation/reliability papers, the lesson supported by the preceding evidence sentence.
- **Don't** put code/URL links in the abstract; these go in the first footnote of Intro or after Conclusion.
- **Don't** write the abstract before the paper is done. The abstract is the last thing you write, and you rewrite it at least 5 times.
- **Don't** add filler sentences of the form "This problem remains a big challenge in practice" / "Such a setting is widely needed" between two slots. If the sentence carries no verifiable claim and adds no new fact, it is dead weight and reviewers will read it as padding. Either fold the urgency into the gap sentence or delete.
- **Don't** turn a training/evaluation detail into a broad guarantee. For example, if the evidence is "trained under complete communication and tested under corrupted messages", say that as the protocol; do not claim immunity to all lossy communication.
- **Don't** use a stiff technical label when an ordinary phrase is precise enough. Avoid abstract phrasing such as `matched input/evidence controls` as a dataset component, `protocol-matched evaluation` before it is explained, or `four-part reasoning diagnostics` when `evidence reasoning` carries the claim.

## Worked skeletons

**Method-driven paper (most common case).**
> {Task} under {condition} remains challenging because {specific reason}. We propose {METHOD}, a {category} that {one-clause insight}. Specifically, {METHOD} {component A operation} to {component A purpose}; moreover, {component B operation} {component B purpose}. This enables {high-level capability} without {cost / assumption that prior work required}. Experiments on {dataset A} and {dataset B} show that {METHOD} achieves +{X}% {metric} over the strongest prior work, while using {Y}× less {cost}. Code will be released.

**Problem-driven paper (new setting / new assumption).**
> {Domain} increasingly depends on {capability}, yet existing methods assume {assumption} that rarely holds in practice. We introduce {PROBLEM-NAME}, a {setting} in which {key twist}, and propose {METHOD} to address it. {METHOD} {key mechanism}, leveraging {property} to {capability}. On the newly collected {benchmark} and {existing dataset}, {METHOD} outperforms adapted baselines by +{X}% {metric}, demonstrating the feasibility of {setting}.

**Observation-driven paper.**
> We observe that {non-obvious property of data / models}. Building on this, we propose {METHOD}, which {uses the property for mechanism}. {METHOD} consists of {component A} and {component B}, jointly optimized via {training strategy}. On {dataset} and {dataset}, {METHOD} improves {metric} from {before} to {after} (+{delta}), establishing a new state of the art under {condition}.

## Self-review checklist (run after every rewrite)

- [ ] Single paragraph, 150–200 words (count them).
- [ ] Every sentence maps to one of 5 slots; no filler.
- [ ] Opener matches paper-type rule (method / problem / observation driven).
- [ ] Method name appears in Slot 3 and is used consistently thereafter.
- [ ] 1–2 numbers, each with named dataset + named metric + named baseline (or "state of the art").
- [ ] Numbers exactly match Intro / main Table / Conclusion.
- [ ] Any robustness / bandwidth / efficiency number states the tested protocol or comparison condition when the scope is narrow.
- [ ] No banned openers ("In recent years...", "With the development of..."), no contractions, no future tense.
- [ ] Final sentence is either a number-backed claim or, for evaluation/reliability papers, a broader lesson directly supported by the preceding evidence.
- [ ] No front-matter leakage: validation counts, protocol-conversion jargon, parser mechanics, resource gates, and control-condition inventories are absent unless they are the central result.
- [ ] Dataset/protocol components are not mixed with diagnostic controls or ablation machinery.
- [ ] No overclaiming — every superlative ("first", "best", "only") is defensible.
- [ ] Method name is searchable and pronounceable (helps citation).

## Exemplar anchors

- **Where2comm** (NeurIPS 2022) — compact method-driven abstract, numbers up-front, clean Slot 4.
- **HEAL** (ICLR 2024) — clean problem-framing, number-backed finish.
- **BEVFormer** (ECCV 2022) — textbook 5-slot method abstract with quantified gains on nuScenes.
- **DETR** (ECCV 2020) — observation-driven opener ("object detection as set prediction"), minimal but strong.
- **NeRF** (ECCV 2020) — observation-driven, heavily rewritten; worth imitating only if you truly have a paradigm shift.
- **SAM** (arXiv 2304.02643) — long, 2-paragraph abstract; not a template, treat as a counter-example for method papers.
