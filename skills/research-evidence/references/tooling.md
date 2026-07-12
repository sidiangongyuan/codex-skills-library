# Research Evidence Tooling

## Dedicated Environment

Use only the dedicated environment:

```bash
${CODEX_HOME:-$HOME/.codex}/tools/research-evidence/bin/paper-search --help
${CODEX_HOME:-$HOME/.codex}/tools/research-evidence/bin/academic-refchecker --help
```

Pinned packages:

- `paper-search-mcp==0.1.3`
- `academic-refchecker==3.0.147`

Do not use global `uv tool install` or assume these commands are on the global `PATH`.

## Paper Search

`paper-search-mcp==0.1.3` installs importable searchers but no console scripts, so this environment includes a local `paper-search` wrapper in the venv `bin/` directory.

Examples:

```bash
${CODEX_HOME:-$HOME/.codex}/tools/research-evidence/bin/paper-search \
  "collaborative perception CVPR infrastructure vehicle" \
  --source arxiv \
  --max-results 5

${CODEX_HOME:-$HOME/.codex}/tools/research-evidence/bin/paper-search \
  "multimodal autonomous driving ICLR" \
  --source arxiv \
  --max-results 10 \
  --format json
```

Available wrapper sources: `arxiv`, `pubmed`, `biorxiv`, `medrxiv`.

Use arXiv first for CV/ML metadata smoke checks. For high-stakes
recent-work or novelty-risk audits, do not rely on `paper-search` as the only
search route: wrapper results can be noisy, can bury exact recent competitors,
and may miss terminology variants. Prefer a direct arXiv API query matrix and
use `paper-search` as a smoke or secondary cross-check.

The skill also includes a standard-library helper:

```bash
python "<skill-dir>/scripts/arxiv_query_matrix.py" \
  --domain-term "your domain term" \
  --method-term "your method term" \
  --task-term "your task term" \
  --neighbor-term "alternate terminology" \
  --since-year 2024 \
  --max-results 5 \
  --dry-run
```

Resolve `<skill-dir>` to the installed `research-evidence` directory before
running the command; do not assume a particular global skills root.

Pass `--run` only when live arXiv metadata is needed. The helper prints to
stdout and does not write report files by default.

Do not use Google Scholar scraping by default. Do not download PDFs unless the
user explicitly asks and the source is open access.

The environment also includes `paper-search-mcp`, a local wrapper for starting the package's stdio MCP server, but Codex MCP is not registered in v1.

## RefChecker

Default non-LLM invocation:

```bash
${CODEX_HOME:-$HOME/.codex}/tools/research-evidence/bin/academic-refchecker --paper /path/to/paper-or-bib
```

Allowed input types include local PDF, local LaTeX, local text references, BibTeX, arXiv ID, or URL. Prefer user-provided local files for submission checks.

Do not pass these flags unless the user explicitly requests LLM-assisted checks:

- `--llm-provider`
- `--hallucination-provider`
- `--llm-model`
- `--hallucination-model`

Do not pass `--output-file` or `--report-file` unless the user explicitly requests saved artifacts.

Use `--semantic-scholar-api-key` only if the user has provided or configured a key.
