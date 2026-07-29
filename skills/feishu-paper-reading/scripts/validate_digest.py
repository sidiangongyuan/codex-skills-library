#!/usr/bin/env python3
"""Validate the structural and evidence invariants of a paper digest."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path


PAPER_HEADING = re.compile(
    r"^##\s+(?:Paper|论文)\s+(\d+)\s*[:：]\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
LEVEL_TWO_HEADING = re.compile(r"^##\s+", re.MULTILINE)
ARXIV_ID = re.compile(
    r"(?:https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/|arxiv\s*:\s*)"
    r"(\d{4}\.\d{4,5})(?:v\d+)?",
    re.IGNORECASE,
)
DOI = re.compile(
    r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/[-._;()/:A-Z0-9]+)",
    re.IGNORECASE,
)
CANONICAL_LINK = re.compile(
    r"https?://(?:"
    r"(?:www\.)?arxiv\.org|"
    r"(?:www\.)?openreview\.net|"
    r"doi\.org|"
    r"proceedings\.[^/\s]+|"
    r"openaccess\.thecvf\.com|"
    r"aclanthology\.org|"
    r"(?:www\.)?vldb\.org|"
    r"(?:www\.)?usenix\.org|"
    r"dl\.acm\.org|"
    r"ieeexplore\.ieee\.org|"
    r"link\.springer\.com"
    r")/\S+",
    re.IGNORECASE,
)
LOCATOR = re.compile(
    r"(?:"
    r"\bp\.\s*\d+|"
    r"\bpages?\s+\d+|"
    r"\bsec(?:tion)?\.?\s*[\dA-Z]+|"
    r"\bfig(?:ure)?\.?\s*\d+|"
    r"\btable\s*\d+|"
    r"\bappendix\s+[A-Z0-9]+|"
    r"\btheorem\s*\d+|"
    r"第\s*\d+\s*页|"
    r"第\s*[\d.]+\s*节|"
    r"图\s*\d+|"
    r"表\s*\d+|"
    r"附录\s*[A-Z0-9]"
    r")",
    re.IGNORECASE,
)
PLACEHOLDER = re.compile(
    r"(?:\bTODO\b|\bTBD\b|\bFIXME\b|\[INSERT[^\]]*\]|待补充|占位符)",
    re.IGNORECASE,
)
WORD = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)
CJK_CHARACTER = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

REQUIRED_SECTIONS = {
    "executive summary": ("## Executive Summary", "## 执行摘要"),
    "search and selection": ("## Search And Selection", "## 检索与筛选"),
    "comparison matrix": ("## Comparison Matrix", "## 对比矩阵"),
    "cross-paper synthesis": ("## Cross-Paper Synthesis", "## 跨论文综合"),
    "research opportunities and reading order": (
        "## Research Opportunities And Reading Order",
        "## 研究机会与阅读顺序",
    ),
    "coverage and confidence": (
        "## Coverage And Confidence",
        "## 覆盖范围与置信度",
    ),
}
REQUIRED_PAPER_SECTIONS = {
    "verified metadata": ("### Verified Metadata", "### 已核验元数据"),
    "thirty-second verdict": ("### Thirty-Second Verdict", "### 30秒结论"),
    "problem and contribution": (
        "### Problem And Contribution",
        "### 问题与贡献",
    ),
    "method": ("### Method", "### 方法"),
    "evidence ledger": ("### Evidence Ledger", "### 证据账本"),
    "original-language evidence": (
        "### Original-Language Evidence",
        "### 原文证据",
    ),
    "figures and tables worth inspecting": (
        "### Figures And Tables Worth Inspecting",
        "### 值得看的图表",
    ),
    "strengths, limitations, and reproduction": (
        "### Strengths, Limitations, And Reproduction",
        "### 优势、局限与复现",
    ),
    "connection to the set": (
        "### Connection To The Set",
        "### 与其他论文的关系",
    ),
}


@dataclass(frozen=True)
class PaperSection:
    number: int
    title: str
    body: str


def split_papers(text: str) -> list[PaperSection]:
    matches = list(PAPER_HEADING.finditer(text))
    sections: list[PaperSection] = []
    for match in matches:
        next_heading = LEVEL_TWO_HEADING.search(text, match.end())
        end = next_heading.start() if next_heading else len(text)
        sections.append(
            PaperSection(
                number=int(match.group(1)),
                title=match.group(2).strip(),
                body=text[match.start() : end],
            )
        )
    return sections


def quote_fragments(section: str) -> list[str]:
    fragments: list[str] = []
    for line in section.splitlines():
        if not line.lstrip().startswith(">"):
            continue
        fragment = line.lstrip()[1:].strip()
        fragment = re.split(r"\[(?:Source|来源|原文)[^\]]*\]", fragment)[0]
        fragments.append(fragment)
    return fragments


def quote_words(section: str) -> int:
    return sum(len(WORD.findall(fragment)) for fragment in quote_fragments(section))


def quote_cjk_characters(section: str) -> int:
    return sum(
        len(CJK_CHARACTER.findall(fragment))
        for fragment in quote_fragments(section)
    )


def normalized_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def normalized_dois(value: str) -> set[str]:
    return {
        match.group(1).rstrip(".,;:)]}").casefold()
        for match in DOI.finditer(value)
    }


def validate(
    text: str,
    *,
    expected_count: int | None,
    max_quote_words: int,
    max_cjk_quote_characters: int = 50,
) -> list[str]:
    errors: list[str] = []

    for label, aliases in REQUIRED_SECTIONS.items():
        if not any(alias.casefold() in text.casefold() for alias in aliases):
            errors.append(f"missing required section: {label}")

    placeholders = sorted(set(match.group(0) for match in PLACEHOLDER.finditer(text)))
    if placeholders:
        errors.append(f"unresolved placeholders: {', '.join(placeholders)}")

    papers = split_papers(text)
    if expected_count is not None and len(papers) != expected_count:
        errors.append(
            f"expected {expected_count} selected paper sections, found {len(papers)}"
        )
    expected_numbers = list(range(1, len(papers) + 1))
    actual_numbers = [paper.number for paper in papers]
    if actual_numbers != expected_numbers:
        errors.append(
            f"paper headings must be sequential from 1: found {actual_numbers}"
        )

    seen_arxiv: dict[str, int] = {}
    seen_doi: dict[str, int] = {}
    seen_titles: dict[str, int] = {}
    for paper in papers:
        label = f"paper {paper.number} ({paper.title})"
        title_key = normalized_title(paper.title)
        previous_title = seen_titles.get(title_key)
        if previous_title is not None:
            errors.append(
                f"duplicate normalized title in papers {previous_title} and "
                f"{paper.number}: {paper.title}"
            )
        else:
            seen_titles[title_key] = paper.number

        for section_label, aliases in REQUIRED_PAPER_SECTIONS.items():
            if not any(
                alias.casefold() in paper.body.casefold() for alias in aliases
            ):
                errors.append(f"{label}: missing required section: {section_label}")

        if not CANONICAL_LINK.search(paper.body):
            errors.append(f"{label}: missing canonical paper link")
        if not LOCATOR.search(paper.body):
            errors.append(f"{label}: missing page, section, figure, table, or appendix locator")

        quote_lines = [
            line for line in paper.body.splitlines() if line.lstrip().startswith(">")
        ]
        if not quote_lines:
            errors.append(f"{label}: missing original-language quote block")
        else:
            unanchored_quotes = [
                line for line in quote_lines if not LOCATOR.search(line)
            ]
            if unanchored_quotes:
                errors.append(
                    f"{label}: every quote block line needs its own source locator"
                )

        word_count = quote_words(paper.body)
        if word_count > max_quote_words:
            errors.append(
                f"{label}: quoted word count {word_count} exceeds "
                f"the conservative limit {max_quote_words}"
            )
        cjk_count = quote_cjk_characters(paper.body)
        if cjk_count > max_cjk_quote_characters:
            errors.append(
                f"{label}: quoted CJK character count {cjk_count} exceeds "
                f"the conservative limit {max_cjk_quote_characters}"
            )

        section_ids = set(ARXIV_ID.findall(paper.body))
        for arxiv_id in section_ids:
            previous = seen_arxiv.get(arxiv_id)
            if previous is not None:
                errors.append(
                    f"duplicate arXiv ID {arxiv_id} in papers {previous} and "
                    f"{paper.number}"
                )
            else:
                seen_arxiv[arxiv_id] = paper.number

        for doi in normalized_dois(paper.body):
            previous = seen_doi.get(doi)
            if previous is not None:
                errors.append(
                    f"duplicate DOI {doi} in papers {previous} and {paper.number}"
                )
            else:
                seen_doi[doi] = paper.number

    return errors


def run_self_test() -> None:
    valid = """# Test

## Executive Summary
Summary.

## Search And Selection
Twenty-five candidates.

## Comparison Matrix
| Paper | Idea |
|---|---|
| One | Test |

## Paper 1: A Test Paper
### Verified Metadata
Paper: https://arxiv.org/abs/2607.12345

### Thirty-Second Verdict
Verdict.

### Problem And Contribution
Problem.

### Method
Method.

### Evidence Ledger
Evidence appears in Sec. 3 and Table 2.

### Original-Language Evidence
> "The model predicts future occupancy." [Source: p. 4, Sec. 3]

Chinese explanation.

### Figures And Tables Worth Inspecting
Table 2.

### Strengths, Limitations, And Reproduction
Limitations.

### Connection To The Set
Connection.

## Cross-Paper Synthesis
Synthesis.

## Research Opportunities And Reading Order
Opportunities.

## Coverage And Confidence
Coverage.
"""
    errors = validate(valid, expected_count=1, max_quote_words=25)
    if errors:
        raise AssertionError(f"valid fixture failed: {errors}")

    valid_chinese = (
        valid.replace("## Executive Summary", "## 执行摘要")
        .replace("## Search And Selection", "## 检索与筛选")
        .replace("## Comparison Matrix", "## 对比矩阵")
        .replace("## Paper 1:", "## 论文 1：")
        .replace("### Verified Metadata", "### 已核验元数据")
        .replace("### Thirty-Second Verdict", "### 30秒结论")
        .replace("### Problem And Contribution", "### 问题与贡献")
        .replace("### Method", "### 方法")
        .replace("### Evidence Ledger", "### 证据账本")
        .replace("### Original-Language Evidence", "### 原文证据")
        .replace(
            "### Figures And Tables Worth Inspecting",
            "### 值得看的图表",
        )
        .replace(
            "### Strengths, Limitations, And Reproduction",
            "### 优势、局限与复现",
        )
        .replace("### Connection To The Set", "### 与其他论文的关系")
        .replace("## Cross-Paper Synthesis", "## 跨论文综合")
        .replace(
            "## Research Opportunities And Reading Order",
            "## 研究机会与阅读顺序",
        )
        .replace("## Coverage And Confidence", "## 覆盖范围与置信度")
    )
    errors = validate(valid_chinese, expected_count=1, max_quote_words=25)
    if errors:
        raise AssertionError(f"valid Chinese fixture failed: {errors}")

    for official_url in (
        "https://www.vldb.org/pvldb/vol19/p123-test.pdf",
        "https://www.usenix.org/conference/osdi26/presentation/test",
    ):
        official_fixture = valid.replace(
            "https://arxiv.org/abs/2607.12345",
            official_url,
        )
        errors = validate(official_fixture, expected_count=1, max_quote_words=25)
        if errors:
            raise AssertionError(
                f"valid official-proceedings fixture failed: {errors}"
            )

    trailing_fixture = valid.replace(
        "## Cross-Paper Synthesis\nSynthesis.",
        """## Paper 2: Another Test Paper
### Verified Metadata
Paper: https://arxiv.org/abs/2607.54321

### Thirty-Second Verdict
Verdict.

### Problem And Contribution
Problem.

### Method
Method.

### Evidence Ledger
Evidence appears in Fig. 2.

### Original-Language Evidence
> "A second model scales efficiently." [Source: p. 5, Fig. 2]

Explanation.

### Figures And Tables Worth Inspecting
Fig. 2.

### Strengths, Limitations, And Reproduction
Limitations.

### Connection To The Set
Connection.

## Cross-Paper Synthesis
Synthesis cites https://arxiv.org/abs/2607.12345.""",
    )
    errors = validate(trailing_fixture, expected_count=2, max_quote_words=25)
    if errors:
        raise AssertionError(f"valid trailing-section fixture failed: {errors}")

    distinct_dois = (
        trailing_fixture.replace(
            "https://arxiv.org/abs/2607.12345",
            "https://doi.org/10.1145/1234567.8901234",
        )
        .replace(
            "https://arxiv.org/abs/2607.54321",
            "https://doi.org/10.1145/7654567.8901299",
        )
    )
    errors = validate(distinct_dois, expected_count=2, max_quote_words=25)
    if errors:
        raise AssertionError(f"valid distinct-DOI fixture failed: {errors}")

    duplicate_doi = (
        trailing_fixture.replace(
            "https://arxiv.org/abs/2607.12345",
            "https://doi.org/10.1145/1234567.8901234",
        )
        .replace(
            "https://arxiv.org/abs/2607.54321",
            "https://doi.org/10.1145/1234567.8901234",
        )
    )
    errors = validate(duplicate_doi, expected_count=2, max_quote_words=25)
    if not any("duplicate DOI" in error for error in errors):
        raise AssertionError("invalid fixture did not detect a duplicate DOI")

    duplicate_title = trailing_fixture.replace(
        "## Paper 2: Another Test Paper",
        "## Paper 2: A Test Paper",
    )
    errors = validate(duplicate_title, expected_count=2, max_quote_words=25)
    if not any("duplicate normalized title" in error for error in errors):
        raise AssertionError("invalid fixture did not detect a duplicate title")

    invalid = valid.replace("## Coverage And Confidence", "## Missing")
    errors = validate(invalid, expected_count=1, max_quote_words=25)
    if not any("coverage and confidence" in error for error in errors):
        raise AssertionError("invalid fixture did not detect a missing section")

    invalid_quote = valid.replace(
        '> "The model predicts future occupancy." [Source: p. 4, Sec. 3]',
        '> "The model predicts future occupancy." [Source: p. 4, Sec. 3]\n'
        '> "This fragment has no locator."',
    )
    errors = validate(invalid_quote, expected_count=1, max_quote_words=25)
    if not any("every quote block line" in error for error in errors):
        raise AssertionError("invalid fixture did not detect an unanchored quote")

    invalid_cjk_quote = valid.replace(
        '"The model predicts future occupancy."',
        f'"{"测" * 51}"',
    )
    errors = validate(invalid_cjk_quote, expected_count=1, max_quote_words=25)
    if not any("quoted CJK character count" in error for error in errors):
        raise AssertionError("invalid fixture did not detect a long CJK quote")

    invalid_paper_section = valid.replace("### Method", "### Missing Method")
    errors = validate(invalid_paper_section, expected_count=1, max_quote_words=25)
    if not any("missing required section: method" in error for error in errors):
        raise AssertionError("invalid fixture did not detect a missing paper section")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, help="Markdown digest to validate")
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--max-quote-words", type=int, default=25)
    parser.add_argument("--max-cjk-quote-characters", type=int, default=50)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and args.path is None:
        parser.error("path is required unless --self-test is used")
    if args.expected_count is not None and args.expected_count < 1:
        parser.error("--expected-count must be positive")
    if args.max_quote_words < 1:
        parser.error("--max-quote-words must be positive")
    if args.max_cjk_quote_characters < 1:
        parser.error("--max-cjk-quote-characters must be positive")
    return args


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        print("Self-test passed.")
        return 0

    try:
        text = args.path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = validate(
        text,
        expected_count=args.expected_count,
        max_quote_words=args.max_quote_words,
        max_cjk_quote_characters=args.max_cjk_quote_characters,
    )
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1

    print(
        f"Digest validation passed: {len(split_papers(text))} selected paper section(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
