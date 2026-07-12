# README Playbook

Use this guide when creating or polishing a README for a GitHub release repository.

## Goal

Make the repository understandable to a new external reader. The README is not a lab note, handoff
message, rebuttal record, submission checklist, or conversation with the project owner.

## Default Style

- Write in English unless the user explicitly asks for another language.
- Prefer a polished GitHub project-page rhythm: centered title, light badges/links, optional curated
  visual, short overview, what is included, setup, run commands, citation, acknowledgements, license.
- Adapt sections to the project. Do not force a fixed template if a section would be empty.
- Keep the first screen concrete: project name, status, authors or organization if relevant, and one
  clear sentence about what the project does.

## Required Coverage

Every release README must answer:

- What is this project?
- What problem does it solve?
- What is included in this repository?
- How does a new user install and run the minimal path?
- What datasets/checkpoints/external assets are required but not included?
- How should users cite the project?
- Which upstream repos/papers should also be credited?

If any answer is unavailable, write an honest placeholder such as `Paper link: coming soon.` or
`Pretrained checkpoints will be released separately.` Do not invent facts.

## Top Section

Use a centered block only when it improves the page:

```md
<div align="center">

# Project Name

<p><b>Venue or status, if public</b></p>

<p>
  <a href="#quick-start"><img src="https://img.shields.io/badge/Code-Runnable-green" alt="Code"></a>
  <a href="CITATION.cff"><img src="https://img.shields.io/badge/Citation-CFF-orange" alt="Citation"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Academic-lightgrey" alt="License"></a>
</p>

</div>
```

Use only real links. If the paper URL is not public, write `Paper link: coming soon.` in prose
instead of making a fake badge.

## Explaining The Project

- Explain key terms only when needed. Do not over-explain common field terms.
- Avoid marketing claims that are not supported by the paper or code.
- State the minimal runnable scope clearly. If only a subset is released, say so plainly.
- If the project is derived from upstream code, explain the current contribution and the upstream
  lineage without blurring them.

## Assets And Results

Allowed when curated and relevant:

- teaser image
- method diagram
- main result table from the paper
- benchmark summary from the paper
- small logo or architecture figure

Do not include:

- raw visualization dumps
- temporary experiment screenshots
- full ablation folders
- logs or metrics copied from training outputs
- large videos or archives
- paper PDFs or camera-ready files

Use paper-confirmed results only. Do not extract numbers from logs unless the user explicitly says
those logs are the release source of truth.

## Paper And Citation

- If the paper/arXiv link is public, link it.
- If not public, write `Paper link: coming soon.`
- Do not upload or link local PDFs, camera-ready files, OpenReview-private material, rebuttals,
  review text, or submission instructions.
- Include BibTeX when available. If exact BibTeX is unknown, use a clearly marked placeholder rather
  than fabricating venue, title, authors, or year.

## Upstream Credit

For derivative research code, include both:

- `Acknowledgements`: plain-language credit with upstream repo links.
- `Citation`: upstream BibTeX entries when the user or repo provides verified citations.

Do not preserve an upstream README as the front page for the new project. Use it only as source
material for setup commands, dependency notes, license terms, and upstream attribution.

## Red Flags To Remove

Remove or rewrite content that mentions:

- local paths such as `/mnt/...`, `/home/...`, or machine-specific usernames
- instructions written to the project owner
- TODOs from the release-preparation conversation
- camera-ready, rebuttal, review, meta-review, or submission-process details
- private datasets, private checkpoints, or unpublished artifact paths
- claims that code, checkpoints, or papers are included when they are not
