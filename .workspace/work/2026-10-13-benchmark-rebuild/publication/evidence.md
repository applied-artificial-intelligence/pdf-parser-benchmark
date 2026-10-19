# Evidence and worked-example notes

This appendix supports [Selecting document parsing and extraction tools](guide.html).
It separates retained observations, upstream reported scores and illustrative
application requirements. No new parsing, grading, model or GPU experiment was
performed for the publication edition.

## Financial-table example {#financial}

The source is Apple 2025 Form 10-K, printed page 19. ParseBench names its input
Apple 10-k_page22.pdf. The article figure is a crop rendered directly from the
retained PDF. Its values and units were checked visually against that page.

- [Pinned upstream input](https://huggingface.co/datasets/llamaindex/ParseBench/resolve/2805a1d940f95a203e0ae4b88be9934f7765b3fc/docs/table/Apple%2010-k_page22.pdf)
- [Retained table references](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/parsebench-comparison-evidence/run-738d3881c229472b8c73fc69f8e8ca01/frozen-plan/references/table.jsonl). Find the row whose PDF is `docs/table/Apple 10-k_page22.pdf`.

The first period is June 29 through August 2, 2025. The printed share count is
33,265, stated in thousands, giving 33,265,000 shares. The average price is $210.43.
The HTML table reference includes the printed count and header, but not the unit
sentence above the table. A normalized application record therefore requires
information beyond agreement with that table reference alone.

The three-period schema, source-evidence requirement and treatment of the total
are illustrative application requirements. No configured candidate was executed
against that schema, and no production qualification is claimed.

## Candidate evidence {#candidates}

The article quotes two rows of the pinned [ParseBench leaderboard CSV](https://github.com/run-llama/ParseBench/blob/d423e529ae329317bcd33c650b367acfb60e6620/leaderboard.csv):

| Evaluated configuration | Table score | Visual-grounding score |
|---|---:|---:|
| Azure Document Intelligence (Layout) | 86.00 | 73.78 |
| LlamaParse Agentic | 88.88 | 84.25 |

Scores are on the source's scale out of 100. They describe its aggregate population,
not the Apple page, a new local run or a current product guarantee. These rows
illustrate cross-supplier candidate inspection, not an exhaustive ranking.
Current prices and task-specific review rates were not measured.

## Invoice result and continuation row {#invoice}

The retained comparison uses generated PDFs from six source template/complexity
combinations, a fixed extractor and frozen task rules. Prior qualification included
coding-agent visual review, not independent human adjudication or real-vendor
sampling. The ten-item invoice used as an illustration was chosen to explain a
continuation-row failure; it is not a representative estimate by itself.

- [Aggregate result](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c/summary.json)
- [Generated source PDF](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-comparison-plan/inputs/invoice_001.pdf)
- [pdfplumber raw output](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c/attempts/pdfplumber--invoice_001/retained-output.md)
- [pdfplumber combination's prediction](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c/attempts/pdfplumber--invoice_001/prediction.json)
- [pypdf combination's prediction](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c/attempts/pypdf--invoice_001/prediction.json)
- [Reference qualification](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-reference-checkpoint.json) and [all failed-pair audit](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/invoice-failure-audit.json)

Both configurations returned content on 100 inputs. Complete-task passes were
84 and 55, respectively. Record F1 is 2 × matched / (expected + predicted), giving
95.84% from 668 / 696 / 698 and 97.62% from 677 / 696 / 691.

In invoice 001, the continuation row has quantity 84.07 and amount $4,407,902.75.
The pdfplumber raw output contains it after the nine-record Markdown table, in the
plain-text section. The selected `markdown_tables` extraction path returned nine
records and omitted that item. The pypdf combination returned ten. Both recovered
all five requested fields on this document. These observations diagnose an
extractor/representation interaction without implying that the raw text lacked
the row.

## Public benchmark assessment {#public-benchmarks}

The [source assessment](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/parsebench-coverage.md)
explains counting units, document observations, metric contracts and the scopes
of ParseBench, ExtractBench, Pro and OmniDocBench. Pro's counts and synthesis
method are upstream reports checked against its pinned card, not a new independent
annotation audit. The guide credits LlamaIndex's confidence-validation method.

## Full ParseBench inventory {#inventory}

The [CSV inventory](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/parsebench-workload-index.csv)
accounts for 2,078 input paths and 2,060 distinct file hashes. Its associated
2,553 cases cover overlapping capability groups. Visual observations cover 221
inputs, while mechanical measurements cover the full pinned population. Unknown
family labels remain unknown; they do not establish missing benchmark coverage.

## Operating observations {#operating}

The [retained source inspection](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/blob/37c821e38e3d61530711278b56207039a7a638f0/.workspace/work/2026-10-13-benchmark-rebuild/parsebench-coverage.md#retained-local-execution-limitations)
identifies fresh processes, converters and model loading in frozen local
configurations. It establishes no measured warm speedup, reload fraction,
serving-cost comparison or general limitation of an underlying SDK.

The article's processing prices, review rates and labor costs are hypothetical.
Its break-even result assumes equal final quality and no other cost differences.
It is a calculation readers can adapt, not a provider recommendation.
