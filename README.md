# PDF-Bench

Select parsing and extraction components that meet quality requirements at an
acceptable total cost for the documents and task the application will handle.

Start with [Selecting document parsing and extraction tools](.workspace/work/2026-10-13-benchmark-rebuild/benchmark-design-guide.md).
The guide assesses what ParseBench, ExtractBench, ExtractBench Pro and
OmniDocBench can tell you,
then explains representative evaluation, quality thresholds, confidence-based
review, latency, throughput and total operating cost. Retained results provide
a compact example of how task acceptance changes a component decision.

The [publication edition](.workspace/work/2026-10-13-benchmark-rebuild/publication/guide.html)
includes a [readable evidence appendix](.workspace/work/2026-10-13-benchmark-rebuild/publication/evidence.html),
a worked financial-table selection and a source/output invoice example. Its
standalone layout was checked at desktop and phone widths. Publication remains
subject to approval.

The [ParseBench coverage assessment](.workspace/work/2026-10-13-benchmark-rebuild/parsebench-coverage.md)
and [filterable workload inventory](.workspace/work/2026-10-13-benchmark-rebuild/parsebench-workload-index.csv)
account for all 2,078 source input paths. Visual observations cover 221 inputs;
this is not independent verification of every annotation or a measurement of
business-wide representativeness.

Published results should be reused when their documents, outputs and metrics
support the decision. We have not established a consequential gap that justifies
another general-purpose corpus. The retained experiments illustrate evaluation
design; they do not establish a new universal parser ranking.

## Current state

The guide and supporting work are on draft [PR #9](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/pull/9).
The [plan](.workspace/work/2026-10-13-benchmark-rebuild/plan.md) now centres on
public evidence, application requirements, operating economics and the guide.
**All benchmark and GPU execution is paused**, including the overnight queue. Full and sampled parser
runs are deferred. No new execution is required to read or check the guide.

See [project orientation](PROJECT_ORIENTATION.md) for authoritative artifacts and
[source status](docs/BENCHMARK_STATUS_REPORT.md) for verification boundaries.
Public-main merge, publication, deployment, release and paid runs have not been
authorized.

## Retained implementation and evidence

The repository preserves an input/run registry, frozen comparison protocols,
saved outputs and prior reproducibility evidence. The work unit's
`report-evidence/latest.json` identifies the earlier generated technical report
and source-linked claim export. Those immutable reports precede the guide.

The invoice example measures a parser plus a fixed extractor on generated
templates. The earlier native ParseBench comparison covers a declared content
and table subset. Other business, legal/HR, SEC, presentation, academic and
commercial pilots remain in their evidence tiers. The
[historical README](docs/archive/readme-2025-11-retained.md) preserves the old
presentation; its recommendations and prices are not current results.

## Developer reference

`scripts/prepare_reconstruction_environment.sh` records developer setup, and
the work unit's `replay-protocol.txt` describes earlier frozen replays. These
operations install dependencies or execute comparisons and are deferred during
the current pause. Do not run them as part of reviewing this guide.

When development is separately resumed, tests use `uv run --no-sync pytest`;
CI checks formatting, lint and mypy. Builder tests also require Pandoc,
LibreOffice Writer and a LaTeX PDF engine. The older `pdfbench run` interface
does not restore missing historical provenance.
