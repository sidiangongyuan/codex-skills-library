# Validation Checklist

## Before Plotting Or Tabulating

- Confirm the source data path and the exact rows/conditions included.
- Confirm sample counts, split names, checkpoint/run identifiers, and metric definitions.
- Check whether generated outputs are tracked source artifacts or disposable build products.
- If the visual replaces an old artifact, remove stale references and stale generated files when appropriate.

## Figure Validation

- Verify `.pdf` and `.png` outputs exist and are nonempty.
- Use `pdfinfo` to confirm the page count for standalone PDFs.
- Render the figure or paper page with `pdftoppm` when layout matters.
- Inspect for clipped labels, overlapping legends, unreadable ticks, and labels placed over data.

## Table Validation

- Compile the paper after LaTeX table edits.
- Search the log for `Overfull`, undefined references, missing citations, and package/icon errors.
- Render the affected page and inspect column widths, row highlights, caption spacing, and font size.
- Check that every number in the table can be traced to a source artifact.

## Common Commands

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error path/to/paper.tex
pdfinfo path/to/output.pdf
pdftoppm -f PAGE -l PAGE -png -r 180 path/to/output.pdf /tmp/rendered_page
rg -n "Overfull|Undefined|LaTeX Warning: Reference|Fatal|Error" path/to/paper.log
```

## Final Report

- State what changed, where the source values came from, and what validation ran.
- Mention if PDF rendering was not possible.
- Mention residual risks such as dense rows, unresolved citations, or secondary metrics that should not be overclaimed.
