# PDF-Bench

Evaluate whether a document benchmark fits the parser decision you need to make,
then compare configured pipelines on the relevant documents and task.

PDF-Bench contains a reconstructed evaluation example, a pinned ParseBench subset
comparison using upstream evaluators, and an inspectable registry of earlier work.
Its contribution is practical benchmark construction and interpretation. It does
not establish a universal parser leaderboard or a business-coverage percentage.

Start with [project orientation](PROJECT_ORIENTATION.md) and the
[current source status](docs/BENCHMARK_STATUS_REPORT.md). The active work unit is
[benchmark reconstruction](.workspace/work/2026-10-13-benchmark-rebuild/plan.md).
Its `report-evidence/latest.json` identifies the generated technical report,
appendix, source-linked claims, replay instructions and editorial handoff.

## Reproduce the evidence

The work unit's `reproduce_invoice_comparison.sh` and
`reproduce_parsebench_comparison.sh` install retained packages in fresh directories,
execute frozen populations and verify offline grading. Public inputs are retrieved
from pinned source URLs and byte-verified when absent. No API keys or metered
provider calls are needed. See `replay-protocol.txt` in the same work unit.

The synthetic invoice result measures a parser plus a fixed extractor on qualified
source templates. The public comparison measures native content and table scores
on a declared subset. Those scores have different meanings. Earlier failures remain
labelled diagnostics, and historical families remain available in evidence tiers.

## Develop

Run `scripts/prepare_reconstruction_environment.sh` with Bash to install the tested
local dependencies and retained PDFsmith backend wheel. It accepts an optional
virtual-environment destination; otherwise it uses this checkout's `.venv`.
Run tests with `uv run --no-sync pytest` after setup. CI also checks formatting,
lint and mypy. The benchmark runtimes remain separately frozen and are not changed
by developer setup or later dependency upgrades.
Full builder tests also require Pandoc, LibreOffice Writer and a LaTeX PDF engine;
the frozen benchmark replays use retained PDFs and do not need those converters.

`scripts/build_internal_benchmark_story.py --qualified-report` generates a new
verified report bundle. Without that flag it inventories current retained history.
The older configured runner is available through `pdfbench run`; current execution
rejects unsafe checkpoint resumption and disables adapter cache reuse.

## Historical work and release status

The registry retains business, legal/HR, SEC, invoice, presentation/deck, academic,
commercial and frontier-parser work, including incomplete or inconsistent runs.
The former README is preserved in
[the historical archive](docs/archive/readme-2025-11-retained.md). Its model
recommendations, prices and winner claims are not current evaluation results.

Reconstruction work is on a draft PR. Public-main merge, publication, deployment,
package release and paid runs require their respective authorization.
