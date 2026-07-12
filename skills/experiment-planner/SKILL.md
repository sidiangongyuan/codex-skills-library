---
name: experiment-planner
description: Use when exploring a deep-learning or computer-science research idea before implementation or paper writing. Converts claims into pilot-first experiment matrices covering ablations, diagnostics, robustness, failure analysis, resource coordination, and paper-story viability.
license: MIT
---

# Experiment Planner

## Overview

Use this skill before paper writing when the user needs to turn a research idea
into a testable story and experiment plan. It is an adapter over existing
research-agent ideas, not a replacement for the user's writing, review,
rebuttal, figure, evidence, or GitHub release skills.

## Core Boundaries

- Default domain: general deep learning and computer science research. Adapt to
  collaborative perception, 3D perception, or autonomous driving only when the
  task context calls for it.
- Do not write Markdown, JSON, reports, logs, or experiment documents unless the
  user explicitly asks for saved artifacts.
- Do not launch long experiments, deploy GPU jobs, modify code, or retry failed
  runs unless the user explicitly asks for execution.
- Do not replace `paper-section-playbook`, `paper-refinement-skills`,
  `paper-review-panel`, `rebuttal-response-skills`, `paper-visual-craft`, or
  `github-project-release`; hand off to them only after the research plan or
  results are ready.
- Treat external projects as references, not installed dependencies. Read
  `references/source-map.md` before discussing provenance or upgrading this
  skill from upstream sources.

## Default Workflow

1. **Grill consensus**: use `$grill-me` style interaction to clarify problem,
   motivation, proposed claim, baseline/control, compute budget, success
   criteria, and unacceptable shortcuts. Ask one high-impact question at a time
   when the answer changes the experiment plan.
2. **Literature inspiration**: after a preliminary consensus, use
   `$research-evidence` for related papers, novelty risk, prior experiment
   patterns, and unsupported claims. Use `$search-first` when the task may need
   existing code, datasets, tools, or implementations.
3. **Story viability check**: decide whether the idea can support a clean paper
   story: important problem, credible gap, specific method difference, feasible
   validation, and claims that will not outrun the evidence.
4. **Claim freeze**: freeze the smallest verifiable claim before planning runs.
   Avoid changing the story repeatedly while experiments are running.
5. **Idea validation first**: design the smallest pilot/smoke/sanity experiment
   that can falsify or support the core hypothesis. If multiple GPUs are idle,
   parallelize only independent exploration runs with clear ownership.
6. **Matrix expansion**: only after the pilot passes, expand to main result,
   ablation, diagnostic, robustness, efficiency, qualitative, and failure
   analysis runs.
7. **Subagent coordination**: keep the main session responsible for planning,
   task decomposition, and final result acceptance. Use `explorer` for read-only
   repo/config/protocol investigation. Use `worker` for implementation with
   explicit file or module ownership. Do not manually override subagent model or
   reasoning settings unless the user explicitly requests it.
8. **Run discipline**: test that the command starts and produces plausible small
   outputs; remove test data after smoke checks; launch the full run only after
   sanity passes; inspect the first few samples/logs/artifacts; stop continuous
   monitoring once the run is confirmed healthy unless the user asks otherwise.

## Output Contract

Default to a concise in-chat experiment matrix. Before producing a matrix, read
`references/experiment-matrix.md`.

The matrix must include:

- `research question`
- `core hypothesis`
- `storyline`
- `literature inspiration`
- `baseline/control`
- `idea validation experiment`
- `expected signal`
- `failure modes`
- `diagnostic checks`
- `follow-up experiments`
- `subagent/task ownership`
- `compute/resource assumptions`
- `success gate`
- `next action`

Use `unknown` or `needs user input` for unresolved fields instead of inventing
project facts. Keep recommendations executable, but do not perform execution
inside this skill unless the user asks for implementation or running commands.

## Handoff Rules

- Use `$research-evidence` before making novelty, citation, or literature
  coverage claims.
- Use `$search-first` before proposing new implementation utilities, pipelines,
  tool integrations, or dataset-processing code.
- Use writing skills only after the experiment story is stable enough to draft
  a paper section, rebuttal, review, table, or figure.
- For code work, assign `worker` tasks with disjoint write scopes and remind the
  worker not to revert others' changes.
- For investigation, assign `explorer` tasks that are specific, read-only, and
  non-overlapping with the main session's current work.

## Failure Modes To Catch

- The idea is interesting but not falsifiable with available data or compute.
- The proposed contribution is only a presentation change, not a testable method
  or analysis difference.
- The baseline/control is missing, unfair, or weaker than the claim requires.
- The pilot experiment cannot distinguish mechanism from implementation noise.
- The plan jumps to full benchmark runs before smoke and sanity checks pass.
- The story changes after seeing results without recording a clear reason.
- Subagents receive vague tasks, overlapping write scopes, or authority to run
  long jobs without main-session acceptance.
