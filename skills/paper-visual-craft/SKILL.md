---
name: paper-visual-craft
description: Use when designing, redrawing, or validating research-paper figures and tables, including Matplotlib plots, LaTeX tables, benchmarks, captions, legends, annotations, color, and typography. Preserves exact evidence and checks rendered PDFs for clipping, overlap, and readability.
license: MIT
---

# Paper Visual Craft

## Routing Boundary

- Use `$paper-framework-figure-studio-pro` first for source-grounded framework
  figure, method overview, architecture diagram, pipeline/process figure,
  system/data-flow figure, mechanism schematic, or agent workflow planning.
- Return to `$paper-visual-craft` for final figure/table polish, Matplotlib or
  LaTeX edits, captions, color/typography cleanup, and rendered PDF/PNG
  validation.

## Core Workflow

1. Inspect before editing.
   - Read the paper context around the target figure or table.
   - Locate the source data, generation script, LaTeX include block, captions, and any reference visual the user named.
   - If data provenance is unclear, stop and identify the exact missing source instead of redrawing from copied numbers.

2. Classify the visual.
   - Decide whether it is a main-result figure, appendix diagnostic, dataset/statistics figure, ablation table, reliability/control table, or qualitative panel.
   - Keep main-paper visuals compact and claim-focused. Use appendix visuals for diagnostics, extended controls, and richer tables.
   - For dataset or benchmark papers, ask what story the visual supports: benchmark positioning, annotation effort, evidence source, main control, or diagnostic richness.
   - Put the comparison axis first. The reader should immediately know what is
     being compared and what conclusion to read; the visual should not preserve
     implementation history, generated-condition inventories, or debug process
     unless those are the claim.

3. Preserve measurement integrity.
   - Preserve exact values, units, sample counts, conditions, and axis semantics.
   - Do not mix raw values, percentages, percentage-point deltas, and relative deltas inside one visual unless the caption makes the units explicit.
   - When adding a numeric result row, fit the row to the table's existing
     measurement schema before inserting it. If the table uses reference cells,
     deltas, arrows, or semantic colors, compute the appropriate comparison
     against the named reference with the same precision and directionality.
     Do not paste raw values into a delta-coded table.
   - Put interpretation in captions or prose, not inside plot areas, unless a small label clarifies a data point without occluding information.
   - For diagnostic figures, show metric behavior without implying a causal
     mechanism unless the experimental design directly tests causality. The
     caption should say what the diagnostic supports and what it does not prove.
   - When table rows, columns, panels, or layout change, update the caption,
     nearby prose, cross-references, and later interpretive paragraphs in the
     same pass. A table edit is incomplete if the surrounding text still
     describes the old rows or comparison target, or if a new row omits the
     table's required reference/delta semantics.

4. Design with restrained hierarchy.
   - Prefer vector outputs for papers and PNG previews for inspection.
   - Use consistent legends, typography, line weights, tick formatting, row highlights, and caption structure.
   - Reserve whitespace for endpoint labels and callouts; avoid labels floating over trends, bars, or dense table cells.
   - For table heatmaps, use semantic color rather than raw sign, fixed-width colored cells, and delta text that is visually smaller than the main value.
   - When a caption defines color semantics, color the color words themselves, such as green, red, amber, or blue.
   - Do not use unconditional table resizing to make a table fill the page width. Resize only to shrink a naturally overwide table; never enlarge a table that already fits.
   - Preserve the reader's intended comparison axis. For appendix diagnostics,
     do not split one wide table into panels merely because it is wide; if the
     user permits `resizebox` and horizontal scanning is the point, keep one
     coherent table and shrink it only as needed.
   - For planned experiments, create a clean paper-style table scaffold with dashes for missing metrics instead of leaving prose TODOs; do not interpret placeholder values.
   - Prune redundancy. Delete or merge duplicate controls, equivalent inputs,
     uninformative panels, and plain scatter plots with no clear message. Fewer
     clear visuals are better than a "fancy" but unfocused figure set.
   - Use icons only when they reduce text and are reproducible from LaTeX or an existing project icon system. Do not copy external paper image assets.

5. Validate rendered output.
   - Compile the paper or render the affected standalone output.
   - Inspect the rendered PDF/PNG visually for clipping, overlap, crowded ticks, unreadable labels, broken references, excessive table scaling, and color imbalance.
   - For dense colored tables, render-check the affected pages at least twice after the final edit.
   - Report exact files changed, commands run, and any remaining visual risk.

## Table Polish Reminders

- Use semantic color, not raw sign: color should answer whether the value is better, worse, a reference, or a diagnostic warning.
- Make tables serve the paper story. A table should let the reader scan the experimental question and evidence, not reconstruct the implementation chronology.
- Make the comparison axis explicit before optimizing style. If the reader
  cannot tell whether rows compare models, controls, tasks, or implementation
  variants, redesign the table before polishing colors.
- Keep colored metric cells visually uniform with fixed-width columns; avoid short values producing tiny color patches.
- Make delta text secondary to the main value through smaller type and compact arrows.
- Before finalizing a new numeric row, audit every metric cell against the
  table contract: reference row, delta sign, lower-is-better or higher-is-better
  direction, color meaning, precision, and surrounding prose. A correct number
  in the wrong cell format is still a table error.
- When captions define color semantics, color the color words themselves, such as green, red, amber, and blue.
- Do not wrap fitting tables in `\resizebox{\linewidth}{!}` or `\resizebox{\textwidth}{!}` just to fill space. Prefer native size; if width protection is needed, use a max-width wrapper that can shrink but cannot enlarge.
- Treat splitting a table into panels as a design decision, not an automatic
  fallback. Split only when separate panels improve the reader's comparison;
  otherwise keep a unified wide table when it preserves scanability. If the
  user explicitly allows `resizebox` and horizontal scanning is the core value,
  prefer one coherent shrunken table over two panels.
- Always compile and render-check dense table pages after LaTeX edits, especially when adding cell-level color or rank cues.
- When a result is not ready, reserve the row/column structure with dashes only if the planned experiment is already part of the paper story and the caption clearly marks the blank metrics.

## Reference Routing

- Read `references/plot-design.md` for Matplotlib figures, line plots, bars, subfigure panels, palettes, legends, annotations, and vector export.
- Read `references/table-design.md` for LaTeX tables, benchmark comparisons, grouped headers, row coloring, icons, compact captions, and table density.
- Read `references/drivebench-patterns.md` when the user asks to borrow DriveBench-style design or when a benchmark table/control diagnostic needs that visual language.
- Read `references/validation-checklist.md` before finalizing any figure or table that will appear in a compiled paper PDF.

## Default Decisions

- Use a portable style; do not hardcode repository paths, dataset names, or paper-specific macros unless the current project already defines them.
- Prefer editing the existing figure/table generator over hand-editing generated outputs.
- Prefer true LaTeX subfigures or minipages with visible panel captions over a single combined image when panels need independent captions.
- Prefer compact table rows with short cells over long explanatory text in the table body.
- Treat judge scores, robustness diagnostics, and qualitative audits as secondary unless the paper explicitly makes them primary evidence.
