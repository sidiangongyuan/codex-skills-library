# Experiment Planner Source Map

This skill is a local Codex adapter. Use these upstream projects as pinned
references for workflow ideas, not as installed dependencies or copied text.

## Pinned References

| Source | Pinned commit | Reference paths | Use in this skill | Not adopted in v1 |
|---|---:|---|---|---|
| modelscope/Awesome-Vibe-Research | `3b13292b7653b12cc6faa37a17fc69fdf1b992e2` | `README.md` | Project map for separating direction scanning, method design, experiment execution, and writing. | No direct install or automatic orchestration. |
| wanshuiyin/Auto-claude-code-research-in-sleep | `dd1ee32dad5fd9a772eea0c5d0553cd938edcbf7` | `skills/idea-discovery/SKILL.md`, `skills/experiment-plan/SKILL.md`, `skills/experiment-bridge/SKILL.md` | Main reference for literature survey, idea refinement, novelty check, claim-driven experiment planning, pilot-first execution, and bridging plan to code. | No full ARIS install, no default report files, no automatic overnight/GPU deployment. |
| Imbad0202/academic-research-skills-codex | `36cc610fca8e3935904c6c175e3a0a05c7d9b8c6` | `skills/academic-research-suite/ars/experiment-agent/WORKFLOW.md` | Safety and reproducibility boundaries: no automatic code changes, no automatic retries, cautious statistical interpretation. | No suite install and no replacement of local writing/review/rebuttal skills. |
| Just-Curieous/Curie | `db1b1f56159b591515f77e03c55bf473d5c1c201` | `README.md`, workflow descriptions | Hypothesis to implementation to execution to analysis to reflection loop. | No Docker/API/key-based agent framework integration. |
| karpathy/autoresearch | `228791fb499afffb54b46200aca536f79142f117` | `README.md` | Short-loop experimental discipline: fixed question, fixed metric, small validation before expansion. | No nanochat-specific assumptions or single-project runner adoption. |

## Adaptation Principles

- Prefer ARIS-style flow for research ideation: survey, refine, novelty check,
  experiment planning, then pilot validation.
- Prefer ARIS experiment-plan style for claim-driven roadmaps: define the claim,
  anchor result, novelty isolation, simplicity check, failure analysis, and run
  order before coding.
- Prefer ARIS experiment-bridge style only as a coordination idea: plan to code
  via explicit tasks, sanity checks, and controlled execution. Keep Codex main
  session in charge of acceptance.
- Prefer Academic Research Skills Codex safety rules when execution pressure is
  high: do not silently modify user code, retry crashed jobs, or overstate
  statistical meaning.
- Prefer Curie/autoresearch only for the research loop and experiment discipline,
  not for their runtime frameworks.

## Upgrade Rule

When updating this skill from upstream projects, first compare the pinned commit
against the new upstream state. Update this file with the new commit, summarize
what changed, and keep the local behavior conservative unless the user approves
heavier automation.
