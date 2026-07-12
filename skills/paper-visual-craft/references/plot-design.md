# Plot Design

## Data Integrity

- Read the source data directly from JSON, CSV, logs, or tables before plotting.
- Print or assert the key values used in the plot when the task involves paper numbers.
- Keep numeric x-values numeric. Do not convert continuous or ordinal numeric settings into equally spaced categories unless that is the intended comparison.
- Label axes with units. If one panel uses meters and another uses percent, make that visible in the y-axis labels and avoid mixed delta callouts.

## Figure Structure

- Use one panel per question. Split panels into separate output files when the paper benefits from LaTeX subfigure captions.
- Comparison axis first. Before choosing a layout, state what the reader should
  compare: models, controls, tasks, classes, metrics, or failure modes. Remove
  panels that do not support that comparison.
- Remove plot-internal titles when LaTeX subfigure captions carry the panel names.
- Keep plot-internal text limited to direct data labels, short endpoint labels, or compact annotations in reserved whitespace.
- For appendix diagnostics, make the figure clean and interpretable rather than visually dramatic.
- Diagnostic figures can explain metric behavior, distribution shift, or
  decoupling, but their captions must not imply a causal mechanism unless the
  experiment directly tests causality.
- Prune redundant views. Duplicate controls, equivalent inputs, uninformative
  summary panels, and plain scatter plots with no clear message should be merged
  or removed rather than dressed up.

## Matplotlib Style

- Prefer `pdf.fonttype = 42` and `ps.fonttype = 42` for editable vector text.
- Save both `.pdf` and `.png` previews when the figure is paper-facing.
- Use a white background, light gridlines, restrained spines, and clear contrast.
- Use color to distinguish semantic roles, not to decorate. Avoid palettes dominated by one hue unless that is required by the paper style.
- Use consistent legend placement across comparable panels. A compact inside legend is acceptable only when it does not overlap data; otherwise place it just above the axes.

## Labels And Annotations

- Place endpoint labels outside or beside the data trend when there is reserved whitespace.
- Label raw values in the same unit as the axis unless there is a strong reason to show deltas.
- If showing deltas, keep the delta unit consistent across panels: all raw, all relative percent, or all percentage points.
- Use compact tick labels, but do not sacrifice clarity. Examples: `0`, `.1`, `.2`, `.5`, `1.0` can work for dense noise-level plots.

## Visual Checks

- Inspect PNG previews for label overlap, clipped legends, crowded ticks, and excessive whitespace.
- Inspect the compiled PDF page, not only the standalone figure.
- If a figure looks acceptable alone but cramped in the paper, adjust the LaTeX layout or split panels rather than shrinking text below readability.
