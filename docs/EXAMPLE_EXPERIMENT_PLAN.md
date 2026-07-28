# Worked example: a pilot-first experiment plan

> Planning example only. No experiment was run and no result is claimed.

This example shows the kind of inspectable artifact that
`$experiment-planner` should leave behind. The starting request is intentionally
short:

```text
$experiment-planner Can uncertainty-gated temporal fusion improve rainy-scene
3D detection on one 24 GB GPU? Design the smallest useful pilot.
```

## Frozen claim

| Field | Plan |
|---|---|
| Research question | Does a lightweight temporal gate help a working single-frame 3D detector under rain without causing an unacceptable clear-weather regression? |
| Core hypothesis | When the previous frame is useful, a learned uncertainty gate will improve the rainy subset more than a parameter-matched control that cannot use valid temporal information. |
| Paper claim | Use only after the claim gate passes: uncertainty-gated temporal fusion improves adverse-weather robustness at bounded compute cost. |
| Literature inspiration | Needs a `$research-evidence` check before making novelty or coverage claims. |

## Assumptions to confirm

- A single-frame detector, training command, and evaluation protocol already
  work.
- The dataset can produce non-overlapping rainy and clear validation subsets;
  the exact labeling rule still needs user input.
- The pilot may use one 24 GB GPU and a reduced training schedule.
- The existing benchmark metric remains the primary quality metric. A new
  metric will not be invented for this pilot.

## Pilot matrix

| Run | Change | Why it exists | Expected signal |
|---|---|---|---|
| B0 | Existing single-frame baseline | Establish the current rainy/clear split and runtime | Stable reference with reproducible evaluation |
| C1 | Lightweight temporal fusion with uncertainty gate | Test the core mechanism | Rainy-subset gain with bounded clear-subset and latency cost |
| N1 | Same fusion path with the previous frame shuffled | Separate temporal information from extra parameters | Smaller gain than C1 if valid temporal context matters |
| A1 | C1 with a fixed gate | Test whether learned gating is necessary | C1 should outperform or be more stable than A1 |

Unavailable result cells stay `--` until runs are accepted.

## Metric contract

| Metric | Definition | Direction | Comparison |
|---|---|---|---|
| Primary detection score | Existing benchmark metric under the repository's current evaluation protocol | Higher is better | C1 vs B0 on rainy and clear subsets |
| Rainy-subset delta | C1 minus B0 on the frozen rainy subset | Higher is better | Must also exceed N1 |
| Clear-subset regression | C1 minus B0 on the frozen clear subset | Closer to zero is better | Must remain inside the user-approved tolerance |
| Inference latency | Median per-sample latency under one frozen hardware and batch-size protocol | Lower is better | Report C1 relative to B0 |

## Gates

**Success gate:** move beyond the pilot only if C1 beats B0 on the rainy subset,
beats the shuffled-frame control N1, and stays inside the agreed clear-weather
and latency tolerances. Numeric tolerances need user input before any run.

**Claim gate:** do not use the paper claim unless the effect survives the full
evaluation protocol and the diagnostic controls. If C1 and N1 are similar, the
temporal explanation is unsupported even when both beat B0.

## Failure checks

- Verify rainy/clear labels before training to catch leakage or overlap.
- Visualize the gate distribution; a constant gate suggests the mechanism is
  not being used.
- Inspect synchronized frames and transforms to separate alignment bugs from a
  weak idea.
- Re-run evaluation on the same checkpoint-selection policy for every run.
- Stop if the reduced pilot schedule changes the baseline ranking or makes the
  comparison unstable.

## Next action

Confirm the subset rule, tolerance values, baseline command, metric name, and
expected runtime. Then run only B0 and a one-batch smoke test for C1 before
scheduling the four pilot runs.
