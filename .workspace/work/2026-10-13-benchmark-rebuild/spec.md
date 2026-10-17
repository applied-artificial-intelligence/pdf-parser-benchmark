# Spec: A practical guide to choosing and evaluating PDF parsers

Revision 5, October 17, 2026. Stefan approved the concept in this conversation and
instructed this owner to update the plan/issues and write the guide using retained
evidence, with all benchmark and GPU runs paused. This supersedes the full-roster
execution requirement and the subsequent sample proposal. Revision 4 and its
engineering contracts remain recoverable at Git commit
`c8fa6abe702c04e9316485e772de29b8b846b3be`; completed work is preserved.

## Objective

A practitioner can decide whether existing public benchmarks support a particular
parser choice, identify what additional validation is justified, and design that
validation without reproducing an existing leaderboard or trusting misleading
references, averages and operating measurements. The deliverable is an independent,
source-verified guide and an inspectable coverage inventory, grounded in the
project's retained successes and mistakes.

## Why

ParseBench provides public references, evaluators and published comparisons that
address much of the project's original ground-truth problem. Our useful
contribution is practical interpretation and evaluation design. An additional
local parser result is valuable only when it can change an unanswered decision.
Missing marginal cases and a smaller duplicate leaderboard do not establish that
value. Stefan has reserved the workstation/GPU for more urgent work.

## Terms

Context: pdf-bench, document-parser-evaluation

| Term | Readings | Status | Basis |
|---|---|---|---|
| Guide | A new leaderboard; or a practical explanation of using and extending existing evaluation evidence | resolved-by-author | Stefan accepted the independent guide, coverage inventory and worked evaluation lessons. |
| Benchmark fit | An unsupported percentage of all business tasks; or correspondence between a declared workload, output requirements and evaluated cases/metrics | resolved-by-author | Stefan requires targeted evaluation of what matters and public reuse when suitable. |
| Retained evidence | A new run; or existing versioned sources, outputs, references, audits and checkpoints | resolved-by-author | The current instruction explicitly requires existing evidence and paused runs. |
| Independent reference | An evaluated parser's output; or source/annotation truth established without that output defining its own answer | resolved-by-author | The earlier commission and reference qualification retain this definition. |
| Completion | Execution of every parser; or a written, checked guide with inspectable evidence and accurate project entry points | resolved-by-author | The accepted concept replaces automatic full/sample execution. |
| Paused execution | Off-hours-only work; or no benchmark, native regrading, GPU profiling or automatic test/benchmark launch | resolved-by-author | Stefan postponed local GPU work and explicitly keeps benchmark/GPU runs paused. |

## Acceptance criteria

1. Write a finished project-local guide for a technical practitioner with no
   conversation context. Its primary document type is explanation. It develops
   decisions and their consequences through examples; exact configurations and
   exhaustive inventories remain linked reference material.
2. Give a clear recommendation about PDF-Bench's contribution. Attribute existing
   benchmark ground truth/results and explain why another broad leaderboard is
   not currently justified. Do not claim a systematic ParseBench flaw or an
   all-business coverage percentage that the evidence does not establish.
3. Explain the distinct scopes of ParseBench, ExtractBench and OmniDocBench using
   checked primary sources and pinned retained snapshots. Separate a published
   aggregate, a matching public subset, an internal acceptance criterion and new
   reference collection. A changed threshold need not require a new corpus.
4. Link the full source inventory and explain input files, pages, annotation
   cases/rules and original documents as different units. Preserve unknown family
   labels and distinguish mechanical inventory, visual inspection and upstream
   statements about human verification.
5. Work through concrete decisions for text/search, structured tables/charts,
   schema-guided extraction and evidence coordinates. Explain why overall scores,
   per-rule averages and business-critical failure rates are different quantities.
6. Teach reference independence, rendition alignment, parser-independent selection,
   paired comparisons, missing/failed outcomes and representation/extractor
   interactions using retained evidence. The synthetic invoice result is a methods
   example, never the principal claim or evidence about real-vendor prevalence.
7. Describe confirmed execution limitations from retained source/receipts: fresh
   processes and converters, forced CPU Marker options, cache/timing boundaries
   and surviving helper processes. Do not infer a measured warm speedup, GPU
   utilization during parsing, energy cost or general SDK incapability.
8. Explain how to specify an internal acceptance evaluation: important document
   conditions and outputs, independent truth, ambiguity, false associations,
   critical errors, attempt denominators, operational limits and when to stop.
   Recommendations are labelled as design choices, not completed experiments.
9. Every material numerical/comparative assertion resolves to a primary source or
   exact retained artifact. Local citations resolve; copied facts are checked
   against actual records; source identities and residual uncertainty are retained
   in one guide evidence record. No parser or grader execution is needed.
10. Update the existing plan, mapped GitHub issues, draft PR and project entry
    points to this scope. Preserve historical implementation and immutable bundles.
    No issue is silently treated as complete merely because its old execution
    requirement was removed. Closing commits still require their verification gates.
11. Benchmark/GPU execution remains disabled in the local policy and the paused
    automation. No corpus acquisition/rerun, native regrading, model import or
    profiling, broad test suite, paid call, sibling PDFSmith change, public-main
    merge, editorial/CMS write, deployment or publication is authorized.
12. Failed source/link/identity verification leaves existing valid evidence and
    disabled execution intact. Unsupported claims are corrected or removed from
    the draft; a missing source is not repaired by fabricating a result or running
    a new experiment. Original output/reference bytes stay unchanged.

## In scope

- Existing-source research and a substantial explanation with worked examples.
- Retained coverage, source/reference, failure and execution evidence.
- Public-benchmark reuse and a practical basis for a future customer evaluation.
- Light text/JSON/hash/link checks, project-local writing, issue/PR maintenance,
  task-branch commits and backup pushes.

## Out of scope

- A new general leaderboard, automatic 208-input screen or full-corpus comparison.
- New parsing, regrading, model/GPU profiling, dependencies or heavyweight tests.
- PDFSmith API repairs, costed provider experiments and new synthetic corpora.
- Website/editorial implementation, publication, release or public-main merge.

## Constraints

Keep all benchmark and GPU work paused. Use only retained data and primary-source
reads. Do not introduce another runner, reporting system or general validation
framework. Preserve inherited dirty work. Public-main merge and publication remain
Stefan's decisions. Reader-facing prose uses plain language, precise evidence
boundaries, no em dashes, and no project-management history as its argument.

## Environment / prior art

The current branch is `codex/benchmark-rebuild`; draft PR #9 contains the retained
engineering work. `parsebench-coverage.md`, the workload index, source measurement,
annotation inventory, invoice failure/reference audits, selection-bias example,
immutable report bundles and frozen PDFSmith source snapshots are the evidence.
The source measurement covers 2078 input paths; visual observations cover 221.
Existing public ParseBench results overlap several local families. ExtractBench
and OmniDocBench provide relevant alternative task/reference contracts.

The registry and prior report remain preserved. They document directional,
prototype and historical tracks alongside the qualified controlled experiment.
They are not relabelled as new production results.

## Existing surface (must not break)

Original sources, outputs, annotations, source/runtime snapshots and immutable
bundles retain their bytes. Prepared sample/full plans remain explicitly deferred.
The local execution policy stays disabled and the overnight heartbeat stays paused.
The guide is a new authored document; generated historical reports are not edited.
Other repositories and unrelated uncommitted work remain untouched.

## Open questions

No decision is needed to write the guide. Editorial approval, public-main merge,
publication and any future experiment are separate decisions. New execution needs
a specified unanswered question and a fresh resource/spend authorization.

## Next actions

No user action is required for this writing work. Benchmark and GPU work stays paused.
