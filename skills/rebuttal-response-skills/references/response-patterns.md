# Rebuttal Response Patterns

Read this reference for full-response drafting, experiment integration, risk
resolution, and blind audits. Adapt the structure to the exact review rather
than copying boilerplate.

## Contents

- Shared response contract
- Five concern-specific response patterns
- Tables and definitions
- Risk markers and decision ledger
- Two-stage blind audit
- Format-verifier contract

## Shared Response Contract

For every concern:

1. Preserve the reviewer's complete decisive wording in the heading when space
   permits.
2. Answer in the first sentence.
3. Define only unfamiliar setup or terminology.
4. Show evidence before interpreting it.
5. State only the implication supported by that evidence.
6. Add a revision or future direction only when needed and approved.

If several new experiments share one dataset, model pair, and protocol, define
that setup once in the response opening. Define exceptions locally.

## 1. Experimental Concern

Use when the reviewer requests robustness, ablation, stratification, latency,
or another measurable behavior.

```markdown
### W1/Q1. "<Complete decisive reviewer wording>"

**Response.** [Direct result or current evidence status.]

[Minimal definition of the tested conditions and controls.]

| Condition | Baseline metric | Method metric |
|---|---:|---:|
| ... | ... | ... |

[Interpret the pattern without overstating causality. State any tested boundary
that materially changes the answer.]
```

Requirements:

- Use the submitted value for a submitted result and matched controls for new
  results.
- Define nonstandard conditions and statistics before the table.
- Retain mixed or negative conditions internally and route them through the
  risk-marker process.
- Do not call aggregate evidence a per-instance guarantee.

## 2. Concept or Scope Clarification

Use when the reviewer questions terminology, assumptions, interfaces, or claim
scope.

```markdown
### W1/Q1. "<Complete decisive reviewer wording>"

**Response.** [State the precise definition or correct the premise.]

[Explain the relevant contract or assumption using submission terminology.]

[Point to the submitted section/table/figure and summarize what it establishes.]

[State the implication. Add a concrete camera-ready clarification only if the
submitted wording needs one.]
```

Separate a required operating contract from the problem the method actually
solves. Do not convert a scope clarification into a new capability claim.

## 3. Comparison Fairness

Use when the reviewer questions baselines, protocol mismatch, upper bounds, or
the interpretation of superiority.

```markdown
### W1/Q1. "<Complete decisive reviewer wording>"

**Response.** [State what the comparison does and does not establish.]

[Define each method's intended setting and the common evaluation constraint.]

| Method | Preparation/assumption | Metric |
|---|---|---:|
| ... | ... | ... |

[Give the narrow comparison conclusion. Correct any overbroad wording if
necessary.]
```

Do not present a stress test outside a baseline's intended setting as general
superiority. Keep native-setting references distinct from matched-constraint
comparisons.

## 4. Implementation or Deployment Behavior

Use for state management, online updates, collaborator changes, scaling, or
runtime questions.

```markdown
### W1/Q1. "<Complete decisive reviewer wording>"

**Response.** [Describe the behavior stated by the submitted method.]

[Method design: what the design permits.]

[Current implementation: what is actually supported, if the paper or verified
implementation establishes it.]

[Evaluation: what has been tested.]

[State the untested operational case once, if it is part of the question.]
```

Use the paper as the primary source. Inspect code only when an explicitly
implementation-specific question remains ambiguous or the user requests it.
Never present a plausible extension as current support.

## 5. Untested or Infeasible Request

Use when the requested experiment or system change cannot be completed within
the rebuttal window.

```markdown
### W1/Q1. "<Complete decisive reviewer wording>"

**Response.** [Answer the technical point using current evidence or reasoning.]

[State exactly what remains untested and why current evidence cannot settle it.]

[If user-approved: describe a bounded future evaluation or extension without
guaranteeing implementation or outcome.]
```

Do not use future work as a substitute for answering the current question.

## Tables and Definitions

- Prefer a normal table when several conditions or metrics must be compared.
- Keep shared values and definitions identical across reviewer responses.
- Reviewer-specific tables may omit irrelevant rows or columns.
- Define a custom condition by its operation, not just its name.
- Define a derived metric with its formula, unit, and favorable direction.
- Define percentile latency as the percentile of the specified per-sample
  timing distribution and list included and excluded stages.
- Do not label an analytical estimate as measured.
- Working tables may contain `-` while evidence is pending. Submission
  candidates may not.

## Risk Marker and Decision Ledger

Use the exact internal form:

```text
[REVIEW NEEDED | Ideal: <evidence or behavior that would fully support the
claim> | Observed: <verified result and its limitation> | Decision: <specific
user choice required>]
```

Create a marker when:

- a new result is mixed, negative, or materially different from expectation;
- a submitted value and reproduction conflict;
- only a proxy is available for the requested quantity;
- a proposed claim, omission, or future commitment needs user approval.

Resolve markers one at a time. Present the ideal, observed evidence, and
recommended response. Do not remove a marker until the user decides. A resolved
marker must record whether the evidence is included, the claim is narrowed, or
the material is omitted as irrelevant. Never omit a reviewer-requested,
previously promised, or claim-critical negative result solely because it is
unfavorable.

For a submitted-versus-rerun conflict, pause the affected claim, table, and all
responses that reuse it. Independent drafting may continue. Resume dependent
work only after the user selects the source of truth. A conflict is material
when it could alter a reviewer-facing conclusion, comparison ordering, or claim
boundary; a universal numeric tolerance is not appropriate across metrics.

The shared decision ledger should record:

| Field | Required content |
|---|---|
| Decision | Exact value, wording, inclusion, exclusion, or stop choice |
| Scope | Reviewers, tables, and claims affected |
| Source | User confirmation or verified artifact |
| Consequence | Edits and checks required |
| Status | Active, superseded, or completed |

All drafting and audit agents that are not blind evaluators must read active
decisions before changing shared evidence. Blind evaluators must never receive
the ledger.

## Two-Stage Blind Audit

Use fresh agents with no access to writing history or internal strategy. If
fresh agents are unavailable, perform the two phases as isolated self-audits
and record that the result is not independent.

### Reviewer Phase 1: Paper Only

Inputs:

- submitted paper and supplement;
- venue scoring scale and public rules.

Do not provide official reviews, responses, target scores, concern maps,
decision ledgers, or suspected weaknesses.

Required output:

- concise independent summary;
- major strengths and concerns;
- score and confidence on the venue scale;
- evidence locations supporting each concern.

Lock this output before Phase 2.

### Reviewer Phase 2: Review and Response

Add only the corresponding exact official review and candidate response.

Required output:

```text
Initial score:
Post-response score:

Concern coverage:
- <concern>: fully answered | partially answered | untested boundary |
  pending evidence

Findings:
- Response defect: ...
- Unresolved paper limitation: ...
- Optional strengthening: ...

Final verdict: ACCEPTABLE | BLOCKED
Blocking response defects:
```

`ACCEPTABLE` means no response defect remains. A genuine paper limitation may
remain without blocking the response.

### AC Phase

Use a fresh AC agent after reviewer audits. Provide the submitted materials,
meta-review when present, official reviews, candidate responses, and reviewer
audit outcomes. Do not provide internal strategy, target scores, or the
decision ledger. Ask whether the responses address the decision-critical
conditions without unsupported claims. Require `ACCEPTABLE` or a list of
blocking response defects.

## Format-Verifier Contract

Give a fresh verifier only the official venue rules and final candidate. If a
fresh verifier is unavailable, run an isolated verifier pass with the same
inputs. Use the platform's official counting method and require text to stay
below a character maximum and a PDF to stay within its page maximum. Combine
the inspection with deterministic checks for:

- exact per-response character count or shared PDF page count;
- Markdown table column consistency;
- balanced supported LaTeX delimiters;
- PDF compilation, page count, clipping, and readability when applicable;
- reviewer IDs, headings, anonymity, links, and machine-specific paths;
- `REVIEW NEEDED`, `TODO`, `pending`, placeholders, and internal artifact
  paths.

The verifier reports only concrete violations. Resolve all blocking findings
before submission.
