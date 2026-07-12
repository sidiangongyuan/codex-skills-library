# Workflow recipes

This guide shows how to invoke and compose the installed skills. Examples use
explicit `$skill-name` calls so that the requested workflow is clear and
repeatable. Codex may also select any included skill implicitly when its
description closely matches the task.

For installation and dependency details, see [Installation](INSTALL.md) and
the generated [Skill catalog](SKILL_CATALOG.md).

## Basic invocation

Name one skill and give it the artifact, goal, constraints, and expected
deliverable:

```text
$experiment-planner Turn the attached research idea into a pilot-first experiment matrix. The pilot must fit on one 24 GB GPU and end with a measurable stop/go decision.
```

Reference files or URLs directly when the task depends on them:

```text
$paper-review-panel Review paper.pdf as a CVPR-style panel. Ground every finding in the submitted text, figures, or tables and report missing evidence separately.
```

When multiple skills are useful, run them in a deliberate sequence. Let each
step produce an artifact or decision that the next step can consume:

```text
$grill-me Stress-test this feature proposal until its success criteria and failure policy are decision-complete.
```

```text
$app-feature-craft Implement the agreed proposal and verify the user-visible workflow, including loading, empty, error, cancellation, and recovery states.
```

## Explore a research idea

Use this sequence when the idea sounds promising but the claim, prior work,
and smallest useful experiment are unsettled.

Start by resolving product or research intent:

```text
$grill-me Interview me about this idea one decision branch at a time. Lock the problem, audience, claim, constraints, and success gate without drifting into implementation.
```

Check whether an existing method, library, benchmark, or workflow already
solves the problem:

```text
$search-first Search for existing implementations and established approaches before proposing custom code. Compare fit, maintenance, license, and integration cost.
```

For academic claims, verify the literature rather than relying on remembered
citations:

```text
$research-evidence Find the closest peer-reviewed work, verify the bibliographic metadata, and classify the proposed claim as established, weakly supported, contradicted, or still open.
```

Turn the remaining opportunity into experiments:

```text
$experiment-planner Build a claim-driven experiment matrix with a cheap pilot, strong baselines, controls, ablations, diagnostics, expected signals, resource estimates, and explicit stop/go gates.
```

The useful handoff is a bounded claim, an evidence map, and a prioritized
experiment matrix rather than a long list of speculative ideas.

## Build a product feature

Use `$app-feature-craft` when the request spans user experience, application
state, APIs or persistence, tests, and verification:

```text
$app-feature-craft Implement this user-visible feature end to end. Follow the existing architecture and design system, cover all expected states, preserve recoverability, add focused tests, and verify the real workflow.
```

Use `$ui-ux-pro-max` for a dedicated interaction and visual-quality pass:

```text
$ui-ux-pro-max Review this operational dashboard for information hierarchy, density, accessibility, responsive behavior, typography, interaction states, and consistency with the existing product.
```

These skills can be used before implementation to define behavior or after
implementation to audit the result. A UI review should produce actionable
changes tied to the actual interface, not a generic style checklist.

## Diagnose an application bug

Use `$app-bug-forensics` when a screenshot, intermittent error, stale request,
provider failure, background task, storage issue, or desktop lifecycle problem
needs root-cause analysis:

```text
$app-bug-forensics Diagnose this intermittent timeout from the screenshot, logs, and reproduction notes. Trace the UI state, request lifecycle, provider response, persistence, and retry path; fix the root cause and add focused regression coverage.
```

A good result distinguishes among:

- a locally reproduced failure;
- a diagnosis supported by code, logs, and tests; and
- a hypothesis that still requires a minimal real-provider or device probe.

Do not report success merely because an error was hidden or a fallback path
returned plausible-looking output.

## Prepare an application release

Use `$app-release-readiness` after the implementation and regression work are
complete:

```text
$app-release-readiness Prepare this update for release. Audit the worktree, run the relevant tests and builds, package the installer, compute hashes, push the intended source commit, upload release assets, and download them back for hash verification.
```

The release report should identify the source commit, branch, tests, artifact
paths, hashes, release URL, upload/download verification, and any remaining
manual checks. Deleting old releases, publishing broadly, or changing repository
visibility still requires explicit authorization.

## Draft and refine a paper

Ground claims before shaping sections:

```text
$research-evidence Verify the papers and claims needed for this Introduction and Related Work. Separate confirmed evidence, uncertain candidates, and unsupported statements.
```

Plan the argument at section and paragraph level:

```text
$paper-section-playbook Design the Introduction and Related Work structure for this computer-vision paper. Assign one rhetorical job to each paragraph and preserve the verified evidence boundaries.
```

Refine prose only after the structure and claims are stable:

```text
$paper-refinement-skills Tighten these paragraphs for clarity, logic, transitions, and venue-appropriate style without strengthening claims, inventing citations, or changing notation.
```

This order prevents polished wording from hiding an unsupported argument.

## Review a paper before submission

Use `$paper-review-panel` for independent reviewer-style scrutiny:

```text
$paper-review-panel Run a top-conference-style panel review of this draft. Assess novelty, technical soundness, evidence, clarity, reproducibility, and likely score risk; prioritize findings that could change the decision.
```

Plan a source-grounded method overview before drawing it:

```text
$paper-framework-figure-studio-pro Read the paper sources and plan a method overview figure. Identify the visual story, modules, data flow, training/inference distinction, labels, and unresolved assumptions; do not generate an image yet.
```

Use `$paper-visual-craft` for final figures, plots, and tables:

```text
$paper-visual-craft Redesign and validate these figures and tables for hierarchy, typography, color accessibility, caption alignment, evidence clarity, and rendered PDF legibility.
```

Finish with `$paper-refinement-skills` only for the text that changed during
the evidence and visual review.

## Prepare a rebuttal

Map every concern to available evidence first:

```text
$research-evidence Build an evidence map for each reviewer concern using the submitted paper, existing results, and verified literature. Mark missing support and claims that require author confirmation.
```

Draft concise, reviewer-specific responses:

```text
$rebuttal-response-skills Draft the author response under the venue limit. Address every concern, lead with direct answers, cite only verified evidence, avoid unsupported promises, and distinguish completed work from proposed changes.
```

Stress-test the result:

```text
$paper-review-panel Audit this rebuttal for missed concerns, unsupported claims, evasive tone, contradictions, and evidence gaps. Do not rewrite it until the coverage audit is complete.
```

The final response should remain faithful to work that actually exists. New
experiments or paper changes must not be presented as complete until verified.

## Share a paper with an audience

Use `$paper-share-html` to turn a paper into a browser-based presentation for a
lab meeting, journal club, or cross-disciplinary report:

```text
$paper-share-html Create a source-grounded 15-minute HTML presentation from this paper. Preserve complete quotations and citations, use legible figure and table assets, write for the stated audience, and verify desktop and mobile layouts in a real browser.
```

Use `$research-evidence` first if the presentation depends on uncertain
external claims. Use `$paper-visual-craft` when a figure or table needs a
substantial redesign instead of faithful extraction.

## Publish a clean GitHub project

Use `$github-project-release` when a local project needs a publication audit,
clean repository boundary, and intentional GitHub release:

```text
$github-project-release Prepare this project as a clean private GitHub repository. Exclude datasets, checkpoints, logs, generated artifacts, credentials, and unpublished paper material; audit the final file set before any push.
```

Repository creation, visibility, pushes, releases, and deletion are external
state changes. State the intended visibility and authorization explicitly. The
handoff should report the repository URL, visibility, branch, commit SHA, audit
result, and anything intentionally excluded.

## Restore Codex Desktop sessions

Use `$codex-session-restore` when non-archived tasks disappear from the sidebar,
show provider-related errors, or cannot continue after a provider switch:

```text
$codex-session-restore Diagnose missing active Codex Desktop sessions after this provider change. Preserve archived sessions, authentication, and provider configuration; back up affected local state before any repair.
```

The skill is intentionally conservative. It should identify the active provider
and local state, explain the mismatch, preserve unrelated sessions, and report
the exact backup and repair performed.

## Composition guidelines

- Use one skill as the owner of each step; invoke the next skill on a concrete
  artifact or decision rather than combining many names into one vague prompt.
- Put evidence gathering before claim writing, review before polish, diagnosis
  before patching, and verification before publishing.
- State resource limits, venue rules, target platform, repository visibility,
  and destructive-action permissions when they affect the workflow.
- Treat skill output as work to inspect, not as an authority override. Repository
  instructions, user intent, licenses, and tool safety boundaries still apply.
- Require confirmation for destructive, publishing, credential, or externally
  visible actions even when a skill can technically perform them.
