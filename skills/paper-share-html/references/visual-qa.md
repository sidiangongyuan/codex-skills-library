# Visual Extraction And Browser QA

## Contents

1. Source hierarchy
2. Figures
3. Tables
4. Presentation layout
5. Progressive disclosure
6. Browser verification
7. Automated crop checks
8. Acceptance checklist

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

- Render the PDF page at about 300-360 DPI or at least 3x scale before cropping.
  Do not begin with a small operating-system screenshot and rely on
  interpolation to recover text.
- Save the initial page or table capture in `assets/tables/raw/`.
- Crop the presentation copy tightly to the table boundary. Remove surrounding
  body text and redundant long captions when the slide already supplies the
  context.
- Prefer PNG for text-heavy tables. Target 1600-2200 pixels wide for a
  full-width 16:9 slide. Widths below 1400 pixels trigger an audit warning.
- Make the effective table content occupy at least 90% of the processed image
  width and 82% of its height when the source permits. Re-crop long captions,
  body text, page headers, and broad white margins rather than enlarging them.
- Preserve the original page or initial capture even when the processed crop is
  resized. Never use interpolation to manufacture missing glyph detail.

### Display

- Give the table the dominant visual area. Avoid placing a dense table in a
  narrow card beside several paragraphs.
- Use a dedicated full-width table stage. At desktop sizes, the rendered table
  should occupy at least 70% of the usable content width or 55% of the usable
  content height unless a narrower table is already comfortably readable.
- Keep a concise, metric-specific interpretation near the table.
- State metric direction and any meaningful exception.
- Make the table click-to-zoom with descriptive alternative text.
- A lightbox is a fallback for inspection, not permission to make the default
  view illegible.
- On mobile, keep the table at a readable intrinsic width inside a horizontal
  scroller instead of shrinking all cells to the viewport.

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

## 5. Progressive disclosure

- Use numbered `data-fragment` groups only for an actual explanatory sequence.
  Start at `1`, keep groups contiguous and in DOM order, and never nest them.
- Elements with the same number appear together. Keep hidden elements in the
  layout so revealing them does not resize the slide.
- Forward controls reveal the next group before advancing. Backward controls
  hide the latest group before returning, and revisited slides retain progress.
- Keep primary result tables, quantitative plots, and side-by-side qualitative
  evidence static so the audience can compare the complete result.
- Ignore clicks on links, buttons, images, form controls, selected text, and
  lightbox content. Closing a lightbox must not consume a presentation step.
- Hide fragments only after JavaScript marks the document as interactive.
  Without JavaScript, expose every slide as a readable continuous document.
- Force all fragments visible on narrow screens and in print. Preserve DOM
  reading order and accessible state when switching between layouts.
- Respect `prefers-reduced-motion`. Use only a restrained 180-250 ms fade or
  slight vertical movement in the normal desktop presentation mode.

## 6. Browser verification

Use a real browser after the static audit. Prefer the installed Playwright CLI
workflow and direct `file://` navigation.

Desktop checks:

- open at 1280x720, 1920x1080, and a non-16:9 viewport such as 1440x900;
- visit every slide with the controls and keyboard;
- verify the active-slide counter and progress state;
- open and close every table lightbox;
- inspect source links and local assets;
- check the browser console for errors;
- capture the full stage and at least one enlarged table.
- read ordinary row labels, column headings, and body values before opening the
  lightbox; record a failure if zoom is required for normal reading.
- when fragments exist, exercise forward reveal, backward retreat, progress
  persistence, first/last boundaries, and mouse-click isolation;

Mobile checks:

- open around 390x844;
- confirm all slides become a readable continuous document;
- confirm no hidden desktop slide state removes content;
- inspect long titles, quotations, tables, source lines, and the final section;
- ensure controls do not cover the text.
- ensure every fragment is visible and exposed to assistive technology.

Print checks:

- emulate print media or create a temporary print preview;
- verify every slide is visible and starts on a new page;
- ensure navigation and lightbox controls are absent;
- confirm backgrounds, borders, and text remain legible.
- when generating a proof with Playwright, use `preferCSSPageSize: true` and
  `printBackground: true`, then confirm the PDF page count matches the slide
  count and render dense pages back to PNG for visual inspection.

Fallback checks:

- disable JavaScript and confirm all slides and fragments remain readable;
- emulate reduced motion and confirm fragment and progress transitions are
  removed;
- verify the console remains free of errors throughout navigation and layout
  changes.

Inspect the screenshots themselves. A zero exit code cannot reveal tiny table
text, visual imbalance, clipped citations, or incoherent overlap.

## 7. Automated crop checks

`audit_paper_share.py` always checks table dimensions and layout context. When
Pillow is available, it also estimates the non-background content bounding box.
It warns when content occupies less than 90% of the image width or 82% of its
height. The check is a high-confidence aid for broad margins, not a replacement
for visual inspection: unusual dark, textured, or borderless tables may need a
manual judgment.

The audit warns when a processed table sits inside known split, card, or
multi-column containers. It also recognizes optional `data-visual-pattern`
markers and warns when three consecutive original-diagram slides use
`horizontal-chain`.

Pillow remains optional for skill users. Without it, structural, resolution,
resource, language, and layout checks still run normally.

## 8. Acceptance checklist

- The package opens without a server or network dependency.
- Every local `src` and `href` resolves.
- Every scientific image has descriptive alternative text.
- Tables are readable before zoom and sharper when enlarged.
- Processed table crops meet the 1400-pixel warning floor and contain little
  irrelevant whitespace.
- Raw and processed table captures are both retained.
- No slide overflows or changes size when an asset loads.
- Desktop navigation and mobile continuous reading both work.
- Optional fragments reveal and retreat in order without intercepting evidence
  inspection or other interactive controls.
- Mobile, print, and no-JavaScript modes expose all progressive content;
  reduced-motion mode removes animation.
- Print layout contains all slides and no interactive controls.
- Final desktop, mobile, and table-lightbox screenshots are stored in `qa/`.
