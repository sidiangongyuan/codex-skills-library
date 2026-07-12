# UI quality checklist

Use the sections relevant to the current interface. This is a release-oriented
checklist, not a requirement to add every possible feature.

## Accessibility

- Normal text contrast is at least 4.5:1; large text and meaningful UI graphics
  meet the applicable 3:1 threshold.
- Keyboard focus is visible, logical, and never trapped without an exit.
- Headings, landmarks, labels, descriptions, roles, values, and live regions
  expose the same meaning available visually.
- Icon-only controls have accessible names and tooltips where their meaning is
  not immediately familiar.
- Color is never the only signal for status, errors, selection, or chart series.
- Meaningful images have useful alternative text; decorative images are hidden
  from assistive technology.
- Zoom, enlarged text, and dynamic type do not clip controls or hide content.
- Reduced-motion preferences remove nonessential motion without removing state
  feedback.
- Drag, swipe, and hover interactions have keyboard or visible-control
  alternatives.

## Interaction and feedback

- Touch targets are at least 44 by 44 points on iOS and 48 by 48 dp on Android,
  with enough separation to prevent accidental activation.
- Hover is enhancement, not the only way to reveal essential controls or
  information.
- Hover, pressed, selected, focused, disabled, and loading states are distinct
  without shifting surrounding layout.
- Async actions give immediate feedback, prevent accidental duplicate
  submission, and end in an honest success or recoverable error state.
- Destructive or externally visible actions are clearly labeled and require
  confirmation appropriate to their impact; undo is preferred where feasible.
- Errors state what happened and how to recover. Form errors appear near the
  field and focus moves to the first invalid input when useful.
- Long forms preserve work through drafts or warn before discarding changes.
- Gestures follow platform conventions and do not interfere with operating
  system navigation.

## Information architecture and navigation

- Each screen has one clear primary task and a hierarchy that can be scanned
  without relying on color alone.
- Navigation labels are stable and predictable; back navigation preserves
  relevant state and scroll position.
- Important screens have stable URLs or deep links when the platform supports
  them.
- Bottom navigation contains at most five labeled destinations; secondary
  destinations live in an appropriate menu, sidebar, or settings hierarchy.
- Breadcrumbs, titles, or other context make deep locations understandable.
- Empty, permission-limited, offline, and first-use states explain the next
  useful action without turning into product marketing.

## Layout and responsive behavior

- The page has no unintended horizontal scroll at supported widths.
- Fixed headers, tab bars, and action bars reserve content space and respect
  notches, safe areas, system bars, and virtual keyboards.
- Text wraps before truncating. Where truncation is required, the complete
  value remains available through expansion or an accessible tooltip.
- Long words, localization, large numbers, loading labels, validation text, and
  user-generated content do not overflow controls.
- Dense operational screens remain scannable; cards are reserved for repeated
  items or genuinely bounded tools rather than nested page sections.
- Boards, grids, charts, toolbars, and tile layouts use stable constraints so
  dynamic content does not resize or shift the interface unexpectedly.
- Small phone, large phone, tablet, desktop, and landscape states are tested as
  applicable, including at least one long-content case.

## Typography, color, and themes

- Body copy uses a readable base size and line height; line length remains
  comfortable on wide viewports.
- Type roles, weights, and spacing create hierarchy without oversized text in
  compact tools or dashboards.
- Semantic tokens replace one-off component colors and arbitrary spacing.
- Light and dark themes are designed and tested independently; borders,
  overlays, disabled states, charts, and focus indicators remain legible in
  both.
- The palette has enough functional range to distinguish surfaces, actions,
  state, and data without becoming a one-hue theme.
- Brand assets use official geometry, proportions, clear space, and approved
  colors.

## Icons, media, and charts

- One icon family and a consistent stroke/fill treatment are used within a
  visual level. Familiar icons replace text labels only when meaning is clear.
- Raster media has appropriate resolution, responsive sources, intrinsic
  dimensions, useful crops, and loading behavior.
- Primary imagery shows the actual product, place, object, person, gameplay, or
  state when users need to inspect it.
- Charts match the relationship being communicated, label units and time
  granularity, expose exact values where needed, and do not rely on color alone.
- Data-heavy charts offer a text summary or table alternative and keyboard
  access where the chart is interactive.
- Empty and failed chart states explain the absence of data and provide retry
  when appropriate.

## Motion and performance

- Motion communicates cause, state, or hierarchy; it is not added only for
  decoration.
- Micro-interactions usually complete within 150-300 ms, remain interruptible,
  and never block input.
- Transform and opacity are preferred over layout-changing animation.
- Images reserve space, below-fold media is lazy-loaded, and critical content
  is not delayed by unnecessary scripts or fonts.
- Long lists are paginated, windowed, or virtualized when measurement shows
  that full rendering is too costly.
- Loading experiences distinguish short waits from long-running work and avoid
  layout shift when content arrives.

## Forms and data entry

- Inputs have persistent labels, appropriate input types, autocomplete hints,
  helper text, required indicators, and visible validation.
- Validation timing does not punish users while typing; server and client
  errors remain distinguishable.
- Read-only and disabled fields look and behave differently.
- Multi-step flows show progress, preserve entered data, and allow predictable
  back navigation.
- Passwords, destructive values, and irreversible choices receive controls and
  confirmation appropriate to their risk.

## Final verification record

Record the viewports or devices inspected, themes, interaction methods,
accessibility settings, dynamic states, automated checks, and any remaining
manual risk. Do not mark an item verified solely because its source code looks
correct.
