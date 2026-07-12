# Conclusion Section Playbook

Domain: CV, 3D perception, autonomous driving, and collaborative perception for CVPR, ICCV, ECCV, NeurIPS, and CoRL.

## Default format

- **Single paragraph**, 150–250 words. Enough room for both summary and broader implication.
- **Style: summary + broader implication.** Restate what was done, then offer 1–2 sentences on what the results *suggest* about the problem or field — not just recap.
- **Do not duplicate Abstract verbatim.** Reviewers read both; duplication signals laziness.
- **End with a forward-looking but grounded sentence**, not a vague "future work" aspiration.
- **For evaluation / reliability papers, the broader lesson may be the close.** Do not replay every component or small diagnostic number if the paper's main value is an evaluation lesson.

## Structural slots

A strong Conclusion has **three slots** in order; an optional fourth slot may state a concrete forward direction:

```
[Slot 1] One-sentence paper recap      (problem + method name, ~1 sentence)
[Slot 2] Key results recap             (~1 sentence, with the anchor number from Abstract)
[Slot 3] Broader implication / lesson  (1-2 sentences — "our results suggest that ...")
[Slot 4] (Optional) Pointer to Appendix limitations / a concrete future direction
```

Target: ~5–7 sentences total. If you find yourself adding more, cut; Conclusion is not the place to re-argue claims.

**Playbook default:** Keep detailed Limitations content in a dedicated Appendix section and avoid spending the final sentence on a procedural pointer. Override this when the venue requires a main-text limitations discussion. Slot 4 is either a concrete forward direction or omitted entirely.

## Slot-by-slot guidance

**Slot 1 — Paper recap (1 sentence).** Name the method and state what problem it solves in the barest form.
- Template: "In this paper, we presented {METHOD}, a {category} for {task} under {condition}."
- Avoid "In this paper" if Abstract also used it — rephrase: "We presented ..." or "This work introduced ..."

**Slot 2 — Results recap (1 sentence).** Cite 1 anchor number, matching Abstract exactly.
- Template: "On {dataset A} and {dataset B}, {METHOD} improves {metric} by +{X}% over {baseline}, demonstrating {one-clause capability}."
- Do not re-list every number. One is enough; the table is where the full evidence lives.
- For evaluation or reliability papers, one planning/result number may establish the empirical anchor, but small diagnostic-number pairs usually belong in Experiments or Appendix unless the entire paper turns on that numeric contrast.

**Slot 3 — Broader implication (1–2 sentences, the distinguishing part).** This is what lifts the Conclusion above a recap. Pick exactly one of these moves:
- **Generalization move.** "Our results suggest that {design principle} is effective beyond {current setting}, which may inform {adjacent problem}."
- **Paradigm move.** "These findings indicate that {paradigm shift}, challenging the common assumption that {prior belief}."
- **Practical move.** "This enables {practical capability} that was previously infeasible under {constraint}, opening {specific application}."
- **Lesson move.** "A key takeaway is that {specific lesson tied to ablation}, a factor often overlooked in {prior work family}."

Pick **one** move; stacking multiple dilutes impact. Do not overclaim — the implication must be grounded in the experiments, not aspirational.

For evaluation or reliability papers, prefer the **Lesson move** when it states
what the benchmark or protocol revealed that standard metrics hide. The final
sentence should make that lesson explicit rather than re-listing annotations,
controls, baselines, and appendix diagnostics.

Do not close by replaying implementation or baseline setup details. Checkpoint
choices, reproduction caveats, guard logic, parser mechanics, and control
inventories belong in Experiments or Appendix when they matter, not in the final
takeaway.

**Slot 4 — Optional forward direction (0–1 sentence).** Do **not** use this slot as a procedural Limitations pointer. Either:
- **Omit entirely** if Slot 3 implication already ends on a strong note (preferred default).
- Or state **one** concrete, grounded future direction tied to a specific ablation or setting — never a wishlist.
- Never apologize, never signpost "limitations are discussed in Appendix X"; the Appendix title is the signpost.

## Coordination with other sections

- **Vs Abstract.** Abstract sells; Conclusion reflects. The same facts, but Conclusion permits *interpretation* beyond what Abstract dares ("our results suggest that..."). Wording must not be identical — rephrase key sentences.
- **Vs Introduction.** Intro promised a contribution; Conclusion certifies it was delivered. The verbs in Conclusion should echo Intro's contribution bullets but in the past tense ("We showed that..." ↔ "We contribute...").
- **Vs Limitations (Appendix).** Do **not** pointer-reference Limitations from Conclusion. Limitations are a self-contained Appendix section; its title carries the signpost. Putting Limitations in Conclusion (even as a single pointer sentence) frames recap as weakness and often reads defensive.
- **Number consistency.** The anchor number in Slot 2 must match Abstract, Intro contribution (iii), and main Table exactly — no rounding drift.

## Banned patterns

- **Pure recap with no implication.** "We presented X, which consists of A, B, C. Experiments show it works." — adds no new information over Abstract.
- **Overclaiming in the implication sentence.** "Our work revolutionizes {field}." — reviewers will flag it.
- **Future work as wishlist.** "In the future, we plan to extend to A, B, C, D." — commits nothing; signals the authors ran out of ideas.
- **Contradictions with Experiments.** "Our method is universally applicable" when Experiments show a failure regime — this is the biggest trust-destroyer in the paper.
- **Introducing a new concept/method in Conclusion.** Never. If it matters, it belongs in Method or Appendix.
- **Introducing a new term or taxonomy in Conclusion.** Never. Conclusion should reuse the paper's established terms in their simplest form.
- **Component inventory close.** "The benchmark includes A, B, C, D, and E" is usually a weak ending. Close on what those components let the paper show.
- **Diagnostic-number dump.** Repeating several small control rates or parser scores in the Conclusion reads like a table caption. Keep the lesson and at most one anchor result.
- **Apologetic tone.** "Although our work is limited, ..." — state limitations factually; do not apologize.
- **Emotional closers.** "We hope this work inspires future research." — weak. End with a grounded statement.

## Style do-s and don't-s

- **Do** use past tense for the work's own contributions ("We presented", "We showed"); present tense for enduring statements ("Our results suggest that...").
- **Do** reuse the method name exactly as introduced (same capitalization, same typesetting — `\textsc{}` or plain, pick one paper-wide).
- **Do** keep Conclusion ≤ ¼ page in a two-column layout.
- **Don't** re-cite many works here; 0–2 citations total. Heavy citation belongs in Related Work.
- **Don't** list acknowledgements or funding — those have a dedicated section after Conclusion.
- **Don't** use "conclude" more than once in the paragraph. Overuse is awkward.

## Worked skeletons

**Method paper with a generalization implication.**
> We presented {METHOD}, a {category} that addresses {problem}. Rather than {common strategy}, {METHOD} {one-clause mechanism}, enabled by {key component}. On {dataset A} and {dataset B}, {METHOD} improves {metric} by +{X}% over {baseline}, while using {Y}× less {cost}. These results suggest that {design principle} is a lightweight alternative to {prior paradigm}, and may benefit adjacent tasks such as {adjacent problem 1} and {adjacent problem 2}.

**Method paper with a paradigm implication.**
> In this paper, we introduced {METHOD} for {task} under {condition}. By {key mechanism}, {METHOD} removes the assumption that {assumption} required by prior work. Experiments on {dataset} show a +{X}% gain in {metric}, setting a new state of the art. These findings challenge the common belief that {prior belief} is necessary for {capability}, and point toward simpler formulations of {problem family}.

**Benchmark or new-setting paper.**
> We formalized {PROBLEM}, a setting in which {key twist}, and released {BENCHMARK-NAME}. Adapted baselines leave {gap}, while our proposed {METHOD} achieves {X}% {metric}, establishing a first reference point. A key lesson from our analysis is that {specific lesson}, an axis underexplored by existing {family}. {BENCHMARK-NAME} provides a reference point for further study of {problem}.

## Self-review checklist (run after writing)

- [ ] Single paragraph, 150–250 words.
- [ ] Slots 1–3 present (recap / results / implication). Slot 4 omitted or one concrete forward direction (no Limitations pointer).
- [ ] Slot 2 anchor number matches Abstract / Intro contribution (iii) / main Table exactly.
- [ ] Slot 3 picks exactly one implication move (generalization / paradigm / practical / lesson).
- [ ] No sentence is copy-pasted verbatim from Abstract.
- [ ] No new concept, method, or citation is introduced here.
- [ ] No fresh coined term or taxonomy is introduced here.
- [ ] If this is an evaluation/reliability paper, the paragraph closes on the evaluation lesson, not a component inventory or diagnostic-number dump.
- [ ] No overclaim, no apology, no emotional closer.
- [ ] Detailed limitations follow the chosen venue policy; the ending is not merely a procedural Appendix pointer.
- [ ] Method name and dataset names are spelled identically to the rest of the paper.
- [ ] Conclusion supports, never contradicts, Experiments.

## Exemplar anchors

- **Where2comm** — concise recap + communication-efficiency implication; clean pointer to future work. Good template.
- **HEAL** — recap + generalization implication to heterogeneous-agent ecosystems. Strong for systems-flavored papers.
- **BEVFormer** — minimal Conclusion; focuses on empirical state-of-the-art. Safe but unambitious; use when implication is unclear.
- **DETR** — paradigm-move implication (set prediction as a new detection paradigm). Only imitate when you genuinely shift paradigm.
- **NeRF** — observation + implication style; Conclusion is short and confident. Rare successful pattern.

## Cross-skill handoff

Once Conclusion is drafted, **run `paper-refinement-skills` over it** for sentence-level polish (tense agreement, weak phrasing removal, filler cut). `paper-section-playbook` ensures structure; `paper-refinement-skills` ensures prose.
