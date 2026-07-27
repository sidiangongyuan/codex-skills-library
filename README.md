<p align="center">
  <img src="assets/library-mark.svg" width="76" height="76" alt="Codex Skills Library mark">
</p>

<h1 align="center">Codex Skills Library</h1>

<p align="center">
  Reusable workflows for research, paper writing, product engineering, visual communication, and release operations.
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="docs/SKILL_CATALOG.md">Skill catalog</a> ·
  <a href="docs/INSTALL.md">Installation</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <a href="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml"><img alt="Quality" src="https://github.com/sidiangongyuan/codex-skills-library/actions/workflows/quality.yml/badge.svg"></a>
  <img alt="17 skills" src="https://img.shields.io/badge/skills-17-0f766e">
  <img alt="Python standard library installer" src="https://img.shields.io/badge/installer-Python%20stdlib-2563eb">
  <a href="NOTICE.md"><img alt="Tracked provenance" src="https://img.shields.io/badge/provenance-tracked-b45309"></a>
</p>

Codex Skills Library is a public collection of reusable workflows for product
development, research, academic writing, visual communication, and project
operations. Each skill is an installable directory with focused instructions,
optional helpers, declared requirements, and traceable provenance.

This is an independent, community-maintained project. It is not an official
OpenAI project and is not affiliated with or endorsed by OpenAI. The repository
itself is the distribution: there is no separate website, GitHub Pages site, or
plugin marketplace.

<table>
  <tr>
    <td width="33%">
      <strong>Find one skill</strong><br>
      Start from the goal-oriented catalog and install only the workflow you need.<br><br>
      <a href="#browse-by-goal">Browse by goal</a>
    </td>
    <td width="33%">
      <strong>Build a workflow</strong><br>
      Compose focused skills across research, writing, review, rebuttal, and release.<br><br>
      <a href="#workflow-map">See workflow paths</a>
    </td>
    <td width="33%">
      <strong>Inspect before use</strong><br>
      Every skill keeps its requirements, license, and provenance close to the installable files.<br><br>
      <a href="docs/SKILL_CATALOG.md">Open the full catalog</a>
    </td>
  </tr>
</table>

## Quick start

Codex includes the `$skill-installer` system skill. Give it the GitHub URL of an
individual skill directory:

```text
$skill-installer Install https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/research-evidence
```

Replace `research-evidence` with any name in the catalog. The installed skill
will be available on the next turn. `$skill-installer` uses the skill directory
configured for the current Codex environment.

Review the selected skill's `SKILL.md`, `LICENSE`, requirements, and provenance
before installing it in a sensitive environment. See the
[single-skill installation details](docs/INSTALL.md#install-one-skill-with-codex)
for private forks and command-line alternatives.

### Install several skills

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
  --skill research-evidence \
  --skill paper-section-playbook \
  --dry-run

python scripts/install.py \
  --skill experiment-planner \
  --skill research-evidence \
  --skill paper-section-playbook
```

Existing skill directories are skipped by default. Use `--replace` only after
reviewing the dry run. Use `--target <directory>` to install elsewhere. The
[installation guide](docs/INSTALL.md) covers Windows paths, manual copying,
legacy `--codex-home` compatibility, and troubleshooting.

## Workflow map

<table>
  <tr>
    <td width="50%">
      <strong>Research discovery</strong><br>
      <code>grill-me</code> &rarr; <code>experiment-planner</code> &rarr; <code>research-evidence</code><br><br>
      Turn an ambiguous idea into a falsifiable plan, then verify the literature and claims.
    </td>
    <td width="50%">
      <strong>Paper lifecycle</strong><br>
      <code>paper-section-playbook</code> &rarr; <code>paper-refinement-skills</code> &rarr; <code>paper-review-panel</code> &rarr; <code>rebuttal-response-skills</code><br><br>
      Structure and refine the paper, review it before submission, then switch to the rebuttal workflow only after official reviews arrive.
    </td>
  </tr>
  <tr>
    <td width="50%">
      <strong>Product delivery</strong><br>
      <code>app-feature-craft</code> &rarr; <code>app-bug-forensics</code> &rarr; <code>app-release-readiness</code><br><br>
      Build a feature, diagnose failures from evidence, and validate the release surface.
    </td>
    <td width="50%">
      <strong>Paper communication</strong><br>
      <code>paper-framework-figure-studio-pro</code> &rarr; <code>paper-visual-craft</code> &rarr; <code>paper-share-html</code><br><br>
      Plan the visual story, refine figures and tables, and prepare an audience-ready presentation.
    </td>
  </tr>
</table>

## Browse by goal

The concise table below is generated from [`skills.json`](skills.json).
Requirements, example prompts, licenses, and pinned source revisions remain in
the generated [full skill catalog](docs/SKILL_CATALOG.md).

<!-- skills-table:start -->

| Goal | Skill | Use it for |
|---|---|---|
| Research Ideation & Experiment Planning | [`experiment-planner`](skills/experiment-planner) | Plan deep-learning and computer-science research ideas as claim-driven, pilot-first experiment matrices. |
| Evidence & Search | [`research-evidence`](skills/research-evidence) | Search academic evidence, verify citation metadata, and check whether sources support research claims. |
| Evidence & Search | [`search-first`](skills/search-first) | Search for maintained tools, libraries, skills, research, and proven patterns before building a custom solution. |
| UI/UX & Product Design | [`ui-ux-pro-max`](skills/ui-ux-pro-max) | Design and review accessible web and mobile interfaces with a searchable UI/UX knowledge base. |
| App Development & Release | [`app-feature-craft`](skills/app-feature-craft) | Build product-grade app features across UX, frontend, backend, tests, and end-to-end verification. |
| App Development & Release | [`app-bug-forensics`](skills/app-bug-forensics) | Diagnose user-reported application failures from symptoms and logs through root cause and regression coverage. |
| App Development & Release | [`app-release-readiness`](skills/app-release-readiness) | Prepare, package, publish, and verify desktop or web application releases without shipping stale artifacts. |
| Research Ideation & Experiment Planning | [`grill-me`](skills/grill-me) | Interview a user one decision at a time to stress-test an underspecified plan or design. |
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

Explicit invocation is the clearest way to make a workflow reproducible:

```text
$app-bug-forensics Diagnose this intermittent provider timeout from the UI state through the request path. Report the root cause before changing code.
```

```text
$experiment-planner Turn this idea into a pilot-first experiment matrix with a falsifiable claim, baselines, diagnostics, and a stop/go gate.
```

Before submission, use the review panel to expose decision-changing paper risks:

```text
$paper-review-panel Review this draft before submission. Separate decision-changing evidence gaps from issues that can be fixed with writing.
```

After official reviews arrive, switch workflow owners:

```text
$rebuttal-response-skills Map these exact reviews, build the evidence ledger, draft reviewer-specific responses, and run the final blind audit.
```

All included skills also allow implicit invocation: Codex may select one when
its description closely matches the request. Explicit `$skill-name` invocation
is preferable when a particular workflow or a repeatable handoff matters.

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
