# Visual Extraction And Browser QA

## Contents

1. Source hierarchy
2. Figures
3. Tables
4. Presentation layout
5. Browser verification
6. Acceptance checklist

## 1. Source hierarchy

Prefer visual evidence in this order:

1. paper PDF or supplementary PDF;
2. official project page or author repository;
3. an explicitly labeled explanatory redraw;
4. generated imagery only when the paper has no suitable visual and the user
   benefits from a new conceptual illustration.

Never replace scientific evidence with atmospheric stock imagery. Keep the
original file or capture whenever cropping, upscaling, annotation, or redraw is
performed.

## 2. Figures

- Extract at a resolution appropriate for a projector, not only for the HTML
  viewport on the current laptop.
- Preserve axes, legends, units, panel labels, and visual encodings needed to
  interpret the claim.
- Crop page furniture and unrelated captions, but do not crop away qualifiers
  or comparison labels.
- Use `object-fit: contain` and a stable figure region so images do not resize
  the slide when loaded.
- If the original is too dense, show a focused crop alongside a short statement
  of what was omitted. Do not silently alter the figure.
- Mark explanatory redraws as schematics and keep their wording traceable to
  the source.

## 3. Tables

### Capture

- Render the PDF page at 2x-4x scale before cropping. Do not begin with a small
  operating-system screenshot and rely on interpolation to recover text.
- Save the initial page or table capture in `assets/tables/raw/`.
- Crop the presentation copy tightly to the table boundary. Remove surrounding
  body text and redundant long captions when the slide already supplies the
  context.
- Prefer PNG for text-heavy tables. A presentation crop around 1600-2200 pixels
  wide is a useful target for a full-width 16:9 slide, but judge character
  sharpness rather than enforcing one width for every table.

### Display

- Give the table the dominant visual area. Avoid placing a dense table in a
  narrow card beside several paragraphs.
- Keep a concise, metric-specific interpretation near the table.
- State metric direction and any meaningful exception.
- Make the table click-to-zoom with descriptive alternative text.
- A lightbox is a fallback for inspection, not permission to make the default
  view illegible.

## 4. Presentation layout

- Use a stable 16:9 stage for desktop presentation and continuous document flow
  on narrow screens.
- Keep all primary content within the stage at 1280x720, 1440x900, and
  1920x1080 viewports.
- Do not scale font size continuously with viewport width. Use deliberate
  breakpoints and stable type sizes.
- Reserve display-scale type for the title slide. Keep chart annotations,
  citations, controls, and panel headings compact but readable.
- Avoid nested cards, decorative page-section cards, ornamental blobs, and
  one-hue palettes. Let the paper visuals carry the page.
- Use familiar icon buttons for previous, next, close, and zoom interactions;
  provide accessible names and fixed hit areas.
- Ensure long English titles and unbroken technical terms wrap without
  overlapping neighboring content.

## 5. Browser verification

Use a real browser after the static audit. Prefer the installed Playwright CLI
workflow and direct `file://` navigation.

Desktop checks:

- open at 1920x1080 and at least one non-16:9 viewport such as 1440x900;
- visit every slide with the controls and keyboard;
- verify the active-slide counter and progress state;
- open and close every table lightbox;
- inspect source links and local assets;
- check the browser console for errors;
- capture the full stage and at least one enlarged table.

Mobile checks:

- open around 390x844;
- confirm all slides become a readable continuous document;
- confirm no hidden desktop slide state removes content;
- inspect long titles, quotations, tables, source lines, and the final section;
- ensure controls do not cover the text.

Print checks:

- emulate print media or create a temporary print preview;
- verify every slide is visible and starts on a new page;
- ensure navigation and lightbox controls are absent;
- confirm backgrounds, borders, and text remain legible.
- when generating a proof with Playwright, use `preferCSSPageSize: true` and
  `printBackground: true`, then confirm the PDF page count matches the slide
  count and render dense pages back to PNG for visual inspection.

Inspect the screenshots themselves. A zero exit code cannot reveal tiny table
text, visual imbalance, clipped citations, or incoherent overlap.

## 6. Acceptance checklist

- The package opens without a server or network dependency.
- Every local `src` and `href` resolves.
- Every scientific image has descriptive alternative text.
- Tables are readable before zoom and sharper when enlarged.
- Raw and processed table captures are both retained.
- No slide overflows or changes size when an asset loads.
- Desktop navigation and mobile continuous reading both work.
- Print layout contains all slides and no interactive controls.
- Final desktop, mobile, and table-lightbox screenshots are stored in `qa/`.
