# Experiment Matrix Reference

Use this reference when `$experiment-planner` needs to produce a plan, matrix,
or subagent task split. Keep output in chat unless the user asks for a saved
artifact.

## Matrix Fields

| Field | Required content |
|---|---|
| `research question` | The exact question the experiment answers. |
| `core hypothesis` | The smallest falsifiable claim. |
| `storyline` | Why the question matters, what gap exists, and how the method could support a paper story. |
| `literature inspiration` | Known related directions, verified or pending `$research-evidence` checks, and novelty risk. |
| `baseline/control` | The minimal fair comparison or negative control needed to interpret results. |
| `idea validation experiment` | The smallest pilot/smoke/sanity run that can support or falsify the core hypothesis. |
| `expected signal` | What pattern would count as success, including the metric, artifact, or qualitative cue. |
| `failure modes` | How the idea could fail, including dataset leakage, weak baseline, noisy metric, or implementation artifact. |
| `diagnostic checks` | Checks that separate mechanism from bugs, protocol mismatch, or confounds. |
| `follow-up experiments` | Main result, ablation, robustness, efficiency, qualitative, and failure-analysis runs after pilot success. |
| `subagent/task ownership` | Explorer/worker split, write scopes, and which tasks stay with the main session. |
| `compute/resource assumptions` | GPU count, expected runtime, data availability, seed policy, and storage constraints when known. |
| `success gate` | The explicit condition for moving from pilot to full experiment. |
| `next action` | The next concrete step: ask user, search literature, inspect repo, write code, smoke test, launch run, or stop. |

## Run Order

1. Confirm the problem, motivation, and minimum claim.
2. Check literature or existing implementations when novelty or feasibility is
   uncertain.
3. Identify the baseline/control before designing a method-heavy experiment.
4. Define the pilot experiment and success gate.
5. Define smoke checks: command starts, config resolves, data loads, first
   batch/output looks plausible, and generated test artifacts can be removed.
6. Only after smoke passes, define full runs.
7. Inspect early full-run samples/logs/artifacts, then stop continuous
   monitoring unless the user asks for ongoing monitoring.
8. After results finish, interpret against the frozen claim before planning
   paper writing or additional ablations.

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
storyline:
literature inspiration:
baseline/control:
idea validation experiment:
expected signal:
failure modes:
diagnostic checks:
follow-up experiments:
subagent/task ownership:
compute/resource assumptions:
success gate:
next action:
```
