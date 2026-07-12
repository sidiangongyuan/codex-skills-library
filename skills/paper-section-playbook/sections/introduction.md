# Introduction

Structural playbook for the Introduction section of a paper in CV / 3D perception / autonomous driving (CVPR / ICCV / ECCV / NeurIPS / CoRL).

For sentence-level polish, defer to `paper-refinement-skills`.

Sources: this file draws on eight exemplar papers — PHCP (arXiv:2509.09310), GenComm (arXiv:2510.19618), Where2comm (arXiv:2209.12836), HEAL (arXiv:2401.13964), DETR (arXiv:2005.12872), NeRF (arXiv:2003.08934), SAM (arXiv:2304.02643), and BEVFormer (arXiv:2203.17270) — plus the generalized principles in `references/design-rationale.md`.

## Default skeleton: Variant A — Limitation-driven new-question

This is the default for papers in collaborative perception, V2X, and most new-method papers in CV / 3D perception / AD. Followed by PHCP, GenComm, Where2comm, HEAL.

Five paragraphs, in order:

1. **P1 — Broad context.** One paragraph establishing the application area (e.g., V2X, autonomous driving, 3D detection) and why it matters. Close by pointing toward the specific sub-problem the paper will address. ~3–5 sentences.
2. **P2 — Specific problem.** Name the concrete obstacle (heterogeneity, bandwidth, open-world, occlusion, etc.). Do not yet discuss prior work. ~2–4 sentences.
3. **P3 — Prior-work taxonomy + shared limitation + transition.** Group existing methods into 2–3 named categories (cite representative papers by name, e.g., "adaptation-based methods such as MPDA, PnPDA"). State the shared limitation that all categories inherit. Close with either a concrete rhetorical question or a direct gap sentence that the method will answer. ~5–8 sentences.
4. **P4 — Our method overview.** Name the proposed method, its core insight, and 2–4 named submodules. Do not yet quantify performance. ~4–6 sentences.
5. **P5 — Evaluation preview + contribution list.** One sentence previewing datasets and one headline number, followed by the contribution bullets (see "Contribution bullet format" below). ~3 sentences of prose + bullets.

Teaser figure (Fig. 1) must be a **paradigm-comparison teaser**: side-by-side panels showing (prior paradigm) vs. (our paradigm). Optionally a fourth panel with a Pareto / cost-vs-accuracy chart (HEAL, GenComm). Do not use a qualitative-gallery teaser for this variant.

## Alternative skeleton: Variant B — Two-motivation parallel structure

Use when the method has two genuinely orthogonal design axes (e.g., spatial + temporal in BEVFormer). Followed by BEVFormer.

Six paragraphs:

1. **P1 — Broad context + rising alternative** (e.g., cameras vs. LiDAR).
2. **P2 — Naïve baseline and its flaws.**
3. **P3 — Axis-1 motivation.** End with one italicized sentence stating the first design motivation.
4. **P4 — Axis-2 motivation.** End with one italicized sentence stating the second design motivation.
5. **P5 — Method overview** that stitches both axes together with named submodules.
6. **P6 — Contribution list** (see format below).

Teaser: pipeline / paradigm diagram showing both axes feeding into the unified representation.

Do not force Variant B if your two "axes" are actually one mechanism with two properties; that collapses back to Variant A.

## Contribution bullet format (default rule for Variant A and B)

Use **3 bullets by default**, in this order:

1. **New method / insight.** State the reformulation or core idea. Use "we propose / we introduce / we show", not "we solve".
2. **Core submodule or mechanism.** Name the concrete technical component that realizes the insight.
3. **Experimental outcome.** Must contain (a) at least one quantitative number and (b) at least one named dataset.

Rationale from the exemplars: BEVFormer bullet 3 reports a quantified NDS gain on nuScenes; GenComm reports large quantified reductions; Where2comm reports communication-volume reduction across multiple collaborative-perception benchmarks. Putting numbers inside the bullet is the single strongest anti-overclaim device available, because the number commits the paper to a verifiable table.

Use 4 bullets only when there are four distinct, validated contributions that would become ambiguous if merged. Promote the extra contribution above the quantified experimental bullet and keep the quantified bullet last. Never exceed 4.

## Cross-cutting rules (apply to both variants)

- **Claim–experiment alignment is mandatory.** Every contribution claim in the Intro must have a corresponding table, figure, or ablation in Experiments. Before submission, verify each bullet by listing the supporting table or figure number in the margin.
- **Quantify inside the contribution bullet when possible.** Follow BEVFormer / GenComm / Where2comm. If a claim cannot be quantified (e.g., conceptual novelty, "first to do X"), hedge with precise scope: "first under this setting / at this fidelity / without this assumption". Generic "first" claims are a reviewer red flag.
- **Handle scope honestly, but do not force a limitation into the Intro.** If the paper has a scope assumption that could otherwise be misunderstood, place one calm scope sentence where it fits. If the limitation is already handled in the Appendix, or if an Intro limitation would read as defensive, omit it from the Intro.
- **Use a terminology gradient.** Abstract and early Introduction use plain, reader-facing phrases such as "same evaluation setting", "controlled diagnostics", or "source attribution". Experiments may introduce precise labels such as "converted external baselines", "shared validation protocol", or "protocol-matched comparison" after setup defines them. Appendix can carry the full conversion, parser, and audit details.
- **Keep category boundaries explicit.** Dataset/protocol contents, model design, diagnostic controls, and baseline-conversion fairness are different claim types. Do not collapse them into one component list in the Intro or contribution bullets. Controls are evaluation tools unless the paper explicitly defines them as benchmark schema.
- **For reliability / evaluation papers, lead with the scientific question.** State the failure mode or uncertainty the field cannot currently see, then introduce the benchmark, dataset, or protocol as the instrument for studying it. Do not let the artifact name become the whole paper's subject before the reader understands the question.
- **Scientific question first, instrument second.** Front matter should make the reader care about the phenomenon before it names every dataset surface, benchmark component, or diagnostic. Contribution bullets should state what the paper establishes, not recite a component inventory.
- **Avoid "we solve".** Prefer "we propose / we show / we design / we introduce". "We solve X" invites reviewers to look for cases where X is not solved.
- **Bind claims to datasets.** When a claim is empirical, name the dataset inside the same sentence. Follow HEAL and Where2comm.
- **"First" claims must carry a scope qualifier.** Generic "first to do X" without qualifier will be challenged. Either bound by setting ("first in open heterogeneous collab perception"), by fidelity, by data regime, or remove the word.
- **Do not compare against an artificially weak baseline in the headline number.** Flag from PHCP: "~30% gain" vs. direct-collaboration baseline invites the reviewer to ask how it compares to SOTA under matched budget. If the headline number is vs. a weak baseline, rephrase or move it out of the Intro.
- **Do not list a "by-product" benefit you did not measure.** Flag from GenComm: claiming "improved communication efficiency" without a comm-volume curve across rates is a soft spot. Every claimed benefit needs a matching plot or table.
- **Do not make structural claims ("preserves privacy", "preserves model details") without an empirical test or an explicit threat model.** Flag from HEAL.
- **For robustness / reconstruction papers, make the corruption mechanism explicit.** A strong arc is: deployment bottleneck -> prior methods only partially cover it -> a concrete corruption or distribution shift appears at test time -> the method reconstructs or repairs the missing signal -> contribution bullets map to the robustness evidence. Do not claim generic robustness if the experiment only covers one corruption protocol.

## Teaser figure (Fig. 1) rules

Priority order (pick the first that fits the paper):

1. **Paradigm-comparison teaser** — 2–4 panels showing prior paradigms vs. ours. Default for Variant A. Exemplars: PHCP, GenComm, HEAL.
2. **Paradigm-comparison + Pareto chart** — add a fourth panel with accuracy vs. cost / bandwidth / parameters, with your method at the Pareto frontier. Exemplars: HEAL (bullseye), GenComm (scaling plot).
3. **Pipeline / architecture overview** — only when the pipeline itself is the contribution (end-to-end removal of components, unified representation). Exemplars: DETR, BEVFormer.
4. **Concept / failure-illustration with a concrete scenario** — use when one scene makes the motivation self-evident. Exemplar: Where2comm (occlusion + collision scene).

Do not use:

- Qualitative-result galleries as Fig. 1, unless the paper's contribution is a new representation and the visual quality is itself the claim (exemplar: NeRF). Not appropriate for method / system papers in collaborative perception.
- A method-architecture block diagram labeled "our method" as Fig. 1 without any comparison baseline — the reader cannot see what is new.

Fig. 1 must be referenced in P1–P3 of the Intro, not only later. The figure should make the limitation–answer story visible at a glance.

### Two-column comparison teasers: structural symmetry rule

When Fig. 1 is a two-column "prior vs ours" comparison (paradigm-comparison teaser), the two columns must be **structurally symmetric** so the reader can sweep the same gaze pattern down each side and immediately see what changed:

- **Same row decomposition on both sides.** Pick one row axis (most often: top = *Training*, bottom = *Test-time deployment*) and apply it to both columns. Do not let one column be a single block while the other is split into rows.
- **Same visual register at each row.** If the top row on the prior-works column is a flow diagram, the top row on the ours column must also be a flow diagram, not a bullet list of properties. Mixing diagram on one side and text labels on the other is the most common asymmetry failure: the reader's gaze is forced to switch modes mid-comparison.
- **Same anchor positions for property/precondition annotations.** When attaching callout chips around each cell (e.g., "requires X" on prior-works, "free of X" on ours), they should occupy the same edges (e.g., both top-edge / right-edge / bottom-edge), so the eye sweeps the same way on both sides.
- **Same per-agent label shape and order across all cells.** If the top-left cell has agents stacked as ego-above / neighbor-below with the labels "Ego (Encoder-A) / Neighbor (Encoder-B)", every other cell must use that same stacking order and same label format. This applies even when one cell does not draw a particular agent.
- **Mark which agent is the ego in every cell.** Do not assume the reader can infer "ego" from a color convention alone — attach a textual "Ego" / "Neighbor" label inside each cell, in addition to any color convention.
- **Caption discipline for two-column teasers.** The caption should first state the column meaning (e.g., "(a) Prior works ... (b) Ours ..."), then state the row meaning once (e.g., "Top row: training. Bottom row: test-time deployment."), then describe each cell using parallel sentence structure. Avoid describing one cell as a flow ("X passes through Y to produce Z") and another as a list of properties ("our method is X, Y, and Z") — match the rhetorical mode to the visual mode.

Failure mode this guards against: a teaser where the prior-works column visualizes a *pipeline* and the ours column visualizes a *list of advantages*. The reader cannot tell what the architectural difference is at a glance, only that "ours sounds better"; reviewers read this as marketing.

## Rhetorical moves (optional but characteristic in V2X / collab perception)

- **Rhetorical question at end of P3.** Used by PHCP, GenComm, Where2comm, HEAL. Use it only when it sharpens the transition. Keep it one sentence, italicized or quoted, with a concrete operational verb ("Can the ego vehicle change its parameters at inference without joint training?"). Generic questions ("How can we do better?") do not count. If it feels theatrical, replace it with a direct gap sentence.
- **Shared-assumption attack.** Identify a premise that "all prior works" adopt, then refute it. Exemplars: Where2comm ("once two agents collaborate, they are obligated to share all spatial areas equally"), HEAL ("all the agents have to be homogeneous"). Strong move when it lands; flat when the "assumption" is a straw man.
- **Two-pronged shared limitation.** Name exactly two limitations the prior-work category all share (GenComm: intrusive retraining + scalability cost). Pairs well with a 3-bullet contribution list where bullets 1–2 each address one.
- **Name prior methods by name when critiquing.** GenComm names MPDA, PnPDA, STAMP, HEAL, CodeFilling directly in P2. Stronger positioning than "some prior works".

## Closing-paragraph subtemplate: asymmetry-exploiting "key insight" paragraph

Use this when the method's central trick is to exploit a structural asymmetry between two regions, two agents, two modalities, or two time scales (one side reliable / dense / labelled, the other side weak / sparse / unlabelled), and the closing Intro paragraph has to preview *how* the trick works without sliding into the Method section.

The paragraph must be a 7-step derivational chain, **one sentence per step, in this order**:

1. **Premise.** State the geometric or structural fact that makes the asymmetry exploitable at all (e.g., "ego and neighbour have large overlapped regions", "tokens within an object are highly correlated", "depth is locally smooth"). Without this sentence the partition that follows reads as ad hoc.
2. **Easy-region mechanism.** Describe what the method does in the partition where supervision / signal is reliable (e.g., reliable side serves as the alignment target).
3. **Hard-region mechanism — by operator reuse.** The hard region must be handled by *applying the same operator learned in the easy region*, not by introducing a second mechanism. This is the rhetorical move that collapses two cases into one.
4. **Implementation collapse.** One sentence: name the artifact ("a lightweight plugin before fusion", "a small head on top of the encoder") that realizes steps 2–3.
5. **Training mode.** One sentence: how it is optimized (label-free, self-distilled, online, frozen-backbone, etc.).
6. **Evidence pointer.** One sentence pointing at the teaser/radar figure that shows the mechanism actually fixes the named gap.
7. **Coined term.** One sentence introducing the named gap or named regime the paper will refer to throughout (`\emph{...}` once at first use, plain text thereafter — see `paper-refinement-skills`).

Hard rules:

- **R1 No step may be merged.** If one sentence simultaneously describes a mechanism and names the implementation artifact, the paragraph collapses back into "procedural" prose. The most common failure is fusing steps 2–3 with step 4 ("This design realizes a small adaptation plugin … updated online via …").
- **R2 The hard-region sentence must reuse vocabulary from the easy-region sentence** (e.g., "the same alignment transformation", "the same operator"), not introduce a new verb. If a reader cannot verify by skim that the two regions share one mechanism, the paragraph reads as two parallel methods, which weakens the contribution.
- **R3 No experimental numbers in this paragraph.** Numbers belong in the contribution bullets (see "Contribution bullet format"). Step 6 points at a *figure*, not at AP gains.
- **R4 The premise sentence must be falsifiable in principle.** "Cooperation is important" is not a premise; "agents share large overlapping fields of view" is.

When *not* to use this subtemplate: papers whose method is a single uniform operator with no region/role split (e.g., a new attention variant, a new loss applied everywhere) — those should preview the method as one mechanism, not as a two-region story.

## Self-review checklist (run before declaring a draft done)

For each draft Intro, check:

- [ ] P1 establishes a concrete application context, not a generic AI-is-important paragraph.
- [ ] P2 names the specific problem in one sentence the way the title does.
- [ ] P3 groups prior work into 2–3 named categories, each with at least one cited representative method, and ends with a concrete gap sentence or rhetorical question (Variant A) or the first italicized motivation (Variant B).
- [ ] P4 names the method and its submodules; no performance numbers yet.
- [ ] P5 preview sentence names datasets; contribution bullets follow the default 3-bullet format, or a justified 4-bullet format with the quantified bullet last.
- [ ] Bullet 3 contains ≥1 number and ≥1 dataset name.
- [ ] No "we solve"; "first" claims carry a scope qualifier.
- [ ] Technical terms follow the section-altitude gradient: simple language in Abstract/early Intro, precise protocol terms only after setup or in Appendix.
- [ ] Dataset/protocol contents, model components, controls, and baseline-conversion fairness are not merged into one component inventory.
- [ ] If the paper is reliability/evaluation-driven, the scientific question appears before the artifact is sold as the contribution.
- [ ] Scope assumptions are handled where appropriate; no defensive limitation sentence is forced into the Intro.
- [ ] Every Intro claim can be traced to a specific table or figure in Experiments; write the table number in the margin next to each claim.
- [ ] Fig. 1 follows the teaser-priority order and is referenced in P1–P3.
- [ ] No claimed benefit appears without a corresponding experiment (e.g., do not claim "efficient communication" without a bandwidth-accuracy plot).
- [ ] No structural/ethical claim (privacy, fairness, safety) appears without either an empirical test or an explicit scope disclaimer.

## Out-of-scope variants (see `decision-trees/paper-type-router.md`)

- **Variant C (compressed methodological, NeRF-style)** — only when the paper proposes a new representation and the representation itself is the pitch. Not recommended for V2X / collab perception method papers.
- **Variant D (analogy-scaffolded foundation-model, SAM-style)** — only when the paper is genuinely a foundation-model contribution with task + model + data pillars. Out of scope for single-method papers.
- **Variant E (removal-as-contribution, DETR-style running prose)** — only when the contribution is the elimination of hand-designed components. Requires a very crisp "what we no longer need" story to work.

If a future paper seems to need one of these, route back to the decision tree and promote the variant to a full section file only if the user confirms.
