# Feishu Onboarding And Recovery

Use this reference when Feishu is the requested destination but no verified
write-and-read path is available. Onboarding is a delivery concern: it must not
block, erase, or weaken the literature research.

## Completion Invariant

Do not describe Feishu as `connected` merely because a package is installed, an
MCP entry exists, OAuth completed, or an authentication status command passes.
The connection is verified only when the current formal report has:

1. been created as one new Feishu document;
2. returned a stable document ID or URL;
3. been fetched again through the same user identity; and
4. passed the report readback checks in `feishu-publishing.md`.

Use `authorization_ready` for a verified login that has not yet passed document
write-and-readback. Never create a disposable test document just to claim
success; the formal report is the write-and-read test.

## Preserve The Research First

Before any installation, configuration change, authorization, callback wait, or
client restart:

- finish or checkpoint the research in the declared local working directory;
- validate the complete Markdown report when possible;
- save the absolute date window, selected paper IDs, canonical links, and
  evidence ledger beside the report;
- keep credentials, authorization URLs, and setup output out of that checkpoint;
- record enough non-secret progress to resume after a restart.

If onboarding fails or the user declines it, return the complete local report.
Never make the research depend on an OAuth session remaining alive.

## Discover Before Installing

Inspect the current tool inventory and local commands without changing state.
Prefer routes in this order:

1. an already loaded, authorized Feishu-compatible connector with both new
   document creation and document readback;
2. an existing healthy official `lark-cli` installation;
3. a fresh official `lark-cli` setup;
4. the official `lark-openapi-mcp` only as the restricted fallback described
   below.

Do not reinstall, re-register, create another Feishu app, log out, or replace a
working profile merely because its name differs from an example. A connector is
compatible only if it can create a new report and fetch it for verification.
Read-only, write-only, or bot-only access is insufficient for this workflow.

Useful read-only probes include:

```text
python "<skill-directory>/scripts/check_feishu_connection.py" --json
codex mcp list
```

The first preflight may locate and hash a PATH candidate, but it never executes
that candidate. Execute only an absolute standalone binary whose SHA-256 came
from this workflow's verified installer result. Once a profile is selected, all
CLI calls must use the same absolute binary, executable hash, named profile, and
Feishu/Lark brand. Windows `.cmd`, `.bat`, and PowerShell shims are ineligible.

`auth status` has no top-level `ok` field in current releases. Require exit code
`0`, explicit `identity == "user"`, an available and server-verified user with a
nonempty `openId`, a nonempty app ID, and the expected Feishu/Lark brand. For
`auth check`, require exit code `0`, `ok == true`, both exact scopes in
`granted`, and an empty `missing` list. Do not test for an OpenAPI-style
`code == 0`, accept generic `authenticated` fields, or relay raw diagnostics.
In the bundled preflight report, `state_recognized` means classification
succeeded, while `ok` and `authorization_ready` are true only after the strict
user-and-scope checks. `delivery_verified` remains false until formal-report
readback.

## Classify The State

| State | Reliable signal | Next action |
|---|---|---|
| Existing compatible connector | Create and read tools are loaded and authorization is valid | Keep it; publish the formal report and verify readback |
| CLI absent | `lark-cli` is not executable and no compatible connector is loaded | Ask once for the bounded setup consent, then install a checksum-verified official release |
| CLI review required | A PATH candidate exists but has not been provenance-bound | Do not execute it; use an existing verified installer receipt or install an isolated official binary |
| Profile selection required | The binary is approved but no exact profile and brand were selected | Preserve all profiles; select a compatible named profile or create one uniquely named profile under consent |
| CLI installed, unconfigured | CLI runs but reports no app/profile configuration | Run the fresh-user configuration path after consent |
| Half-configured profile | App/profile metadata exists but configuration is incomplete | Resume or repair that profile; do not run a destructive reinitialization |
| Not logged in | Configuration is valid but no user identity or token exists | Start the protected minimum-scope login helper |
| Token invalid or expired | `auth status --json --verify` reports an invalid user token | Reauthorize incrementally; do not log out first |
| Scope incomplete | `auth check` or an API error lists missing scopes | Request only the allowlisted missing scope |
| Identity confirmation required | A verified app/user fingerprint is available but not yet confirmed | Show only the safe hashes and profile/brand; confirm the intended account and tenant before publishing |
| Identity mismatch | Profile, brand, app, or user hash differs from the confirmed identity | Stop and resolve it; never silently switch profiles or accounts |
| `authorization_ready` | User identity verifies and create/read scopes are present | Publish the formal report; connection is not yet proven |
| MCP registered, not loaded | `codex mcp list` shows it but this task has no tools | Preserve the checkpoint, restart Codex or open a new task, then rediscover |
| Callback conflict | The chosen fallback callback port is already bound | Do not kill the owner; choose another supported port and match the redirect URL |
| Write outcome unknown | Create request timed out after it may have reached Feishu | Do not blindly create again; preserve the report and investigate duplicates |
| Readback failed | Create returned a document ID but fetch or content checks failed | Retry or repair readback against that same ID; do not create a duplicate |
| Connected | The formal report was written and passed readback | Return the verified URL and readback result |

## Ask For One Bounded Consent

Explicit invocation of this skill expresses intent to produce a report, but it
does not by itself authorize installing software, creating an application,
changing Codex configuration, or starting OAuth. When setup or repair changes
state, first identify the expected Feishu China or Lark international account,
tenant, and active CLI profile. Then ask one blocking question that names the
entire bounded operation:

> May I install or reuse the checksum-verified official `lark-cli` at
> `<resolved-install-path>`; create or
> repair one named local profile, using the new private dedicated directory
> `<resolved-profile-parent>` when a fresh profile is needed; create or update one developer application in
> the specified Feishu/Lark tenant; enable and, if the platform requires it,
> publish or submit that app for only document-create and document-read access;
> start browser authorization for the named user; create this one literature
> report; and read it back? This may write the named CLI binary and protected
> profile data at `<resolved-profile-location>` and may require tenant-admin
> approval. It will not edit PATH or
> Codex configuration, request delete/chat/mail/calendar/broad Drive access, or
> restart a client unless those separate changes are shown and approved.

The isolated helpers clear inherited `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`,
`NO_PROXY`, `SSL_CERT_FILE`, and `SSL_CERT_DIR` variables as well as
Lark-specific transport overrides. They never route OAuth or document content
through an ambient proxy or custom CA by default. If the environment genuinely
requires one, stop with the local report and ask for a separate network-routing
decision that identifies the non-secret proxy endpoint and certificate
fingerprint. Do not pass credential-bearing proxy URLs through chat, argv,
state, or logs, and do not weaken the default helper implicitly.

One affirmative answer covers those listed steps and their non-expansive
retries. Browser confirmation is still performed by the user. Ask again only
when the recovery would add a new permission, use a different identity, expose a
new destination folder, overwrite/update a document, install a different
connector, change PATH or Codex/MCP configuration, restart a client, perform a
tenant action not listed above, or perform a destructive action.

If a compatible connector is already healthy, do not ask an onboarding question
or touch its configuration. Follow the ordinary publishing rules.

## Existing Connector Binding

A healthy existing connector remains the preferred route, but it still needs a
restart-safe publication binding. Use its stable loaded connector/tool ID and
derive a SHA-256 fingerprint from stable, non-secret authenticated user and
tenant identity metadata. Show that identity description to the user and
confirm it is the intended account; persist only the hash. If the connector
cannot distinguish accounts or tenants, do not guess.

Prepare the checkpoint with `--delivery-route "connector"`,
`--connector-id "<stable-connector-id>"`, and
`--connector-identity-sha256 "<confirmed-identity-hash>"` as shown in
`feishu-publishing.md`. Immediately before create, re-read the connector
identity and run `begin-create` with those same three arguments. Any mismatch
stops publication. No CLI installation, profile setup, or OAuth consent is
needed for this already-authorized route.

## Fresh User: Official lark-cli

The default fresh-user route is the official
[`larksuite/cli`](https://github.com/larksuite/cli). It supports guided app
creation, user device-flow login, Docs create/fetch commands, structured JSON,
and protected credential storage. Use the bundled installer helper to fetch an
official GitHub release asset and verify the release checksum before extraction.
Inspect `--help` when a flag differs from this guide.

### 1. Preflight

- Confirm the user is using Feishu China or Lark international and keep the
  corresponding official domain throughout.
- Probe `lark-cli` before checking installation prerequisites; a healthy
  standalone binary does not require Node.js or `npx`.
- With the pinned absolute binary, read `lark-shared`, then run its current
  config/profile inspection commands. Check every existing profile before
  creating anything.
- Keep the report working directory separate from the skill and CLI
  configuration directories.

### 2. Install Once

When the command is absent, first resolve a read-only installation plan:

```text
python "<skill-directory>/scripts/install_lark_cli.py" --inspect
```

This fetches only official release metadata and `checksums.txt`; it does not
download or execute the binary, create the install directory, or edit PATH. Put
the returned exact version, asset, SHA-256, install directory, destination, and
replacement status into the bounded consent question. After consent, pin that
same plan:

```text
python "<skill-directory>/scripts/install_lark_cli.py" \
  --version "<inspected-exact-version>" \
  --expected-asset "<inspected-exact-asset>" \
  --expected-sha256 "<inspected-archive-sha256>" \
  --install-dir "<inspected-install-directory>" \
  --consent-confirmed
```

The helper must resolve `larksuite/cli` through the official GitHub API, select
the exact release asset for the current OS and architecture, download
`checksums.txt` and that asset from allowlisted HTTPS GitHub hosts, compare the
asset's SHA-256 before extraction, reject traversal/symlink/unexpected archive
members, and install one binary atomically in a user-scoped directory. It does
not edit PATH. Record the exact release tag, asset name, checksum, and installed
path, never credentials. Stop on a host, tag, checksum, archive, platform, or
overwrite mismatch.

The `--consent-confirmed` flag is an attestation that the blocking consent above
was actually obtained; never add it speculatively. If the inspected destination
already exists, do not pass `--replace` until its exact path and replacement
were included in consent and it was confirmed as the intended prior
`lark-cli`; otherwise choose a new explicit `--install-dir`. If the pinned
install no longer matches the inspected tag, asset, or checksum, stop and
inspect again. After installation, invoke the returned absolute path directly
and retain its returned `executable_sha256` as the approval binding for every
later helper call. The installer rejects a changed asset or checksum before
downloading the binary, and it never executes the installed file. Do not fall
back to a floating `npx` command or an organization npm mirror without a
separate supply-chain decision.

For an existing PATH candidate, the preflight reports its path and hash without
executing it. Reuse it only when an official installer receipt or equivalent
organization provenance binds that exact executable hash; otherwise install the
official binary into a separate user-scoped directory. Never approve a hash
merely because it was found on PATH.

After selecting a profile, resolve its exact absolute configuration directory.
For the ordinary default store this is the canonical absolute form of
`~/.lark-cli`; a fresh setup below returns dedicated config and data
directories. For an existing profile, preserve its existing protected-data
location and omit `--data-dir` unless that nondefault location is already known
and verified. Pass the same installation and configuration binding explicitly:

```text
python "<skill-directory>/scripts/check_feishu_connection.py" --json \
  --lark-cli "<absolute-lark-cli-path>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --expected-brand "<feishu-or-lark>"
```

Every later CLI example means the returned absolute executable plus
`--profile "<selected-profile>"`; never substitute a PATH lookup. Do not
persistently edit PATH just to shorten the examples.

Read `lark-shared` through the pinned absolute binary before configuration or
authentication so the installed version's setup, QR, identity, scope, and
error-envelope rules take precedence over version-sensitive examples here.

### 3. Create The Fresh Isolated Profile

Enumerate every existing profile using the pinned binary and the
version-matched commands in `lark-shared`. Reuse a compatible profile after
confirming its brand and app identity. If all existing profiles are unrelated,
preserve them and, under the bounded consent, create a fresh profile only
through the bundled helper. Never invoke `config init` directly and never run it
against the user's shared `~/.lark-cli/config.json`.

Create one absolute, current-user-private parent directory outside the report,
repository, skill, and ordinary `.lark-cli` tree. It must already exist, must not
be a symlink, junction, or reparse point, and its exact path must have appeared
in the consent. Create a new unpredictable state-file path in another private
directory, then run:

```text
python "<skill-directory>/scripts/run_feishu_config_init.py" \
  --state-file "<private-temporary-directory>/feishu-config-state.json" \
  --config-parent "<private-dedicated-profile-parent>" \
  --brand "<feishu-or-lark>" \
  --lark-cli "<absolute-lark-cli-path>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --consent-confirmed
```

`--consent-confirmed` attests that the bounded setup consent was actually
obtained. The helper generates a globally collision-resistant
`codex-paper-reading-<128-bit-random-id>` profile and atomically creates a
same-named, owner-private permanent configuration directory. Every retry gets a
new name and new directory; never rerun initialization in an existing one.

The helper sets the official `LARKSUITE_CLI_CONFIG_DIR` override to that new
directory, isolates the Linux data store under its `data` child, and uses an
environment allowlist so ambient profile, credential, proxy-auth, OpenClaw,
Hermes, or Lark-channel selectors cannot redirect setup. It rechecks the pinned
executable and directory identities immediately before launch. The blocking
child is parent-death-contained and both raw streams are consumed without being
logged or returned.

For application configuration, the helper accepts only the exact HTTPS page
`open.feishu.cn/page/cli` for Feishu or
`open.larksuite.com/page/cli` for Lark, with the exact official query shape. It
opens that ephemeral page directly in the user's default browser and emits only
`browser_opened: true`; the URL, user code, device code, App ID, App Secret, and
raw diagnostics never enter state or tool output. Keep the same helper alive
until the user completes the browser action, denies it, cancels, or it expires.
Starting another initializer can invalidate the first flow.

The initial safe event and final state contain the generated `profile`,
`config_dir`, and `data_dir`, plus non-secret directory identity hashes. Retain
those exact values. Inspect a resumed flow with:

```text
python "<skill-directory>/scripts/run_feishu_config_init.py" --status \
  --state-file "<private-temporary-directory>/feishu-config-state.json" \
  --brand "<feishu-or-lark>" \
  --profile "<generated-profile>" \
  --config-dir "<generated-config-dir>" \
  --data-dir "<generated-data-dir>" \
  --approved-executable-sha256 "<installed-executable-sha256>"
```

The helper refuses to clean a successful or materially configured directory.
After a failed terminal flow, `--cleanup` with the same binding removes only an
empty directory created by that run. Never delete a configured directory,
protected-store entry, or remote application as automatic rollback.

The official flow places the new App Secret in the CLI's protected platform
store. On Windows and macOS that protected store is OS-global rather than scoped
by the dedicated config directory; the 128-bit profile name and newly registered
App ID prevent collision, but the consent must still name this protected-store
write. Do not copy an App Secret into a report, repository, shell history,
command argument, environment file, Codex MCP configuration, or log. If
protected storage is unavailable, stop; never downgrade to plaintext silently.

If a partial existing profile is intended for this workflow, preserve and
repair it with version-matched commands instead of starting the fresh helper.
Do not change another profile's app identity, brand, tenant, strict mode, or
active selection.

From this point onward, bind every helper to `--config-dir
"<selected-config-dir>"`; for a fresh isolated route also bind the returned
`--data-dir "<selected-data-dir>"`. For every direct `lark-cli` child, use
`scripts/feishu_process_environment.py`'s
`build_isolated_cli_environment()` or reproduce that exact minimal allowlist.
Then set `LARKSUITE_CLI_CONFIG_DIR` to the selected directory and, only when the
route has an explicit data directory, set `LARKSUITE_CLI_DATA_DIR` to that
directory. Otherwise leave the data override absent so an existing profile
continues using its original platform-protected store.

Never inherit any other `LARKSUITE_CLI_*`, `OPENCLAW_*`, `HERMES_*`, or
`LARK_CHANNEL*` variable. In particular, ambient profile, app, token,
strict-mode, auth-proxy, transport-proxy, custom-CA, and workspace selectors
must not survive. The shared allowlist retains only OS/runtime essentials; it
also strips generic proxy and certificate environment overrides. Pass global
`--profile "<selected-profile>"` to auth, status, scope, create, fetch, QR, and
skill-reading commands. Use an argv-based child process with that explicit
environment, not a shell-concatenated command.

### 4. Login With Minimum Scope

For a new report plus readback, request only:

```text
docx:document:create
docx:document:readonly
```

The CLI adds the refresh capability needed by its device flow. Do not use
`--recommend`, `--domain all`, or broad Docs/Drive presets when exact scopes are
available. Do not use `--no-wait`: its structured output contains a device code
that would enter the tool transcript. Start the bundled protected helper as one
long-lived background process:

```text
python "<skill-directory>/scripts/run_feishu_auth.py" \
  --lark-cli "<absolute-lark-cli-path>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --brand "<feishu-or-lark>" \
  --state-file "<private-temporary-directory>/feishu-auth-state.json"
```

Create that temporary directory with current-user-only permissions or ACLs and
an unpredictable name. The helper requires the parent to exist and refuses to
overwrite a state file; never reuse a path from an earlier flow.

The helper owns this exact blocking child command:

```text
"<absolute-lark-cli-path>" --profile "<selected-profile>" auth login \
  --scope "docx:document:create docx:document:readonly" --json
```

The child itself holds and polls the device code in process memory. The helper
never uses a `--device-code` argument, relays raw child output, or stores a device
code, user code, token, or CLI diagnostic. It atomically writes only a
whitelisted ephemeral status file with the exact brand/profile/executable
binding. The child is placed in parent-death containment: a Windows kill-on-close
Job Object or a gated POSIX process group with a watchdog. If the helper is
forcibly terminated, the CLI is terminated too and cannot complete OAuth later
as an orphan. Poll the state file through:

```text
python "<skill-directory>/scripts/run_feishu_auth.py" --status \
  --brand "<feishu-or-lark>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --state-file "<private-temporary-directory>/feishu-auth-state.json"
```

When status is `pending`, require an HTTPS URL on exactly
`accounts.feishu.cn` for Feishu or `accounts.larksuite.com` for Lark. Show that
unaltered URL, optionally generate an ephemeral QR image with
the pinned binary and selected profile's `auth qrcode` command, and open the
same validated URL in the default browser.
The helper process must remain alive while the user acts; it will finish polling
without a later secret-bearing command. Remove the QR and run:

```text
python "<skill-directory>/scripts/run_feishu_auth.py" --cleanup \
  --brand "<feishu-or-lark>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --state-file "<private-temporary-directory>/feishu-auth-state.json"
```

after success, denial, expiry, or cancellation.
Remove the now-empty private temporary directory only if it was created by this
run.

After a Codex task restart or lost process handle, run the helper's `--status`
against the same state file before doing anything else. If it reports
`starting` or `pending` and the recorded process is live and unexpired, keep
polling that flow; do not start a concurrent login. Start a fresh flow only
after status is terminal, expired, or reports that the recorded process is no
longer running, then clean the old state. Never reconstruct a code or ask the
user to paste one. Use `--domain docs` only after a new permission decision when
the installed CLI cannot resolve the two exact scopes and the expanded scope
list contains no unrelated document management.

### 5. Verify Readiness

Run the bundled preflight with the same binary, profile, and brand:

```text
python "<skill-directory>/scripts/check_feishu_connection.py" --json \
  --lark-cli "<absolute-lark-cli-path>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --expected-brand "<feishu-or-lark>"
```

Require the strict fields listed in `Discover Before Installing`, both exact
scopes, and the expected brand/profile/app identity. The first successful
identity probe returns only SHA-256 fingerprints and
`identity_confirmation_required`. Show those safe hashes with the chosen
profile and brand, confirm they belong to the intended account and tenant, then
rerun with:

```text
--expected-app-id-sha256 "<confirmed-app-hash>" \
--expected-user-open-id-sha256 "<confirmed-user-hash>"
```

Persist these non-secret bindings in the delivery checkpoint and pass the same
profile to create and fetch. Any later mismatch stops the workflow; never
silently switch. Only the second matching preflight is
`authorization_ready`, and delivery is still unverified.

### 6. Publish The Formal Report And Read It Back

Before the first create request, assign a durable run ID and content digest with
the bundled checkpoint helper:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" prepare \
  --report "report.md" \
  --title "<report title>" \
  --state ".feishu-publication.json" \
  --payload ".feishu-publication.md" \
  --delivery-route "lark-cli" \
  --lark-cli "<absolute-lark-cli-path>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --brand "<feishu-or-lark>" \
  --app-id-sha256 "<confirmed-app-hash>" \
  --user-open-id-sha256 "<confirmed-user-hash>"
```

The helper refuses to overwrite an existing run, writes atomically, and appends
a visible provenance footer containing the run ID and source digest to the
publication payload. It also binds the run to the verified executable, profile,
brand, app, and user hashes. Keep this credential-free state beside the report.
A resumed task must inspect it and rerun the strict preflight before any create.

Before choosing flags or formatting content, read the version-matched official
guidance shipped with the installed CLI:

```text
"<absolute-lark-cli-path>" --profile "<selected-profile>" skills read lark-doc
"<absolute-lark-cli-path>" --profile "<selected-profile>" skills read lark-doc references/lark-doc-create.md
"<absolute-lark-cli-path>" --profile "<selected-profile>" skills read lark-doc references/lark-doc-md.md
"<absolute-lark-cli-path>" --profile "<selected-profile>" skills read lark-doc references/style/lark-doc-style.md
"<absolute-lark-cli-path>" --profile "<selected-profile>" skills read lark-doc references/style/lark-doc-create-workflow.md
```

Treat those installed instructions and the pinned profile's
`docs +create --help` as authoritative. If they conflict with an example below,
adapt the flags without expanding permissions or changing the safety rules.

Validate the payload path, chosen input form, arguments, and CLI help before
changing the checkpoint. Immediately before dispatching the one remote create,
atomically record the write-ahead transition:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" begin-create \
  --state ".feishu-publication.json" \
  --delivery-route "lark-cli" \
  --lark-cli "<absolute-lark-cli-path>" \
  --approved-executable-sha256 "<installed-executable-sha256>" \
  --profile "<selected-profile>" \
  --config-dir "<selected-config-dir>" \
  --data-dir "<selected-data-dir>" \
  --brand "<feishu-or-lark>" \
  --app-id-sha256 "<confirmed-app-hash>" \
  --user-open-id-sha256 "<confirmed-user-hash>"
```

`begin-create` re-hashes the executable and publication payload and compares
every identity binding before changing state. Only after it succeeds, pass the
generated publication payload as UTF-8 stdin
or a declared relative file using an argv-based process call, not
shell-concatenated user text. Run from the declared working directory and use
the already bound profile:

```text
"<absolute-lark-cli-path>" --profile "<selected-profile>" docs +create --as user --doc-format markdown --title "<report title>" --content - --format json
"<absolute-lark-cli-path>" --profile "<selected-profile>" docs +create --as user --doc-format markdown --title "<report title>" --content "@.feishu-publication.md" --format json
```

Choose one input form, not both. For a report too large for one create request,
split only at heading boundaries and preserve order. If continuing the same
document requires `docs +update`, include
`docx:document:write_only` in the one initial consent and authorization when the
size risk is known before setup. If it was not included, pause for a new
permission decision rather than silently broadening access.

Capture `data.document.document_id` and `data.document.url` only when
`ok == true`, then atomically record them before any fetch or other remote
operation:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" record-created \
  --state ".feishu-publication.json" \
  --document-id "<returned-document-id>" \
  --document-url "<returned-document-url>"
```

The document ID is the durable key. If the returned URL has an unfamiliar but
otherwise harmless presentation format, omit `--document-url` and record the ID
immediately rather than delaying the checkpoint. Never persist a URL containing
a query, fragment, credential, userinfo, or nonstandard port.

Fetch that exact returned document:

```text
"<absolute-lark-cli-path>" --profile "<selected-profile>" docs +fetch --as user --doc "<returned ID>" --doc-format markdown --format json
```

Then apply all readback checks from `feishu-publishing.md`. Only now mark the
route `connected` and run:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" record-verified \
  --state ".feishu-publication.json"
```

Do not overwrite or delete the document during verification. If create times
out, loses its connection, or is interrupted after the request may have reached
Feishu and no ID was returned, use exactly one safe reason:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" mark-unknown \
  --state ".feishu-publication.json" \
  --reason "timeout_after_send"
```

Do not send another create in the same or a later task. The user must check
recent documents for the recorded title, run ID, and digest and explicitly
confirm no matching document exists. Only then unlock one retry:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" confirm-no-match-and-retry \
  --state ".feishu-publication.json" \
  --user-confirmed-no-match
```

If a local argument, payload, preflight, or launch failure is proven to have
occurred before any HTTP request could be sent, use the distinct audited
transition and then repair:

```text
python "<skill-directory>/scripts/publication_checkpoint.py" abort-before-send \
  --state ".feishu-publication.json" \
  --reason "local_argument_validation_failed"
```

Never use `abort-before-send` when network transmission is possible; mark that
case unknown instead. Each retry requires another successful `begin-create`.

## Restricted Fallback: lark-openapi-mcp

Use the official
[`larksuite/lark-openapi-mcp`](https://github.com/larksuite/lark-openapi-mcp)
only when direct `lark-cli` use is unavailable, a compatible MCP route is
required, and the user has agreed to this different setup. It is currently
Beta, its OAuth mode is Beta, and its documented document support is narrower
than `lark-cli`; direct document editing is not supported, while import and read
are available.

Apply all of these restrictions:

- first reuse an existing healthy registration; never add a duplicate server;
- expose only the exact import/create and read tools needed for the report,
  using the current tool allowlist rather than default broad presets;
- use user identity and explicit `user_access_token` mode for user-owned
  documents;
- do not place an App Secret literally in MCP arguments, JSON/TOML config, a
  repository, or a persistent environment variable;
- proceed only when an existing organization-approved secret injector or
  OS-keychain wrapper can supply the secret without printing it; otherwise keep
  the Markdown fallback;
- verify the exact package version and current flags because Beta behavior can
  change.

Its local OAuth callback defaults to `localhost:3000`. Before login, verify the
port is free. If it is occupied, identify the owner read-only and either choose
a free supported port with `--port` or use `lark-cli`; never terminate an
unknown process. The Feishu developer-console redirect URL must exactly match
the chosen host, port, and `/callback` path. Bind only to loopback and stop the
temporary callback listener after success, denial, timeout, or error.

Adding or changing an MCP server may require a Codex restart or a new task before
tools appear. Back up the non-secret MCP configuration, add one uniquely named
entry, confirm it with `codex mcp list`, preserve the research checkpoint, and
restart once. A listed server with no loaded tools is `registered, not loaded`,
not connected.

## Recovery Matrix

| Symptom | Recovery |
|---|---|
| Release installer cannot reach GitHub | Preserve the report and retry once after connectivity recovers; do not switch registries or execute an unverified package |
| Platform or architecture unsupported | Stop with the Markdown report and link the official release page; do not guess an asset |
| Install succeeded, command missing | Use the absolute destination and executable hash returned by the installer; do not search PATH or reinstall in a loop |
| Existing profile is partial | Preserve it, inspect non-secret status, and resume the missing stage; do not clear profiles or keychain entries |
| Configuration URL expired | Let the original process exit, discard the URL, and start one new initializer |
| User denied/cancelled | Stop setup, preserve the local report, and return the Markdown fallback without pressure |
| Device authorization expired | Let the protected helper exit, clean its ephemeral status/QR files, then start one fresh blocking flow |
| Token expired or refresh failed | Run status verification, then repeat minimum-scope login; do not log out or delete credentials first |
| Missing user scope | Parse `error.missing_scopes`; request only `docx:document:create` and/or `docx:document:readonly` under the existing consent |
| Missing app scope or unpublished app | Relay the exact official `console_url`; enable/publish/approve only if that remote tenant action was named in consent, otherwise ask again; then reauthorize incrementally |
| Wrong identity | Stop; do not silently switch between bot and user. This workflow requires user identity unless the user explicitly chooses otherwise |
| Wrong Feishu/Lark domain | Keep the local report, repair the profile/domain deliberately, and never send credentials across platform domains |
| Callback port occupied | Do not kill the owner; select another supported loopback port and update the redirect exactly, or return to device-flow CLI |
| MCP listed but tools absent | Do not duplicate the entry; restart/open a new task and rediscover tools |
| HTTP 401 | Verify the token and reauthorize minimum scopes, then retry the same read or a not-yet-sent write |
| HTTP 403 | Distinguish missing scope, app publication, document ownership, and folder access; change only the cause named by primary diagnostics |
| HTTP 429 | Honor `Retry-After`; otherwise use bounded exponential backoff with jitter. Do not create concurrent duplicate reports |
| Local failure proven before send | Run `abort-before-send` with the matching fixed reason, repair locally, then run `begin-create` again |
| Network failure before send | Use `abort-before-send` only when the CLI proves no request was emitted; otherwise treat the outcome as ambiguous |
| Timeout after create may have been sent | Atomically mark `outcome_unknown`; use the returned ID if any, otherwise require user reconciliation by recorded title/run ID/digest and `confirm-no-match-and-retry` before one retry |
| Create returned an ID but fetch failed | Retry fetch against the same ID after token/scope repair; never create a second report as a readback workaround |
| Readback is truncated or missing sections | Keep the returned URL, mark verification failed, and do not claim connected. Obtain permission before creating or updating a replacement |
| JSON is malformed or mixed with notices | Use exit code and the documented `ok` envelope; suppress update notices when supported, but retain the raw redacted diagnostic |
| CLI/MCP version drift | Inspect the installed version and official `--help`; update only after consent and do not loosen permissions to work around incompatibility |

Bound retries: one repair attempt for deterministic configuration errors and at
most three delayed attempts for explicit transient throttling. Repeated failure
must end in a preserved local report and an exact blocker, not a reinstall loop.

## Rollback And Resume

- Stop only callback listeners and background setup processes started by the
  current run.
- Remove ephemeral QR files after use; never retain authorization material.
- Remove the protected auth helper's ephemeral status file after its process
  reaches a terminal state. It may contain only the current validated URL, never
  a code or token.
- Keep a successful configuration helper state with its permanent config/data
  bindings until they have been transferred to the resumable delivery
  checkpoint. Its state never contains the setup URL or a raw identifier. On a
  failed run, use its bound cleanup only when the generated directories are
  empty.
- Never delete an existing profile, token, app, connector, document, or Feishu
  authorization as automatic rollback.
- If this run added an MCP entry and it must be reverted, show the exact entry
  and remove only that entry after explicit approval; restore the prior
  non-secret configuration snapshot.
- Do not uninstall `lark-cli` merely because authorization was declined. Treat
  installation removal as a separate request.
- Do not revoke an app or its scopes automatically; it may be shared with other
  workflows.
- Preserve the validated report and evidence checkpoint until successful
  readback or an explicit retention decision.
- After a required restart, resume from the saved report, rediscover the route,
  inspect the config/auth helper states and `.feishu-publication.json`, and re-check the
  pinned binary hash, profile, identity hashes, and scopes. Continue polling a
  live unexpired auth helper. Reuse a recorded document ID for fetch; do not
  create when publication state is `create_in_flight`, `created`, `verified`, or
  `outcome_unknown`. A stale in-flight state requires proof of no send plus
  `abort-before-send`, or ambiguous-outcome reconciliation; never edit the JSON
  manually. Do not repeat literature collection unless the user asks for a
  refreshed date window.

## Security Boundaries

Never ask the user for, display, persist, or place in report/checkpoint/chat
output:

- a Feishu/Lark password or browser cookie;
- an App Secret;
- access or refresh tokens;
- a device code;
- a previously issued authorization URL or QR payload.

The agent must not call the split device-code flow. The configuration helper
opens its validated setup URL directly and never exposes it to tool output or
state. The later authorization helper keeps the code inside the long-lived
`lark-cli` child and exposes only the current validated authorization URL. Show
that URL only for the required user action, then let it expire naturally and
clean its ephemeral state. Do not
broaden permissions to diagnose a failure. Do not expose delete, owner-transfer,
broad Drive management, IM, Mail, Calendar, or organization-administration
tools for this workflow.

## Official Sources

- Official lark-cli repository and current quick start:
  <https://github.com/larksuite/cli>
- Official Feishu one-click application creation:
  <https://open.feishu.cn/document/mcp_open_tools/integrating-agents-with-feishu/scan-to-create-an-app-in-one-click-nodejs>
- Official Feishu user OAuth guide:
  <https://open.feishu.cn/document/sso/web-application-end-user-consent/guide?lang=zh-CN>
- Official Feishu document creation API:
  <https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/create?lang=zh-CN>
- Official lark-openapi-mcp repository and Beta notice:
  <https://github.com/larksuite/lark-openapi-mcp>
