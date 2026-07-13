# Visual Story Patterns

## Contents

1. Selection rule
2. Relationship-to-layout map
3. Evidence fidelity
4. Repetition check
5. Responsive behavior

## 1. Selection rule

Choose a composition only after naming the relationship the audience must see.
The visual should make that relationship faster to understand than a paragraph
or short list. Keep a text-led slide when no visual structure adds information.

Do not treat variety as a quota. Reuse a layout when the same relationship
genuinely recurs, but avoid turning every idea into a left-to-right sequence of
rectangular cards.

Add `data-visual-pattern` to a slide that contains an original explanatory or
synthesis diagram. Use a stable descriptive value such as `timeline`,
`matrix`, `vertical-causal`, `radial`, `layered`, `cycle`, `spectrum`,
`annotated-figure`, `evidence-map`, `before-after`, `swimlane`, or
`horizontal-chain`. Do not mark slides that simply reproduce a paper figure or
table.

## 2. Relationship-to-layout map

| Relationship to show | Preferred compositions | Avoid |
|---|---|---|
| Historical or methodological sequence | Timeline, stepped path, vertical milestones | Equal cards with arrows when dates or stages are not visible |
| Cause, consequence, and intervention | Top-down causal chain, branching tree, fishbone | A flat row that hides branching or feedback |
| Alternatives across shared criteria | Two-dimensional matrix, aligned comparison table, small multiples | Separate cards that force the audience to remember each criterion |
| Hierarchy or abstraction levels | Layered bands, nested structure, tree | A horizontal process that falsely implies time |
| Several signals converging on one claim | Center-radial map, funnel, converging paths | Repeating the claim inside every source box |
| Feedback or repeated refinement | Cycle or loop with an explicit return edge | A one-way chain that removes the feedback relation |
| Degree, trade-off, or assumption strength | Axis, spectrum, slope, quadrant | Discrete boxes that erase continuity |
| Claim supported by heterogeneous evidence | Evidence map with claim, observations, and caveat | A chain that implies one result causes the next |
| State change | Before/after pair, delta overlay, paired frames | Three generic stages when only two states matter |
| One dense source figure needing guidance | Large original figure with restrained callouts | Shrinking the figure beside a paragraph or redrawing its data |
| Parallel modules or agents | Swimlanes with aligned events and crossings | Boxes whose order and ownership are ambiguous |

Use lines, axes, whitespace, alignment, and direct annotation before adding
containers. Avoid cards inside cards. Keep labels close to the marks they
describe and use one reading direction per diagram.

## 3. Evidence fidelity

Original diagrams may summarize background, related work, method mechanics, or
the presenter's interpretation. They must not fabricate measurements, redraw a
result with altered geometry, or imply a causal mechanism that the experiments
did not isolate.

For a synthesis diagram:

- trace every factual node to a paper claim, figure, table, or verified source;
- distinguish observed evidence from interpretation with wording or visual
  treatment;
- preserve exceptions and unresolved links;
- use a concise source line when several paper elements are combined;
- prefer the original figure when a redraw would remove axes, labels, or
  qualifiers needed to judge the result.

## 4. Repetition check

Review the storyboard before styling. If three consecutive original-diagram
slides use `horizontal-chain`, stop and inspect the underlying relationships.
Keep the chain only when all three are truly sequential. Otherwise select the
composition that exposes comparison, hierarchy, convergence, feedback, or
evidence structure more honestly.

Also check deck-level monotony: repeated white rectangles, equal three-column
grids, and identical top-border cards can feel repetitive even when their CSS
class names differ. Fix the semantic composition, not merely colors, corner
radii, or arrow styles.

## 5. Responsive behavior

- Convert horizontal timelines to vertical milestones on narrow screens.
- Let matrices and dense tables scroll horizontally at a readable intrinsic
  width; do not reduce text until it becomes illegible.
- Reflow radial or evidence maps into a source-to-claim sequence while keeping
  labels and connections adjacent.
- Keep before/after pairs together when possible; otherwise stack them with
  explicit state labels.
- Preserve reading order in the DOM so mobile and print layouts remain
  understandable without desktop positioning.
