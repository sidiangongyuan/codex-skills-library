# Feishu Publishing

Treat Feishu as a delivery surface, not the source of truth for the research
process. Finish and validate the report before creating a cloud document.

## Discover Capabilities

Use an authorized Feishu-compatible connector when one is available. Detect
capabilities instead of assuming a particular local installation:

1. Rich document creation with headings, links, tables, quotes, callouts, and
   semantic text styles.
2. Local DOCX or Markdown import when figures must be preserved.
3. Document readback for verification.
4. Optional whiteboard or mind-map creation.

If no connector exists or authorization is missing, keep the complete Markdown
report and disclose that publishing was skipped. Do not install a connector or
request broader permissions unless the user asks.

## Choose The Route

- Use rich-document creation for text, links, tables, and quote-heavy reports.
- Use DOCX import when approved figures or complex tables must survive.
- Use Markdown import only when the connector preserves its structure.
- Create a mind map only when it clarifies relationships across at least three
  papers and the connector can verify the result.

Create one new document per run. Update an existing document only when the user
identifies it and explicitly requests the update.

## Document Design

Use restrained semantic styling:

- title and subtitle: dark neutral text with one accent color;
- scope and date window: compact callout;
- evidence: cool accent or quote block;
- limitation and uncertainty: amber or red used sparingly;
- action or recommended reading: green used sparingly;
- body text: neutral, readable, and left aligned.

Avoid decorative color on every paragraph. Keep heading hierarchy consistent.
Use tables for comparison, not for long prose. Place original-language
fragments in quote blocks and Chinese explanations directly below them.

For each paper, keep canonical paper and code links near its verified metadata.
Use source figure captions and clear attribution when embedding is allowed.
Never imply that a generated diagram is a source figure.

## Publish Safely

- Request only the permissions needed to create and read back the new document.
- Do not expose general delete, drive-management, or broad folder tools.
- Do not overwrite or delete prior documents.
- Do not persist credentials in the report or skill directory.
- Keep temporary export files inside a declared working directory.

When the user requests Feishu-only retention, delete only temporary files
created by the current run after successful readback. Never delete downloaded
source papers, user files, or unrelated outputs without an exact inventory and
explicit authorization.

## Readback Verification

Read the published document back and verify:

- title, date interval, candidate count, and selected count;
- all selected paper headings;
- canonical links and code links;
- comparison matrix and cross-paper synthesis;
- original-language fragments with locators;
- limitation and coverage sections;
- expected figures or explicit figure-link fallbacks;
- no placeholders, truncation, duplicated blocks, or empty sections.

When the connector supports block inspection, also verify heading levels,
tables, quote blocks, callouts, links, and media counts. Report any downgrade
from the intended presentation.
