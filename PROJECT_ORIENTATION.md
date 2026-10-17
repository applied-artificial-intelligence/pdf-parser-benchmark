# PDF-Bench orientation

Current source work is the benchmark reconstruction in
`.workspace/work/2026-10-13-benchmark-rebuild/`. Its `spec.md` and `plan.md` record
the approved scope; `progress.txt` records verified progress and the next step.
Draft PR #9 contains the milestone implementation. GitHub issues remain open
until an approved merge to public main.

## Purpose

Assess whether public benchmark documents, tasks and operating conditions fit the
team's intended parser decision. Reuse ParseBench, ExtractBench or their relevant
subsets when they fit. Additional internal evaluation needs a consequential
mismatch. Do not invent marginal omissions or a business-wide coverage percentage.

Retain the project's history as strong within a declared task, directional,
prototype, historical and rerun evidence. Teach benchmark construction through
actual selection, reference, cache, configuration and grading mistakes.

## Authoritative artifacts

- `report-evidence/latest.json` in the work unit identifies the generated technical
  report, appendix, claim export, replay protocol and integration handoff.
- `invoice-run-checkpoint.json` identifies corrected primary invoice runs, their
  frozen task/runtime and the failure audit. Earlier v2 runs are integration
  diagnostics, not primary quality evidence.
- `parsebench-run-checkpoint.json` identifies the executed public subset, pinned
  native evaluation and fresh/offline reproduction evidence.
- `retained-evidence/latest.json` identifies the immutable historical registry.
- `parsebench-assessment.json` and the qualified selection distinguish broad fit
  assessment from the dimensions actually executed.

The source-first invoice example measures a configured parser plus a fixed
extractor on generated templates. Public parsing dimensions and invoice task
scores have different meanings. No universal parser or paid-model winner follows.

## Resume and verify

Read the current work-unit progress and checkpoints before making new runs.
`reproduce_invoice_comparison.sh` and `reproduce_parsebench_comparison.sh` rebuild
retained runtimes and execute the frozen protocols. New provider/library changes
require new execution identities. Do not silently upgrade a frozen comparison.

`scripts/build_internal_benchmark_story.py --qualified-report` generates a new
source-verified report/export bundle. Without that flag it builds a new registry
from current retained artifacts. These are different operations.

The developer setup script is `scripts/prepare_reconstruction_environment.sh`.
Tests use `uv run --no-sync pytest`. Core lint/format and mypy checks match CI.
The older mixed-corpus runner remains available through `pdfbench run`; it does
not restore historical provenance or accept unsafe checkpoint resumption.

## Ownership and boundaries

This conversation owns source implementation, evaluation and evidence. Editorial
and website owners decide synthesis and rendering. The checked article context
is in `editorial-context.json` in the work unit. No editorial/CMS changes, paid
calls, package release, publication or deployment belong to this milestone.
Stefan must approve public-main merge and any future spending cap.

The prior orientation is preserved byte-for-byte as `orientation-before-rebuild.txt`
in the work unit. Its older tier labels are historical, not current findings.
Inherited dirty/untracked work remains preserved unless explicitly adopted.
