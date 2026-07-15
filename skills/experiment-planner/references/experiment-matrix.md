# Experiment Matrix Reference

Use this reference when `$experiment-planner` needs to produce a plan, matrix,
or subagent task split. Keep output in chat unless the user asks for a saved
artifact.

## Matrix Fields

| Field | Required content |
|---|---|
| `research question` | The exact question the experiment answers. |
| `core hypothesis` | The smallest falsifiable claim. |
| `paper claim` | The reviewer-facing claim the completed experiment may support. |
| `storyline` | Why the question matters, what gap exists, and how the method could support a paper story. |
| `literature inspiration` | Known related directions, verified or pending `$research-evidence` checks, and novelty risk. |
| `baseline/control` | The minimal fair comparison or negative control needed to interpret results. |
| `table contract` | Final row/column structure for the main result, ablation, and only the necessary diagnostics; use `--` until values are accepted. |
| `metric definitions` | Plain definition, unit, direction, aggregation population, and delta reference for every reported metric. |
| `idea validation experiment` | The smallest pilot/smoke/sanity run that can support or falsify the core hypothesis. |
| `expected signal` | What pattern would count as success, including the metric, artifact, or qualitative cue. |
| `failure modes` | How the idea could fail, including dataset leakage, weak baseline, noisy metric, or implementation artifact. |
| `diagnostic checks` | Checks that separate mechanism from bugs, protocol mismatch, or confounds. |
| `follow-up experiments` | Main result, ablation, robustness, efficiency, qualitative, and failure-analysis runs after pilot success. |
| `subagent/task ownership` | Explorer/worker split, write scopes, and which tasks stay with the main session. |
| `compute/resource assumptions` | GPU count, expected runtime, data availability, seed policy, and storage constraints when known. |
| `seed policy` | Single-run or repeated-seed decision, with the cost and evidence-risk reason. |
| `success gate` | The explicit condition for moving from pilot to full experiment. |
| `claim gate` | The result threshold or comparison pattern required before using stronger paper wording. |
| `next action` | The next concrete step: ask user, search literature, inspect repo, write code, smoke test, launch run, or stop. |

## Run Order

1. Confirm the problem, motivation, and minimum claim.
2. Check literature or existing implementations when novelty or feasibility is
   uncertain.
3. Identify the baseline/control before designing a method-heavy experiment.
4. Freeze the final paper/table contract, metric definitions, and claim gate.
5. If experiment execution is requested, persist the contract in the in-scope
   LaTeX manuscript; otherwise update an existing experiment-planning document
   or create repository-root `experiment-plan.md`.
6. Define the pilot experiment and success gate.
7. Define smoke checks: command starts, config resolves, data loads, first
   batch/output looks plausible, and generated test artifacts can be removed.
8. Only after smoke passes, define the minimum sufficient full runs.
9. Inspect early full-run samples/logs/artifacts, then stop continuous
   monitoring unless the user asks for ongoing monitoring.
10. After results finish, interpret against the frozen claim before planning
   paper writing or additional ablations.

## Result Contract Rules

- Make each main table answer one reviewer question.
- Prefer standard metrics. Introduce a new metric only when existing metrics
  cannot test the claim, and define it before any result is interpreted.
- Keep the main comparison first; make ablations and diagnostics secondary.
- Use `--`, never `TBD` or `pending`, for unavailable table values.
- Do not write result claims from placeholders.
- Record an existing seed, but do not require repeated expensive training by
  default. Repeat seeds only when variance could change the claim, the margin is
  small, the runs are inexpensive, or the venue requires them.

## Subagent Task Patterns

Use `explorer` for:

- Repo/config/data-path inspection.
- Existing baseline/protocol discovery.
- Dependency, command, or logging investigation.
- Read-only comparison of candidate implementation paths.

Use `worker` for:

- A bounded code or script change with explicit file/module ownership.
- A smoke-test command or runner repair after the main session approves the
  write scope.
- Independent implementation slices that do not overlap with other workers.

Keep in the main session:

- Research claim decisions.
- Whether a pilot result is accepted.
- Whether to launch long experiments.
- Final result interpretation and handoff to writing skills.

## Default Matrix Skeleton

```text
research question:
core hypothesis:
paper claim:
storyline:
literature inspiration:
baseline/control:
table contract:
metric definitions:
idea validation experiment:
expected signal:
failure modes:
diagnostic checks:
follow-up experiments:
subagent/task ownership:
compute/resource assumptions:
seed policy:
success gate:
claim gate:
next action:
```
