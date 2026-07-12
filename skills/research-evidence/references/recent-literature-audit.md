# Recent Literature / Novelty Risk Audit

Use this checklist when a paper's novelty, related-work coverage, reviewer risk,
or first/SOTA/new-benchmark positioning depends on not missing recent or adjacent
work.

## Claim Axes

Extract the paper claim into searchable axes before querying:

- Domain/input: the data source, sensing setup, modality, system context, or user population.
- Method family: model class, algorithm route, training style, or analysis framework.
- Task/output: prediction target, interaction format, benchmark task, or evaluation endpoint.
- Evaluation protocol: metrics, controls, robustness checks, calibration, human study, or audit style.
- Dataset/benchmark: named datasets, new benchmark type, split, annotation, or release claim.
- Reliability/failure mode: hallucination, leakage, grounding, bias, uncertainty, safety, or metric failure.

## Query Matrix

Build at least these query families for high-stakes novelty checks:

- Direct claim query: combine the strongest domain, method, and task terms.
- Method-route query: search method family plus domain, without the exact task term.
- Task/benchmark query: search the task or benchmark type plus evaluation protocol terms.
- Dataset/domain query: search dataset, sensing setup, or domain terms plus broader task words.
- Neighboring terminology query: search older names, adjacent community terms, acronyms, and alternate spellings.
- Newest broad query: search one broad domain/task expression sorted by recent submission date.

Avoid relying on one exact phrase. If the user supplies a term, search its
synonyms and adjacent expressions before concluding that no close work exists.

## Evidence Routes

Use at least two routes for high-stakes checks:

- Direct metadata search: arXiv API, official venue/open-access pages, DOI/Crossref where appropriate.
- Local sources: provided PDFs, `reference/` folders, BibTeX, LaTeX source, related-work notes, or prior paper lists.
- Wrapper search: local `paper-search` or similar tools as a smoke/cross-check, not as sole evidence.
- Citation graph or venue pages when direct metadata is inconclusive and the deadline risk is high.

State source limits. Absence of hits is not strong evidence unless query
families, dates, and source routes are explicit.

## Classification Rubric

- Direct competitor: substantially same input/domain, task/output, and evaluation claim.
- Claim limiter: adjacent work that weakens first/SOTA/only/new-benchmark language but does not replace the contribution.
- Table candidate: close enough for a benchmark or method comparison row.
- Prose citation: relevant adjacent work that belongs in related work but not in the main comparison table.
- Background: useful context but not a threat to the central claim.
- Irrelevant: mismatched task, modality, domain, or contribution after abstract/source inspection.

## Required Output

For a novelty-risk audit, report:

- Search matrix summary: query families, source routes, and date/venue scope.
- Candidate table: title, year/date, identifier, classification, and why it matters.
- Claim-impact verdict: keep, weaken, add citation/table row, revise positioning, or avoid first/SOTA language.
- Recommended paper edits: concrete citation, wording, table, or limitation changes.
- Residual risk: what may still be missing and how serious that uncertainty is.
