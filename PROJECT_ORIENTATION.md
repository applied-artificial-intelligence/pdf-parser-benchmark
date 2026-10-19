# PDF-Bench orientation

The current deliverable is [Selecting document parsing and extraction tools](.workspace/work/2026-10-13-benchmark-rebuild/benchmark-design-guide.md).
It explains component selection for a defined document collection, downstream
task, quality threshold and total cost, including confidence and review policies.
It uses retained examples rather than a new general leaderboard. All benchmark and GPU execution remains paused, including
the overnight heartbeat. Prepared full and sampled comparisons are deferred.

The work unit is `.workspace/work/2026-10-13-benchmark-rebuild/`. Revision 7 of
its `spec.md` and current `plan.md` supersede the earlier full-roster execution
scope. `progress.txt` records the delivery/checkpoint status. Draft
[PR #9](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark/pull/9)
contains the work. Issues are not closed merely because a draft was delivered.

## Purpose

Assess whether public benchmark documents, required outputs and scoring rules
support the intended component decision. Consult ParseBench, ExtractBench,
ExtractBench Pro and OmniDocBench before proposing new experiments. Additional evaluation needs an
important uncertainty that existing evidence cannot resolve. Do not invent
marginal omissions or a percentage of all business use cases.

Retain the project's history in its evidence tiers. Explain reference mismatch,
parser-dependent selection, conflicting metrics, output-contract limitations
and execution lifecycle using actual artifacts. A controlled invoice example
does not estimate arbitrary real-vendor performance.

## Authoritative artifacts

Paths below are relative to the work unit:

- `publication/guide.html` is the portable publication edition;
  `publication/evidence.html` is the readable appendix. Regenerate with
  `uv run --no-sync python publication/render.py` from the work unit, or invoke
  that script by its full path. It renders authored text only, with no inference.
  `publication/review/` retains desktop/375px screenshots.
- `benchmark-design-guide.md` is the current authored guide;
  `guide-evidence.json` records its source identities, checks and claim limits.
- `parsebench-coverage.md`, `parsebench-workload-index.csv` and
  `parsebench-source-coverage.json` cover all 2,078 input paths. Visual observations
  cover 221 inputs, not an independent human audit of every annotation.
- `invoice-reference-checkpoint.json`, `invoice-failure-audit.json` and
  `invoice-selection-bias-demonstration.json` support the worked design examples.
- `invoice-run-checkpoint.json` and `parsebench-run-checkpoint.json` identify
  earlier executed comparisons and their historical replay evidence.
- `report-evidence/latest.json` identifies the earlier immutable generated report,
  appendix and claim export. `retained-evidence/latest.json` identifies the
  historical registry. Neither is regenerated for this writing task.
- `overnight-policy.json` disables execution; `execution-stop-20261017.json`
  records the later cleanup of four owned Marker helper processes.

## Verification and ownership

The October 19 brief requires a reader-focused guide and an ExtractBench Pro
assessment. Keep Swiss Re/Swift3, patent and inventorship material separate.
No website/service page or speculative acquisition narrative is included.
This writing task permits light source, JSON, hash, arithmetic and link checks.
It does not authorize parser or native-evaluator execution, model imports,
profiling, dependency installation or heavyweight tests. Historical replay
instructions remain available in `replay-protocol.txt`; they are not current
instructions to run. Do not silently upgrade a frozen comparison.

This conversation owns the project-local guide, evidence and plan. No sibling
PDFSmith implementation, editorial package, website or CMS changes are included.
Public-main merge, publication, release, deployment and new spending remain
separate decisions. No user decision is required to complete the writing.

The prior orientation is retained as `orientation-before-rebuild.txt` in the work
unit. Preserve unrelated dirty/untracked work unless explicitly adopted.
