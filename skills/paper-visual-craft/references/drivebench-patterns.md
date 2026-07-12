# DriveBench-Style Patterns

Use DriveBench as a design reference, not an asset source. Borrow layout logic, not files.

## What To Borrow

- Benchmark tables with compact capability columns and visually distinct marks.
- Grouped headers that let readers scan task families, metrics, or controls quickly.
- Icons used as semantic compression, paired with short abbreviations and a concise caption.
- Clean / corrupt / no-image control organization that exposes visual-prior reliance.
- Diagnostic tables that show metric disagreement instead of forcing one synthetic score.

## What Not To Borrow

- Do not copy DriveBench PNG icons, figures, or table images.
- Do not reproduce a full corruption taxonomy unless the paper's claim needs it.
- Do not add large benchmark-style tables to the main paper if the result is only an appendix diagnostic.
- Do not make a figure look DriveBench-like at the cost of hiding exact values, units, or sample counts.

## Applying The Pattern

- Start with the experimental question: capability comparison, input control, corruption diagnostic, QA evaluation, or metric disagreement.
- Put conditions as rows when comparing one model across controls.
- Put models as rows when comparing benchmark or model families.
- Use light highlights for the reference input, proposed dataset/model, and strongest control rows.
- Keep captions short but explicit about mark meanings, control definitions, and whether judge scores are secondary.
- Let the table carry the comparison and let the prose carry the story. DriveBench-style polish works because the reader can scan the conditions, controls, and metric families without reading implementation notes.
- For pending QA or control diagnostics, it is acceptable in an internal draft to reserve the DriveBench-style table structure with dash-valued metric cells, but do not write result language until the metrics are filled.

## Claim Safety

- Say "diagnostic" when the experiment is a stress test, control, or appendix probe.
- Avoid "full robustness" unless the corruption set, protocol, and baselines justify it.
- For QA, distinguish objective accuracy from free-form semantic judge scores.
- For CoT, do not treat fluent explanations as proof of grounded evidence unless the metric actually checks evidence source.
