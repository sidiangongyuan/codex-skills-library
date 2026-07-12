<p align="center">
  <img src="assets/library-mark.svg" width="76" height="76" alt="Codex Skills Library mark">
</p>

<h1 align="center">Codex Skills Library</h1>

<p align="center">
  Practical Codex skills distilled from real workflows, with clear provenance and community contributions.
</p>

<p align="center">
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="docs/SKILL_CATALOG.md">Skill catalog</a> ·
  <a href="docs/INSTALL.md">Installation</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

Codex Skills Library is a public collection of reusable workflows for product
development, research, academic writing, visual communication, and project
operations. Each skill is an installable directory with focused instructions,
optional helpers, declared requirements, and traceable provenance.

This is an independent, community-maintained project. It is not an official
OpenAI project and is not affiliated with or endorsed by OpenAI. The repository
itself is the distribution: there is no separate website, GitHub Pages site, or
plugin marketplace.

## Install one skill

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

## Install several skills

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

## Browse by goal

The table below is generated from [`skills.json`](skills.json). Requirements
listed as “None” mean that the skill itself has no extra runtime dependency;
the work it performs may still require task-specific tools or access.

<!-- skills-table:start -->

| Goal | Skill | Extra requirements | Source |
|---|---|---|---|
| Research Ideation & Experiment Planning | [`experiment-planner`](skills/experiment-planner) | None | `adapter` |
| Evidence & Search | [`research-evidence`](skills/research-evidence) | Network access for literature lookup<br>Optional paper-search MCP or RefChecker backends | `original` |
| Evidence & Search | [`search-first`](skills/search-first) | Network or repository search access | `third-party-adapted` |
| UI/UX & Product Design | [`ui-ux-pro-max`](skills/ui-ux-pro-max) | Python 3 for the bundled design search scripts | `third-party-adapted` |
| App Development & Release | [`app-feature-craft`](skills/app-feature-craft) | None | `original` |
| App Development & Release | [`app-bug-forensics`](skills/app-bug-forensics) | None | `original` |
| App Development & Release | [`app-release-readiness`](skills/app-release-readiness) | Target application's build and packaging toolchain<br>GitHub CLI for GitHub publishing tasks | `original` |
| Research Ideation & Experiment Planning | [`grill-me`](skills/grill-me) | None | `third-party-exact` |
| Paper Writing | [`paper-section-playbook`](skills/paper-section-playbook) | None | `original` |
| Paper Writing | [`paper-refinement-skills`](skills/paper-refinement-skills) | None | `original` |
| Review & Rebuttal | [`paper-review-panel`](skills/paper-review-panel) | None | `original` |
| Review & Rebuttal | [`rebuttal-response-skills`](skills/rebuttal-response-skills) | None | `third-party-adapted` |
| Figures & Tables | [`paper-framework-figure-studio-pro`](skills/paper-framework-figure-studio-pro) | None | `adapter` |
| Figures & Tables | [`paper-visual-craft`](skills/paper-visual-craft) | The plotting or LaTeX toolchain used by the source artifact<br>PDF rendering tools for visual verification | `original` |
| Paper Communication | [`paper-share-html`](skills/paper-share-html) | Browser automation for visual QA<br>PDF extraction or rendering tools when the source is a PDF | `original` |
| Operations & Release | [`github-project-release`](skills/github-project-release) | Git<br>GitHub CLI for remote repository operations | `original` |
| Operations & Release | [`codex-session-restore`](skills/codex-session-restore) | Python 3 for the bundled recovery script<br>Local access to the Codex Desktop data directory | `original` |

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

```text
$paper-review-panel Review this draft as a top-conference panel. Separate fatal evidence gaps from issues that can be fixed with writing.
```

All included skills also allow implicit invocation: Codex may select one when
its description closely matches the request. Explicit `$skill-name` invocation
is preferable when a particular workflow or a repeatable handoff matters.

Skills can be composed in sequence. A research idea might move through
`$grill-me`, `$experiment-planner`, and `$research-evidence`; a product release
might use `$app-feature-craft`, `$app-bug-forensics`, and
`$app-release-readiness`. See [workflow recipes](docs/USAGE.md) for complete
examples.

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
