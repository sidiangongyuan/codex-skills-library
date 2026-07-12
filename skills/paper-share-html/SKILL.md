---
name: paper-share-html
description: Use when creating or revising a responsive static HTML presentation from a paper, PDF, DOI, or arXiv page for a journal club, lab meeting, or cross-disciplinary report. Preserves source fidelity, extracts legible figures and tables, and verifies browser layout for a live audience.
license: MIT
---

# Paper Share HTML

Build a source-grounded paper presentation that works as a live talk first and
as a readable static page second. Keep the narrative audience-facing: the page
must present the research, not explain the editing process to the requester.

## Read First

- Read [references/editorial-style.md](references/editorial-style.md) before
  drafting Chinese copy, quotations, or slide titles.
- Read [references/visual-qa.md](references/visual-qa.md) before extracting
  figures/tables or validating the finished page.
- Use [assets/template/index.html](assets/template/index.html) as a structural
  starter, not as a fixed slide count or visual theme.

## Workflow

### 1. Ground the report in primary sources

Inspect the complete paper before drafting. Prefer the local PDF; otherwise use
the official publisher, arXiv, project, and code pages. Record the exact title,
authors, version, venue or identifier, project URL, code URL, and BibTeX when
available. Download the paper and supplementary material into `source/` when
licensing and access permit.

Treat the paper as the source of truth for claims, metrics, captions, and
quotations. Use external primary sources to verify cited work and full titles.
Never reconstruct missing citation metadata from memory. If verification is
not possible, mark it as unverified in working notes and omit it from the
audience-facing page rather than guessing.

### 2. Ask one compact intake

After inspecting the supplied material, use `request_user_input` or the
available equivalent when the answers are not already known. Ask at most three
questions in one intake:

1. audience and talk duration;
2. emphasis: balanced, method, results, or critical discussion;
3. delivery language.

Offer concrete choices and put the recommended choice first. If the tool is
unavailable or the user does not answer, use these defaults:

- cross-disciplinary research group;
- 15-20 minutes;
- balanced reconstruction plus evidence review;
- natural Chinese narration with English paper titles, technical terms, and
  verbatim quotations preserved where accuracy benefits.

Do not ask for decisions that can be derived from the paper or workspace.

### 3. Build a claim-evidence map

Before writing HTML, identify:

- the problem and why existing approaches are insufficient;
- the paper's central claim and assumptions;
- the mechanism that is necessary to understand the claim;
- the strongest evidence, including metric direction and comparison scope;
- limitations, unresolved questions, and unsupported extrapolations;
- the final takeaway appropriate for the selected audience.

Separate author claims, observed experimental results, and the presenter's
assessment. Use a problem -> claim -> mechanism -> evidence -> boundary ->
takeaway arc when it fits, but add, merge, or reorder sections to match the
paper. Do not force every paper into the same number of slides.

### 4. Create the paper package

Run:

```bash
python scripts/init_paper_share.py --title "FULL PAPER TITLE" --root "OUTPUT ROOT"
```

Use `--folder-name` only when the user explicitly chooses a short title or the
automatic main-title folder is ambiguous. The script refuses to overwrite an
existing package.

Maintain this output contract:

```text
Paper Main Title/
├── index.html
├── assets/
│   ├── figures/
│   └── tables/
│       └── raw/
├── source/
└── qa/
    └── archive/
```

Keep CSS and JavaScript inside `index.html`; keep visual assets as relative
files. The report must open directly through `file://` without a development
server or network dependency.

### 5. Prepare visual evidence

Use paper and project-page visuals before decorative or generated imagery.
Preserve original figures unless a simpler explanatory redraw is genuinely
needed; label any redraw as a schematic and do not alter the scientific claim.

For experimental tables, render the PDF at high resolution, crop to the table
content, preserve the uncropped or initial capture in `assets/tables/raw/`, and
place the presentation-ready crop in `assets/tables/`. Prefer a faithful image
over manually retyping values. Make tables large in the slide and click-to-zoom.
Explain whether each metric is higher-is-better or lower-is-better and state
exceptions honestly.

### 6. Write for the audience

Use direct, formal, natural statements. Make slide titles carry the finding or
question rather than editorial labels. Explain unfamiliar terms where they
first matter without calling the audience outsiders or announcing a simplified
version.

When literary, historical, or cross-disciplinary language participates in the
paper's argument, include it only when it improves the talk. Preserve the full
English sentence, provide the full title of the cited article or book, and let
the Chinese text continue the argument. Do not create a compulsory quote slide
or cite only an internal location such as “Section 2” or “the abstract.”

### 7. Build the presentation

Adapt the template's theme and composition to the paper while retaining:

- desktop 16:9 slide navigation;
- continuous narrow-screen reading;
- keyboard and icon-button navigation;
- progress indication;
- an accessible image lightbox;
- print styles;
- stable dimensions that prevent layout shifts;
- descriptive alternative text.

Remove every placeholder and unused component. Do not add visible instructions
about how the presentation was written or how the audience should operate it.

### 8. Audit and verify

Run the static audit:

```bash
python scripts/audit_paper_share.py "PATH/TO/PAPER PACKAGE"
```

Fix all errors and review every warning. Then open `index.html` in a real
browser and validate at desktop and mobile viewports. Exercise every slide,
keyboard navigation, table lightbox, local asset, external source link, and
print layout. Save final screenshots under `qa/` and iteration artifacts under
`qa/archive/`. Inspect screenshots visually; a successful command is not proof
that the page is legible.

### 9. Deliver the package

Report the direct local link to `index.html`, the source and QA artifacts
created, and any claim or citation that could not be verified. Do not deploy
the report unless the user explicitly asks for hosting.

## Non-Negotiable Checks

- Do not address the requester inside the presentation.
- Do not use meta labels such as `一句话版`, `外行版`, `值得展示的表述`,
  `下面保留`, `这页适合`, `结果解读`, or `表格解读`.
- Do not shorten a quotation while presenting it as a complete sentence.
- Do not invent a full reference title or metric value.
- Do not claim universal superiority when the table supports only most metrics
  or a subset of tasks.
- Do not accept a small table merely because a zoom control exists; the default
  slide view must remain readable.
- Do not finish without desktop and mobile visual inspection.
