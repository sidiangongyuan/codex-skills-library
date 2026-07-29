# Literature Digest Schema

Use this structure unless the user provides a better one. Keep the information
and order. Use canonical English or Chinese structural headings for validator
compatibility even when the body uses another requested language. Use
`## Paper N:` or `## 论文 N：` for selected-paper headings.

## Title And Scope

- Specific topic, not "recent papers".
- Absolute inclusive date window.
- Selection mode: quality-first, attention-first, or a stated balance.
- Retrieval date and reading version policy.

## Executive Summary

Answer, in compact prose:

- What changed in this literature window?
- Which 2 or 3 papers should the user read first, and why?
- What result looks most credible?
- What remains uncertain or overclaimed?
- What opportunity is most relevant to the user's goal?

## Search And Selection

Record:

- queries and adjacent terms;
- primary and secondary sources searched;
- raw candidate count and deduplicated count;
- inclusion and exclusion rules;
- full-text availability;
- quality and attention evidence;
- important coverage gaps.

## Comparison Matrix

Use rows for papers and columns for:

| Paper | Problem | Core idea | Data or setting | Main evidence | Quality | Attention | Code or data | Main limitation | Read first? |
|---|---|---|---|---|---|---|---|---|---|

Keep cells short. Put evidence details in the paper sections.

## Paper N: Original Title

Use the original paper title in the heading. Include:

### Verified Metadata

- Authors, arXiv or DOI, v1 date, read version and date.
- Status: preprint, under review, accepted, or published.
- Canonical paper, PDF, project, code, data, and checkpoint links.
- Why this paper passed selection.

### Thirty-Second Verdict

One paragraph that states the central idea, strongest evidence, largest caveat,
and who should read it.

### Problem And Contribution

Explain the research question, why existing methods are insufficient, and the
claimed contribution. Label author claims explicitly.

### Method

Explain the representation, architecture or algorithm, training objective,
data flow, inference path, and important design choices. Retain original method
names, symbols, and technical terms where they help the reader inspect the
paper.

### Evidence Ledger

Use a table:

| Claim | Label | Evidence | Locator | Confidence | Caveat |
|---|---|---|---|---|---|

Include datasets, baselines, metrics, main quantitative or theoretical results,
ablations, robustness checks, and negative evidence. Report numbers with
direction and comparison context.

### Original-Language Evidence

Include 2 to 4 short quote blocks when useful, conservatively totaling no more
than 25 source-language words from the paper by default. For Chinese, Japanese,
or Korean source text, also stay within 50 CJK characters:

> "Exact short fragment." [Source: p. 4, Sec. 3.2]

Immediately explain in the requested output language, Chinese by default:

- literal meaning;
- why the wording matters;
- what evidence supports it;
- what it does not establish.

### Figures And Tables Worth Inspecting

Name the figure, table, theorem, or appendix and explain how to read it. Embed a
source figure only when the license and publishing surface permit it; otherwise
link to the source and provide a precise reading guide.

### Strengths, Limitations, And Reproduction

Separate:

- strongest technical contribution;
- evidence or assumption that may not generalize;
- failure cases and missing comparisons;
- available resources and estimated reproduction burden;
- one smallest useful reproduction or follow-up experiment.

### Connection To The Set

State whether this paper agrees with, contradicts, or complements the other
selected papers.

## Cross-Paper Synthesis

Go beyond shared keywords:

- common assumptions and representations;
- genuine methodological trends;
- conflicting findings and plausible reasons;
- benchmark or evaluation blind spots;
- ideas that transfer across papers;
- evidence that would resolve the disagreements.

## Research Opportunities And Reading Order

Prioritize 3 to 5 opportunities by expected insight, feasibility, and fit to
the user's resources. For each, name the closest papers, testable question,
minimum experiment, and failure signal.

Give a deliberate reading order with a reason for each transition.

## Watchlist

Optionally include promising candidates that lacked full text, fell outside the
window, duplicated a selected idea, or did not yet meet the quality bar. State
the reason; do not present them as deeply read.

## Coverage And Confidence

State what was searched, what could not be accessed, which claims are
author-reported, how attention was measured, and where conclusions may change
with new versions or stronger evidence.
