# Does the benchmark measure the parser decision you need to make?

Document kind: explanation. Source evidence for editorial review, not publication approval.

PDF-Bench now provides a reproducible example of evaluating configured document
pipelines and inspecting the benchmark itself. The practical starting point is to
check whether a public benchmark contains the documents, information needs and
operating conditions that matter to a team. Use the public benchmark, or its
relevant subset, when it does. Additional internal evaluation needs a consequential
mismatch, such as an acceptance task or document distribution that the selected
public cases do not test.

ParseBench already contains substantial business material and deterministic
semantic and table evaluation. ExtractBench addresses schema-guided extraction,
including repeated records and evidence attribution. We have not established that
either benchmark misses most business work, or that our synthetic invoices fill a
general gap in their coverage. PDF-Bench's contribution is a worked construction
and audit example, supported by retained mistakes, qualified references, actual
executions and replayable evidence.

The corrected invoice experiment measures complete information recovery through a
parser and a fixed extractor. The public experiment runs the same local parser
configurations on a declared ParseBench subset using pinned upstream evaluators.
Their scores answer different questions. The historical results remain available
in evidence tiers, with their provenance limits attached.

## Begin with the documents and the decision

A team selecting a parser for procurement documents should describe the actual
inputs before choosing a benchmark. Supplier documents may be born digital or
scanned, single-page or long, multilingual, amended, signed or split across
attachments. The decision might concern readable retrieval text, correct table
cells, a payable invoice record or evidence supporting an exception. Those tasks
need different reference facts and acceptance rules.

The assessment inventories every annotation file at the pinned ParseBench dataset
revision. It finds 169,011 rule rows, 2,553 group/input cases,
2,078 exact input paths and 2,060 published content identities.
These are different counting units. An annotated page excerpt is not necessarily
an original document, and the published identity field mixes Git blob and LFS
content identifiers. We did not independently reconstruct original-document
lineage or a population-weighted estimate of business coverage.

Source inspection confirmed financial reports, contracts, insurance material,
forms, correspondence, operational records and presentations. The initial
inspection covered every annotation dimension and text-tag family. Further
inspection qualified the cases used in the actual comparison. Filenames only
identified candidates. A file called `synthetic_invoice_page1.pdf` is a crew
timesheet; `text_simple__bill.pdf` explains legislation. A funeral notice and a
thesis approval page selected by correspondence-like filenames were excluded
before outputs and replaced by the next candidates under the declared rule.

These observations support reusing relevant public cases. They cannot establish
that a particular organization's volumes, languages or failure costs are covered.
That judgment needs the organization's workload description and weights. A large
dataset with a mismatched task can be unhelpful; a relevant subset can be useful
without claiming to represent every business.

The selection and observations are retained in
[the qualified public selection](../../parsebench-comparison-qualified-selection.json).
[The assessment](../../parsebench-assessment.json) records broader fit judgments
and unknowns separately from the executed comparison.

## Define success before choosing the score

The invoice example asks whether a pipeline recovers the invoice number, vendor,
due date, grand total and currency marker, together with every applicable line-item
record. A record keeps its description, quantity, unit, unit price and line total
associated wherever those roles apply. Whole-invoice success requires every field
and complete record, with no missing or extra records.

This criterion is stricter than recovering most words. Swapping quantity and rate
headers can preserve the tokens while changing the meaning of a payable line.
The development controls transpose headers on actual backend output and confirm
that complete-record scoring rejects the result. Duplicate records count with
their multiplicity. Missing records reduce recall; extra records reduce precision.
The field and record diagnostics explain a failed invoice rather than replacing
the complete-invoice acceptance criterion.

The extractor is a standard-library program that receives parser text, not the
source DOCX, invoice identifier or reference path. It keeps raw surfaces beside
canonical values. Decimal values, signs, currency markers and role assignments
remain explicit. Date formats and harmless whitespace are normalized under a
frozen contract. Vendor and description comparisons use case folding. The grader
compares persisted predictions against separately qualified references.

The extractor's supported representations are part of the evaluated pipeline.
It prefers Markdown tables where present and otherwise uses linear text rules.
It cannot infer every party column or repair every continuation. Tuning it after
seeing the primary results would create a new protocol and require another
labelled experiment. A better downstream extractor may change the parser choice.

## Qualify reference truth before judging outputs

The new invoice references come from retained DOCX source facts, independently of
the parsers being compared. They preserve values as printed, including awkward
generated arithmetic, rather than silently repairing totals. Metadata provides a
cross-check rather than the sole reference. Source facts were checked against all
182 rendered physical PDF pages across 100 inputs and 696 line
records. Coding-agent visual review is recorded explicitly. It is not independent
human adjudication.

The population contains 6 source template/complexity cells and
3 record schemas. Repeated fills of those source templates are useful for
testing amounts, row counts and page continuations. They are not independent trials
of arbitrary supplier layouts. Some descriptions split awkwardly across pages;
some amounts and business details are implausible. The experiment supports a
controlled task comparison and a benchmark-design demonstration, not a production
accuracy estimate for real vendors.

Reference-derived faithful Markdown controls pass the declared extractor format.
They show that the grader and extractor can recover the intended facts in that
representation. They do not establish a universal extractor ceiling or prove that
the PDF layouts are easy. Actual parser output still determines each prediction.

Reconstructing the old references also exposed a historical limitation. Current
source extraction reproduces the backup text references rather than the references
currently stored in the old corpus. The original bytes actually scored in the
historical invoice run remain unknown. New qualified references support the new
experiment; they do not retroactively validate the old similarity scores.

The [reference checkpoint](../../invoice-reference-checkpoint.json) links the
qualified immutable bundle, page decisions, hashes and replay evidence.

## The corrected invoice comparison

| Pipeline | Complete invoices | Correct fields | Matched / expected / predicted records | Record F1 |
| --- | ---: | ---: | ---: | ---: |
| pypdf | 84/100 | 500/500 | 668 / 696 / 698 | 0.958393 |
| pdfplumber | 55/100 | 468/500 | 677 / 696 / 691 | 0.976208 |

The complete-invoice criterion favors the configured pypdf pipeline in this
population. Exact line-record recovery favors pdfplumber. A team accepting only
complete invoices and keeping this extractor would prefer the former under this
test. A team optimizing line-item recovery would investigate the latter and its
field-assignment failures. Neither decision establishes an inherent parser winner
outside the stated task, references and distribution.

| Source cell | Inputs | pypdf complete | pdfplumber complete |
| --- | ---: | ---: | ---: |
| enterprise/simple | 19 | 11 | 10 |
| small_business/simple | 19 | 14 | 16 |
| economy/medium | 17 | 17 | 0 |
| enterprise/medium | 15 | 15 | 15 |
| small_business/medium | 15 | 12 | 14 |
| economy/complex | 15 | 15 | 0 |

The source cells expose concentrated behavior that the aggregate conceals. The
economy variants flatten sender and recipient information in pdfplumber's output,
so the fixed extractor cannot assign the vendor even when it recovers the numeric
line records. Other cells contain description and page-continuation problems.
An absent source cell is not an observed success or failure. The table should not
be extrapolated to independent real-vendor layout frequencies.

Every eligible input stays in both parser denominators. Empty output, a parser
failure or an enforced timeout receives no invoice-task success credit. Required
evaluator failure invalidates the affected aggregate instead of removing difficult
inputs. Separate mechanism controls exercise actual corrupt inputs, blank PDFs and
an enforced timeout whose delayed writer is stopped before returning. An eligible
timeout control and an all-failed initialization control test the denominator
policy independently of the successful primary parsing calls.

## Audit why the task failed

The audit reviewed all 61 failed task pairs across 52
documents, including all 43 documents on which the pipeline
task decisions differ and 9 shared-failure documents.
Every failed pair was inspected using raw output, prediction/reference differences
and the prior source/PDF qualification. The review found unsupported extractor
representations in 61 pairs. In 32 pairs,
party-column association was also lost in the parser representation. Causes can
overlap; these counts must not be summed as exclusive categories.

Examples include within-word line breaks in `Implementation`, descriptions that
continue after their numeric values, a final record present in linear text but
outside the preferred Markdown table, and sender/recipient columns merged into
the same line. Source pages were reopened for the disputed final-page description
fragments. No reference gap or grading defect was found in this reviewed set.
That is an audit finding with a stated reviewer and scope, not proof that every
possible reference or extractor defect has been eliminated.

The failures show why a parser leaderboard cannot directly choose an extraction
pipeline. A downstream component can reject information that remains visible in
raw output. A parser can also retain the words while losing their useful
association. Inspecting both representations is necessary before attributing an
end-to-end score difference to parsing alone.

[The complete failure audit](../../invoice-failure-audit.json) retains each pair,
source/output hashes, differences, review decision and notes. Earlier CLI-path and
cold-dependency failures remain separately labelled integration diagnostics. They
are not included as primary parser-quality results.

## What the native public comparison adds

The public population was frozen before comparison outputs: 30
text-content cases and 20 table cases. It is a purposive business-relevant
subset. The table selection balances upstream easy/hard tags and deliberately
oversamples insurance among the additional hard cases. It is not a prevalence
sample, and the inputs are mostly page excerpts rather than full workflow packets.

| Pipeline | Native content faithfulness | Native table composite |
| --- | ---: | ---: |
| pypdf | 0.599212 (30/30) | 0.000000 (20/20) |
| pdfplumber | 0.570951 (30/30) | 0.106763 (20/20) |

These are native `content_faithfulness` and `grits_trm_composite` measurements from
the pinned ParseBench evaluator. Each number is the unweighted mean of the stated
case population in that dimension. All selected pairs have native evaluation
results. Operational empty outputs remain visible and included. The local
baselines do not perform OCR, so their failure to recover scanned content is an
observed limitation, not a reason to remove the inputs.

Both pipelines use the pinned upstream Markdown-table-to-HTML conversion before
native table evaluation. We execute that exact helper's function body from its
verified upstream source without importing the provider registry. The plain pypdf
configuration emits no structured tables, producing zero on the native table
metric even where its text contains table values. Pdfplumber emits some table
markup, but the recovered structures still score poorly on this selected set.
This measures the configured output contract. It does not show that the underlying
PDF text has no useful values, or compare modern OCR/layout systems.

Charts, layout and formatting were assessed for fit but not executed in this
comparison. Normalization is off; no paid parser or LLM judge was called. The
experiment cannot be presented as a replication of the full published leaderboard.
Its native dimensions also cannot be averaged with complete-invoice success or
compared as though the percentage units were interchangeable.

The public cases are useful for checking parsing behavior. They do not, by
themselves, establish the complete-invoice acceptance behavior of our pipeline.
That distinction concerns the task being measured. It is not evidence that
ParseBench contains no invoices or that a public extraction benchmark cannot
support an invoice workflow.

## Reuse extraction evaluation too

[The bounded ExtractBench assessment](../../extractbench-contract-assessment.json)
reviews a pinned revision's schema, value, record and failure contracts. Its
one-to-one record assignment and cell-level value credit address incomplete,
reordered and surplus records. Evidence alternatives and grounding support a
broader class of schema-guided document tasks than this invoice example. The
published corpus statistics are attributed to its README, not independently
verified by our review.

Our complete-record multiset criterion differs from partial cell credit, and our
whole-invoice acceptance criterion differs from a document-mean value F1. Those
differences should follow an operational need. They are not grounds to duplicate
an existing generic assignment framework. If ExtractBench's documents, schema and
grading semantics match a team's decision, use them and add an acceptance criterion
only where needed.

The pinned README's treatment of omitted fields differs from its unified scorer's
missing/default/null contract. The older array-record scorer retains the README's
implicit-null behavior. We verified this discrepancy by inspecting source, without
running an ExtractBench comparison. It illustrates why adopting a metric requires
pinning its implementation and checking the exact semantics. It does not establish
that the published leaderboard is wrong.

## Historical evidence remains useful with its limits attached

The authoritative registry preserves 117 artifacts, original bytes,
declared and observed counters, metric definitions and provenance unknowns.
Artifacts include runs, checkpoints and diagnostics; they are not all independent
experiments. The report does not replace missing historical versions, inputs or
timing boundaries with current configuration guesses.

| Retained family | Tier | Supported interpretation |
| --- | --- | --- |
| academic_arxiv | directional | Technical-paper text metrics; exact source-to-PDF and equation correspondence require qualification. |
| investor_decks_prototype | prototype | Synthetic PPTX/PDF prototype, limited templates and realism; no corporate-deck population claim. |
| frontier_premium_pilot | historical | Historical paid pilot; metric subsets and configuration identities must be inspected before interpreting differences. |
| frontier_budget_unified | historical | Historical paid model pilot; current provider/model/configuration and cost comparability are unverified. |
| invoices_source_first | historical | Retained DOCX extraction matches backups, not current references. The original scored reference bytes are not established; source-first independence is unverified for this run. |
| legacy_presentations | directional | Retained presentation evidence with uneven reference/source correspondence; not a full-deck task comparison. |
| sec_filings_real_business | directional | Current selection config uses pypdfium2 >= 0.90; ARS PDFs and 10-K HTML may differ. Similarity to that reference is diagnostic, not independent task correctness. |
| sec_commercial_pilot | historical | Observed rows contradict declared failure count. Preserve paid-run diagnostics and separate counters; no current paid-parser winner. |
| sec_screening_full | directional | One-parser screen over observed rows. Title All 89 conflicts with 320 observed document IDs; no parser ranking or impartial sample follows. |

Legal, HR and broad mixed-corpus runs also remain in the full registry as historical
evidence and rerun candidates. Academic papers can inform equation, reading-order
and technical-layout experiments. Presentations and source-first decks retain
their pipeline and reference-quality lessons. Paid pilots retain configuration
and accounting lessons, even where current model names, options, costs or winner
claims are unsupported. No current commercial comparison follows from those old
artifacts.

The SEC example shows a concrete selection problem. The retained selection
configuration uses one parser's similarity threshold, while annual-report PDFs
and filing HTML may not represent the same content. That screen can identify
diagnostic cases. It cannot supply an impartial new parser-comparison population
or establish extraction correctness against the PDF.

The new invoice matrix demonstrates selection bias directly. On the full fixed
population, record F1 is 0.958393 for pypdf and 0.976208 for
pdfplumber. Keeping only the 84 invoices that pypdf completes
changes those scores to 1.000000 and 0.995671. The record
ordering reverses. This counterfactual is deliberately performance-selected and
never substitutes for the primary result. It cannot reconstruct the historical
SEC counterfactual because the other parsers were not run on every excluded case.

## Execution identity and operating limits

| Component | Frozen configuration |
| --- | --- |
| Parser Python | 3.13.5 |
| PDFsmith | Distribution 0.2.0; source 0.3.0.dev0 |
| pypdf | Version 6.3.0; `{'extraction_mode': 'plain', 'backend_name': 'pypdf', 'cache_mode': 'bypass'}` |
| pdfplumber | Version 0.11.8; `{'layout': False, 'x_tolerance': 3.0, 'y_tolerance': 3.0, 'backend_name': 'pdfplumber', 'cache_mode': 'bypass'}` |
| ParseBench code | `d423e529ae329317bcd33c650b367acfb60e6620` |
| Public dataset | `2805a1d940f95a203e0ae4b88be9934f7765b3fc` |
| Native evaluator Python | 3.14.3 |

Each comparison freezes inputs, references, protocol, backend options and runtime
identity before parsing. Isolated workers retain the exact returned bytes in
exclusive attempt directories. Adapter cache reads and writes are disabled, and
legacy checkpoint resumption is rejected. Old cache/checkpoint files are preserved
as diagnostic evidence. Input changes and option changes cannot silently reuse
prior outputs.

The retained PDFsmith wheel captures the actual selected source modules. Its
distribution metadata and source declaration disagree, and both are recorded.
Later PDFsmith changes are not imported into these results. A dependency upgrade
requires a new execution identity, rather than an undocumented continuation of a
previous comparison. Frozen packages, source hashes and dependency locks make
rebuilding possible; a Git hash alone would not recover an editable dirty package.

Later typing and CI maintenance has a separate current development protocol.
The primary results retain their original extractor/grader snapshots and packages.
The report cites the task protocol inside the scored run; it does not relabel
those results as executions of the current checkout.

Repeated fresh runs reproduce outputs, normalized predictions and deterministic
scores. Relocated runs rebuild the declared runtimes outside the checkout.
Standalone invoice regrading needs retained raw output, predictions and references,
with original PDFs removed. Public regrading uses the pinned native evaluator,
retained outputs and annotations while forbidding parser imports, PDF reads,
network access and parser subprocesses. Durations are observations, not equality
targets.

The machine and timing boundaries are recorded. Per-attempt parse/read/retention
duration starts after backend initialization; wall duration includes worker
startup. Runs are sequential, without exclusive-host or OS-cache control and
without measured peak-memory limits. The public harness retained monotonic
durations but no exact UTC start/completion timestamps; its dated execution
observation records that limitation. No speed winner is claimed.

There were no metered API charges in these local experiments. That does not make
their total operating cost zero. Hardware, energy, labor and workflow review were
not monetized, so the export leaves total operating cost unknown. A deployment
decision should add those measurements under its actual service limits.

## Apply the method to an internal decision

Describe the task, eligible documents and consequences of wrong output. Inspect
public examples and their references, including failures that resemble the team's
inputs. Choose a relevant public subset when it captures the decision. A remaining
material gap may concern document distribution, missing workflow context, complete
record acceptance or operating constraints. State that gap before collecting
additional cases.

Then freeze a parser-independent selection and reference protocol. Review source
and rendered PDF agreement; specify unknown and ambiguous facts. Define extraction
and scoring separately, with acceptable normalization and duplicate/missing-record
semantics. Test the evaluator with wrong associations and missing outputs, not
only clean examples. Retain every eligible attempt, inspect disagreements, and
replay the actual artifacts before choosing a configured pipeline.

The bounded follow-on protocols remain separate work. Scans need suitable OCR
configurations on meaningful degraded/clean cases. More complex tables and charts
can reuse additional public categories and their native metrics. Decks need source,
slide-boundary and chart-fact qualification. Academic papers need matched revisions
and equation-aware references. SEC work needs parser-independent selection and
audited PDF/HTML correspondence. Paid systems need a named decision, frozen provider
configuration and an approved spending cap before calls.

The generated appendix and claim export identify the evidence behind the tables.
[Replay instructions](replay-protocol.txt) describe the tested artifact paths and
fresh-environment runs. The checked editorial benchmark-interpretation article is
identified in [the context record](../../editorial-context.json); it has no verified
public URL here. Editorial and website owners can use this source evidence for
synthesis. Author approval, public-main merge and publication remain separate.
