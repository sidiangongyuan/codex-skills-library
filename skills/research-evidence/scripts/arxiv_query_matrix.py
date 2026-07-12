#!/usr/bin/env python3
"""Generate and optionally run an arXiv query matrix for novelty-risk audits."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Iterable


ARXIV_API = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


def clean_term(term: str) -> str:
    return " ".join(term.strip().split())


def quote_field(term: str) -> str:
    escaped = term.replace('"', '\\"')
    return f'all:"{escaped}"'


def and_query(terms: Iterable[str]) -> str:
    return " AND ".join(quote_field(term) for term in terms if term)


def any_terms(groups: list[list[str]]) -> list[str]:
    return [terms[0] for terms in groups if terms]


def build_queries(args: argparse.Namespace) -> list[tuple[str, str]]:
    domains = [clean_term(t) for t in args.domain_term]
    methods = [clean_term(t) for t in args.method_term]
    tasks = [clean_term(t) for t in args.task_term]
    evals = [clean_term(t) for t in args.eval_term]
    neighbors = [clean_term(t) for t in args.neighbor_term]

    queries: list[tuple[str, str]] = []

    for domain, method, task in itertools.product(domains or [""], methods or [""], tasks or [""]):
        terms = [term for term in [domain, method, task] if term]
        if terms:
            queries.append(("direct_claim", and_query(terms)))

    for domain, method in itertools.product(domains or [""], methods or [""]):
        terms = [term for term in [domain, method] if term]
        if terms:
            queries.append(("method_route", and_query(terms)))

    for task, eval_term in itertools.product(tasks or [""], evals or [""]):
        terms = [term for term in [task, eval_term] if term]
        if terms:
            queries.append(("task_benchmark", and_query(terms)))

    for domain, task in itertools.product(domains or [""], tasks or [""]):
        terms = [term for term in [domain, task] if term]
        if terms:
            queries.append(("dataset_domain", and_query(terms)))

    for neighbor in neighbors:
        terms = [neighbor]
        if tasks:
            terms.append(tasks[0])
        elif methods:
            terms.append(methods[0])
        queries.append(("neighboring_terms", and_query(terms)))

    broad_terms = any_terms([domains, methods, tasks, neighbors])
    if broad_terms:
        queries.append(("newest_broad", and_query(broad_terms[:2])))

    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for family, query in queries:
        key = (family, query)
        if query and key not in seen:
            deduped.append(key)
            seen.add(key)
    return deduped


def apply_since_year(query: str, since_year: int | None) -> str:
    if since_year is None:
        return query
    return f"{query} AND submittedDate:[{since_year}01010000 TO 999912312359]"


def api_url(query: str, max_results: int, sort: str, since_year: int | None = None) -> str:
    query = apply_since_year(query, since_year)
    params = {
        "search_query": query,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": sort,
        "sortOrder": "descending",
    }
    return f"{ARXIV_API}?{urllib.parse.urlencode(params)}"


def text_or_empty(parent: ET.Element, path: str) -> str:
    node = parent.find(path)
    return " ".join(node.text.split()) if node is not None and node.text else ""


def parse_entries(payload: bytes, family: str, query: str) -> list[dict[str, object]]:
    root = ET.fromstring(payload)
    rows: list[dict[str, object]] = []
    for entry in root.findall(f"{ATOM}entry"):
        arxiv_id = text_or_empty(entry, f"{ATOM}id").rsplit("/", 1)[-1]
        authors = [
            text_or_empty(author, f"{ATOM}name")
            for author in entry.findall(f"{ATOM}author")
        ]
        categories = [
            category.attrib.get("term", "")
            for category in entry.findall(f"{ATOM}category")
            if category.attrib.get("term")
        ]
        rows.append(
            {
                "matched_query_family": family,
                "matched_query": query,
                "arxiv_id": arxiv_id,
                "submitted": text_or_empty(entry, f"{ATOM}published"),
                "updated": text_or_empty(entry, f"{ATOM}updated"),
                "title": text_or_empty(entry, f"{ATOM}title"),
                "authors": authors,
                "categories": categories,
                "abstract_snippet": text_or_empty(entry, f"{ATOM}summary")[:500],
                "url": text_or_empty(entry, f"{ATOM}id"),
                "doi": text_or_empty(entry, f"{ARXIV}doi"),
            }
        )
    return rows


def fetch_rows(
    queries: list[tuple[str, str]],
    max_results: int,
    sort: str,
    since_year: int | None,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index, (family, query) in enumerate(queries):
        query_with_date = apply_since_year(query, since_year)
        url = api_url(query, max_results, sort, since_year)
        with urllib.request.urlopen(url, timeout=30) as response:
            rows.extend(parse_entries(response.read(), family, query_with_date))
        if index != len(queries) - 1:
            time.sleep(3.0)
    return rows


def print_dry_run(
    queries: list[tuple[str, str]],
    max_results: int,
    sort: str,
    since_year: int | None,
) -> None:
    for family, query in queries:
        query_with_date = apply_since_year(query, since_year)
        print(f"{family}\t{query_with_date}\t{api_url(query, max_results, sort, since_year)}")


def print_jsonl(rows: list[dict[str, object]]) -> None:
    for row in rows:
        print(json.dumps(row, ensure_ascii=False, sort_keys=True))


def print_tsv(rows: list[dict[str, object]]) -> None:
    headers = [
        "matched_query_family",
        "arxiv_id",
        "submitted",
        "updated",
        "title",
        "authors",
        "categories",
        "url",
        "matched_query",
        "abstract_snippet",
    ]
    print("\t".join(headers))
    for row in rows:
        values = []
        for header in headers:
            value = row.get(header, "")
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            values.append(str(value).replace("\t", " ").replace("\n", " "))
        print("\t".join(values))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate or run a generic arXiv query matrix for novelty-risk audits."
    )
    parser.add_argument("--domain-term", action="append", default=[], help="Domain/input term.")
    parser.add_argument("--method-term", action="append", default=[], help="Method-family term.")
    parser.add_argument("--task-term", action="append", default=[], help="Task/output term.")
    parser.add_argument("--eval-term", action="append", default=[], help="Evaluation/protocol term.")
    parser.add_argument("--neighbor-term", action="append", default=[], help="Adjacent terminology.")
    parser.add_argument("--since-year", type=int, default=None, help="Filter arXiv submittedDate from this year.")
    parser.add_argument("--max-results", type=int, default=5, help="arXiv results per generated query.")
    parser.add_argument(
        "--sort",
        default="submittedDate",
        choices=["submittedDate", "lastUpdatedDate", "relevance"],
        help="arXiv sortBy value.",
    )
    parser.add_argument("--format", choices=["jsonl", "tsv"], default="jsonl")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Print generated query URLs only.")
    mode.add_argument("--run", action="store_true", help="Fetch arXiv metadata and print rows.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    queries = build_queries(args)
    if not queries:
        print("error: provide at least one search term", file=sys.stderr)
        return 2

    if not args.run:
        print_dry_run(queries, args.max_results, args.sort, args.since_year)
        return 0

    rows = fetch_rows(queries, args.max_results, args.sort, args.since_year)
    if args.format == "tsv":
        print_tsv(rows)
    else:
        print_jsonl(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
