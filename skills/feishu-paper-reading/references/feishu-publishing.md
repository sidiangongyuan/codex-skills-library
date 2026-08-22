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

Treat a connector as eligible only when it exposes the required create and
readback capabilities and its user authorization is valid. Do not create a
disposable probe: publish the formal report exactly once, then fetch that same
document before calling the route connected. When those capabilities are absent,
unregistered, unauthorized, or unhealthy, load
`references/feishu-onboarding.md` and follow its state-based recovery or guided
official setup. Do not silently downgrade merely because the first capability
check fails.

If a compatible connector is already verified, publish normally without
repeating onboarding. Ask for explicit consent before creating an app,
authorizing an account, or changing Codex MCP configuration during first-time
setup. Fall back to the complete Markdown report only when the user declines
setup, no compatible route exists, or setup remains unsuccessful after the
bounded recovery steps. Disclose the exact reason publishing was skipped.

## Choose The Route

- Use rich-document creation for text, links, tables, and quote-heavy reports.
- Use DOCX import when approved figures or complex tables must survive.
- Use Markdown import only when the connector preserves its structure.
- Create a mind map only when it clarifies relationships across at least three
  papers and the connector can verify the result.

If the request explicitly requires key figures or tables to appear in Feishu,
use DOCX import with the source visuals embedded. Markdown image syntax is not
an acceptable fallback when it leaves only a caption or paper locator. Keep a
single stable visual template across issues: blue for conclusions/headings,
green for strengths and transferable insights, purple for source excerpts,
orange for attention/resources, red for limits, and gray for metadata.

Create one new document per run. Update an existing document only when the user
identifies it and explicitly requests the update. Use the publication checkpoint
from `feishu-onboarding.md`; never issue create when its state is `created`,
`verified`, `create_in_flight`, or `outcome_unknown`. A retry must first pass
the matching audited recovery transition.

For an existing connector, derive a SHA-256 fingerprint from its stable,
non-secret authenticated user/tenant identity and choose a stable connector ID.
If the connector cannot expose enough identity metadata to distinguish accounts,
stop rather than guessing. Prepare with:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" prepare \
  --report "report.md" --title "<report title>" \
  --state ".feishu-publication.json" \
  --payload ".feishu-publication.md" \
  --delivery-route "connector" \
  --connector-id "<stable-connector-id>" \
  --connector-identity-sha256 "<verified-identity-hash>"
```

Immediately before the one create call, re-verify that connector identity and
run:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" begin-create \
  --state ".feishu-publication.json" \
  --delivery-route "connector" \
  --connector-id "<stable-connector-id>" \
  --connector-identity-sha256 "<verified-identity-hash>"
```

The helper re-hashes the publication payload and rejects any binding change.

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

Keep the report in article voice. Do not include direct-to-reader coaching or
meta-asides; uncertainty belongs in the paper's evidence, assumptions, and
limitations sections.

For each paper, keep canonical paper and code links near its verified metadata.
Use source figure captions and clear attribution when embedding is allowed.
Never imply that a generated diagram is a source figure.

## Publish Safely

- Request only the permissions needed to create and read back the new document.
- Do not expose general delete, drive-management, or broad folder tools.
- Do not overwrite or delete prior documents.
- Do not persist credentials in the report or skill directory.
- Keep temporary export files inside a declared working directory.
- Persist the run ID and returned document ID atomically before readback. An
  explicit write-ahead state must precede create. An in-flight or ambiguous
  outcome requires the documented recovery and, when delivery may have
  occurred, user reconciliation before retry, never an automatic second create.

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
