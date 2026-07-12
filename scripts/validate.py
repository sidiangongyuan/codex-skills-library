#!/usr/bin/env python3
"""Validate the skill catalog, metadata, provenance, and repository links."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import unquote, urlsplit

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by the direct CLI message
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TAG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
ALLOWED_PROVENANCE = {
    "original",
    "adapter",
    "third-party-adapted",
    "third-party-exact",
}
REQUIRED_FIELDS = {
    "name",
    "category",
    "description",
    "path",
    "example_prompt",
    "tags",
    "requirements",
    "provenance",
    "source_url",
    "source_revision",
    "license_spdx",
    "notice_path",
}
KNOWN_PINS = {
    "grill-me": "62f43a18177be6ec82da242e59ffbc490a4c22ea",
    "search-first": "99baa8250096f2d295583572399a5c9aba2ce312",
    "ui-ux-pro-max": "232f201dfa3ec3d74af5dff80ec61eb8144c7507",
    "rebuttal-response-skills": "e5132630e26e26e24d256a149b85f17b0cc6dcac",
    "paper-framework-figure-studio-pro": "426d74b18852aaf8e4307997ff47b8c3b6089f14",
}
PUBLIC_WORDING_PATTERNS = {
    "legacy Vault brand": re.compile(r"codex(?:-|\s+)skills(?:-|\s+)vault", re.IGNORECASE),
    "private-vault wording": re.compile(
        r"\b(?:my|this|our) private vault\b|\bkeep private\b|\blocal vault\b",
        re.IGNORECASE,
    ),
    "personal Windows path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    "personal macOS path": re.compile(r"/Users/[^/\s]+/"),
    "legacy installed-skill path": re.compile(
        r"(?:\$HOME|~)/\.codex/skills(?:/|\b)", re.IGNORECASE
    ),
}


def _read_json(path: Path, errors: list[str]) -> dict[str, object] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing catalog: {path.name}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(
            f"{path.name}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        )
        return None
    if not isinstance(value, dict):
        errors.append(f"{path.name}: root must be an object")
        return None
    return value


def _safe_yaml(text: str, source: str, errors: list[str]) -> object:
    if yaml is None:
        errors.append("PyYAML is required for validation; install requirements-dev.txt")
        return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        errors.append(f"{source}: invalid YAML: {exc}")
        return None


def _front_matter(path: Path, root: Path, errors: list[str]) -> dict[str, object] | None:
    label = path.relative_to(root).as_posix()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        errors.append(f"{label}: cannot read: {exc}")
        return None
    if not lines or lines[0].strip() != "---":
        errors.append(f"{label}: missing opening YAML front matter delimiter")
        return None
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        errors.append(f"{label}: missing closing YAML front matter delimiter")
        return None
    value = _safe_yaml("\n".join(lines[1:end]), label, errors)
    if value is None:
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: front matter must be a mapping")
        return None
    return value


def _is_string_list(value: object, *, nonempty: bool) -> bool:
    return (
        isinstance(value, list)
        and (bool(value) or not nonempty)
        and all(isinstance(item, str) and bool(item.strip()) for item in value)
    )


def _validate_catalog_item(
    item: object,
    index: int,
    root: Path,
    notice_texts: dict[Path, str],
    errors: list[str],
) -> tuple[str | None, str | None]:
    prefix = f"skills.json: skills[{index}]"
    if not isinstance(item, dict):
        errors.append(f"{prefix} must be an object")
        return None, None

    missing = sorted(REQUIRED_FIELDS - set(item))
    if missing:
        errors.append(f"{prefix} missing fields: {', '.join(missing)}")
    if "install_default" in item:
        errors.append(f"{prefix} uses removed field install_default")
    if missing:
        return None, None

    name = item["name"]
    path_value = item["path"]
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f"{prefix}.name must be a lowercase hyphenated name of at most 64 chars")
        return None, None
    if not isinstance(path_value, str) or path_value != f"skills/{name}":
        errors.append(f"{prefix}.path must be exactly skills/{name}")
        return name, None

    for field in ("category", "description", "example_prompt", "provenance", "source_url", "source_revision", "license_spdx", "notice_path"):
        if not isinstance(item[field], str):
            errors.append(f"{prefix}.{field} must be a string")
    description = item["description"]
    if isinstance(description, str) and not (1 <= len(description) <= 350):
        errors.append(f"{prefix}.description must contain 1-350 characters")
    if isinstance(item["category"], str) and not item["category"].strip():
        errors.append(f"{prefix}.category must not be empty")
    if isinstance(item["example_prompt"], str) and f"${name}" not in item["example_prompt"]:
        errors.append(f"{prefix}.example_prompt must invoke ${name}")

    tags = item["tags"]
    if not _is_string_list(tags, nonempty=True):
        errors.append(f"{prefix}.tags must be a non-empty string array")
    elif any(not TAG_RE.fullmatch(tag) for tag in tags):
        errors.append(f"{prefix}.tags must contain lowercase hyphenated tags")
    elif len(set(tags)) != len(tags):
        errors.append(f"{prefix}.tags contains duplicates")
    if not _is_string_list(item["requirements"], nonempty=False):
        errors.append(f"{prefix}.requirements must be a string array")

    provenance = item["provenance"]
    if isinstance(provenance, str) and provenance not in ALLOWED_PROVENANCE:
        errors.append(f"{prefix}.provenance must be one of {sorted(ALLOWED_PROVENANCE)}")
    source_url = item["source_url"]
    revision = item["source_revision"]
    if provenance == "original":
        if source_url or revision:
            errors.append(f"{prefix}: original skills must leave source_url and source_revision empty")
    elif isinstance(source_url, str) and isinstance(revision, str):
        if not source_url:
            errors.append(f"{prefix}: non-original skills require a source_url or local source map")
        elif source_url.startswith(("https://", "http://")):
            if not REVISION_RE.fullmatch(revision):
                errors.append(f"{prefix}: external sources require a 40-character source_revision")
            elif revision not in source_url:
                errors.append(f"{prefix}: source_url must include its pinned revision")
        else:
            if revision:
                errors.append(f"{prefix}: local source maps must leave source_revision empty")
            local_source = (root / source_url).resolve(strict=False)
            try:
                local_source.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{prefix}: source_url escapes the repository: {source_url}")
            else:
                if not local_source.is_file():
                    errors.append(f"{prefix}: local source_url does not exist: {source_url}")

    expected_pin = KNOWN_PINS.get(name)
    if expected_pin and revision != expected_pin:
        errors.append(f"{prefix}.source_revision must remain pinned to {expected_pin}")

    if item["license_spdx"] != "MIT":
        errors.append(f"{prefix}.license_spdx must be MIT for the distributed local skill")
    notice_path_value = item["notice_path"]
    if isinstance(notice_path_value, str):
        notice_path = (root / notice_path_value).resolve(strict=False)
        try:
            notice_path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{prefix}.notice_path escapes the repository")
        else:
            if not notice_path.is_file():
                errors.append(f"{prefix}.notice_path does not exist: {notice_path_value}")
            else:
                text = notice_texts.setdefault(
                    notice_path, notice_path.read_text(encoding="utf-8")
                )
                if provenance != "original" and name not in text:
                    errors.append(f"{prefix}: {notice_path_value} does not mention {name}")

    return name, path_value


def _validate_skill_files(
    root: Path,
    name: str,
    relative_path: str,
    license_spdx: str,
    errors: list[str],
) -> None:
    skill_dir = root / relative_path
    if not skill_dir.is_dir():
        errors.append(f"{relative_path}: skill directory does not exist")
        return

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        errors.append(f"{relative_path}: missing SKILL.md")
    else:
        metadata = _front_matter(skill_file, root, errors)
        if metadata is not None:
            if metadata.get("name") != name:
                errors.append(f"{relative_path}/SKILL.md: front matter name must be {name}")
            description = metadata.get("description")
            if not isinstance(description, str) or not (1 <= len(description) <= 350):
                errors.append(
                    f"{relative_path}/SKILL.md: description must contain 1-350 characters"
                )
            if metadata.get("license") != license_spdx:
                errors.append(
                    f"{relative_path}/SKILL.md: license must be {license_spdx}"
                )

    license_files = [skill_dir / "LICENSE", skill_dir / "LICENSE.md"]
    if not any(path.is_file() for path in license_files):
        errors.append(f"{relative_path}: missing standalone LICENSE or LICENSE.md")

    agent_path = skill_dir / "agents" / "openai.yaml"
    if not agent_path.is_file():
        errors.append(f"{relative_path}: missing agents/openai.yaml")
        return
    value = _safe_yaml(
        agent_path.read_text(encoding="utf-8"),
        agent_path.relative_to(root).as_posix(),
        errors,
    )
    if not isinstance(value, dict):
        errors.append(f"{relative_path}/agents/openai.yaml: root must be a mapping")
        return
    interface = value.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{relative_path}/agents/openai.yaml: missing interface mapping")
    else:
        for field in ("display_name", "short_description", "default_prompt"):
            field_value = interface.get(field)
            if not isinstance(field_value, str) or not field_value.strip():
                errors.append(
                    f"{relative_path}/agents/openai.yaml: interface.{field} must be non-empty"
                )
        short_description = interface.get("short_description")
        if isinstance(short_description, str) and len(short_description) > 100:
            errors.append(
                f"{relative_path}/agents/openai.yaml: short_description exceeds 100 characters"
            )
        default_prompt = interface.get("default_prompt")
        if isinstance(default_prompt, str) and f"${name}" not in default_prompt:
            errors.append(
                f"{relative_path}/agents/openai.yaml: default_prompt must invoke ${name}"
            )
    policy = value.get("policy")
    if not isinstance(policy, dict) or policy.get("allow_implicit_invocation") is not True:
        errors.append(
            f"{relative_path}/agents/openai.yaml: policy.allow_implicit_invocation must be true"
        )


def _markdown_files(root: Path) -> Iterable[Path]:
    for pattern in (
        "README*.md",
        "NOTICE.md",
        "CONTRIBUTING.md",
        "docs/**/*.md",
        "skills/**/*.md",
        ".github/**/*.md",
    ):
        yield from root.glob(pattern)


def _link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    # Markdown titles follow the URL after whitespace. Repository paths with
    # spaces should use angle brackets, so splitting here is unambiguous.
    return target.split(maxsplit=1)[0] if target else ""


def _validate_links(root: Path, errors: list[str]) -> None:
    root_resolved = root.resolve()
    seen: set[Path] = set()
    for path in _markdown_files(root):
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root).as_posix()}: cannot read links: {exc}")
            continue
        for match in MARKDOWN_LINK_RE.finditer(text):
            raw = _link_target(match.group(1))
            if not raw or raw.startswith("#"):
                continue
            parsed = urlsplit(raw)
            if parsed.scheme or parsed.netloc:
                continue
            local = unquote(parsed.path)
            if not local:
                continue
            candidate = (path.parent / local).resolve(strict=False)
            try:
                candidate.relative_to(root_resolved)
            except ValueError:
                errors.append(
                    f"{path.relative_to(root).as_posix()}: link escapes repository: {raw}"
                )
                continue
            if not candidate.exists():
                errors.append(
                    f"{path.relative_to(root).as_posix()}: broken relative link: {raw}"
                )


def _public_text_files(root: Path) -> Iterable[Path]:
    for path in root.glob("README*.md"):
        yield path
    for name in ("NOTICE.md", "CONTRIBUTING.md", "skills.json"):
        path = root / name
        if path.exists():
            yield path
    for base in (root / "docs", root / "scripts", root / "skills"):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml"}:
                if path.resolve() == Path(__file__).resolve():
                    # The validator necessarily contains the regression patterns.
                    continue
                if "github-project-release" in path.parts:
                    # This skill intentionally supports private staging repositories.
                    continue
                yield path


def _validate_public_wording(root: Path, errors: list[str]) -> None:
    seen: set[Path] = set()
    for path in _public_text_files(root):
        if path in seen:
            continue
        seen.add(path)
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for label, pattern in PUBLIC_WORDING_PATTERNS.items():
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{path.relative_to(root).as_posix()}:{line}: {label}: {match.group(0)!r}"
                )


def validate_repository(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    document = _read_json(root / "skills.json", errors)
    if document is None:
        return errors
    if document.get("schema_version") != 2:
        errors.append("skills.json: schema_version must be integer 2")
    if document.get("repository") != "sidiangongyuan/codex-skills-library":
        errors.append(
            "skills.json: repository must be sidiangongyuan/codex-skills-library"
        )
    if "install_default" in document:
        errors.append("skills.json: removed field install_default is not allowed")
    skills = document.get("skills")
    if not isinstance(skills, list):
        errors.append("skills.json: skills must be an array")
        return errors

    names: list[str] = []
    paths: list[str] = []
    valid_items: list[tuple[dict[str, object], str, str]] = []
    notices: dict[Path, str] = {}
    for index, item in enumerate(skills):
        name, path = _validate_catalog_item(item, index, root, notices, errors)
        if name is not None:
            names.append(name)
        if path is not None:
            paths.append(path)
        if isinstance(item, dict) and name is not None and path is not None:
            valid_items.append((item, name, path))

    for duplicate in sorted({name for name in names if names.count(name) > 1}):
        errors.append(f"skills.json: duplicate skill name: {duplicate}")
    for duplicate in sorted({path for path in paths if paths.count(path) > 1}):
        errors.append(f"skills.json: duplicate skill path: {duplicate}")

    skills_root = root / "skills"
    actual = {path.name for path in skills_root.iterdir() if path.is_dir()} if skills_root.is_dir() else set()
    declared = set(names)
    for name in sorted(actual - declared):
        errors.append(f"skills/{name}: directory is not declared in skills.json")
    for name in sorted(declared - actual):
        errors.append(f"skills.json: declared directory is missing: skills/{name}")

    for item, name, path in valid_items:
        _validate_skill_files(root, name, path, str(item["license_spdx"]), errors)

    _validate_links(root, errors)
    _validate_public_wording(root, errors)
    return sorted(set(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    errors = validate_repository(args.root)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
