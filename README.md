# PDF-Bench: evaluating document parsing

PDF-Bench contains PDF parsing adapters, corpus configurations, scoring code and retained benchmark outputs. The project helps examine extraction quality, output structure, coverage and failure behavior for document-processing systems.

Parser selection depends on the documents and the downstream work. Text edit similarity, table structure and successful workflow completion measure different things. A high score on one does not establish the others.

## Interpreting the retained results

The November 2025 materials describe separate runs, including a 28-document frontier-model sample, a 30-document budget-model sample and larger open-source/commercial evaluations. These populations, configurations and reference treatments must not be combined into one ranking.

The earlier README's 14-point premium advantage was calculated across different samples. It does not establish a matched quality improvement. Its cost ratio was also wrong: $0.05 divided by $0.003 is approximately 16.7, not 50. These are historical quoted prices, not current provider prices or complete workflow costs.

The invoice documentation contains incompatible summaries. Its detailed 100-document table reports 90.6% edit similarity for Azure and 77.1% for PyMuPDF4LLM, while an older summary reports 49.9% as the best score. Those reports do not support the former claim that no parser exceeds 50%. The detailed section also says its references were regenerated from extracted PDF text. Comparing those scores requires identifying the reference revision and normalization used in each run.

See [result scope and unresolved inconsistencies](docs/RESULTS.md) and the [historical cohort guide](docs/LEADERBOARDS.md). The original [README](docs/archive/readme-before-2026-11-03.md), [leaderboard proposals](docs/archive/leaderboards-before-2026-11-03.md) and [results report](docs/archive/results-before-2026-11-03.md) are retained for provenance. Their recommendations and prices are historical, not current parser-selection guidance.

## Source and configuration

```bash
git clone https://github.com/applied-artificial-intelligence/pdf-parser-benchmark.git
cd pdf-parser-benchmark
```

The package entry point is `pdfbench`, defined in [pyproject.toml](pyproject.toml). Inspect the checked-out [benchmark configurations](benchmarks/) and [parser adapters](pdf_bench/systems/) before running a workload. Some adapters use external services and incur charges.

[pdfsmith](https://github.com/applied-artificial-intelligence/pdfsmith) supplies parsing adapters for the project. Reproducing an existing result requires its original dependency revision, configuration, documents and references; installing a newer library does not reproduce a frozen run.

## Applying a benchmark to a document workflow

Define the fields, evidence and structure needed by the next step of the workflow. Evaluate representative documents and consequential exceptions on a common reference set. Count failures and missing results in the denominator. Inspect extraction mistakes separately from any downstream model or business decision, and include human review and correction in the operating-cost comparison.

The [Applied AI document workflow material](https://applied-ai.com/services/workflow-automation/) places parsing within requirements discovery, source-linked interpretation, evaluation and operation.

## License

MIT. Individual parsers, source datasets and services have their own licences and terms.
