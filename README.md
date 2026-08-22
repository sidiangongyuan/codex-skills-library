<p align="center">
  <img src="assets/library-mark.svg" width="76" height="76" alt="Codex Skills Library mark">
</p>

<h1 align="center">Codex Skills Library</h1>

<p align="center">
  Installable Codex workflows for research, papers, apps, and everyday technical work.
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="docs/FEISHU_PAPER_READING.md">Featured workflow</a> ·
  <a href="docs/SKILL_CATALOG.md">Skill catalog</a> ·
  <a href="docs/INSTALL.md">Installation</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <a href="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml"><img alt="Quality" src="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml/badge.svg"></a>
</p>

<p align="center">
  <a href="assets/readme-overview.svg"><img src="assets/readme-overview.svg" width="100%" alt="A task moves through an installed skill and Codex checkpoints to an inspectable result"></a>
</p>

Codex Skills Library collects 19 installable workflows distilled from repeated
research, software, and technical operations work. A skill is closer to a
lightweight SOP than a prompt: it tells Codex what to inspect, which checkpoints
matter, what artifact to leave behind, and when to stop for a human decision.

Use one skill for a focused job or compose several across a longer project.
Each installable directory keeps its instructions, declared requirements,
license, and provenance together.

Research and paper work make up the largest part of the current catalog, but
this is not a research-only library:

- **Research and papers · 10 skills**: experiments, evidence, recent-paper
  reading, writing, review, rebuttal, figures, and presentations.
- **Apps and UI · 5 skills**: product design, feature delivery, debugging, and
  application releases.
- **General methods · 2 skills**: clarify an underspecified plan and search
  before building.
- **GitHub and Codex operations · 2 skills**: publish a clean repository or
  restore missing Codex Desktop sessions.

_Independent community project; not affiliated with or endorsed by OpenAI._

## Featured · Feishu paper reading

> **Turn a research question into an evidence-grounded, read-back-verified
> Feishu brief, not a link dump.**

[`feishu-paper-reading`](docs/FEISHU_PAPER_READING.md) owns the whole path:
broad candidate retrieval, primary-source verification, full-text and appendix
reading, an evidence ledger, cross-paper synthesis, report validation,
checkpointed Feishu publication with no blind duplicate retries, and read-back
verification. When no writable route exists, it can guide a least-privilege
official setup without bundling credentials or silently taking over an account.

The delivery contract is concrete: key source figures and tables are embedded
directly into the Feishu document through a DOCX import route, the
blue/green/purple/orange/red/gray reading palette stays consistent across
issues, and the report remains article voice rather than a conversation with
the reader.

<p align="center">
  <a href="docs/FEISHU_PAPER_READING.md"><img src="assets/feishu-paper-reading/actual-summary.png" width="100%" alt="An anonymized crop from an actual Feishu paper-reading report showing a concise conclusion grounded in the selected paper"></a>
</p>

<p align="center"><sub>Actual connector-backed output, cropped to the document canvas; private account and document identifiers are omitted.</sub></p>

**[Explore the workflow, real output excerpts, setup behavior, and install
prompts &rarr;](docs/FEISHU_PAPER_READING.md)**

## Start with one skill

Codex includes the `$skill-installer` system skill. Give it the GitHub URL of an
individual skill directory. Choose the example closest to the work in front of
you.

**Research or coursework**

```text
$skill-installer Install https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/experiment-planner
```

On the next turn, try a concrete request:

```text
$experiment-planner Turn my image-classification course project into a one-day pilot with baselines, metrics, resource assumptions, and a stop/go decision.
```

A useful result should contain a falsifiable claim, comparisons, the smallest
pilot, expected signals, and a decision gate, not just a longer brainstorm.
The [worked example](docs/EXAMPLE_EXPERIMENT_PLAN.md) shows the shape of that
artifact without pretending that unrun experiments produced results.

**Application debugging**

```text
$skill-installer Install https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/app-bug-forensics
```

On the next turn:

```text
$app-bug-forensics Trace this intermittent timeout from the visible symptom through logs and the request path. Identify the root cause before changing code.
```

A useful result should distinguish observations from hypotheses, identify the
failing boundary, and leave behind a focused regression check.

There is no need to install all 19 skills. Replace `experiment-planner` with any
name in the [catalog](#browse-by-goal). The installed skill is available on the
next turn. Review its `SKILL.md`, `LICENSE`, requirements, and provenance before
using it in a sensitive environment. See the
[single-skill installation details](docs/INSTALL.md#install-one-skill-with-codex)
for private forks and command-line alternatives.

<details>
<summary><strong>Install several skills</strong></summary>

The repository installer supports selected or bulk installation and has no
runtime dependencies outside the Python standard library. It defaults to the
shared user-level directory `$HOME/.agents/skills`.

```bash
git clone https://github.com/sidiangongyuan/codex-skills-library.git
cd codex-skills-library
python scripts/install.py
python scripts/install.py --all --dry-run
python scripts/install.py --all
```

Running the installer without selection arguments only prints the catalog and
usage. `--all` is always explicit. To install a smaller set:

```bash
python scripts/install.py \
  --skill experiment-planner \
  --skill app-bug-forensics \
  --skill search-first \
  --dry-run

python scripts/install.py \
  --skill experiment-planner \
  --skill app-bug-forensics \
  --skill search-first
```

Existing skill directories are skipped by default. Use `--replace` only after
reviewing the dry run. Use `--target <directory>` to install elsewhere. The
[installation guide](docs/INSTALL.md) covers Windows paths, manual copying,
legacy `--codex-home` compatibility, and troubleshooting.

</details>

## Start from the work in front of you

- **A vague plan or an unfamiliar task**:
  `grill-me` &rarr; `search-first` clarifies the decisions that matter and
  checks maintained tools or prior work before anything custom is built.
- **A software coursework or capstone project**:
  `grill-me` &rarr; `search-first` &rarr; `app-feature-craft` turns a vague brief
  into a bounded project, checks existing tools, and carries the chosen path
  through implementation and verification.
- **A deep-learning research idea**:
  `grill-me` &rarr; `search-first` / `research-evidence` &rarr;
  `experiment-planner` separates the claim from the hunch, checks prior work,
  and ends with a pilot-first experiment matrix.
- **A recent-paper reading digest**:
  [`feishu-paper-reading`](docs/FEISHU_PAPER_READING.md) searches a broad
  candidate pool, deeply reads the
  selected papers, preserves short original-language evidence, synthesizes the
  set, and publishes a verified Feishu report. If no verified connection
  exists, it guides the official least-privilege Feishu setup step by step
  before publishing; Markdown fallback is reserved for a declined,
  incompatible, or unsuccessful setup.
- **A paper before submission**:
  `paper-section-playbook` &rarr; `paper-refinement-skills` &rarr;
  `paper-review-panel` structures the argument, tightens it without inflating
  claims, and exposes decision-changing review risks.
- **Official reviews and rebuttal**:
  `rebuttal-response-skills` takes over only after reviews arrive, mapping exact
  concerns to evidence and reviewer-specific responses.
- **Figures, tables, and a research talk**:
  `paper-framework-figure-studio-pro` &rarr; `paper-visual-craft` &rarr;
  `paper-share-html` plans the visual story, refines the evidence, and prepares
  an audience-ready presentation.
- **An application or open-source release**:
  `app-feature-craft` &rarr; `app-bug-forensics` &rarr;
  `app-release-readiness` builds the feature, traces failures to root cause,
  and verifies what is actually shipped.
- **Repository publishing or Codex recovery**:
  `github-project-release` audits a project before publishing, while
  `codex-session-restore` handles a specific Codex Desktop session-recovery
  problem after provider switches.

## Browse by goal

The concise table below is generated from [`skills.json`](skills.json).
Requirements, example prompts, licenses, and pinned source revisions remain in
the generated [full skill catalog](docs/SKILL_CATALOG.md).

<!-- skills-table:start -->

| Goal | Skill | Use it for |
|---|---|---|
| Research Ideation & Experiment Planning | [`experiment-planner`](skills/experiment-planner) | Plan deep-learning and computer-science research ideas as claim-driven, pilot-first experiment matrices. |
| Evidence & Search | [`research-evidence`](skills/research-evidence) | Search academic evidence, verify citation metadata, and check whether sources support research claims. |
| Evidence & Search | [`feishu-paper-reading`](skills/feishu-paper-reading) | Find, deeply read, and synthesize recent papers, then publish verified Feishu reports with guided official setup when no connection exists. |
| General Planning & Search | [`search-first`](skills/search-first) | Search for maintained tools, libraries, skills, research, and proven patterns before building a custom solution. |
| UI/UX & Product Design | [`design-taste-frontend`](skills/design-taste-frontend) | Infer a design language and build distinctive landing pages, portfolios, and redesigns with strict layout, motion, accessibility, and pre-flight checks. |
| UI/UX & Product Design | [`ui-ux-pro-max`](skills/ui-ux-pro-max) | Design and review accessible web and mobile interfaces with a searchable UI/UX knowledge base. |
| App Development & Release | [`app-feature-craft`](skills/app-feature-craft) | Build product-grade app features across UX, frontend, backend, tests, and end-to-end verification. |
| App Development & Release | [`app-bug-forensics`](skills/app-bug-forensics) | Diagnose user-reported application failures from symptoms and logs through root cause and regression coverage. |
| App Development & Release | [`app-release-readiness`](skills/app-release-readiness) | Prepare, package, publish, and verify desktop or web application releases without shipping stale artifacts. |
| General Planning & Search | [`grill-me`](skills/grill-me) | Interview a user one decision at a time to stress-test an underspecified plan or design. |
| Paper Writing | [`paper-section-playbook`](skills/paper-section-playbook) | Plan and restructure sections of computer-vision, 3D-perception, and autonomous-driving research papers. |
| Paper Writing | [`paper-refinement-skills`](skills/paper-refinement-skills) | Refine research-paper logic and prose while preserving verified claims, terminology, notation, and citation boundaries. |
| Paper Review & Readiness | [`paper-review-panel`](skills/paper-review-panel) | Independently review a paper before submission, synthesize top-conference concerns, and identify decision-changing readiness risks without editing the manuscript. |
| Rebuttal & Author Response | [`rebuttal-response-skills`](skills/rebuttal-response-skills) | Run an evidence-grounded rebuttal lifecycle from exact concern mapping and approved experiments through reviewer-specific responses and blind final audits. |
| Figures & Tables | [`paper-framework-figure-studio-pro`](skills/paper-framework-figure-studio-pro) | Plan source-grounded method, architecture, pipeline, system, and agent-workflow figures for CS and deep-learning papers. |
| Figures & Tables | [`paper-visual-craft`](skills/paper-visual-craft) | Design, redraw, and validate publication-ready research figures and tables while preserving exact evidence. |
| Paper Communication | [`paper-share-html`](skills/paper-share-html) | Create source-grounded, responsive paper presentations with readable PDF-extracted tables, varied explanatory diagrams, optional presenter-paced reveals, and live-talk browser QA. |
| Operations & Release | [`github-project-release`](skills/github-project-release) | Prepare a clean GitHub project repository with publication audits and controlled release workflows. |
| Operations & Release | [`codex-session-restore`](skills/codex-session-restore) | Diagnose and restore active Codex Desktop sidebar sessions after provider switches without changing authentication. |

<!-- skills-table:end -->

For example prompts, dependency notes, licenses, and pinned upstream revisions,
open the generated [full skill catalog](docs/SKILL_CATALOG.md). Attribution and
source treatment are recorded in [NOTICE.md](NOTICE.md).

## Use a skill

Explicit invocation is the clearest way to make a workflow reproducible. Start
with a general method when the task itself is still unclear:

```text
$search-first Find maintained tools and libraries for this dataset utility before we decide to build it ourselves.
```

For an application failure:

```text
$app-bug-forensics Diagnose this intermittent provider timeout from the UI state through the request path. Report the root cause before changing code.
```

For research planning:

```text
$experiment-planner Turn this idea into a pilot-first experiment matrix with a falsifiable claim, baselines, diagnostics, and a stop/go gate.
```

Before submission, use the review panel to expose decision-changing paper
risks:

```text
$paper-review-panel Review this draft before submission. Separate decision-changing evidence gaps from issues that can be fixed with writing.
```

Most included skills allow implicit invocation when their description closely
matches the request. Skills whose default workflow publishes externally may
require explicit `$skill-name` invocation; their `agents/openai.yaml` records
that policy. Explicit invocation is preferable for repeatable handoffs.

Skills can be composed in sequence, but each stage keeps a clear owner. See
[workflow recipes](docs/USAGE.md) for complete examples and handoff points.

## Contribute

Contributions are welcome from any domain. A proposal issue is optional; a pull
request may add a useful skill directly. New skills must include:

- a focused `SKILL.md` with a matching lowercase kebab-case name;
- an example prompt and complete requirements in `skills.json`;
- an applicable license inside the installable skill directory;
- original-work or pinned-upstream provenance; and
- safe defaults for destructive, publishing, or externally visible actions.

Do not include credentials, private conversations, unpublished project
material, machine-specific paths, datasets, checkpoints, or redistribution
rights that are unclear. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the template,
validation commands, and review criteria.

## License and safety

Original project material is licensed under the [MIT License](LICENSE).
Third-party material remains under its upstream license and copyright; every
installable skill carries the license text that applies to it. See
[NOTICE.md](NOTICE.md) for provenance labels and fixed source revisions.

Skills can influence tool use and may include executable helpers. The library
installer only copies files and never executes installed helpers, but users
should still inspect skills before granting them access to sensitive data,
credentials, publishing surfaces, or destructive tools. Report security issues
through the process in [SECURITY.md](SECURITY.md).
