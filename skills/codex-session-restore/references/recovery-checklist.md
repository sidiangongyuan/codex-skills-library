# Recovery Checklist

Use this checklist after `scan` or `scan-thread`.

## Provider Drift

- First determine the target provider from the user's current login/config goal.
  `--provider` means "the provider Codex Desktop should recognize now," not
  necessarily the provider that originally created the session.
- If the user is currently using official OAuth and wants old krill/custom
  sessions visible again, repair active sessions with `--provider openai`.
- If the user explicitly wants to switch back to krill, then repair with
  `--provider krill`.
- Do not edit `config.toml`, `auth.json`, cc-switch current-provider settings,
  or third-party auth tokens unless the user explicitly asks to change
  providers.
- If `threads.model_provider` differs from the target provider and rollout
  `session_meta` has the old provider, repair both together.
- Prefer the provider in `${CODEX_HOME:-$HOME/.codex}/config.toml` when the user
  does not specify one.

## Rollout Structure

- Parse errors or missing rollout files are blockers for bulk repair.
- Modern open turns have `turn_context.payload.turn_id`.
- Duplicate `turn_context` records for the same `turn_id` must be coalesced.
- Legacy `turn_context` records without `turn_id` are not safe mutation targets.
- Close stale modern turns with `turn_aborted`, not `task_complete`.
- Do not close open turns newer than 30 minutes unless the user confirms the
  continuation is stale.

## Spawn Edges

- Close stale `thread_spawn_edges` only after the child rollout has no stale
  modern open turns.
- Use the locally observed closed value: `closed`.

## Goals

- Report `active`, `blocked`, `usage_limited`, and `budget_limited` goals by
  default.
- Complete a stale goal only when it is confirmed to block restore and the
  repair command uses the explicit goal-completion flag.

## Archived Sessions

- Leave `${CODEX_HOME:-$HOME/.codex}/archived_sessions` and archived SQLite rows
  untouched unless the user explicitly asks for archived repair and the command
  includes `--include-archived`.

## Desktop Restart

- If verification is clean but Codex Desktop still shows missing threads or
  `systemError`, restart Codex Desktop so the app server reloads session state
  from disk.
- If an app thread-list tool is available, search for a known old title or id
  before restart. Seeing old local sessions in the live list confirms the repair
  is loaded even if the visible sidebar needs a refresh.
