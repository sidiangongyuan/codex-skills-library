# Table Design

## Table Role

- Main-paper tables should answer one claim quickly.
- Design the final table before launching its experiments. Freeze the row and
  column meanings, comparison axis, reference row, and claim that owns the table
  so result collection cannot silently redefine the paper story.
- Appendix tables can contain more rows, but still need short cells, grouped headers, and clear row ordering.
- Reliability/control tables should make conditions and controls visually scanable before showing interpretation.
- Tables are part of the paper narrative, not a dump of execution artifacts. Choose rows and groups around the experimental question the reader should understand.
- Comparison axis first. A table's first job is to make the comparison target
  and conclusion obvious, not to display every generated condition,
  implementation branch, or debugging history.
- For dataset or benchmark papers, tables should make the benchmark story visible: positioning, annotation/evidence scale, control conditions, and diagnostic breadth.
- Prune redundancy. Duplicate controls, equivalent inputs, aliases, empty
  conditions, and rows with no interpretive value should be deleted or merged.
  Keep fewer rows when that makes the scientific comparison clearer.
- When rows, columns, grouped headers, or table layout change, update the whole
  table context: caption, immediately preceding or following prose,
  cross-references, and later interpretive paragraphs. Stale text around a
  corrected table is a table bug, not just a prose issue.

## DriveBench-Inspired Structure

- Use compact headers, grouped columns, and strong horizontal rules.
- Put icons or compact symbols in headers only when they reduce repeated prose.
- Use self-made LaTeX icons such as `fontawesome5`, `pifont`, or project-local macros. Do not copy PNG icons from another paper.
- Use `\midrule\midrule` or clear group separators only when the table has real group transitions.
- Highlight the central method, reference row, or key control rows with light row colors. Do not color every other row by default.

## Cell Content

- Keep table cells short: `FDE/Cmd/Macro`, `Acc`, `Language/GPT`, `Ego + infra`, `No image`.
- Move definitions and caveats into the caption or surrounding prose.
- Avoid sentence-length interpretation cells unless the table is explicitly a diagnostic summary.
- Use `--` for unknown or intentionally omitted values; do not invent scale numbers for symmetry.
- Fit new result rows to the table's existing cell contract. If nearby rows use
  `value + delta`, reference cells, arrows, rank colors, or diagnostic colors,
  the new row must use the same contract or the table must be redesigned. Do not
  add plain metric values to a table whose cells encode comparison against a
  reference.
- If a planned experiment is accepted as part of the paper structure but the
  data are not ready, use a polished scaffold table with `--` metric cells. The
  caption should define the comparison and metrics without exposing internal
  status such as `TODO`, `TBD`, or `pending`; the prose must not claim results
  from those rows.
- Keep comparison axes intact. If a wide appendix table is designed for
  left-to-right comparison across task groups, models, or controls, prefer one
  coherent table when the user allows shrinking or explicitly permits
  `resizebox`. Splitting into panels is appropriate only when it improves the
  comparison rather than merely reducing width.

## Cell-Level Color

- Use semantic color, not raw sign: green means better, red means worse, amber means warning or secondary, and blue means reference.
- Interpret direction per metric. Lower-is-better metrics use green for decreases and red for increases; higher-is-better metrics use green for increases and red for decreases.
- In diagnostic tables, color by interpretation when raw magnitude is misleading. A high claim rate under no visual evidence can be red because it indicates visual-prior reliance.
- Make colored cells fill a consistent column width. Prefer fixed-width metric columns over coloring only the text box, so short values do not produce shorter color patches.
- Keep delta text visually secondary to the main value. Use a smaller font, lighter line height, or compact arrow annotation such as `value` plus `small delta`.
- Captions must define what color means in that table: metric movement, rank cue, reference row, warning state, or diagnostic failure.
- When a caption defines color semantics, color the color words themselves: green should appear green, red should appear red, amber should appear amber, and blue should appear blue.
- For rank-color tables, state that color is within-column only. Green means the best value in that metric column; amber means the closest secondary value when informative. Do not imply overall model superiority.

## Caption And Note Semantics

- State the reference row or reference column directly when using blue reference cells.
- For delta tables, say whether green and red encode metric movement relative to the reference row or a task-level diagnostic interpretation.
- For rank tables, say `green = best` and `amber = secondary` within each metric column; never let rank color imply overall superiority across unrelated metrics.
- For diagnostic tables, make failure semantics explicit. A numerically high value can be red when it indicates unsupported evidence use, visual-prior reliance, or hallucination.
- Keep caption color definitions short. A good caption defines the encoding once, then leaves interpretation to the row labels, deltas, and surrounding prose.
- Avoid captions that read like run notes. Replace "we implemented / ran / generated" with the paper-level role: comparison, control, diagnostic, or protocol note.
- Do not use captions to preserve engineering anxiety. Checkpoint status,
  runner names, local paths, failed attempts, and adapter details belong in
  setup notes or Appendix only when they change how the table should be read.
- Use two visual audit passes for dense colored tables: first verify color meaning against the metric direction, then verify layout, clipping, and caption readability in the rendered PDF.

## Numeric Consistency

- Define every non-standard metric by measured quantity, aggregation
  population, unit, direction, and precision. For deltas, name the reference row
  or condition and state the sign convention.
- Align rounding with the paper's existing precision.
- Keep deltas tied to a named baseline in the header or caption.
- When a new row compares against a different reference than earlier rows, state
  that reference in the caption or a compact table note and mirror it in the
  nearby prose. The reader should not have to infer whether a delta is relative
  to the row above, a blue reference row, a method baseline, or a main-paper
  reference.
- Check derived cells after inserting values: recompute deltas from the source
  artifact, apply metric direction correctly, and verify color semantics match
  the sign. Lower-is-better metrics invert the meaning of positive and negative
  deltas relative to accuracy-style metrics.
- Do not mix checkpoint policies, sample counts, or metric definitions in one table without a visible note.
- If a table combines deterministic metrics and judge scores, mark judge scores as secondary.

## LaTeX Practicalities

- Prefer `booktabs` rules and avoid vertical lines unless the venue or existing style requires them.
- Do not use `\resizebox{\linewidth}{!}{...}` or `\resizebox{\textwidth}{!}{...}` to make a table fill available width. This enlarges fitting tables and creates inconsistent font sizes.
- Resize only to shrink a naturally overwide table. Prefer a max-width wrapper such as `adjustbox` with `max width=\linewidth` or `max width=\textwidth`, because it preserves native size when the table fits and shrinks only when needed.
- Before shrinking, try reducing text, tightening `\tabcolsep`, using compact grouped headers, or fixed-width `p{}` columns. Split the table only when the resulting panels still preserve the intended reader scan path. If the user explicitly permits `resizebox` and horizontal scanability is the point, a single coherent shrunken table is preferred over automatic panel splitting.
- Use `\small` or `\scriptsize` sparingly. A readable table is better than a dense table with every metric.
- Prefer a compact table over a decorative or multi-panel figure when rows and
  columns already express the comparison. Complexity must earn space by making a
  relationship materially easier to understand.
- Compile and check for overfull boxes, clipped cells, broken references, and captions that push tables awkwardly across pages.
- Render dense colored table pages at least twice after final edits. Check that color blocks align by column, delta text is subordinate, color-word captions are readable, and no cell is ambiguous.
