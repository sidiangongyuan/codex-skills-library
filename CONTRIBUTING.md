# Contributing

Codex Skills Library accepts useful skills from any domain. A proposal issue is
welcome but not required; a pull request may add a skill directly.

## Add a skill

1. Copy `templates/skill` to `skills/<skill-name>`.
2. Use a lowercase kebab-case name that matches the directory.
3. Write a concise `description` that states what the skill does and when it
   should be used.
4. Add scripts, references, or assets only when they materially support the
   workflow. Keep file references relative to the skill root.
5. Add the skill to `skills.json`, including an example prompt, requirements,
   provenance, license, and any pinned upstream revision.
6. Regenerate the catalog and run the checks below.

## Provenance and licensing

- Original submissions are contributed under this repository's MIT License.
- Adapted or vendored submissions must link to a fixed upstream revision and
  include the upstream license and copyright notice inside the skill folder.
- Do not submit content when its redistribution rights are unclear.
- Do not include private conversations, unpublished project material,
  credentials, machine-specific paths, datasets, checkpoints, or generated
  artifacts that are not intended for redistribution.

## Safety and quality

- Installation must remain copy-only. Do not make an installer execute a
  contributed skill or its helper scripts.
- Destructive, publishing, or externally visible actions must require clear
  user intent and confirmation inside the skill workflow.
- Document required CLIs, runtimes, MCP servers, network access, and operating
  system constraints.
- Keep `SKILL.md` focused. Move detailed reference material to `references/`
  and deterministic helpers to `scripts/`.

## Local checks

```bash
python -m pip install -r requirements-dev.txt
python scripts/catalog.py --write
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/install.py --all --dry-run
```

Pull requests are reviewed for usefulness, clarity, provenance, safe defaults,
and maintainability. Passing automation is necessary but does not guarantee
merging.
