# Plan: Select document parsing and extraction components

Revision 6, October 19, 2026, implements the attached revision brief. The guide
explains component selection for a defined document collection, downstream task,
quality threshold and total cost. Include ExtractBench Pro, OpenDocRouter and
confidence-score evidence. Keep client case studies, patent/inventorship material
and speculative acquisition narratives separate. All benchmark, regrading,
profiling and GPU execution stays paused.

## Gating and preserved work

Issues 1-8 below retain their implemented engineering contracts as history. Their
acceptance references resolve to the earlier specification at Git commit
`c8fa6abe702c04e9316485e772de29b8b846b3be`. Commands in those historical sections are
not current execution authorization. Their existing evidence remains preserved.

Current work is Issues 9-11, mapped to GitHub #10-#12: qualify public evidence and
reuse recommendations -> document retained evaluation/execution lessons -> write
and check the guide. These steps use file/source reads and light metadata checks;
no parser, native grader, model import, corpus rerun or broad test suite runs.

The earlier full-roster and 208-input proposals are deferred research artifacts,
not milestone requirements. A new experiment needs an unanswered decision, a
specified comparison and fresh authorization for resources/spending. The current
execution policy and heartbeat remain paused throughout this writing work.

The active owner is this conversation on `codex/benchmark-rebuild`, using the
existing checkout and draft PR #9. Original data and inherited dirty work stay intact.
Public-main merge, editorial changes and publication are outside this plan.

### Milestone: `rebuild-1 - Practical PDF parser evaluation guide`

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

**Issue 9 - Qualify public benchmark evidence and reuse recommendations**

Use the complete retained ParseBench inventory, source measurement and visual
observations. Reconcile the five metric contracts and actual source units; do not
rerun acquisition or inspection. Check published parser coverage and distinguish
provider families from configurations and local wrappers from hosted services.
Use pinned ExtractBench/ExtractBench Pro/OmniDocBench primary sources to explain
alternative tasks. For Pro, check synthesis, challenge counts, same-evaluator
contract, perfect-document metrics and source-review limits. Verify OpenDocRouter
from its official SDK/API and confidence scoring from primary documentation.
Correct the brief's launch dates, dimension count and unsupported ranking claims.
Refresh `parsebench-coverage.md` to recommend public reuse and remove all promises
of automatic parser runs. Preserve the inventory and unknown family labels.

Files: existing coverage report, retained primary-source record and the guide's
single evidence record. Verify by reading source records, independently counting
inventory rows and resolving citations/hashes. A missing source or changed identity
prevents the affected claim; previous evidence and disabled execution stay intact.
No new benchmark or GPU work. This fulfills current spec criteria 2-4 and 9.

### Premises

Input: guide public evidence

| Question | Answer | Kind |
|---|---|---|
| record | A source-backed guide assertion tied to its exact retained artifact or primary source. | definitional |
| absent-record | Missing or unreviewed evidence remains unknown; it is not absence, success or a new result. | definitional |
| ordering-spacing | Case counts, source files, original documents and benchmark dimensions are distinct; no global rank follows from row order. | definitional |
| entity-identity | Source revision, artifact hash, configuration and evidence scope identify the claim. | definitional |
| known-at | The guide uses already retained evidence; recommendations do not become executed experiments. | definitional |
| institution | Upstream contracts define public metrics; declared workflow requirements define acceptance; Stefan controls new execution and release. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| guide-public-evidence-qualified | Public-reuse recommendations distinguish checked benchmark scope from unproven coverage gaps. | A material assertion lacks the cited source, confuses its units or scope, or implies unperformed execution. |

Closes: guide-public-evidence.record, guide-public-evidence.absent-record, guide-public-evidence.ordering-spacing, guide-public-evidence.entity-identity, guide-public-evidence.known-at, guide-public-evidence.institution, guide-public-evidence-qualified

**Issue 10 - Explain evaluation and PDFSmith execution failures from retained evidence**

Depends on Issue 9's source boundaries. Explain reference/rendition mismatch,
parser-dependent selection, incomplete task acceptance, output-contract loss,
cache/timing identity and model/process lifecycle using already retained records.
Recompute illustrative arithmetic from saved grades only; do not execute parsers,
native evaluators, models or performance probes. Separate the qualified synthetic
invoice example from real-vendor claims, and observed code behavior from unmeasured
warm speedup or GPU utilization. Treat full/sample runs as incomplete preparations.

Files: existing failure/selection/reference receipts, frozen source snapshots and
the guide evidence record; no sibling PDFSmith or runner changes. Verify numerical
examples against actual saved rows and inspect source/call boundaries for each
mechanism. Recorded test/replay receipts are prior evidence, not freshly rerun
checks. Use explicit limits, not synthetic examples as the guide's principal value.
This fulfills current spec criteria 5-7, 9 and 12.

### Premises

Input: guide retained lessons

| Question | Answer | Kind |
|---|---|---|
| record | A source-backed guide assertion tied to its exact retained artifact or primary source. | definitional |
| absent-record | Missing or unreviewed evidence remains unknown; it is not absence, success or a new result. | definitional |
| ordering-spacing | Case counts, source files, original documents and benchmark dimensions are distinct; no global rank follows from row order. | definitional |
| entity-identity | Source revision, artifact hash, configuration and evidence scope identify the claim. | definitional |
| known-at | The guide uses already retained evidence; recommendations do not become executed experiments. | definitional |
| institution | Upstream contracts define public metrics; declared workflow requirements define acceptance; Stefan controls new execution and release. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| guide-retained-lessons-qualified | Worked lessons follow retained sources and make no new parser-quality or operating-performance claim. | A material assertion lacks the cited source, confuses its units or scope, or implies unperformed execution. |

Closes: guide-retained-lessons.record, guide-retained-lessons.absent-record, guide-retained-lessons.ordering-spacing, guide-retained-lessons.entity-identity, guide-retained-lessons.known-at, guide-retained-lessons.institution, guide-retained-lessons-qualified

**Issue 11 - Write and check the practical parser evaluation guide**

Depends on Issues 9-10. Rewrite `benchmark-design-guide.md` as a finished explanation
for practitioners selecting parsing and extraction components. Lead with the
least total cost among configurations meeting task-specific quality and operating
requirements. Explain the distinct parsing/extraction contracts, then public
benchmark scopes and representative evaluation. Use public evidence when it fits;
collect new truth only for a consequential unanswered requirement.
Include concrete task/metric choices, reference construction, failure accounting,
paired comparisons, uncertainty, operational constraints and a stopping rule.
Include confidence validation, false acceptance, missing output, review workload,
latency/throughput boundaries and a hypothetical cost comparison with checked
arithmetic. Close with a concise connection to complete document intelligence
systems. Remove internal project confessions and operational scheduling from the
reader narrative. Keep Swiss Re/Swift3, patents, inventorship and broader website
copy separate. Preserve historical/controlled work with its limits in reference
material; use a compact worked example only where it develops the argument.

Files: the guide and one evidence JSON, existing orientation/README/progress and
integration handoff. Check every local link, exact cited numbers, source identities
and distinctions between findings and recommendations. Read the complete guide for
coherence, usable examples and unsupported claims. No new testing framework,
parser/native scoring, broad test suite or GPU work is needed. Update draft PR #9
and mapped issues to the actual delivery; publication remains a separate decision.

The guide can be delivered for review without claiming the milestone's engineering
coverage gates or public release passed. Issue-closing commits remain gated by the
verification workflow; ordinary documentation checkpoints do not close issues.
This fulfills current spec criteria 1, 8-12.

### Premises

Input: guide delivery

| Question | Answer | Kind |
|---|---|---|
| record | A source-backed guide assertion tied to its exact retained artifact or primary source. | definitional |
| absent-record | Missing or unreviewed evidence remains unknown; it is not absence, success or a new result. | definitional |
| ordering-spacing | Case counts, source files, original documents and benchmark dimensions are distinct; no global rank follows from row order. | definitional |
| entity-identity | Source revision, artifact hash, configuration and evidence scope identify the claim. | definitional |
| known-at | The guide uses already retained evidence; recommendations do not become executed experiments. | definitional |
| institution | Upstream contracts define public metrics; declared workflow requirements define acceptance; Stefan controls new execution and release. | definitional |

### Claims

| Id | Claim | How it could be false |
|---|---|---|
| guide-delivery-inspectable | The authored guide and linked evidence explain actionable decisions without inventing results or restarting execution. | A material assertion lacks the cited source, confuses its units or scope, or implies unperformed execution. |

Closes: guide-delivery.record, guide-delivery.absent-record, guide-delivery.ordering-spacing, guide-delivery.entity-identity, guide-delivery.known-at, guide-delivery.institution, guide-delivery-inspectable

## Deferred execution and release

Full-population and 208-input parser plans, model lifecycle/GPU repairs, new native
grading, OCR/deck/formula experiments and paid comparisons remain deferred. They
are not hidden dependencies of the guide. Existing outputs, snapshots and historical
reports stay available. No blanket inference follows about all business workloads.

All benchmark and GPU execution remains paused. Native protocol qualification of
the unexecuted sample is unfinished and cannot be represented as a scored result.
Current source writing does not authorize changes to the editorial repository,
website CMS, publication, deployment or public main.

## Next actions

No user action is required to write and check the guide. New runs and release need
separate decisions; none is requested as part of this work.
