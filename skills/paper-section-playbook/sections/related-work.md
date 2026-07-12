# Related Work Section Playbook

Domain: CV, 3D perception, autonomous driving, and collaborative perception for CVPR, ICCV, ECCV, NeurIPS, and CoRL.

## Placement and budget

- **Default placement.** Put Related Work between Introduction and Method, commonly as §2. This is the CVPR/ICCV/ECCV norm; move it only when the venue or paper structure provides a strong reason.
- **Length budget.** Around **1 page** total, single column. If the main paper is tight, compress to ~¾ page by tightening prose, not by dropping a whole theme.
- **Theme count.** 2–3 themes. **Quality of each theme matters more than the count.** Prefer 2 well-written themes with sharp positioning over 3 thin themes that read like paper lists.

## Section skeleton

```
2. Related Work
├── 2.1 Theme A  (technical lineage 1, e.g., "Early / intermediate / late collaborative fusion")
│   ├── Paragraph 1: define the lineage, list seminal works
│   ├── Paragraph 2: list recent representative works with one-line technical summary
│   └── Closing sentence: "Unlike these, we ..."
├── 2.2 Theme B  (technical lineage 2, e.g., "Heterogeneous perception")
│   └── (same 3-part structure)
└── 2.3 Theme C  (optional, e.g., "Learning-based V2X communication")
    └── (same 3-part structure)
```

Each theme is a **technical genealogy**, not a chronological list. The reader should walk away knowing *what family of solutions exists* and *why none of them suffice*, not *who published when*.

## Theme selection rule

Themes must be chosen so that:

1. **Each theme is a coherent technical lineage**, sharing a common assumption or design paradigm that your paper challenges or extends.
2. **Every theme contains a critique** — there must be a *common limitation* across the works in that theme. If you cannot state one, that theme does not belong.
3. **Themes are mutually separable** — a prior work should fit cleanly in one theme, not two. Overlap signals weak axis selection.
4. **Your contribution should strictly require positioning against each theme.** If removing a theme does not weaken your positioning, drop it.

**Banned theme patterns.**
- "Deep learning for {task}" — too broad; reads as a textbook survey.
- A theme that only lists papers without a shared limitation.
- A theme that restates your own contribution instead of discussing prior work.

## Per-theme internal structure (technical-lineage mode)

Each subsection has 2–3 paragraphs following this rhythm:

**Paragraph 1 — Lineage and seminal works (3–5 sentences).**
- Sentence 1: *define the technical path* ("Collaborative perception methods can be categorized as early-, intermediate-, and late-fusion, depending on where inter-agent information is exchanged.").
- Sentence 2–3: *list 2–3 seminal works* with a single-clause technical label each ("Early fusion \cite{X} transmits raw sensor data; late fusion \cite{Y} transmits detections.").
- Sentence 4: *name the dominant direction this paper engages with* ("Intermediate-fusion methods strike a balance and are the current mainstream.").

**Paragraph 2 — Recent representative works and shared limitation (4–6 sentences).**
- Sentence 1–3: *list 3–5 recent works*, each with one clause: *what it proposes* + *what axis it optimizes*. Cite heavily but keep each item ≤ 1 sentence. No one-paragraph-per-paper.
- Sentence 4–5: *extract the common failure mode or unmet need* across these works ("All of these methods assume homogeneous agents / shared backbones / clean synchronization / …").
- This is the theme's **critique anchor**. It must be specific and testable, not vague ("existing methods have limitations" is banned).

**Closing sentence — positioning (1 sentence, mandatory).**
- Template: "Unlike {these works / this line of work}, {our method} {key differentiator tied to Method}, {one-clause benefit tied to Experiments}."
- This sentence does *not* need to explain the method; that is Sec. 3's job. It states the *axis of difference* and a *one-word benefit*.
- Do not merge the positioning into the critique paragraph — a separate sentence is more legible and easier for reviewers to scan.

## Citation discipline

- **Breadth target.** Each theme cites roughly 8–15 works. Heavy citation is fine and expected — Related Work is the one place where dense `\cite` stacking reads as thorough rather than name-dropping.
- **Must-cite coverage.** Include: (a) the 1–2 most-cited seminal works of the lineage, (b) the 2–3 most recent same-venue papers of the past 1–2 years, (c) any concurrent / closely related work even if not yet peer-reviewed (arXiv preprints OK, but mark them as concurrent if needed).
- **Strong-baseline rule.** Every method appearing in your Experiments' main table **must** appear in Related Work. Conversely, a method discussed at length in Related Work should usually be compared against in Experiments, or justified why not.
- **Self-citation.** Cite your group's prior work normally; if the current paper extends a prior workshop / preprint of yours, disclose in a footnote.
- **Grouping citations.** Multi-cite with `\cite{a,b,c}` after a collective label ("Attention-based fusion \cite{a,b,c}") is preferred over listing each author name for tertiary works.

## Rhetorical moves

- **Categorization move.** "{Task} methods can be broadly categorized into {axis}, including {A}, {B}, and {C}."
- **Mainstream-direction move.** "{Axis-B} methods are the current mainstream due to {reason}."
- **Lineage-list move.** "Early work \cite{X} {one-clause}. More recent methods \cite{Y,Z} improve upon this by {axis}."
- **Critique anchor move.** "However, these methods share a common assumption: {assumption}, which breaks down in {scenario}."
- **Positioning move.** "Unlike {these}, our method {key differentiator}, enabling {one-clause benefit}."
- **Concurrent-work move.** "Concurrent to our work, \cite{X} also explores {axis}; our approach differs in {one crisp difference}."

## Style do-s and don't-s

- **Do** write in present tense for prior work ("X proposes..."), not past tense ("X proposed...").
- **Do** keep each paper to ≤ 1 sentence unless it is a direct baseline worth a full-paragraph contrast.
- **Do** use `et~al.` (with `\,` or `~` for non-break) consistently.
- **Don't** open with "In the past few years, {field} has gained tremendous attention" — filler, reviewers skip past it.
- **Don't** describe a paper's full method in detail — that is the job of that paper, not yours.
- **Don't** write Related Work as a literature review for a survey — readers want *positioning*, not *coverage*.
- **Don't** cite 5 papers for one trivial fact; one representative citation suffices.
- **Don't** use "however" / "nevertheless" more than once per theme — stacking contrastives signals vague critique.

## Coordination with Introduction

Related Work and Introduction must not duplicate each other.

- **Introduction** frames the *problem* and *insight*. It may cite 3–6 works in paragraphs 2–3, each serving the narrative ("existing X fails because Y").
- **Related Work** provides the *technical landscape* and *axis of difference*. It cites 20–40 works organized by lineage.
- Any critique that appears in Introduction should reappear in Related Work's **critique anchor sentence** — same claim, deeper citation. Readers should feel Related Work *substantiates* Intro, not repeats it.

**Anti-pattern.** Copy-pasting the same 3 sentences from Intro's "existing work" paragraph into Related Work's opening. Fix by making Intro's version narrative (1 sentence per family) and Related Work's version technical (per-family critique paragraph with 5-10 cites).

## Coordination with Method

- Method's opening paragraph (§3.1 / M1) often needs 1–2 re-citations of the direct competitor (HEAL, Where2comm, etc.) to frame the building block you extend. Related Work should have already named and critiqued these competitors — the Method section *borrows the name* and moves on, not re-introduces.
- If Method uses a specific prior-work technique as a module (e.g., "we use a DETR-style decoder"), it is acceptable to cite that work in Method without discussing it in Related Work, since it is instrumental, not competitive.

## Self-review checklist (run before submission)

- [ ] Related Work is §2, between Introduction and Method.
- [ ] Total length ≈ 1 page, 2–3 themes.
- [ ] Each theme has a **stated axis** (one sentence categorizing the lineage).
- [ ] Each theme has a **critique anchor** — a specific shared limitation, not hand-waving.
- [ ] Each theme ends with a **"Unlike these, we..."** sentence.
- [ ] Every method in the Experiments main table is cited in Related Work.
- [ ] No paper is discussed in more than one theme (axis cleanness).
- [ ] No theme can be removed without weakening positioning.
- [ ] Citation density is 20–40 works across the section.
- [ ] No filler openers ("In recent years, ..."), no paper-by-paper walkthroughs, no full-method restatements.
- [ ] Concurrent work (past ~3 months) is disclosed if relevant.

## Exemplar anchors

- **Where2comm** §2: 2-theme structure (collaborative perception lineage + attention-based communication); clean "Unlike these, we..." closing.
- **HEAL** §2: 3-theme structure (collab perception, heterogeneous agents, model alignment); strong critique anchors per theme.
- **BEVFormer** §2: 2-theme structure (camera-only 3D detection + BEV representation); compact 1-page, heavy on lineage.
- **DETR** §2: exceptional pedagogical structure using set-prediction lineage + Hungarian matching — worth reading even outside detection.
- **NeRF** §2: short and narrative-first; works because the paradigm is new. **Not a template for most papers.**
- **SAM** §2: an anti-example for typical research papers — too broad, reads like a tech report. Use as a counter-reference, not a model.
