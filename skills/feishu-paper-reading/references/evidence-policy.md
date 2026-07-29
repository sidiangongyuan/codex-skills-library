# Evidence And Selection Policy

Use this policy to keep recency, quality, attention, and technical evidence
separate.

## Source Hierarchy

Use the strongest available source for each job:

1. Paper PDF and supplement for methods, experiments, limitations, and exact
   wording.
2. Official proceedings, OpenReview, DOI, or publisher page for publication
   status and bibliographic metadata.
3. arXiv metadata for version history and v1 submission date.
4. Author project page and official repository for code, data, checkpoints,
   demos, and implementation notes.
5. Scholarly indexes for discovery and cross-checking only.
6. Social posts, newsletters, aggregators, repository activity, and ranking
   sites for attention signals only.

Never cite a search-result page for a technical claim. When sources disagree,
record the disagreement and prefer the source closest to the claimed fact.

## Date And Status Rules

- Interpret "previous N calendar days" as an inclusive interval from
  `today - (N - 1)` through today in the user's timezone, or UTC when unknown.
- Use arXiv v1 date for inclusion in an arXiv-only or newly posted window.
- Use the official decision or publication date for newly accepted or
  published work.
- For general recent-work requests, accept either path and label the qualifying
  date basis per paper.
- Read the newest version and record its version number and date.
- Label a work `accepted` or `published` only when an official venue source
  confirms it.
- Label OpenReview submissions under review unless a decision is public.
- Treat preprints as provisional even when they are popular.

## Quality And Attention

Keep these dimensions separate:

| Dimension | Evidence |
|---|---|
| Relevance | Direct match to the user's research question |
| Novelty | Clear difference from close prior work |
| Rigor | Appropriate baselines, controls, ablations, statistics, or proofs |
| Evidence strength | Results support the paper's main claim under stated assumptions |
| Reproducibility | Code, data, checkpoints, detail, and feasible resource needs |
| Attention | Observable engagement with source, metric, and retrieval date |

Use qualitative ratings such as strong, mixed, weak, or unverified unless the
user requests a scoring rubric. Missing evidence is `unverified`, not zero.
Attention can break a tie; it cannot rescue weak technical evidence when the
brief says quality first.

## Claim Labels

Apply one label to each consequential statement:

- `Source fact`: directly observable metadata or reported measurement.
- `Author claim`: the authors' interpretation or asserted contribution.
- `Codex interpretation`: synthesis, criticism, or implication derived during
  review.

Attach a source locator to the first two. Mark the confidence of Codex
interpretations and name the evidence that would change them.

## Full-Read Standard

A deep-read paper must have:

- accessible full text;
- method and main result inspection;
- at least one evidence locator beyond the abstract;
- limitations, assumptions, or failure modes checked;
- relevant appendix or supplement checked when it changes a claim.

If any condition fails, move the paper to the watchlist or label the exact
coverage limitation. Never infer missing experimental details.

## Original-Language Excerpts

Choose fragments that expose definitions, central findings, or limitations.
Keep total direct quotation from one paper within 25 source-language words by
default, split across 2 to 4 micro-excerpts when that improves inspection. For
Chinese, Japanese, or Korean source text, also keep the total within 50 CJK
characters. Each excerpt must be exact and carry a page, section, figure, table,
theorem, or appendix locator.

Do not reproduce an abstract, conclusion, or continuous long passage. Use
paraphrase for breadth and short original fragments for auditability. A source
license or user-provided text may permit more, but only expand when the
applicable policy clearly allows it.

## Confidence And Coverage

At completion, disclose:

- databases and sites searched;
- inaccessible PDFs, supplements, or repositories;
- attention sources that were unavailable;
- selection decisions affected by missing evidence;
- claims that remain author-reported rather than independently verified.
