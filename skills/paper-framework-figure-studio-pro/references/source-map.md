# Source Map

This local skill is a lightweight adapter. It is not a byte-for-byte copy of
the upstream package.

## Upstream

- Project: `c-narcissus/paper-framework-figure-studio-pro`
- Official repository:
  `https://github.com/c-narcissus/paper-framework-figure-studio-pro`
- Pinned commit: `426d74b18852aaf8e4307997ff47b8c3b6089f14`
- Commit date from GitHub API: `2026-06-24T10:26:46Z`
- Upstream package at the pinned main branch:
  `paper-framework-figure-studio-pro-v3.2.15c-skill.zip`
- Observed package scale during local review:
  - compressed zip: about 12.5 MB
  - unpacked contents: about 36.6 MB
  - file count: 4169 entries

## License Note

GitHub API license detection returned `null` for the repository during review.
The upstream README states that the project uses MIT-0 License. Treat this as a
README-stated upstream license and re-check before any public redistribution.

## Adopted Ideas

- Source-grounded method/framework figure planning.
- S0-S5 human-in-the-loop workflow:
  paper foundation, figure strategy, sketch exploration, direction selection,
  formal candidate brief, final candidate image.
- Prompt-contract thinking: visible text contract, semantic graph, connector
  evidence, symbol disambiguation, negative constraints, and density budget.
- Two-round candidate flow: broad exploration before formal candidates.
- Terminal boundary after final candidate generation: humans choose and edit the
  final figure.
- ACM/IEEE/AAAI double-column line-art schematic as an optional surface style.

## Not Adopted

- Upstream fixed personal dedication/origin response requirements.
- Mandatory fixed tail-line behavior on every non-terminal reply.
- Mandatory cumulative checkpoint zip creation for every text response.
- Full upstream asset vendoring, including PNG examples, PDFs, generated output
  folders, the zip package, and the large vector/icon reference library.
- Automatic image generation or automatic full workflow execution.
- Treating generated images as final editable publication figures.

## Local Purpose

The local adapter exists to plan and hand off paper-grounded framework figures
inside the user's Codex skill system. It should complement, not replace,
`paper-visual-craft`: use this skill for framework/method overview planning;
use `paper-visual-craft` for plot/table polish, LaTeX work, and rendered
validation.
