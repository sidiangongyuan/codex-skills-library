# Refinement Guidelines

- Keep this skill generic across papers, venues, and repos.
- Promote only reusable writing heuristics into the skill.
- Do not hardcode a specific target file, project, dataset, or model name in the skill.
- Keep paper-specific conventions outside the skill unless the user explicitly asks for a project-local note.
- Avoid em dashes in paper prose by default. Rewrite with complete sentences, commas, semicolons, parentheses, or sentence splits.
- Allow colons only when they genuinely improve structure; avoid using them as a shortcut for loose explanation or apposition.
- Before revising, identify the venue, audience, and section role.
- Before revising, identify the paper's narrative role: dataset/benchmark, method, analysis, or system. A good revision makes that role easier to read; it does not simply preserve the chronology of how experiments were run.
- Preserve verified claims, citations, equations, and numbers unless the user explicitly asks to change them.
- Prefer claim-driven prose, clear transitions, and concise sentences over component lists and repetitive setup.
- Write as the author inside the manuscript. A revised paragraph, caption, or
  table note must be ready for reviewers; author instructions and internal work
  status belong only in the chat response or project records.
- Treat experiments as evidence in a story, not as a lab notebook. Main text should state the question, table/figure evidence, and interpretation. Put command lines, runner stages, parser internals, checkpoint bookkeeping, and other operational detail in appendix notes only when needed for reproducibility.
- Use section-aware disclosure. Abstract, Introduction, main result paragraphs, and Conclusion should expose only the details that change the scientific claim or reader interpretation. Checkpoint initialization, runner names, guard conditions, adapters, artifact paths, download failures, and failed smoke runs belong in Appendix or internal records unless they affect fairness, validity, or reproducibility.
- Do not sound anxious. Do not pile up caveats in captions or prose to pre-answer every possible reviewer question. State the necessary scope cleanly, then move non-interpretive engineering detail out of the main flow.
- Use a section-altitude gradient. Abstract and early Introduction should say what problem the paper asks, what it contributes, and what the evidence implies. Experiments can name the protocol, controls, conversions, and diagnostics after the setup has defined them. Appendix can carry the full operational machinery.
- Prefer simple wording until precision requires a term. Do not coin a new phrase, expose a runner name, or introduce a fairness/conversion label in front matter when "same evaluation setting", "controlled diagnostics", or another ordinary phrase is accurate enough.
- Keep category boundaries visible. Dataset/protocol contents, model components, diagnostic controls, baseline-conversion fairness, and appendix audit mechanics are different kinds of claims; do not collapse them into one component inventory.
- Keep the claim hierarchy visible. Establish the main method, dataset, or
  system result first. Treat ablations, reliability controls, and diagnostics as
  supporting evidence unless the paper explicitly makes one of them central.
- When a reader is confused, first check for a category error before polishing the sentence. A dataset component, diagnostic experiment, baseline setup, and implementation note should not be merged into one list or claim.
- Prioritize natural academic English. Prefer familiar words, standard phrasing, and direct syntax over ornate, rare, or thesaurus-like wording.
- Remove AI-like filler: generic intensifiers, repetitive transitions, unnecessary hedges, and sentences that sound polished but do not add information.
- Respect venue- or project-specific constraints when they are provided in the repo or by the user.
- If a new preference appears to be universally useful across paper polishing tasks, add it to the skill. If it is only specific to one paper, do not add it here.

## Structural Refinement Heuristics

- Distinguish structural problems from sentence problems before editing. If a section has the wrong argumentative arc, fix the arc before polishing wording.
- In method sections, keep the task definition separate from the paper's realization of that task. Do not let a generic `Problem Formulation` quietly assume the paper's own module choices unless that is explicitly intended.
- When a paragraph is trying to do too many jobs, compress it to one dominant role: motivate, define, compare, or conclude.
- Prefer idea-first summaries over component inventories in introduction and conclusion paragraphs.
- Treat repeated secondary properties as setup facts, not as slogans. Mention them once where they matter, then stop repeating them across the paper.
- In evaluation and reliability papers, foreground the scientific question first and treat the benchmark, dataset, or protocol as the instrument used to answer it. The data artifact should not eclipse the phenomenon the paper reveals.
- Preserve logical continuity across neighboring paragraphs. A revised sentence should not introduce a motivation, assumption, or conclusion that the surrounding text has not prepared.
- Merge duplicate names for the same condition, component, or ablation. Prefer
  one ordinary, reviewer-readable term over multiple internal aliases.

## Claim Safety and Validation

- Treat honesty as a writing constraint, not a post-hoc caveat. Claims should be strong only when the paper's own evidence can support them.
- Before strengthening a claim, ask what table, figure, equation, citation, or stated assumption supports it. If the support is absent or indirect, use narrower wording.
- Avoid absolute guarantees such as "ensures", "solves", "eliminates", or "fully robust" unless the paper proves them under the stated scope.
- State comparison scope clearly: dataset, protocol, metric, budget, corruption model, or training condition when the scope matters.
- If the user asks for a stronger claim and the evidence is uncertain, flag the gap and ask for the missing support rather than fabricating a justification.
- When related work supports only a shared design pattern, state that pattern
  and the relevant difference. Do not imply architectural identity merely to
  make the paper's design sound established.
- After editing a section with figures, tables, equations, or citations, check for stale references, mismatched labels, undefined symbols, and prose that contradicts captions or tables.
- After changing a table or figure, audit the table body, caption, and local
  explanatory paragraph as one unit. If rows, columns, panel structure, or
  comparison targets changed, update all three before considering the edit done.
- Search for stale terminology after visual edits. Remove obsolete condition
  names, old abbreviations, runner names, parser tags, internal words such as
  `alias`, and previous table logic unless they are necessary reproducibility
  details in the appropriate section.

## Experiments and Tables

- Keep setup prose factual and protocol-centered. Use it to define datasets, metrics, corruption models, and evaluation conditions, not to defend the paper.
- For dataset and benchmark papers, the experimental arc should show why the benchmark matters: what capability it exposes, which controls reveal hidden failure modes, and how the baseline demonstrates the evaluation surface. Do not let "how we implemented the baseline" displace "what the benchmark teaches."
- Align each experiment paragraph with the specific table or figure it interprets. Remove stale phrases when a figure, caption, or row changes.
- Keep the reader's comparison path consistent. If a table is meant to be
  scanned horizontally across tasks or controls, the prose and caption should
  preserve that comparison rather than silently reframing it after a layout edit.
- When an experiment is planned but not yet reported, prefer a clean table scaffold with `--` over ad hoc prose promises. Keep the caption focused on the comparison and metric contract; do not expose internal status such as `TODO`, `TBD`, or `pending`, and do not draw conclusions from placeholders.
- Define non-standard metrics at first use with their measured quantity,
  aggregation population, unit, direction, and reference row or condition for
  any delta. If this contract is hard to explain, simplify or remove the metric.
- Present baselines by their normal method names in main tables and result prose unless a qualifier changes how the number should be read. If a baseline is partially reproduced, converted, adapted, or guarded in a way that affects fairness, validity, or reproducibility, state that precisely in the setup, caption, footnote, or Appendix; avoid turning every baseline row into an implementation caveat.
- Distinguish different comparison axes precisely:
  - native-budget versus budget-matched
  - no-loss versus lossy evaluation
  - total message contribution versus the effect of an additional conditioning path
- In ablation descriptions, state clearly what all rows share before describing what is varied. This prevents readers from mistaking a local ablation effect for the total contribution of a module or signal.
- Use appendix setup space for measurement definitions when needed, especially for communication cost, packet-loss simulation protocol, and runtime reporting.

## Appendix and Review-Driven Cleanup

- Appendix prose should read like supplementary material, not like a concealed rebuttal. Keep the tone explanatory, not adversarial.
- If a reviewer misunderstanding is caused by ambiguous wording, repair the ambiguous sentence, caption, or paragraph directly instead of only adding defensive explanation elsewhere.
- When a criticism cannot be solved by wording alone, tighten the paper's claim to match the evidence instead of pretending the gap is closed.
- For setup appendices, expand benchmark descriptions and evaluation protocol before adding more architecture minutiae.
- For conclusions, prefer a single compact paragraph that restates the central claim and broader takeaway without replaying the full method arc.
