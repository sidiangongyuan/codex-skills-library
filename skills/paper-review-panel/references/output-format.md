# Output Format

Write in English by default. Keep the result concise enough to guide revision,
but complete enough to resemble a real top-conference review.

## Default Synthesis Template

```markdown
**Overall Assessment**
[One paragraph: paper goal, main contribution, and acceptance risk.]

**Estimated Score**
- Overall: [venue-aware score, or 1-10 if venue unknown]
- Confidence: [venue-aware confidence, or 1-5 if venue unknown]
- Acceptance risk: [likely reject / borderline / weak accept risk / likely accept if fixed]

**Strengths**
- [Specific strength with anchor.]
- [Specific strength with anchor.]

**Weaknesses**
- [Acceptance-critical concern with anchor and why it matters.]
- [Major concern with anchor and why it matters.]

**Questions / Clarifications**
- [Question a reviewer would ask.]
- [Clarification needed.]

**Main-Agent Judgment**
- Valid concerns to fix: [short list.]
- Misunderstandings caused by paper clarity: [short list.]
- Unsupported or incorrect reviewer concerns: [short list or "None."]
- Optional polish: [short list.]

**Compact Revision Priorities**
- Main paper: [highest-impact changes.]
- Experiments / evidence: [needed evidence or safer framing.]
- Figures / tables / appendix: [layout, consistency, or support changes.]
```

## Scoring

- If the venue is known and the user expects a specific scoring convention,
  follow it.
- If the venue is unknown, use `Overall 1-10` and `Confidence 1-5`.
- Treat scores as a synthesized risk estimate, not a claim that the paper would
  receive exactly that score.

## Acceptance-Risk Language

- `Likely reject`: one or more main claims lack credible support, novelty is
  unclear, or protocol validity is seriously threatened.
- `Borderline`: the idea is plausible but evidence, clarity, or positioning
  would likely split reviewers.
- `Weak accept risk`: the paper is probably acceptable if targeted issues are
  fixed, but still has visible reviewer attack points.
- `Likely accept if fixed`: the main contribution is clear and supported; fixes
  are mostly clarity, presentation, or limited evidence additions.

## Style Rules

- Do not include long raw reviewer transcripts.
- Do not write a generic praise-first review if the evidence is weak.
- Do not soften critical issues into vague suggestions.
- Do not over-index on typography if the real risk is claim-evidence mismatch.
- Keep revision priorities actionable but non-mutating.
