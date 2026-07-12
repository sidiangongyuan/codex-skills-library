# Living To Tell Casebook

These are anonymized implementation lessons from a desktop writing app. Use
them as diagnostic patterns, not as project-specific requirements.

## Startup Feedback

Problem: an HTML startup shell still allowed several seconds of black window
because the blank period happened before the WebView loaded the HTML.

Pattern: move visible feedback earlier in the stack. For a Tauri-like desktop
app, show a lightweight splash or native window immediately, set a light window
background, keep main WebView hidden until ready, and log startup milestones.

## Frontend/Backend Version Mismatch

Problem: new frontend UI called new backend endpoints, but an old sidecar
process remained alive. The UI displayed raw `Not Found`.

Pattern: add a capabilities/version endpoint, clean up old sidecar processes
before starting a new one, make installers fail instead of half-updating, and
translate missing capability into a clear reinstall/restart message.

## Stale Selection Races

Problem: quickly switching articles left old note/collection/motif requests in
flight. Late 404 responses polluted the current article page.

Pattern: token every selection-scoped request with the selected id. On response,
error, and finally blocks, verify the token and selected id still match before
writing state.

## AI Provider Transport

Problem: a Gemini-labeled configuration used a relay key and custom base URL.
Native Gemini wire protocol returned provider HTML 403, while CLI usage worked.

Pattern: keep the provider name user-friendly, but choose wire protocol from
key shape and base URL. Share that transport across polish, chat, card
generation, and connection tests.

## Real AI Testing

Problem: "test connection" only checked local configuration and gave confidence
that the provider worked.

Pattern: split local config checks from real test requests. A real test sends a
minimal prompt and reports provider, model, transport, duration, and a short
sample without exposing secrets.

## Data Location Safety

Problem: uninstall copy suggested deleting app data, creating fear that writing
content would be erased.

Pattern: hide destructive uninstall data cleanup for public builds, show actual
data paths in settings, support copy migration to a new directory, keep the old
directory intact, and restart after switching.

## Motif / Excerpt Deduplication

Problem: text anchors moved after edits, so the same sentence could be attached
to the same motif repeatedly. Removing one motif link could remove shared text
from other motifs.

Pattern: resolve excerpts by exact range, current parsed position, text with
context, then unique text fallback. Merge duplicates within the same source
only, and unlink a motif from an excerpt before deleting an orphan excerpt.

## AI Profile Selection

Problem: a multi-model comparison UI showed several selected profiles, but the
default profile was still sent implicitly and produced an unexpected extra
result.

Pattern: treat the default profile as a normal selectable item. If the user
selects explicit alternatives, send exactly that snapshot and render results
from that snapshot only.

## Profile-Owned Credentials

Problem: two relay models used the same provider type but different local API
keys. Saving one key made the other profile's credential source disappear from
the UI.

Pattern: generate or reuse a profile-owned local environment reference, keep it
visible in credential choices, and never overwrite another profile's source.

## AI Long Job Recovery

Problem: a long AI enrichment request blocked an unclosable dialog. When the
local request timed out, the upstream service may already have consumed tokens
and the user lost the result path.

Pattern: create an in-process job before sending the provider request. Let the
dialog close, poll job status, show honest stages, reconnect without resending,
and explain that local cancellation cannot guarantee remote billing stops.

## AI Result Visibility

Problem: a "back" action hid generated AI results, making users think the
output disappeared.

Pattern: keep results visible until the user explicitly clears, replaces, or
starts a new run. Use precise action labels for destructive or hiding behavior.

## Release Asset Verification

Problem: a release command uploaded installer assets, but the only proof was
local command success.

Pattern: inspect the GitHub Release asset list, compare remote asset sizes,
download the assets back, and verify SHA256 before saying the release is live.

## Release Retention

Problem: many historical release records made the GitHub Releases page noisy.

Pattern: when asked to prune, keep the newest agreed count of release records
by published order, delete older release records only, and do not delete tags
unless explicitly requested.
