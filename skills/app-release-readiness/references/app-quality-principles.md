# App Quality Principles

Use these principles when building or changing a user-facing app.

## Product Truth

- Users experience workflows, not endpoints. A feature is incomplete until the
  visible state, failure copy, persistence, and recovery path all work together.
- Users should not have to infer where work went. Results, drafts, and long
  running job state should remain visible or recoverable until the user
  explicitly clears them.
- Ground decisions in the current repo before asking. Inspect code, tests,
  logs, configs, packaging scripts, and screenshots first.
- Do not hide failures behind fake success. A mocked provider or mocked API
  proves the branch, not real availability.
- Separate "configuration exists" from "service works". Real connectivity
  tests must send a real minimal request.

## Data Safety

- Prefer copy-first migrations over move/delete migrations.
- Preserve old data directories as rollback points unless the user explicitly
  requests deletion.
- Never make uninstall cleanup delete writing/user content by default.
- Show storage paths and backup/checkpoint paths in user language when storage
  location matters.

## Error Handling

- Public UI must not show raw strings such as `Not Found`, `Failed to fetch`,
  provider HTML, stack traces, or unlocalized backend exceptions.
- Stale requests should be ignored. Current valid failures should be translated
  into actionable copy.
- Optional capability failures should degrade in-place instead of breaking the
  whole page.
- Capabilities/version endpoints help detect frontend/backend mismatch before
  users hit confusing missing-route errors.

## Frontend And UX

- Design for the target user workflow, not for exposing internal knobs.
- Put controls near the task they affect. Avoid rigid extra panels when a
  compact control beside the current context is enough.
- Prefer reading-first surfaces for writing, knowledge, and concept archives.
  Editing should be explicit and focused instead of always showing raw fields.
- Empty states should be quiet and honest. Do not invent demo data unless the
  user requested it.
- Startup should show immediate feedback or become fast enough that feedback is
  unnecessary. Avoid black or blank windows during cold start.
- For dense app surfaces, use restrained controls near the user's task context.
  Avoid bolted-on panels that make the workflow feel rigid.
- Verify UI with screenshots or a real browser/app when layout, spacing,
  overlap, or animations are part of the task.
- Avoid ambiguous navigation that hides output. Use explicit "clear result",
  "close draft", or "discard" actions when user work would otherwise vanish.

## Integration Discipline

- One AI/provider path should serve all AI features unless there is a proven
  reason to branch. Avoid "tool A works, tool B uses a different private path".
- Provider transport must match the actual key and base URL, not only the
  provider label shown to the user.
- Model fetching must state whether results are live, preset, or from a public
  catalog fallback. Do not label fallback data as authenticated access.
- Run only explicit user-selected models or profiles. A default provider is a
  selectable option, not an invisible extra participant.
- Saved provider profiles should own their credential source. Multiple relay
  profiles with different local keys must coexist without overwriting each
  other.

## AI Long Tasks

- Long provider work should be closable and recoverable inside the current app
  session when practical.
- Show honest stages such as preparing context, sending request, waiting for
  model, parsing response, succeeded, failed, or cancelled. Do not invent
  percentages for model internals the app cannot observe.
- Reconnect to local job status after UI close, navigation, or polling failure.
  Do not automatically resend a full provider request, because the first
  request may already be consuming tokens remotely.
- Cancellation should explain its limits: local waiting can stop, but the app
  may not be able to stop remote generation or billing once the request was
  sent.
- AI-generated content should default to preview/confirm flows before writing
  to user libraries, notes, cards, or source text.

## Test Integrity

- Keep mock tests and real checks separate in both implementation and reports.
  Mock tests prove branch behavior; they do not prove provider availability.
- For paid or rate-limited providers, use the smallest real prompt that proves
  the configured provider, model, transport, and credential path.
- Do not add fake fallback data or fake success states just to make automated
  tests pass.

## External Workflow Inspirations

These references informed the workflow shape. Use them for ideas, not as text
to copy:

- OpenAI Codex Skills documentation: https://developers.openai.com/codex/skills
- Anthropic webapp-testing skill page: https://mcpservers.org/agent-skills/anthropic/webapp-testing
- Addy Osmani code-review-and-quality skill: https://github.com/addyosmani/agent-skills/blob/main/skills/code-review-and-quality/SKILL.md
- officialskills frontend / investigate / qa / ship collection: https://officialskills.sh/
- Datadog agent skill examples: https://github.com/DataDog/agent-skill-examples
