# Notices and provenance

Codex Skills Library combines original skills, locally maintained adapters,
and attributed third-party skills. The repository-level MIT License covers
original material and project modifications. Third-party material remains
under its upstream license and copyright.

Each installable skill carries its applicable license text inside its own
directory so attribution is preserved when that skill is installed by itself.
The machine-readable counterpart to this document is `skills.json`.

## Provenance labels

| Label | Meaning |
|---|---|
| `original` | Created and maintained in this project. |
| `adapter` | Original local workflow informed by cited projects without vendoring their long-form content. |
| `third-party-adapted` | Upstream material modified for this library, with the source revision and license retained. |
| `third-party-exact` | Exact content from a pinned upstream revision. |

## Original skills

The following skills are maintained as original project work under the MIT
License, copyright 2026 sidiangongyuan:

- `app-bug-forensics`
- `app-feature-craft`
- `app-release-readiness`
- `codex-session-restore`
- `github-project-release`
- `paper-refinement-skills`
- `paper-review-panel`
- `paper-section-playbook`
- `paper-share-html`
- `paper-visual-craft`
- `research-evidence`

## Third-party and adapted skills

| Skill | Provenance | Pinned source | License and local treatment |
|---|---|---|---|
| `grill-me` | `third-party-exact` | [`mattpocock/skills@62f43a1`](https://github.com/mattpocock/skills/blob/62f43a18177be6ec82da242e59ffbc490a4c22ea/skills/productivity/grill-me/SKILL.md) | MIT, copyright 2026 Matt Pocock. The installable directory includes the upstream license. |
| `search-first` | `third-party-adapted` | [`affaan-m/ECC@99baa82`](https://github.com/affaan-m/ECC/blob/99baa8250096f2d295583572399a5c9aba2ce312/skills/search-first/SKILL.md) | MIT, copyright 2026 Affaan Mustafa. Adapted for Codex and for optional academic-evidence routing. |
| `ui-ux-pro-max` | `third-party-adapted` | [`nextlevelbuilder/ui-ux-pro-max-skill@232f201`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/232f201dfa3ec3d74af5dff80ec61eb8144c7507) | MIT, copyright 2024 Next Level Builder. Symlinked upstream resources are packaged as regular files and the instructions are adapted for Codex. |
| `rebuttal-response-skills` | `third-party-adapted` | [`wanshuiyin/Auto-claude-code-research-in-sleep@e513263`](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/e5132630e26e26e24d256a149b85f17b0cc6dcac/skills/skills-codex/rebuttal/SKILL.md) | MIT, copyright 2026 wanshuiyin. The local version is a smaller Codex-oriented adaptation. |

## Local adapters and referenced projects

`experiment-planner` is a locally maintained adapter informed by research
agent and short-loop experimentation projects. Its pinned reference map lives
in `skills/experiment-planner/references/source-map.md`; those projects are not
vendored or installed by this library.

`paper-framework-figure-studio-pro` is a lightweight local adapter informed by
[`c-narcissus/paper-framework-figure-studio-pro@426d74b`](https://github.com/c-narcissus/paper-framework-figure-studio-pro/tree/426d74b18852aaf8e4307997ff47b8c3b6089f14).
At that revision the upstream README declares MIT-0, but the repository does
not contain a standalone license file. This library does not vendor its zip
bundle, PDF/PNG examples, generated outputs, or large asset library.

## External tools

`research-evidence` may use
[`openags/paper-search-mcp`](https://github.com/openags/paper-search-mcp) and
[`markrussinovich/refchecker`](https://github.com/markrussinovich/refchecker)
when they are available. These tools are dependencies, not copied skill
content, and remain subject to their own terms.

## Safety

Skills are executable instructions and may include helper scripts. Review a
skill and its dependencies before using it in a sensitive workspace. The
library installer copies files only; it never runs installed skill scripts.
