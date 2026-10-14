# Plan: PDF-Bench reconstruction and internal-benchmark design demonstration

This decomposes `spec.md`, seeded by the reconstruction commission and Stefan's
October 14 decision to focus on practical parser selection and teaching teams how
to design their own document benchmark. The first deliverable is this plan and a
self-contained review packet. No substantial implementation starts before actual
GPT and Claude reports are returned and correctness blockers are disposed.

## Gating and implementation boundaries

Registry reconciliation -> qualify source references -> establish the downstream
task contract -> repair execution/provenance -> execute a consequential comparison
-> generate an inspectable report and export. The ordered issues below define one
engineering milestone. Later research coverage and release approvals are separate.
The first invoice run is a worked example, not all-family project completion.

Reuse `pdf_bench/inventory.py`, the existing story generator, BenchmarkRunner,
PDFsmith adapter, caching utilities and atomic persistence. Prefer extending these
surfaces over a second runner, database or parser abstraction. The smoke wrapper
is prior evidence and a useful failure example, not the new architecture.

Existing checked-out base is `bf8285b4cf4e69295eda2391665d54d9077d4d0a`.
Reviewed checkpoint is `d9305d6100e5288fa2fc255e088bfd8e22664b98`.
Dirty inherited files and untracked corpora are preserved. Exact implementation
and evidence hashes, rather than this base label alone, define the review input.
An owned checkpoint must not stage inherited changes incidentally. No source-main
merge, paid call or website/editorial write is included.

## Review dispositions and progress

Before Issue 1, retain both returned reviews unchanged and record each finding,
severity, affected acceptance criterion/issue, disposition and evidence required.
Resolve correctness blockers before the dependent issue. Testable alternatives
can be adopted; optional extensions go to later scope without restarting planning.
Record explicit unresolved disagreements. `progress.txt` records current milestone,
changes, actual checks, next owner action and decisions needed. A review requested
or a prior coordinator check is never recorded as a returned specification review.

## Verification policy

Reproduce defects through existing CLI/generator/runner paths before repairs.
The specific proposed test files below will be created by their issues, not assumed
to exist now. Show red/green for actual producing-code defects, not source-string
assertions or artificial records that the pipeline cannot produce. Timing remains
descriptive until a repeat protocol and resource boundaries justify comparison.

Run focused checks per issue, `uv run ruff format .` and `uv run ruff check .` at
implementation checkpoints, and inspect owned diffs. Preserve unrelated work while
fixing observed hygiene under the reviewed scope. Before code changes, inventory
the inherited lint/test baseline and identify ownership. Do not run global
formatting over another worker's dirty files during review preparation.

### Milestone: `rebuild-1 - Reconciled evidence and a reproducible internal-benchmark example`

**Issue 1 - Reconcile retained runs into one authoritative registry**

Depends on actual external review dispositions. Extend the existing inventory and
replace the story generator's independently maintained SLATE with registry-backed
selection. Reconcile result/config links, checkpoints and merges, input/reference
availability, historical selection, backend and wrapper identity, cache/timing
unknowns and metric coverage. Keep all families and claimed historical values.
Record conflicting descriptions without asserting the entire old run is false.
Do not reconstruct a past version from today's config. Establish an artifact
classification and claim-specific tier with reasons and evidence paths.

Files: existing inventory, story generator, inventory overrides, configuration and
result schemas as necessary; proposed `tests/test_run_registry.py`; generated
registry/appendix under a new versioned evidence directory. Retained results stay
unchanged. Acceptance criteria 2-5 and historical parts of 12-14 apply.

Verify: reproduce generator means with uneven metric coverage and the real SEC
selection/reference-description disagreements. The repaired generator must expose
eligible/scored IDs and missing provenance instead of silently ranking unequal
subsets. `uv run pytest tests/test_inventory.py tests/test_run_registry.py -q`
must pass, including unreadable/unknown schema, duplicate IDs, invalid summary,
missing config, checkpoint classification and failed regeneration preserving the
previous appendix. Registry coverage equals the independently enumerated retained
artifact set. Raw artifact hashes remain unchanged.

### Premises

Input: retained artifacts

| Question | Answer | Kind |
|---|---|---|
| record | One discovered artifact, classified separately from the run it may describe; a result row identifies an input/parser attempt. | definitional |
| absent-record | Missing rows are unknown unless a recorded manifest proves the pair was planned; absence is never success. | definitional |
| ordering-spacing | Directory or JSON row order supplies no ranking or chronology; documented timestamps and derivation links do. | definitional |
| entity-identity | Run/artifact hash, rendition/input identity and backend/config identity distinguish apparently equal filenames. | definitional |
| known-at | Only provenance available from retained bytes or recorded history describes a past run; current observations are separately dated. | definitional |
| institution | The recorded producing pipeline/config and this specification govern interpretation; orientation tier labels are hypotheses. | empirical |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| retained-artifacts-accounted | Every retained artifact is addressable with explicit kind, provenance gaps and claim tier. | Discovery silently misses a file, merges overwrite chronology, or an override conceals missing references. |
| historical-claims-scoped | Historical comparisons expose selection, reference and metric/timing limits beside results. | A generator averages unequal rows or labels a present-day source as the historical source. |

Closes: retained-artifacts.record, retained-artifacts.absent-record, retained-artifacts.ordering-spacing, retained-artifacts.entity-identity, retained-artifacts.known-at, retained-artifacts.institution, retained-artifacts-accounted, historical-claims-scoped

**Issue 2 - Freeze and qualify independent invoice references**

Depends on Issue 1. Use the fixed 100 retained invoice IDs. Inspect actual DOCX
paragraph/table source and metadata, not the current PDF-extracted ground_truth
directory, to establish field and line-item references before parser execution.
Freeze a manifest containing all source/PDF/reference hashes and applicability.
Resolve date, currency, rounding, totals, duplicate rows and header identity by
inspecting source and rendered PDFs. Source-DOCX order is not automatically PDF
reading order. Text similarity remains diagnostic with that limit stated.

Compare available source/backup/PDF-extracted reference versions and report what
can be established about their generators. Retained DOCX source is authoritative
for the new semantic references only after rendition qualification. An unknown
historical reference cannot be retroactively promoted by a new one. Where rerendering
is needed, preserve the old PDF and identify the new rendition/converter version.
Do not rerun random/date-dependent source generators to pretend to recover old
truth. Make all disagreements and independent qualification evidence inspectable.

Files: extend existing invoice builder/reference mechanisms where suitable;
proposed `tests/test_invoice_reference_qualification.py`; frozen run manifest,
semantic references and qualification record in a new run bundle. No original
source/reference is overwritten. Acceptance criteria 6-8 and 15 apply.

Verify: introduce a real generator/converter defect that changes rendered totals
or drops source table content. The actual reference qualification pipeline must
reject the disagreement while preserving valid prior output, and pass on the
correct rendition. Run `uv run pytest tests/test_invoice_reference_qualification.py -q`.
Inspect rendered examples across all observed regions/templates/complexities and
each discrepancy. Every one of the 100 inputs has an eligibility decision before
parser execution. Unresolved truth blocks a strong affected comparison.

### Premises

Input: invoice sources

| Question | Answer | Kind |
|---|---|---|
| record | One retained DOCX/PDF invoice rendition plus source-derived field and line-item facts and a qualification record. | definitional |
| absent-record | Missing or inconsistent source truth is an explicit reference gap, not an inferred parser error or reason to hide the document. | definitional |
| ordering-spacing | Source table order carries row association; harmless formatting is normalized only under the frozen contract. | empirical |
| entity-identity | Invoice ID plus DOCX, rendition and reference hashes; repeated item descriptions do not collapse distinct rows. | definitional |
| known-at | References, applicability and input set are frozen before evaluated parser outputs exist. | definitional |
| institution | Source semantics and displayed PDF content decide truth; metadata and old extraction are cross-checks rather than independent oracles. | empirical |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| references-independent | New task truth is established from qualified sources without evaluated-output leakage. | Reference builder reads parser outputs, a PDF rendition disagrees, or metadata is assumed correct without inspection. |
| reference-generation-preserves | Failed qualification or generation preserves existing valid references and inputs. | Conversion writes over an original PDF or validation occurs after replacing the completed bundle. |

Closes: invoice-sources.record, invoice-sources.absent-record, invoice-sources.ordering-spacing, invoice-sources.entity-identity, invoice-sources.known-at, invoice-sources.institution, references-independent, reference-generation-preserves

**Issue 3 - Establish task scoring that detects wrong associations**

Depends on Issue 2. Specify one downstream extractor over actual parser Markdown/text
and one independent grader over its extracted fields/records. Keep extraction
blind to expected values. Version and freeze normalization, required fields, row
matching, extra/missing row penalties and all-fields/all-records document success.
Test semantic correctness separately from edit similarity/chrF++. Reuse a pinned
established record metric only if its input semantics match; do not implement a
new generic TableRecordMatch framework to satisfy this one invoice task.

No structured rows from an otherwise completed parser is zero task recovery for
eligible records. Unsupported reference semantics is distinct from unsupported
parser capability. Report downstream extractor limitations alongside parser scores.
Make formatting-only acceptable changes pass while wrong values, shifted headers,
ambiguous duplicates and omissions fail. Acceptance criteria 9, 11 and 16 apply.

Files: extend the existing task-evaluation mechanism, proposed
`tests/test_invoice_task_evaluation.py`, frozen extractor/grader protocol and hashes.

Verify: use real produced parser outputs and producing-path mutations that reorder
labels/values, transpose headers, drop/duplicate rows or corrupt an amount. The
task check must fail for those errors even when value tokens remain present, and
pass for correct output and declared harmless formatting. Run
`uv run pytest tests/test_invoice_task_evaluation.py tests/test_local_evaluation.py -q`.
Demonstrate extractor blindness by withholding the reference until extraction ends;
change reference facts and confirm the extracted prediction does not change.

### Premises

Input: extracted invoice records

| Question | Answer | Kind |
|---|---|---|
| record | A prediction contains label/value fields and header-associated line-item records extracted solely from parser output. | definitional |
| absent-record | Missing eligible field or row is a task error; missing reference truth is separately unavailable. | definitional |
| ordering-spacing | Whitespace/currency/date normalization is fixed before execution; row reordering may preserve record semantics but header/value swaps do not. | empirical |
| entity-identity | Run, input and parser/config hashes identify prediction; source row multiplicity remains meaningful even for equal descriptions. | definitional |
| known-at | Predictions precede access to truth for grading; the fixed extraction/normalization contract precedes scored execution. | definitional |
| institution | The declared downstream task and independently frozen source facts define acceptance, not a parser's preferred representation. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| task-checks-association | Task scoring rejects wrong field/record associations without rejecting declared harmless representation changes. | A value-token check passes transposed headers or normalization equates different amounts. |
| extractor-blind | Expected answers cannot affect extracted predictions. | Extractor reads source metadata or uses grader truth as a parsing hint. |

Closes: extracted-invoice-records.record, extracted-invoice-records.absent-record, extracted-invoice-records.ordering-spacing, extracted-invoice-records.entity-identity, extracted-invoice-records.known-at, extracted-invoice-records.institution, task-checks-association, extractor-blind

**Issue 4 - Repair execution identity, cache handling and failure accounting**

Depends on Issue 1; can be designed while Issues 2-3 qualify truth, but execution
of the scored run depends on all three. Extend existing runner/adapter/persistence
to record backend versions/options/source identity, cache/checkpoint mode, planned
attempts, empty outputs, failures/timeouts and duration boundaries. The scored
run explicitly bypasses cache reads/writes and checkpoint reuse. Normal cached
operation must still distinguish output-affecting options/backend identity. Any
reusable checkpoint must validate matching protocol/inputs/references, not only
parser name and doc_id. Unknown old cache timing stays unknown.

Keep separate parser output locations, including same-stem inputs and worker
execution. Record failed durations correctly rather than default zero. Use existing
atomic writer and validate bundle completeness before registering a completed run.
Keep an incomplete attempt journal for interruption/failure, without overwriting
old evidence. Report both PDFsmith metadata versions and exact used backend source;
resolve local dependency identity without editing that sibling's API/metadata.

Files: runner, loader, adapter, cache and persistence where needed; existing runner,
cache/persistence tests and proposed `tests/test_run_provenance.py`. Acceptance
criteria 10-16 apply.

Verify: reproduce stale-cache behavior by changing a real backend option and
submitting the same PDF through the existing adapter; reproduce incompatible
checkpoint reuse through the actual runner. After repair, cached and fresh paths
agree for matched identity and differ or reject when identity changes. Actual
empty/corrupt inputs and an enforced delayed backend control must record distinct
outcomes. Inject serializer and I/O failure through producing code and verify
old completed artifacts remain byte-identical. Run
`uv run pytest tests/test_runner.py tests/test_local_evaluation.py tests/test_run_provenance.py -q`
plus focused existing cache/persistence tests discovered during implementation.
No fixture that only mocks the new logic establishes closure.

### Premises

Input: parser attempts

| Question | Answer | Kind |
|---|---|---|
| record | One planned input/parser/config pair with an explicit execution mode, terminal outcome or incomplete status, and artifact/timing evidence. | definitional |
| absent-record | A planned but absent terminal record means incomplete execution, never a completed success; old manifests may not establish planned work. | definitional |
| ordering-spacing | Execution order and cold/warm effects are recorded; parallel completion order does not change identity or aggregates. | empirical |
| entity-identity | Input/reference/protocol, backend/options and implementation identities decide cache and checkpoint compatibility. | empirical |
| known-at | Manifest/backend identity exists before execution; output/outcome/timing becomes known at completion or interruption and is recorded then. | definitional |
| institution | This run protocol decides applicability, timeout, completion and timing boundaries; PDFsmith's actual installed backend decides implementation identity. | empirical |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| execution-not-silent-replay | Fresh work cannot silently read unrelated cached/checkpoint output. | Cache ignores a backend option/version or a checkpoint accepts changed input/reference bytes. |
| failures-visible | Every planned pair has inspectable terminal or incomplete status, with empty output distinct from failure and unavailable timing distinct from zero. | Exception paths omit records, timeout is inferred only from arbitrary error text, or empty output is counted as task success. |
| bundle-atomic | A failed generation cannot replace a previously valid completed bundle or register an incomplete one as complete. | Registry switches before all artifacts validate or a partial file replaces its previous version. |

Closes: parser-attempts.record, parser-attempts.absent-record, parser-attempts.ordering-spacing, parser-attempts.entity-identity, parser-attempts.known-at, parser-attempts.institution, execution-not-silent-replay, failures-visible, bundle-atomic

**Issue 5 - Execute and reproduce the fixed invoice comparison**

Depends on Issues 2-4. Execute all 100 frozen invoice inputs with pypdf and
pdfplumber on shared bytes, sequentially and without paid calls. Record at least
200 planned primary pairs, plus separately labelled actual corrupt, empty and
enforced-timeout controls. Fixed source fields and line-item records determine the
task score; real parser outputs determine the predictions. Control expectations
come from their producing paths, not benchmark-wide averages.

Export planned, attempted, complete/nonempty, empty, failed, timed-out, incomplete,
reference-eligible and scored counts/IDs. Primary task success includes failed,
timed-out and empty attempts as unsuccessful on eligible inputs. Report paired
quality on matching ID sets and common-success diagnostics separately. Report
historical/new evidence separately, backend/configuration identity, hardware,
resource/time boundaries and individual timings without claiming a speed winner.

Run a second fresh execution over the frozen inputs and offline regrade retained
outputs; input/reference hashes and deterministic aggregates must match or a
precise nondeterminism finding must remain unresolved. Exercise replay from a
different directory with declared dependencies, not absolute local checkout paths.
Strong comparison closure requires resolving reference gaps, not quietly lowering
the denominator. Acceptance criteria 6-14 and 17 apply.

Files: versioned manifest, outputs, attempt journal, run result, replay instructions
and environment snapshot; proposed `tests/test_reconstruction_export.py` integration
checks using the actual run producing path. Do not overwrite run-03 or old results.

Verify: execute the frozen CLI protocol into new run directories; audit every
planned pair and metric denominator from independent artifact enumeration; compare
two fresh runs and a replay. Run `uv run pytest tests/test_reconstruction_export.py -q`.
The reported result is allowed to be a tie, poor performance or a constrained
extractor failure. No score target or favorable finding is required.

### Premises

Input: invoice comparison

| Question | Answer | Kind |
|---|---|---|
| record | A frozen input/parser attempt with task and diagnostic metrics and a source-linked reference decision. | definitional |
| absent-record | Missing planned attempts remain incomplete; absent applicable metrics expose a reason and denominator, never fabricated zero or success. | definitional |
| ordering-spacing | Fixed population and task apply to both parsers; comparable scores use identical IDs and timing cold/order context remains explicit. | empirical |
| entity-identity | Run ID and artifact hashes identify primary population separately from controls and any rerendered input. | definitional |
| known-at | Eligibility is frozen before outputs; reported observations derive only from recorded executed attempts and qualified truth. | empirical |
| institution | Frozen protocol defines population and scores; the retained corpus cannot stand for all real vendors or current paid parsers. | definitional |

### Claims

| Id | Claim | How it could be false | Kind |
|---|---|---|---|
| invoice-results-reproducible | Reported task/coverage aggregates and per-attempt duration observations reproduce from the actual run artifacts under declared boundaries. | Failed calls disappear, regrading reads new references, timing is cache replay, or relocated replay uses a different backend. | measured |

### Measured: invoice-results-reproducible

| Question | Answer |
|---|---|
| limiter | Counts are bounded by fixed planned/eligible inputs; timing observations depend on backend parsing and declared machine conditions, verified during the run rather than asserted from code. |
| alternatives | Cache replay, cold imports, downstream extractor behavior, source mismatch, failed fast calls and machine contention can alter apparent performance; each is recorded or tested separately. |
| work-happened | Retain input/output hashes, terminal attempt records and semantic prediction checks; regrade used outputs and confirm both parsers actually ran with cache reads/writes disabled. |
| configured-alike | Identical PDF bytes/reference/task/normalization, fixed per-parser versions/options, sequential uncached mode and declared timeout/resource limits; report configuration comparisons rather than isolated algorithm merit. |
| within-limits | Successes cannot exceed eligible/planned counts; scored IDs are subsets of eligible IDs; positive call durations and total sequential wall time must reconcile with declared measurement regions. No speedup claim follows from single-call observations. |

Closes: invoice-comparison.record, invoice-comparison.absent-record, invoice-comparison.ordering-spacing, invoice-comparison.entity-identity, invoice-comparison.known-at, invoice-comparison.institution, invoice-results-reproducible

**Issue 6 - Generate benchmark-design lessons, appendix and integration export**

Depends on Issues 1 and 5. Generate the appendix and structured export from the
authoritative registry and qualified run. Write a project-local technical report
whose worked example teaches internal-benchmark design: define the team's task
and distribution, assess corpus fit, choose and validate reference truth, freeze
extraction/scoring, retain failures, and interpret results within operating limits.
Use actual historical selection/reference/cache mistakes and new counterexamples
to show which conclusions change. Distinguish observed findings, historical
lessons and untested recommendations; include actionable reproducible instructions.

Include all retained families in their tiers, plus bounded next protocols below.
Explain why semantic metrics and dataset size alone do not establish use-case fit.
Acknowledge ParseBench without inventing gaps in its capabilities or duplicating
its broad leaderboard. Record reusable upstream interfaces/metrics and what still
requires local tasks/references. Link the checked retained benchmark-interpretation
article for editorial context, with no manuscript/CMS changes.

Files: existing story/export generator and inventory-driven outputs; project-local
technical report and example protocol; one concise `integration-handoff.txt`.
Export claim objects link run/artifact hashes/JSON pointers, input/reference
provenance, denominators, versions/options/cache/time boundaries, tier and supported
interpretation. Consumer renderers receive paths/hashes rather than hidden absolute
runtime dependencies. Acceptance criteria 18-21 apply.

Verify: every reported number regenerates from source-linked rows; independently
recompute selected numerator/denominator pairs and test stale/missing/tampered
artifacts through the actual generator. `uv run pytest tests/test_reconstruction_export.py tests/test_inventory.py -q`
must pass. Review the report against actual results and run the documented replay
from its instructions. Export preservation and unknown/null handling remain tested.
Handoff identifies exact commit, bundle hashes, visitor task and claim limits.

### Premises

Input: report evidence

| Question | Answer | Kind |
|---|---|---|
| record | A report/export claim with run/artifact/JSON-pointer provenance, exact population, task/metric, tier and limitation. | definitional |
| absent-record | Missing evidence prevents that numerical claim; diagnostic history and supported non-numerical lessons remain usable. | definitional |
| ordering-spacing | Families and task protocols are separate sections; no global rank or undated mixing of old and new numbers. | definitional |
| entity-identity | A claim's run ID, source/artifact hashes and pointer identify the underlying measurement, not a display name. | empirical |
| known-at | Claims are dated by actual executed evidence; author review and publication state remain separate. | definitional |
| institution | Source owner verifies evidence; editorial and website owners decide synthesis/rendering; Stefan owns public release and spending approval. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| report-inspectable | An engineer can inspect and reproduce each declared result and understand the decision it informs. | Numbers lack matching pointers/denominators, instructions fail offline, or failures are visible only in hidden artifacts. |
| design-lessons-demonstrated | The worked example explains internal-benchmark design through actual decisions and counterexamples. | The report offers only limitation prose, presents a template as validated on real vendors, or invents an operational result. |

Closes: report-evidence.record, report-evidence.absent-record, report-evidence.ordering-spacing, report-evidence.entity-identity, report-evidence.known-at, report-evidence.institution, report-inspectable, design-lessons-demonstrated

## Bounded follow-on scope, separate from the first engineering milestone

The following are protocols to qualify, not promised October results. Each gets
its own reviewed input/reference/configuration manifest before execution. No paid
call, large download or model installation is assumed available.

| Track | Fixed candidate inputs and task | Reference and comparison | Completion and gate |
|---|---|---|---|
| Scans/OCR | Twenty qualified invoices selected by source metadata across observed templates/complexities, rendered as image-only PDFs at 150 and 300 dpi; same field/row recovery task. | Reuse independently qualified source facts; keep paired digital/raster hashes. Compare the no-OCR baseline with two installed local OCR-capable configurations after actual capability/version checks. | Report paired task recovery, OCR omissions, empties/timeouts and page counts. If suitable local models are absent, prepare the exact model/download/resource request instead of claiming OCR coverage. |
| Complex tables/charts | Thirty pinned ParseBench table examples selected by reference-defined header/merge/multipage categories, plus a separately scoped ten-chart probe. | Assess reuse of pinned upstream GriTS/record matching and chart rules with declared normalization/applicability; inspect annotations before outputs. Compare two suitable available local configurations on shared inputs. | Scores distinguish detected, recovered, wrong associations and unsupported reference forms. No access to annotated answers during extraction. Document source/license/annotation limits. Chart incapability is a measured outcome, not exclusion. |
| Presentations/decks | Qualify the ten retained synthetic source-first investor decks; task is slide-boundary/title/bullet ordering and exact chart/table facts where source truth exists. | Preserve PPTX/PDF pair identity; independently qualify rendering and source references. Compare two suitable local parsers. Keep public legacy decks as a distinct directional track. | Report source/template realism and task failures; do not call the synthetic ten-deck result representative of corporate presentations. Resolve missing pairs before strong scores. |
| arXiv | Qualify the ten retained academic inputs and exact source revisions; task is reading order and equation/table recovery on those papers. | Audit LaTeX/Pandoc source-to-PDF agreement and unsupported formulas; compare two suitable local configurations. Never use HTML from another paper revision as exact truth. | Separate equation/text/structure denominators and source-coverage gaps. Technical-paper conclusions remain separate from business-invoice recommendations. |
| Cloud/frontier | Choose one of the qualified task protocols only after a specific remaining decision requires paid comparison. | Exact provider/model/SDK/config/prompt, shared frozen inputs, retries/cache policy and cost accounting. Inspect a one-document pilot first. | Stefan approves maximum total spend and stop rules before calls. Report failures and actual costs; no historical paid pilot becomes a current winner. |

SEC follow-on can use a parser-independent source/provenance rule over the retained
catalog, audited PDF/HTML spans and a fixed information-extraction task. It does
not reuse the pypdfium2 score threshold as a new impartial selection rule.

## Next actions

Stefan submits the review packet to GPT and Claude and returns both reports.
No spending, publication or deployment decision is needed for review preparation.
