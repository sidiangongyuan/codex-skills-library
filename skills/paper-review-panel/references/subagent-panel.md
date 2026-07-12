# Subagent Panel Workflow

Use this file only when the user explicitly asks for subagents, multiple
reviewers, reviewer panel, parallel review, or equivalent delegation.

## Spawn Policy

- Spawn exactly three independent reviewer agents unless the user requests a
  different number.
- Follow project-level agent instructions such as `AGENTS.md`. If none are
  available, inherit the parent model and reasoning settings.
- Do not hardcode a model override in the skill. Use explicit overrides only
  when the user or project instructions require them.
- Subagents are read-only reviewers. They must not edit files, run training,
  rerun experiments, or rewrite paper text.
- Give each subagent the same artifacts but a different role prompt.
- Do not pass your expected conclusion or other reviewers' findings to a
  reviewer subagent.

## Main-Agent Responsibilities

- While reviewers run, inspect non-overlapping artifacts yourself: paper
  structure, figure/table list, result consistency, and venue/template issues.
- When reviews return, synthesize them. Do not paste raw reviews by default.
- For each important concern, decide whether it is:
  - valid and should be fixed;
  - a reviewer misunderstanding caused by unclear writing;
  - unsupported or incorrect and should not drive changes;
  - optional polish.
- Use reviewer disagreement as signal. If only one reviewer notices an issue,
  verify whether the artifact supports it before including it.

## Reviewer Prompts

Replace bracketed fields with concrete artifact paths or descriptions.

### Reviewer 1 Prompt

```text
Review [paper/artifacts] as Reviewer 1 for a top-tier conference. Focus on
contribution, novelty, positioning, motivation, related work, venue fit, and
overclaiming. Do not edit files or run experiments. Cite concrete anchors:
page, section, table, figure, equation, appendix item, or source location.
Return an official-style review with summary, strengths, weaknesses, questions,
overall score, confidence, and acceptance-critical concerns.
```

### Reviewer 2 Prompt

```text
Review [paper/artifacts] as Reviewer 2 for a top-tier conference. Focus on
technical correctness, method/protocol clarity, experiments, metrics, baselines,
ablation sufficiency, statistical support, leakage risk, and claim-evidence
alignment. Do not edit files or run experiments. Cite concrete anchors: page,
section, table, figure, equation, appendix item, or source location. Return an
official-style review with summary, strengths, weaknesses, questions, overall
score, confidence, and acceptance-critical concerns.
```

### Reviewer 3 Prompt

```text
Review [paper/artifacts] as Reviewer 3 for a top-tier conference. Focus on
writing clarity, figures/tables, captions, notation, terminology, citations,
appendix/main consistency, release/reproducibility claims, and reviewer
readability. Do not edit files or run experiments. Cite concrete anchors: page,
section, table, figure, equation, appendix item, or source location. Return an
official-style review with summary, strengths, weaknesses, questions, overall
score, confidence, and acceptance-critical concerns.
```

## Panel Synthesis Rules

- Lead with the main acceptance risk, not with process details.
- Aggregate duplicate concerns into one finding.
- Keep raw reviewer comments internal unless the user asks for them.
- Include reviewer score spread only if it helps explain the acceptance risk.
- Convert reviewer concerns into compact revision priorities, but do not
  implement them.
