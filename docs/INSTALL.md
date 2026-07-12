# Installation

Codex Skills Library supports two installation paths:

- use Codex's `$skill-installer` for one skill; or
- clone the repository and use its Python installer for selected or bulk
  installation.

Install complete skill directories, not only `SKILL.md`. A skill may include
scripts, references, UI metadata, assets, and a license that must travel with
it.

## Install one skill with Codex

The `$skill-installer` system skill accepts a GitHub directory URL:

```text
$skill-installer Install https://github.com/sidiangongyuan/codex-skills-library/tree/main/skills/grill-me
```

Change the final path segment to any name in the
[skill catalog](SKILL_CATALOG.md). The installed skill is available on the next
turn. `$skill-installer` chooses the destination configured for the current
Codex environment and aborts when that skill directory already exists.

For a private fork, make sure the machine already has GitHub access through Git
credentials or `GITHUB_TOKEN`/`GH_TOKEN`, then provide the private repository's
tree URL in the same form. `$skill-installer` first tries a direct download and
can fall back to a sparse Git checkout.

## Install several skills

### Prerequisites

- Git for cloning the repository.
- Python 3.10 or newer, available as `python` (or `py -3` on Windows).
- No Python package installation is needed for the installer.

Clone the public repository:

```bash
git clone https://github.com/sidiangongyuan/codex-skills-library.git
cd codex-skills-library
```

Inspect the catalog and usage. This command does not write files:

```bash
python scripts/install.py
```

Preview an explicit bulk installation, then run it:

```bash
python scripts/install.py --all --dry-run
python scripts/install.py --all
```

The default destination is the cross-agent user directory:

```text
$HOME/.agents/skills
```

On Windows this normally resolves to
`%USERPROFILE%\.agents\skills`. Start a new Codex turn after installation; if
the client still shows an old skill list, reopen the task or restart Codex.

## Install selected skills

Repeat `--skill` for each selection:

```bash
python scripts/install.py \
  --skill experiment-planner \
  --skill research-evidence \
  --skill paper-section-playbook \
  --dry-run

python scripts/install.py \
  --skill experiment-planner \
  --skill research-evidence \
  --skill paper-section-playbook
```

PowerShell accepts the same arguments on one line:

```powershell
python scripts/install.py --skill experiment-planner --skill research-evidence --skill paper-section-playbook --dry-run
python scripts/install.py --skill experiment-planner --skill research-evidence --skill paper-section-playbook
```

Use exact catalog names. If any requested name is unknown or any source
directory is invalid, the installer exits with a nonzero status before copying
the selection.

## Choose another destination

`--target` names the directory that will directly contain the skill folders:

```bash
python scripts/install.py --skill search-first --target /path/to/shared/skills --dry-run
python scripts/install.py --skill search-first --target /path/to/shared/skills
```

```powershell
python scripts/install.py --skill search-first --target D:\Codex\shared-skills --dry-run
python scripts/install.py --skill search-first --target D:\Codex\shared-skills
```

The legacy option `--codex-home <directory>` remains temporarily available.
It treats the value as a Codex home and targets its `skills` child directory,
while printing a migration warning. New commands should use `--target` with
the final skills directory instead.

## Existing skills and replacement

An existing destination is skipped by default. Preview before replacing it:

```bash
python scripts/install.py --skill ui-ux-pro-max --replace --dry-run
python scripts/install.py --skill ui-ux-pro-max --replace
```

Replacement is restricted to an exact skill-name child of the selected target
directory. The installer removes a matching ordinary directory without
traversing above the target root. If the matching entry is a symbolic link, it
unlinks the link rather than following and deleting its external destination.

`--dry-run` does not create the target directory, copy skills, remove existing
entries, or execute helper scripts.

## Command reference

| Command or option | Behavior |
|---|---|
| `python scripts/install.py` | Print the catalog and usage; make no changes. |
| `--list` | List catalog entries and installation status. |
| `--skill NAME` | Select one skill; repeat for multiple skills. |
| `--all` | Explicitly select every cataloged skill. |
| `--target PATH` | Install directly under `PATH`. |
| `--dry-run` | Validate and report planned actions without writing. |
| `--replace` | Replace exact-name destinations after validation. |
| `--codex-home PATH` | Deprecated compatibility option targeting `PATH/skills`. |

`--skill` and `--all` are selection modes; do not combine them. Run `--list`
or open the [full catalog](SKILL_CATALOG.md) before deciding what to install.

## Manual copy

Use manual copying only when Python is unavailable. Copy the entire directory
and preserve its files:

```bash
mkdir -p "$HOME/.agents/skills"
cp -R skills/research-evidence "$HOME/.agents/skills/"
```

```powershell
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse skills\research-evidence "$HOME\.agents\skills\"
```

Confirm that both the skill instructions and license arrived:

```powershell
Get-ChildItem "$HOME\.agents\skills\research-evidence" -Force
```

## Troubleshooting

| Symptom | Resolution |
|---|---|
| `Unknown skill` | Run `python scripts/install.py --list` and use the exact name. |
| An existing skill is skipped | Inspect the destination, run `--replace --dry-run`, then repeat with `--replace`. |
| The target path is wrong | Pass the final skill-container directory with `--target`. |
| A skill is installed but not selected | Invoke it explicitly as `$skill-name`; reopen the task or restart Codex if discovery is stale. |
| A helper command is unavailable | Check that skill's `requirements` in the full catalog and install the external dependency separately. |
| GitHub returns `Repository not found` | Check the URL; for a private fork, confirm Git or token-based access. |

Before using a skill with credentials, unpublished material, publishing
permissions, or destructive tools, review its files, its catalog requirements,
and the provenance notes in [NOTICE.md](../NOTICE.md).
