# PDF text extraction can succeed while invoice extraction fails

Review draft. This resource reports a bounded local experiment executed on
October 13, 2026. It does not update the historical parser leaderboard or
authorize publication of the withdrawn benchmark article.

## What was tested

A downstream invoice workflow needs the right value associated with each field,
not a bag of text containing all the expected values. This comparison tests that
distinction with source-first documents and a fixed label/value extractor. It
also checks whether empty parser outputs and broken files remain visible in
the evaluation rather than disappearing from the denominator.

The independent source specifies five fields: invoice identifier, vendor, total,
currency and due date. The renderer produces an inline PDF, a two-column PDF
with labels written before values in the PDF content stream, and an image-only
copy of the inline PDF. A deliberately truncated upload is a separate failure
control. The PDFs contain fictional data. The semantic and text references are
written before either parser runs, without reconstructing them from extraction.

Installed PDFsmith backends call pypdf 6.3.0 and pdfplumber 0.11.8. The existing
BenchmarkRunner performs eight sequential attempts, with no checkpoint reuse
and no adapter-cache reads or writes. A local wrapper enforces a 15-second
timeout and gives each parser its own output directory. No network request,
paid parser, downloaded model or production document is needed.

## Field associations distinguish these controlled inputs

| Input | pypdf correct fields | pdfplumber correct fields |
| --- | --- | --- |
| Inline labels and values | 5/5 | 5/5 |
| Labels and values in separate columns | 0/5 | 5/5 |
| Image-only PDF | 0/5 | 0/5 |
| Truncated PDF | Parser failure; unscored | Parser failure; unscored |

Both parsers extracted every value token from the two-column PDF. pypdf returned
the labels as a group, followed by the values. pdfplumber returned each label
beside its corresponding value. The declared downstream extractor could use
the latter representation and rejected the former. A different extractor could
recover some associations from pypdf output, so this is a pipeline comparison,
not proof that pypdf can never process such documents.

On the two-column input, pypdf's ChrF++ text score was 78.7524, but none of the
five label/value associations passed the task check. pdfplumber's output matched
the text reference and all five associations. The task result depends on the
document layout, parser configuration and downstream extractor together.

Both calls on the image-only PDF completed successfully and returned empty
text. Those inputs score zero for field recovery, not missing data or parser
exceptions. Neither tested backend performs OCR. Both parsers rejected the
truncated upload, and those two attempts remain in the failure counts.

Each parser therefore attempted four inputs, completed three, rejected one and
timed out on none. The common scored subset contains the three valid inputs.
pypdf completed the entire field task on one of those three; pdfplumber did so
on two. These hand-selected variants cannot estimate performance on real vendor
invoices. TEDS is unavailable on these non-table outputs and is exported as
null, never a fabricated table score. Failed-call duration is unknown in the
runner and is explicitly null in the comparison pack. Successful timings
include local wrapper and first-import effects and are not latency rankings.

## The export writer now preserves earlier valid results

The old persistence function opened the destination before serializing it.
Injecting an unserializable return value into the actual metric producer caused
BenchmarkRunner to produce a bad result, and saving it truncated an earlier
valid export. The regression test failed on that producing path before repair.

The repaired writer serializes strict JSON first, writes a temporary sibling,
flushes it and atomically replaces the destination. Invalid generation leaves
the original bytes unchanged. Nonfinite metric values serialize as null. The
same writer saves both runner results and the structured comparison pack.

Focused checks also exposed outdated runner fixtures that still used the old
`pdf_path` constructor argument and a test that expected valid Markdown to fail
element-F1 scoring. Those tests now exercise the current contract. Lightweight
comparisons no longer import the unused Tika package at startup; a subprocess
test first reproduced that import-time warning and now passes with warnings
treated as errors.

The focused runner, persistence and new comparison suites passed: 48 tests,
without warnings. Ruff formatting and focused lint passed.

## Inspect or rerun the experiment

Run from `/home/stefan/applied-ai/pdf-bench` into a new directory:

```bash
uv run python -m pdf_bench.local_evaluation --output .workspace/work/2026-10-13-local-parser-evaluation/run-04
```

The writer refuses an existing run directory. `run-03/comparison.json` contains
all eight attempts, input/reference/output hashes, package versions, backend
source hashes, the exact execution timestamp, common inputs and task scores.
`run-03/runner-results.json` preserves the standard text metrics. The source
reference JSON, generated PDFs and parser outputs are retained beside them.

PDFsmith's installed distribution metadata says 0.2.0 while its checked-out
module declares 0.3.0. Both are recorded, along with backend implementation
hashes. The original experiment also used a dirty source checkout; its base
revision alone does not identify the tested implementation. The recorded code
hashes and reviewed patch, not a single version label, identify the experiment.

The earlier SEC, controlled invoice, presentation, source-first deck, arXiv and
commercial tracks remain separate historical, directional or prototype evidence.
This experiment neither deletes them nor establishes a current universal winner.
The next local comparison should expand layout and OCR coverage using independently
known references. A paid comparison is unnecessary to establish the export repair
or the empty-output and association failures demonstrated here.

## Next actions

- Stefan reviews this exact report and the code checkpoint before any public
  resource release; the source review branch is not website deployment approval.
