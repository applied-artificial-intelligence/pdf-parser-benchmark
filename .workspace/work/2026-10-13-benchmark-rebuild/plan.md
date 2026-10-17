# Plan: Assess ParseBench coverage and compare the available PDFSmith parsers

Revision 4, October 17, expands completion after Stefan rejected the two-parser demonstration as insufficient. Issues 1-8 preserve implemented groundwork; Issues 9-11 are required before this reconstruction is considered complete. Full ParseBench source assessment and all available local parser families are in scope.

Revision 3 incorporates Stefan's October 15 scope confirmation. Assess ParseBench
coverage before choosing a relevant public subset or justifying custom evaluation.
The existing invoice example demonstrates a specific task without presuming a
public-benchmark gap. Revision 2 incorporated GPT and Fable reports, with dispositions
in `review-dispositions.txt`. This decomposes `spec.md`, seeded by the commission and Stefan's
October 14 decision to focus on practical parser selection and teaching teams how
to design their own document benchmark. The first deliverable is this plan and a
self-contained review packet. Both reports recommend bounded revision. Registry
work and non-scored execution repair can proceed under the amended contract.
Scored-run closure requires qualified references, a frozen blind task/extractor
protocol, complete attempt accounting and actual regression evidence.

## Gating and implementation boundaries

Assess public-benchmark fit and snapshot retained evidence -> qualify references and
freeze extractor/grader -> repair execution/provenance -> execute both comparisons
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

Both returned reviews are retained unchanged. `review-dispositions.txt` records each finding,
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

Format and lint owned files, run non-mutating repository-wide checks, and inspect
owned diffs at checkpoints. Preserve unrelated dirty work. Record inherited findings
separately from new regressions and repair relevant inherited defects as those files
enter reviewed scope. Global formatting or cleanup of another worker's files is
not a hidden milestone dependency.

### Milestone: `rebuild-1 - Assessed ParseBench coverage and PDFSmith parser comparison`

**Issue 1 - Assess ParseBench coverage against meaningful business workloads**

Inventory all five annotation groups at pinned code/data revisions and reconcile
page, document and case counts with launch/current primary sources. Preserve source
URLs, revision IDs, file hashes and original domain/type labels. Inspect actual
source pages and rules across declared domains, document forms and dimensions.
Build a traceable workload-fit matrix covering reports, contracts/policies,
transactional records/forms, presentations and technical documents, including
language, scan/digital form, multipage context and downstream information needs.
These are practical workload categories, not a representative survey of business.
Unknown labels or uninspected documents stay unknown, not absent. Separate source
availability, annotation presence and whether the metric tests the needed behavior.

For each substantive coverage claim retain document/case IDs, annotation pointers,
inspection evidence and relevant evaluator behavior. Distinguish present, partial,
not observed and unknown. A gap requires inspection of the plausible matching
strata and a consequential business task; no marginal examples are manufactured.
Assess source rights and limits separately from code licensing. Recommend direct
use, matched subset, or additional internal task/data with reasons. Do not claim a
percentage of all business workloads without a defined weighted population.
Select and freeze the first public-run subset only after this assessment. The
invoice comparison remains a controlled teaching example, not proof that ParseBench
omits invoice processing. Acceptance criteria 22-24 apply.

Files: proposed `pdf_bench/parsebench.py`, `tests/test_parsebench.py`, pinned
assessment manifest and project-local `parsebench-coverage.md` in this work unit.
Keep downloaded originals outside version control; commit reproducible acquisition
instructions, hashes, derived inventory and inspection records. Existing upstream
annotation/evaluation methods remain authoritative.

Verify: acquire the full pinned annotation inventory, reconcile independent unique
source counts and inspect stratified real pages. Test identity across groups,
page/document/case counting, unknown labels and preservation of source attributes
through the real acquisition/inventory path. Corrupt or changed downloads must
leave prior valid assessment artifacts intact. `uv run pytest tests/test_parsebench.py -q`
must pass with producing-code mutation witnesses. The fit report cites exact
inspected evidence and makes no unsupported global coverage percentage.

### Premises

Input: public benchmark cases

| Question | Answer | Kind |
|---|---|---|
| record | One upstream annotated case within a capability group; source documents and pages may be shared across cases/groups. | definitional |
| absent-record | Missing labels or observations mean unknown coverage; absence in this inventory alone does not establish workload exclusion. | definitional |
| ordering-spacing | File order and repeated annotations do not determine prevalence; document/page identity and declared sampling do. | empirical |
| entity-identity | Pinned dataset revision, group, case ID, source path/pages and hashes distinguish source documents from annotations. | empirical |
| known-at | Original annotations precede parser execution; inspection and fit judgments are dated before subset selection and scores. | definitional |
| institution | Upstream annotation/evaluator definitions govern public metrics; the explicitly defined business workload governs relevance. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| public-inventory-faithful | The inventory accounts for every pinned annotated case without counting shared sources as independent documents. | A group is omitted, one case is silently lost, or page fragments are counted as whole independent documents. |
| benchmark-fit-evidenced | Recommendations distinguish observed coverage from uncertainty and justify additional evaluation with a meaningful task mismatch. | A missing type label is treated as proof of absence, a documented capability is ignored, or global prevalence is invented. |

Closes: public-benchmark-cases.record, public-benchmark-cases.absent-record, public-benchmark-cases.ordering-spacing, public-benchmark-cases.entity-identity, public-benchmark-cases.known-at, public-benchmark-cases.institution, public-inventory-faithful, benchmark-fit-evidenced

**Issue 2 - Reconcile retained runs into one authoritative registry**

Returned reviews and dispositions authorize this issue. Extend the existing inventory and
replace the story generator's independently maintained SLATE with registry-backed
selection. Reconcile result/config links, checkpoints and merges, input/reference
availability, historical selection, backend and wrapper identity, cache/timing
unknowns and metric coverage. Keep all families and claimed historical values.
Freeze the inventory input boundary before generating new exports. Preserve
original counters/labels beside independently derived counts and claim dispositions.
Record conflicting descriptions without asserting the entire old run is false.
Do not reconstruct a past version from today's config. Establish an artifact
classification and claim-specific tier with reasons and evidence paths.

Files: existing inventory, story generator, inventory overrides, configuration and
result schemas as necessary; proposed `tests/test_run_registry.py`; generated
registry/appendix under a new versioned evidence directory. Retained results stay
unchanged. Acceptance criteria 2-5 and historical parts of 12-14 apply.

Verify: use the real SEC commercial summary (15 rows, 14 actual successes/one
failure versus declared 14 successes/13 failures), screening title "All 89" versus
320 rows, and invoice reference-description disagreement as red fixtures.
Reproduce generator means with uneven metric coverage and the real SEC
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

**Issue 3 - Freeze and qualify independent invoice references**

Can begin after snapshotting retained inputs; exhaustive historical recovery in
Issue 2 need not finish first. Define the controlled invoice-to-records use case
and public schema first. Use the fixed 100 retained invoice IDs. Inspect actual DOCX
paragraph/table source and metadata, not the current PDF-extracted ground_truth
directory, to establish field and line-item references before parser execution.
The unscored pre-run inventory records 182 pages, six source template/complexity
cells, 696 rows, three header schemas and no observed merges. Economy description
retains embedded price/unit text rather than inventing a separate column.
Freeze a manifest containing source/PDF/reference/protocol hashes and applicability.
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
Current DOCX extraction reproduces all 100 backup references and none of the 100
current references (reference-reconstruction-check.json); historical bytes actually
used remain unknown. Qualify each rendition with unscored PyMuPDF diagnostics plus
all-page rendered review and task-association checks. Producer/timestamps cannot
establish content identity. Changed source/PDF/reference/protocol bytes invalidate
qualification. Displayed transcription truth is distinct from arithmetic accuracy.

Files: extend existing invoice builder/reference mechanisms where suitable;
proposed `tests/test_invoice_reference_qualification.py`; frozen run manifest,
semantic references and qualification record in a new run bundle. No original
source/reference is overwritten. Acceptance criteria 6-8 and 15 apply.

Verify: introduce a real generator/converter defect that changes rendered totals
or drops source table content. The actual reference qualification pipeline must
reject the disagreement while preserving valid prior output, and pass on the
correct rendition. Run `uv run pytest tests/test_invoice_reference_qualification.py -q`.
Replace an already-qualified PDF through actual finalization; stale qualification
must fail. Inspect all rendered pages, observed source/layout cells and discrepancies.
Every one of the 100 inputs has an eligibility decision before
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

**Issue 4 - Establish task scoring that detects wrong associations**

Depends on Issue 3. Specify one downstream extractor over actual parser Markdown/text
and one independent grader over its extracted fields/records. Keep extraction
blind to all source/metadata/document-ID answer lookups; persist predictions before
grading. Version and freeze normalization, required fields, row
matching, extra/missing row penalties and all-fields/all-records document success.
Test semantic correctness separately from edit similarity/chrF++. Reuse a pinned
established record metric only if its input semantics match; do not implement a
new generic TableRecordMatch framework to satisfy this one invoice task. Use exact
multiset matching of complete displayed-column records, preserving duplicates,
currency markers, units and Decimal values. Do not repair wrong associations to
maximize a score. Initial development IDs are invoice_001 through invoice_006,
the first observed example of each source template/complexity cell, plus smoke
fixtures. Freeze the extractor before scoring; later changes version the protocol
and require comparable regrading. These retained inputs are not an unseen test set.

No structured rows from an otherwise completed parser is zero task recovery for
eligible records. Unsupported reference semantics is distinct from unsupported
parser capability. Report downstream extractor limitations alongside parser scores.
Run a faithful parser-independent representation control with its supported-format
scope stated. Audit disagreements and a stratified sample of shared failures, at
least 40 failure cases if available; allow mixed/unknown attribution rather than
inventing a sole parser cause.
Make formatting-only acceptable changes pass while wrong values, shifted headers,
ambiguous duplicates and omissions fail. Acceptance criteria 9, 11 and 16 apply.

Files: extend the existing task-evaluation mechanism, proposed
`tests/test_invoice_task_evaluation.py`, frozen extractor/grader protocol and hashes.

Verify: use real produced parser outputs and producing-path mutations that reorder
labels/values, transpose headers, drop/duplicate rows or corrupt an amount. The
task check must fail for those errors even when value tokens remain present, and
pass for correct output and declared harmless formatting. Run
`uv run pytest tests/test_invoice_task_evaluation.py tests/test_local_evaluation.py -q`.
Demonstrate blindness in a subprocess with gold references, metadata, DOCX,
original paths and answer constants inaccessible. Change gold labels, facts and
row counts; prediction bytes cannot change. Blank/corrupt actual parser output;
predictions must change appropriately. Grader tests use independent literal
predictions; extractor positives use faithful representations and real outputs.

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

**Issue 5 - Repair execution identity, cache handling and failure accounting**

Depends on Issue 2; can be designed while Issues 3-4 qualify truth, but execution
of the scored run depends on all three. Extend existing runner/adapter/persistence
to record backend versions/options/source identity, cache/checkpoint mode, planned
attempts, empty outputs, failures/timeouts and duration boundaries. The scored
run uses the actual PdfsmithAdapter with explicit bypass of cache reads/writes and
checkpoint reuse. Normal cached
operation must still distinguish output-affecting options/backend identity. Any
reusable checkpoint must validate matching protocol/inputs/references, not only
parser name and doc_id. Unknown old cache timing stays unknown.

Persist/hash exactly 200 unique planned pairs before capability filtering and
initialization. Separate parse/prediction/grading outcomes. Reject unknown required
metrics before execution; required grader exceptions invalidate affected claims,
and optional unavailability carries a reason. Empty output and enforced typed
timeout have explicit outcomes; error-text substrings do not classify timeout.
Started-call error duration uses a monotonic clock. Missing terminal rows are
incomplete. Keep exclusive output locations per attempt, including same-stem inputs and worker
execution. Record failed durations correctly rather than default zero. Use existing
atomic writer and validate bundle completeness before registering a completed run.
Keep an incomplete attempt journal for interruption/failure, without overwriting
old evidence. Stop timed-out work before it can mutate finalized output. Validate
checkpoint protocol/population identity, foreign/duplicate membership and counters
before import; unsafe reuse stays disabled until repaired. Stage-specific identities
allow corrected truth to trigger regrading without unnecessary reparsing.
Report both PDFsmith metadata versions and exact used backend source;
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
Test changed PDF/reference bytes and extractor/metric definitions under the same
IDs, foreign/duplicate checkpoints, same-stem/configuration collisions through
parallel dispatch, and equality of graded/hashed/exported bytes. A controlled
delayed backend tests the timeout mechanism, not parser quality; an ordinary error
containing "exceeded" must not be classified as timeout. Finalization uses a new
incomplete directory, validated hashes/outcomes/pairs and completion manifest last,
then directory finalization and atomic registry-pointer replacement. Inject errors
after intermediate generation, at output writing, before completion and before
registry replacement, including missing required artifacts despite valid JSON.
No transaction service or fixture that only mocks new logic establishes closure.

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

**Issue 6 - Execute and reproduce the fixed invoice comparison**

Depends on Issues 3-5. Execute all 100 frozen invoice inputs with pypdf and
pdfplumber on shared bytes, sequentially and without paid calls. Record exactly
200 unique planned primary pairs per execution, plus separately labelled actual corrupt, empty and
enforced-timeout controls. Fixed source fields and line-item records determine the
task score; real parser outputs determine the predictions. Control expectations
come from their producing paths, not benchmark-wide averages.

Export planned, attempted, complete/nonempty, empty, failed, timed-out, incomplete,
reference-eligible and scored counts/IDs. Primary task success includes failed,
timed-out and empty attempts as unsuccessful on eligible inputs. Report paired
quality on matching ID sets and common-success diagnostics separately. Report
historical/new evidence separately, backend/configuration identity, hardware,
resource/time boundaries and individual timings without claiming a speed winner.
Freeze document task, field micro and record precision/recall/F1 denominators as
defined by the specification. An asymmetric eligible-input failure/timeout and an
all-failed parser must not remove inputs or inflate scores. Required evaluation
failure invalidates an affected aggregate rather than removing its hard examples.

Run a second fresh execution over the frozen inputs and offline regrade retained
outputs; input/reference hashes, per-document normalized predictions/outcomes and
deterministic aggregates must match or a
precise nondeterminism finding must remain unresolved. Exercise replay from a
different directory with declared dependencies, not absolute local checkout paths.
Offline grading forbids parser imports, original answer paths, network and ambient
cache access. Fresh relocation separately uses retrievable immutable backend source
or package artifacts and checks versions/hashes; hashes alone cannot rebuild code.
Duration equality is not required, and mismatched implementation is not reproduction.
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

**Issue 7 - Execute a pinned ParseBench comparison with upstream evaluators**

Depends on Issues 1 and 5. Use the assessment to freeze relevant public cases,
initially targeting 30 content-faithfulness and 20 table cases. Publish selection
rules, IDs, source/page hashes, strata, exclusions and fit limitations before
parser execution. Use suitable local configurations on identical input bytes.
Integrate pinned upstream test-case/output interfaces and native deterministic
content/table evaluation, preserving normalization and metric versions. Do not
reimplement a similar score and label it ParseBench. Confirm source rights/access
and dependencies first. No paid parsing, normalization or judge calls.

Retain planned/actual attempts, failures, output-format limitations, denominator
and detailed upstream metrics per case. Report each dimension separately. Repeat
and offline regrade using retained outputs and pinned dependencies. No equivalence
to the published full leaderboard or claims across unexecuted dimensions. Compare
public-case findings with the separately defined invoice task only where the
measured quantities support the comparison. Integration failure is an explicit
finding rather than a substituted metric. Acceptance criteria 22-24 apply.

Files: extend `pdf_bench/parsebench.py`, shared execution/provenance surfaces,
`tests/test_parsebench.py`, immutable run artifacts and replay protocol.

Verify: execute two local parsers through real adapters and native upstream
scoring; independently enumerate every planned pair and recompute selected metrics
with upstream evaluators. Persist predictions before grading and deny reference
access to parser execution. Regrade relocated retained outputs with network and
parser calls unavailable. `uv run pytest tests/test_parsebench.py -q` must detect
missing attempts, changed native score/protocol identities and stale source bytes.

### Premises

Input: public comparison

| Question | Answer | Kind |
|---|---|---|
| record | One frozen case/pipeline attempt with native per-dimension metrics and execution evidence. | definitional |
| absent-record | Missing required output is failed or incomplete, never silently excluded from the planned denominator. | definitional |
| ordering-spacing | Selection precedes scores and comparative metrics use matching case populations. | empirical |
| entity-identity | Case/source/output, pipeline and upstream evaluator revision hashes identify each measurement. | empirical |
| known-at | Fit/eligibility and protocol freeze precede inference; scores derive from retained outputs afterward. | definitional |
| institution | Pinned upstream evaluator defines ParseBench metric semantics; our declared subset limits interpretation. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| native-public-comparison | Local results use the actual pinned upstream evaluators on identical selected inputs with inspectable failures. | A proxy metric replaces upstream scoring, reference data leaks into parsing or failed cases disappear. |
| public-results-regrade | Retained outputs reproduce deterministic per-case native scores under the frozen evaluation protocol. | Regrading reads changed inputs, uses different normalization or requires live parser/API access. |

Closes: public-comparison.record, public-comparison.absent-record, public-comparison.ordering-spacing, public-comparison.entity-identity, public-comparison.known-at, public-comparison.institution, native-public-comparison, public-results-regrade

**Issue 8 - Generate benchmark-fit findings, design lessons and integration export**

Depends on Issues 1, 2, 6 and 7. Generate the appendix and structured export from the
authoritative registry and qualified run. Write a project-local technical report
whose worked example teaches internal-benchmark design: define the team's task
and distribution, assess corpus fit, choose and validate reference truth, freeze
extraction/scoring, retain failures, and interpret results within operating limits.
Use actual historical selection/reference/cache mistakes and new counterexamples
to show which conclusions change. Report the six observed source template/complexity
cells and independently inspected layouts rather than treating 100 fills as 100
independent layout trials. State a conditional pipeline decision, tie or integration
failure from the measured task. Distinguish observed findings, historical
lessons and untested recommendations; include actionable reproducible instructions.

Include all retained families in their tiers, plus bounded next protocols below.
Explain why semantic metrics and dataset size alone do not establish use-case fit.
Use the full coverage assessment and actual ParseBench comparison to explain
when its relevant subset suffices and when meaningful task/distribution mismatch
requires additional evaluation. Do not presume gaps or duplicate its leaderboard. Assess ExtractBench's schema/value/record/failure contracts
against this invoice-specific protocol without importing its generic assignment
framework or executing another benchmark. Record reusable upstream interfaces/metrics and what still
requires local tasks/references. Link the checked retained benchmark-interpretation
article for editorial context, with no manuscript/CMS changes.

Files: existing story/export generator and inventory-driven outputs; project-local
technical report and example protocol; one concise `integration-handoff.txt`.
Export claim objects link run/artifact hashes/JSON pointers, input/reference
provenance, denominators, versions/options/cache/time boundaries, tier and supported
interpretation. Consumer renderers receive paths/hashes rather than hidden absolute
runtime dependencies. Acceptance criteria 18-24 apply.

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

**Issue 9 - Complete the ParseBench source and capability coverage assessment**

Acquire all pinned source inputs using verified upstream identities and retained SHA256 bytes. Extend the existing ParseBench inventory with actual page counts, text/scan properties, content-evidenced family classification, source concentration and explicit unresolved labels. Audit consequential and ambiguous strata through rendered sources. Explain the exact text, table, chart, formatting and grounding contracts and compare relevant OmniDocBench/ExtractBench contracts using primary sources. Deliver an explicit reuse/gap judgment, not a global business-coverage percentage. No new synthetic corpus without a consequential demonstrated mismatch.

Files: extend `pdf_bench/parsebench.py` or a narrowly scoped coverage module, `tests/test_parsebench_coverage.py`, source inventory/inspection evidence and the existing coverage report. Verify full membership, actual source-byte checks, unknown classifications, dimension semantics and failure atomicity. Run the real acquisition/classification on the complete corpus. Tests must reject omitted sources and mismatched bytes without replacing a valid inventory.

### Premises

Input: public source coverage

| Question | Answer | Kind |
|---|---|---|
| record | A pinned source or planned input/configuration result with its actual bytes and contract. | definitional |
| absent-record | Missing evidence is unknown or incomplete, never an omitted difficult case or an assumed success. | definitional |
| ordering-spacing | Source order and repeated annotation groups do not establish prevalence or independent documents. | definitional |
| entity-identity | Dataset revision, input hash, pipeline options and source/runtime identities bind each result. | definitional |
| known-at | Membership and configuration precede scored outputs; subsequent repairs create a new execution identity. | definitional |
| institution | Upstream evaluator semantics define native scores; declared business tasks define fitness; Stefan controls paid runs and release. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| public-source-coverage-complete | Every annotated source has an evidence-bearing coverage record and the assessment distinguishes documented measurement scope from an unproven corpus gap. | A source/failure/dimension is silently omitted, identities change, or an unsupported conclusion is asserted. |

Closes: public-source-coverage.record, public-source-coverage.absent-record, public-source-coverage.ordering-spacing, public-source-coverage.entity-identity, public-source-coverage.known-at, public-source-coverage.institution, public-source-coverage-complete

**Issue 10 - Execute the PDFSmith local roster through all ParseBench dimensions**

Depends on Issue 9 source identity; readiness work can overlap acquisition. Inventory the entire current PDFSmith backend registry without invoking paid services. Exercise every local backend on actual public sources; distinguish installed, usable, missing runtime/model, incompatible integration and paid-only. Freeze actual code/configuration/dependency/model identities. Extend the existing comparison path beyond its two-parser and two-dimension assumptions, using pinned upstream evaluators across text, tables, charts, formatting and grounding. Preserve native output contracts: Markdown-only PDFSmith does not magically expose grounding. Record unsupported contracts beside native scores. Do not silently relabel native direct-SDK results as PDFSmith results. Repair feasible benchmark/dependency issues in an isolated task runtime, preserving sibling ownership.

Files: existing comparison/evaluation modules and focused roster tests. Verify actual local parser output reaches the native evaluators, paid integrations are never initialized, parser options/identities are preserved, output-lacking capabilities remain visible, and required evaluator errors invalidate completeness. Execute the full pinned input population for available local backends. Use predeclared initialization failure policies rather than burning thousands of identical failed calls; retain unstarted membership separately. Fresh outputs and a representative offline regrade must agree.

### Premises

Input: public roster execution

| Question | Answer | Kind |
|---|---|---|
| record | A pinned source or planned input/configuration result with its actual bytes and contract. | definitional |
| absent-record | Missing evidence is unknown or incomplete, never an omitted difficult case or an assumed success. | definitional |
| ordering-spacing | Source order and repeated annotation groups do not establish prevalence or independent documents. | definitional |
| entity-identity | Dataset revision, input hash, pipeline options and source/runtime identities bind each result. | definitional |
| known-at | Membership and configuration precede scored outputs; subsequent repairs create a new execution identity. | definitional |
| institution | Upstream evaluator semantics define native scores; declared business tasks define fitness; Stefan controls paid runs and release. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| public-roster-execution-complete | The comparison includes the available local parser families, the full declared population and every dimension, with failures and unsupported output contracts explicit. | A source/failure/dimension is silently omitted, identities change, or an unsupported conclusion is asserted. |

Closes: public-roster-execution.record, public-roster-execution.absent-record, public-roster-execution.ordering-spacing, public-roster-execution.entity-identity, public-roster-execution.known-at, public-roster-execution.institution, public-roster-execution-complete

**Issue 11 - Deliver useful parser results and a public-benchmark recommendation**

Depends on Issues 9-10. Replace the two-parser demonstration as the report's principal result with generated full-population local comparisons. Report native dimensions separately, family diagnostics and failure counts with exact denominators. Inspect source/output examples that explain differences, including charts, scanned content, tables, formatting and grounding. Clearly distinguish PDFSmith output limitations from underlying SDK capabilities. Answer whether ParseBench supplies the needed ground truth, which meaningful needs require another benchmark or additional internal cases, and what readers can choose using the new results. Preserve historical and invoice work as supporting examples. Prepare an exact paid-run proposal only for unresolved consequential comparisons, with provider/configuration, shared inputs and a spending ceiling to approve before calls. Keep the PR draft until the expanded acceptance criteria are met.

Files: existing source report/export path, coverage report, runtime/result checkpoints and focused result aggregation tests. Verify complete membership, correct dimension/family denominators, no silent failure omission, and source-linked recommendation examples. Regrade retained outputs independently and recompute published tables before issue closure. Run focused checks, core lint/types and the complete test suite; preserve unrelated dirty files.

### Premises

Input: public results assessment

| Question | Answer | Kind |
|---|---|---|
| record | A pinned source or planned input/configuration result with its actual bytes and contract. | definitional |
| absent-record | Missing evidence is unknown or incomplete, never an omitted difficult case or an assumed success. | definitional |
| ordering-spacing | Source order and repeated annotation groups do not establish prevalence or independent documents. | definitional |
| entity-identity | Dataset revision, input hash, pipeline options and source/runtime identities bind each result. | definitional |
| known-at | Membership and configuration precede scored outputs; subsequent repairs create a new execution identity. | definitional |
| institution | Upstream evaluator semantics define native scores; declared business tasks define fitness; Stefan controls paid runs and release. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| public-results-assessment-complete | The final recommendation follows inspected coverage and executed parser results rather than issue completion or synthetic examples alone. | A source/failure/dimension is silently omitted, identities change, or an unsupported conclusion is asserted. |

Closes: public-results-assessment.record, public-results-assessment.absent-record, public-results-assessment.ordering-spacing, public-results-assessment.entity-identity, public-results-assessment.known-at, public-results-assessment.institution, public-results-assessment-complete

## Retained follow-on candidates, subordinate to the expanded public comparison

The public comparison now includes available local OCR, tables/charts and other dimensions. These earlier custom-corpus candidates remain secondary; they cannot replace the full public assessment and comparison. Paid calls still require approval.

| Track | Fixed candidate inputs and task | Reference and comparison | Completion and gate |
|---|---|---|---|
| Scans/OCR | Twenty qualified invoices selected by source metadata across observed templates/complexities, rendered as image-only PDFs at 150 and 300 dpi; same field/row recovery task. | Reuse independently qualified source facts; keep paired digital/raster hashes. Compare the no-OCR baseline with two installed local OCR-capable configurations after actual capability/version checks. | Report paired task recovery, OCR omissions, empties/timeouts and page counts. If suitable local models are absent, prepare the exact model/download/resource request instead of claiming OCR coverage. |
| Complex tables/charts | Additional pinned ParseBench table categories beyond the executed subset, plus a separately scoped ten-chart probe. | Assess reuse of pinned upstream GriTS/record matching and chart rules with declared normalization/applicability; inspect annotations before outputs. Compare two suitable available local configurations on shared inputs. | Scores distinguish detected, recovered, wrong associations and unsupported reference forms. No access to annotated answers during extraction. Document source/license/annotation limits. Chart incapability is a measured outcome, not exclusion. |
| Presentations/decks | Qualify the ten retained synthetic source-first investor decks; task is slide-boundary/title/bullet ordering and exact chart/table facts where source truth exists. | Preserve PPTX/PDF pair identity; independently qualify rendering and source references. Compare two suitable local parsers. Keep public legacy decks as a distinct directional track. | Report source/template realism and task failures; do not call the synthetic ten-deck result representative of corporate presentations. Resolve missing pairs before strong scores. |
| arXiv | Qualify the ten retained academic inputs and exact source revisions; task is reading order and equation/table recovery on those papers. | Audit LaTeX/Pandoc source-to-PDF agreement and unsupported formulas; compare two suitable local configurations. Never use HTML from another paper revision as exact truth. | Separate equation/text/structure denominators and source-coverage gaps. Technical-paper conclusions remain separate from business-invoice recommendations. |
| Cloud/frontier | Choose one of the qualified task protocols only after a specific remaining decision requires paid comparison. | Exact provider/model/SDK/config/prompt, shared frozen inputs, retries/cache policy and cost accounting. Inspect a one-document pilot first. | Stefan approves maximum total spend and stop rules before calls. Report failures and actual costs; no historical paid pilot becomes a current winner. |

SEC follow-on can use a parser-independent source/provenance rule over the retained
catalog, audited PDF/HTML spans and a fixed information-extraction task. It does
not reuse the pypdfium2 score threshold as a new impartial selection rule.

## Next actions

No new user decision is required. Paid comparisons and public release remain deferred.
