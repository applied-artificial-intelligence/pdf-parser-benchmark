# 1. Disposition: **Revise**

Retain the six-issue milestone, the fixed 100-invoice population, and the pypdf/pdfplumber comparison. The proposed work can produce a useful engineering demonstration. It does not require a new corpus, a universal leaderboard, or full ParseBench replication.

The acceptance contract needs targeted revisions before the affected implementation begins. Its principal weaknesses are insufficiently bound reference qualification, incomplete extractor/grader isolation tests, a denominator regression that does not exercise eligible-input failure, and underspecified bundle completion. The supplied code also establishes cache/checkpoint identity defects that the plan correctly proposes to repair.

**The first milestone should support a reproducible comparison of two configured pipelines on these qualified invoices.** “Strong” should describe the integrity of that bounded comparison, not general vendor-invoice accuracy. The specification already distinguishes those claims; the implementation and report need to enforce the distinction. external-review-packet external-review-packet

In the findings below, **established** means visible directly in a supplied excerpt or internally inconsistent retained record. **Risk** means a concrete failure the proposed implementation could admit. None of the counterexamples below was executed during this review.

# 2. Numbered findings

## 1. High — Reference qualification must attest to the exact rendered content, not merely inventory three hashes

**Affected:** AC 6–8, 13; Issue 2. Relevant excerpts: `generate_invoice_corpus.py:78–124, 264–307`.

The source reference builder reads DOCX paragraphs and tables; it does not verify PDF content. Metadata comes from the same generation inputs. Agreement between those two outputs therefore cannot independently establish that the PDF displays the reference facts. AC 8 requires a record for every rendition but only explicitly requires rendered spot checks across strata and detected disagreements. The independent verification mechanism for the remaining PDFs is unspecified. external-review-packet external-review-packet external-review-packet

**Concrete failure:** An unsampled invoice loses its final line item during conversion. DOCX and metadata still agree. Its PDF hash is recorded, but nothing establishes that this particular PDF was checked against these particular reference bytes. Alternatively, a revised PDF receives a new manifest hash while an earlier qualification decision and reference are carried forward. Both cases can pass a “files exist, hashes recorded, strata sampled” implementation.

**Acceptance change:** Before a strong 100-document claim, require task-relevant verification for every PDF: scored fields, line-item values and associations, and pages where truncation or continuation matters. For this corpus size, direct rendered review is the simplest sufficient procedure; another independent procedure is acceptable if it produces equivalent per-document evidence.

Bind each qualification decision to the exact DOCX, PDF, reference, and qualification-protocol hashes. Any changed member invalidates that decision. Test replacement of an already-qualified PDF and rejection of its stale qualification through the real qualification/finalization path.

Also distinguish **transcription truth from arithmetic correctness**. An incorrectly calculated total displayed in the PDF is a document defect, not permission for the grader to substitute the mathematically correct amount. Any rerender belongs to an explicitly identified new rendition.

## 2. High — The semantic contract needs executable definitions of record identity, multiplicity, and normalization

**Affected:** AC 9, 11; Issue 3.

Issue 3 correctly requires row matching, missing/extra penalties, and normalization to be frozen. Those definitions remain substantive implementation choices; “wrong associations fail” alone does not resolve them. external-review-packet

**Concrete failure:** Suppose the reference contains:

```text
Item A | quantity 1 | unit price 10 | line total 10
Item B | quantity 2 | unit price 20 | line total 40
```

A prediction attaches the second numeric tuple to Item A and the first to Item B. Every value token and the invoice total remain unchanged. Token checks, independent column comparisons, or row matching that disregards item identity can accept the wrong associations.

Likewise, converting records to a set makes two identical reference rows indistinguishable from one recovered row. A normalizer that strips currency or guesses decimal/date conventions can equate substantively different values.

**Acceptance change:** Freeze a small invoice-specific contract before implementation:

- Typed fields, including which “total” is required, vendor versus customer identity, currency, and date interpretation.
- Header aliases determined independently of reference values.
- One-to-one matching of complete records, preserving duplicate multiplicity.
- Explicit missing/extra-record penalties and an all-required-fields/all-records document-success condition.

Use decimal-safe amount handling and preserve currency/unit meaning. Resolve ambiguous dates from permitted document information or return an ambiguity; do not consult reference metadata to choose the interpretation.

The producing-path tests must reject swapped numeric tuples, detached/transposed headers, duplicate loss, and extra records, while accepting declared harmless row or column reorderings. Grader-side matching may align already-extracted records; it must not repair their header/value associations to maximize agreement.

## 3. High — The proposed blindness test can pass despite extraction from source answers

**Affected:** AC 6 and 9; Issue 3. Relevant excerpt: `local_evaluation.py:141–153`.

The current `grade_fields(text, expected)` combines extraction and grading and derives searched labels from `expected`. **The shown implementation does not use expected values to extract predictions.** It should not be accused of demonstrated answer-value leakage. Its architecture nevertheless provides an unsuitable isolation boundary for the expanded task. external-review-packet

**Concrete failure:** A future extractor receives `invoice_001` and reads its retained metadata YAML to fill the due date or vendor. A test changes the supplied reference dictionary and confirms unchanged predictions. That test passes because the extractor consulted another copy of the answers. “Withholding the reference until extraction ends” also fails to detect this if source metadata, DOCX files, or reference constants remain accessible. The proposed test currently specifies withholding the reference and changing reference facts, without defining that broader boundary. external-review-packet

**Acceptance change:** Make prediction generation a separate interface over parser output and a fixed public task schema. It must have no source-document, metadata, gold-reference, or document-ID lookup dependency. Persist and hash prediction objects before grading.

Add an integration test in which those answer-bearing files are unavailable. Changing reference values, reference record counts, and reference-side labels must not change prediction bytes. With the same reference, blanking or corrupting parser output must change the prediction appropriately.

Change AC 6’s “every parser receives the same frozen PDFs and references” to state that **parsers receive PDFs; the grader receives references**. A separate process for this isolation test is sufficient; a generalized sandbox framework is unnecessary.

## 4. High — The existing denominator regression does not cover the failure it claims to protect against

**Affected:** AC 10–11, 16; Issues 3 and 5. Relevant excerpts: `local_evaluation.py:198–225`; `test_local_evaluation.py:54–70`.

The smoke summary computes quality over documents for which **both parsers have status `success`**. Its failure control is explicitly reference-ineligible. The test checks that the corrupt input remains in attempt/failure counts, but it never causes a reference-eligible input to fail on only one parser. external-review-packet external-review-packet

**Concrete failure:** Make pypdf fail on the valid `columns` document while pdfplumber still recovers it correctly. The current `common` construction removes that document from both summaries. Pypdf’s difficult input disappears, and pdfplumber loses credit for a successful recovery. The existing corrupt-control test does not detect this.

**Acceptance change:** Define the primary document metric explicitly. For a frozen, reference-eligible set \(E\):

\[
\operatorname{TaskSuccess}(p)
=
\frac{\sum_{d\in E}
\mathbf{1}[\text{pipeline }p\text{ completes the required task on }d]}
{|E|}.
\]

Parser failures, timeouts, and empty outputs contribute zero. Unresolved reference truth is separately unavailable, with reference coverage reported against all 100 documents. It is not silently converted into either parser error or success.

Freeze field- and record-level denominators and distinguish micro- from document-macro aggregation. Require **200 unique planned primary pairs per execution**, not merely “at least 200” rows; retries and controls must not satisfy that count.

Add asymmetric eligible-input failure and timeout controls through the runner, plus an all-failed parser case. Assert unchanged primary membership and denominators. Retain common-success results only as secondary diagnostics.

## 5. High — Metric failures can masquerade as successful parsing and disappear from quality aggregates

**Affected:** AC 10–11, 15–16; Issue 4. Relevant excerpt: `runner.py:197–230`.

The worker silently skips unknown metric names, converts metric exceptions to `NaN`, and still returns `success=True`. Persistence converts nonfinite metric values to null. The story generator averages the numeric values that remain. This is an established route from evaluation failure to selectively missing scores. external-review-packet external-review-packet external-review-packet

**Concrete failure:** The line-item grader raises on difficult multi-page tables. Those attempts remain “successful,” their metric becomes null, and the aggregate improves because difficult cases are absent. A misspelled required metric can disappear altogether without a configuration error.

The runner also reads generated output and ground truth within the broader attempt exception boundary. The supplied excerpt does not establish stage-specific error classification. Separately, incompatible image tasks are filtered before result records are created. external-review-packet

**Acceptance change:** Separate parse outcome, prediction outcome, and grading outcome. Reject unknown required metrics before execution. A required grader exception must invalidate the affected comparison claim; it is neither a parser failure nor legitimate reference unavailability. Optional diagnostic unavailability needs a reason.

Persist planned pairs before capability filtering and execution initialization. Every omitted or unstarted pair must remain addressable.

Use typed timeout outcomes rather than searching error text for `"exceeded"`, as the smoke wrapper currently does. Test an ordinary error containing that word and an actual enforced delay. Measure started-call durations with a monotonic clock in the appropriate `finally` boundary, and prevent timed-out workers from later modifying finalized evidence. external-review-packet

## 6. High — Checkpoint reuse accepts changed inputs and can import foreign result rows

**Affected:** AC 12–13, 16; Issue 4. Relevant excerpt: `runner.py:328–350`.

The runner imports checkpoint results and counters, then marks work complete using only `(parser_name, document_id)`. No input, reference, configuration, or metric identity check appears in this path. external-review-packet

**Concrete failure:** Replace `invoice_001.pdf`, correct its reference, or change the extractor while retaining its document ID and parser name. The checkpoint suppresses execution and returns old results. A checkpoint from a larger document set can also import rows outside the current population because the existing result list is copied wholesale.

**Acceptance change:** Bind reusable checkpoints to a frozen protocol and population manifest, including actual input/reference bytes, configured stages, implementations, and metric definitions. Validate membership, uniqueness, and compatibility before importing any rows or counters.

Historical formats should remain readable, but checkpoints without sufficient identity must not be silently resumable as verified new work. Changed references may permit explicit regrading of retained parser outputs; they cannot permit reuse of old grades. Retry behavior should preserve separate attempt identity and be explicitly distinguished from resuming terminal outcomes.

Required witnesses are changed PDF bytes under the same ID, changed reference bytes, changed metric/extractor configuration, and an otherwise readable checkpoint containing foreign or duplicate pairs.

## 7. High — Cache identity omits output-affecting configuration and backend implementation

**Affected:** AC 12–14; Issue 4. Relevant excerpts: `pdfsmith_adapter.py:68–95, 142–162`; `caching.py:109–111`.

The adapter passes `kwargs` to the backend, but the cache key contains only input content, adapter name, and PDFsmith’s declared version. Only `model` is incorporated into the name. Cache lookup precedes backend initialization. The omitted configuration and backend identity are established defects; whether a particular supported option produces stale output needs the real-backend witness required by the plan. The packet does not include enough backend implementation to verify a specific option. external-review-packet external-review-packet external-review-packet

**Concrete failure:** An editable backend changes its parsing behavior without changing PDFsmith’s `__version__`. The next call returns the earlier cached output before loading the changed backend.

**Acceptance change:** Keep the first scored run explicitly uncached, with tests proving both reads and writes are bypassed through the actual adapter. A “fresh” label is insufficient.

For ordinary operation, either implement and test sufficient identity or temporarily disable unsafe reuse. Do not leave known-unsafe defaults while declaring the execution layer repaired.

Keep identities stage-specific:

- Parsed output depends on PDF and parser implementation/configuration.
- Prediction depends on parsed output and extractor/schema.
- Grade depends on prediction, qualified reference, and grader/normalizer.

A corrected reference should force regrading, not unnecessary reparsing. Record the actual loaded backend implementation and dependency snapshot alongside the PDFsmith metadata/source disagreement. Resolving that identity does not require changing the sibling library’s release metadata.

## 8. High — Output-path ownership remains a possible route to grading another attempt’s bytes

**Affected:** AC 15–16; Issue 4. Relevant excerpts: `pdfsmith_adapter.py:156–162`; `runner.py:201–208`.

The adapter writes `output_dir / input_path.stem + ".md"`. The worker passes its supplied `results_dir` to the parser and subsequently reads the returned path. Cache hits return the cache result directly rather than materializing an owned copy in the requested output directory. external-review-packet external-review-packet

**Concrete failure:** Two workers given a shared directory process different same-stem inputs, or different parsers process the same input. One overwrites the Markdown before the other reads or caches it. The first attempt can then receive the second attempt’s content.

**Status:** This is a concrete path-level risk, not demonstrated historical contamination. The dispatch code establishing actual worker directory arguments and the complete cache helpers are not included.

**Acceptance change:** Give each attempt an exclusive output namespace based on run, pipeline configuration, and input identity. Retain the actual returned output bytes in the immutable run bundle; do not infer their location from a filename or leave replay dependent on mutable cache storage.

Test same-stem inputs, distinct configurations, and concurrent writes through the real CLI dispatch. Verify that the bytes graded, hashed, and exported are identical for each attempt. Late timeout output must not overwrite another attempt or a completed bundle.

## 9. High — Single-file atomicity does not establish bundle or registry atomicity

**Affected:** AC 15; Issues 2, 4, and 6.

The reviewed JSON writer correctly serializes before replacement and uses a temporary sibling file. Preserve it. The existing invoice builder, however, saves DOCX, converts PDF, writes reference text, and writes metadata as separate operations. Running it against existing destinations can modify earlier artifacts before a later stage fails. external-review-packet external-review-packet

**Concrete failure:** All result rows are serialized successfully, but one referenced parser output is missing or the report write fails. A registry entry based on the result JSON or a `complete` flag accepts the partial bundle. Another failure leaves a new DOCX beside an old PDF and reference.

**Acceptance change:** Specify a minimal commit protocol: write only into a new run-owned staging directory; validate required artifacts, hashes, outcome consistency, and exact planned-pair membership; write a completion manifest; then atomically update the authoritative registry’s reference to that immutable bundle.

Readers must validate the bundle contract rather than trust a status flag. A valid completed benchmark may contain parser failures; an eligible successful attempt missing its required output is different.

Inject failures after intermediate generation, during output writing, before completion, and before registry replacement. Include interruption and a missing required artifact despite valid JSON. Prior completed artifacts and registry bytes must survive unchanged.

A staged directory and one final commit point suffice. Distributed transactions and a database are unnecessary. Power-loss durability should be specified separately if claimed.

## 10. High for reporting — The registry must not preserve unsupported authority along with preserved history

**Affected:** AC 2–5, 11, 18; Issues 1 and 6.

The story generator labels the invoice run source-first although its configuration describes PDF-extracted ground truth. It also independently averages available metrics per parser and assigns ranks. These are established producing-code problems, already recognized by the plan. external-review-packet external-review-packet external-review-packet

There is also an explicit retained summary contradiction: the SEC commercial artifact declares 15 results, 14 successes, and 13 failures; the packet’s row summary reports 14 successes and one failure. These cannot all describe the same outcome count. external-review-packet

**Concrete failure:** A registry faithfully preserves a hand-authored strong tier, reads current source files as historical provenance, and regenerates an authoritative-looking ranking over unequal subsets. Preservation has then legitimized the original interpretation rather than preserving evidence.

**Acceptance change:** Preserve original values and labels as historical fields, alongside validated derived counts and current claim dispositions. Historical unknowns must remain unknown. Present-day references cannot upgrade an old run’s reference independence.

Generate primary comparisons only from identical declared populations and metric contracts. Unequal-subset means may remain inspectable diagnostics, but a disclosure footnote should not turn them into the principal ranking.

Define the inventory boundary and snapshot before generating its own outputs. Independently enumerate retained artifacts and classify unreadable, unknown, checkpoint, and merged artifacts. Missing provenance should produce a named limitation, not indefinite forensic reconstruction or silent exclusion.

## 11. Medium — Relocation and repeat checks need to test isolation and per-document reproducibility

**Affected:** AC 12, 14, 17; Issues 4–5.

AC 17 requires a second execution with matching hashes and deterministic aggregates, and a relocation exercise. The earlier comparison records absolute implementation paths and Git-checkout information; the historical invoice configuration also contains an absolute corpus path. Merely changing the working directory would not establish independence from the installed editable checkout. external-review-packet external-review-packet external-review-packet

**Concrete failure:** Replay succeeds from another directory because Python still imports PDFsmith from the original workstation checkout. Separately, two executions exchange correct/incorrect outcomes between two documents but retain the same aggregate, satisfying an aggregate-only repeat check.

**Acceptance change:** Test offline regrading with parser imports, original source directories, network access, and ambient caches unavailable. It should require only the frozen grading dependencies, retained predictions/outputs, and references.

Test fresh relocation separately using retrievable immutable backend source or a package artifact plus declared dependencies. Hashes alone cannot reconstruct missing implementation bytes.

Compare per-document outcomes and normalized predictions, not only totals. Record any output nondeterminism even when aggregates agree. Do not require repeated durations to match. The existing restriction against latency rankings from single-call observations is appropriate; additional performance experiments are not needed for this milestone.

## 12. Medium — The 100-invoice example needs an operational decision and a development-exposure policy

**Affected:** AC 6, 9, 20; Issues 2, 3, and 6.

The packet establishes the intended fixed synthetic population, but does not establish its actual visual diversity. Metadata fields such as region, industry, complexity, and template style cannot substitute for inspection of layouts. The specification appropriately permits ties and poor results. external-review-packet external-review-packet external-review-packet

**Concrete failure:** One hundred invoices share substantially the same structure with different names and amounts. A tailored extractor performs well and the report presents the count as evidence about general invoice ingestion. Alternatively, both parsers preserve the necessary information but the fixed extractor cannot use either representation; the report attributes the failures to parser capability.

**Acceptance change:** Declare a concrete illustrative decision—for example, selecting a local parsing configuration for a controlled born-digital invoice-to-records workflow. Describe observed layout families, page counts, line-item counts, wrapping, continuation, and relevant date/currency conventions.

Freeze extractor development before the scored execution using identified development fixtures. Any subsequent adjustment creates a new protocol version and requires comparable regrading of both parsers. Do not call these retained invoices an unseen test set merely because this execution is new.

Require positive extractor tests on faithful supported representations, inspect parser disagreements, and inspect a sample of shared failures. Attribute errors to reference qualification, lost/misassociated parser information, extractor limitations, or evaluation defects.

A tie can support “both satisfy this contract”; shared failure can support “this integration is inadequate.” Neither requires collecting real vendor documents before completing the worked example.

# 3. Necessary plan changes and scope reductions

**Keep the six issues.** The required changes are acceptance changes and a small dependency adjustment, not a new planning cycle.

Move the use-case definition and public field/record schema to the beginning of Issue 2, before reference qualification is frozen. Issue 3 can then finalize extraction and grading against that contract. Issue 1 must still account for all retained artifacts before milestone closure, but exhaustive recovery of unknowable historical provenance should not become a serial prerequisite for all reference work.

Add the concrete regression witnesses above to the existing issues: changed-PDF/stale qualification; swapped associations and duplicate multiplicity; inaccessible answer-bearing files; asymmetric eligible-input failure; required-metric exception; incompatible/foreign checkpoint rows; cache identity changes; output collision; and partial-bundle finalization. Fault injection at real producer boundaries is appropriate. Tests that only manufacture final JSON or assert that new helper functions reject it are insufficient.

**Remove unconditional repository-wide formatting from the implementation checkpoint commands.** The plan specifies `ruff format .`, while the baseline reports 19 files needing formatting and 183 inherited lint findings. That command can alter unrelated dirty work. Format owned files, run non-mutating repository-wide checks, and distinguish inherited findings from new regressions. Global cleanup should not become this milestone’s hidden dependency. external-review-packet external-review-packet

Full cache functionality can be sequenced separately from the uncached comparison **provided unsafe reuse is disabled or rejected**, rather than left silently available. Preserve the existing atomic writer and runner surface. Do not build a transaction service, a second registry, or a generic record-matching framework.

The already bounded OCR, complex-table/chart, deck, academic, and paid tracks remain follow-on research. Real-vendor sampling, extractor comparisons, latency ranking experiments, and broader robustness studies are also follow-ons. None should block the first milestone’s bounded result, and none should be implied by it. external-review-packet

# 4. Contribution after ParseBench

The packet’s positioning is substantially correct. ParseBench already evaluates enterprise documents, semantic correctness, table associations, and operationally relevant parsing failures. Its launch also discusses quality and cost. Those are not new contributions available to PDF-Bench. [llamaindex.ai](https://www.llamaindex.ai/blog/parsebench)

I verified the paper’s stated 2,078 pages, 1,180 documents, and 169,011 rules, its model-generated/human-verified annotation process, and its TableRecordMatch/GTRM description. The record metric’s preservation of header/value associations and penalties for unmatched records are directly relevant to reuse assessment. They do not automatically define the correct invoice task contract. [arXiv](https://arxiv.org/html/2604.08538v3)

The README at the packet’s pinned code revision states 1,211 unique documents, 180+ pipelines, and deterministic evaluation by default with opt-in chart normalization. The pinned inference runner contains explicit timeout handling and retained error records. Thus, claims that ParseBench lacks operational evidence would be unsupported. I did not independently verify the packet’s cross-page-module assertion. [GitHub](https://raw.githubusercontent.com/run-llama/ParseBench/d423e529ae329317bcd33c650b367acfb60e6620/README.md) [GitHub](https://raw.githubusercontent.com/run-llama/ParseBench/d423e529ae329317bcd33c650b367acfb60e6620/src/parse_bench/inference/runner.py)

**One relevant addition to the prior-art assessment is ExtractBench**, linked from the pinned ParseBench README. Its current documentation addresses schema-guided enterprise extraction, one-to-one record alignment, missing/extra records, and zero scores for failed or missing documents. Acknowledge it and perform a bounded interface/metric comparison; this is not a reason to restart the milestone or execute another benchmark. I inspected its documentation and paper abstract, not its implementation or results. [GitHub](https://github.com/run-llama/ExtractBench)

The reconstruction’s defensible contribution is the **worked engineering method**: turn a particular workflow into a task contract; qualify references against actual inputs; separate predictions from grading; demonstrate how seemingly reasonable evaluation code changes conclusions; preserve failures; and make every claim reproducible from a self-contained bundle.

The 100 retained invoices are sufficient material for that lesson if their actual structure is documented and the protocol works. Their count alone supplies no evidence of general vendor-invoice accuracy. The report should produce a concrete conditional selection outcome and show how a team replaces the illustrative population with its own permitted documents—not merely append a warning about representativeness.

**Source/version limits:** I retrieved the pinned ParseBench README, license, and selected source files. The pinned Hugging Face dataset revision could not be retrieved through the available web route; the current dataset page reports Apache-2.0, but that does not verify the pinned dataset’s contents or source-document rights. I did not reproduce either benchmark’s scores or verify that the packet’s code revision is the latest repository head. [GitHub](https://raw.githubusercontent.com/run-llama/ParseBench/d423e529ae329317bcd33c650b367acfb60e6620/LICENSE)

# 5. Inspection record and execution limits

**Reviewer:** GPT-6 Astra Pro. **Review date:** October 14, 2026. No separate model was selected or invoked; an API snapshot identifier was not exposed.

I read the entire attached packet: confirmed intent, complete specification and plan, review-input manifest, baseline reports, all retained track summaries, the smoke comparison, producing-code and test excerpts, and the retained technical-report excerpt.

I independently computed the uploaded packet’s SHA-256:

```text
aa33a7e48c92d50e923d8e919addcdd872a87e11242952a36dd0eb7a9174f0d5
```

The embedded complete `start-here.txt`, `review-context.txt`, `spec.md`, and `plan.md` all match their declared SHA-256 hashes when only the packet’s separating newlines are removed. This establishes those review-document bytes, not the authenticity or completeness of every reported historical observation.

I did **not** inspect the underlying repository, complete runner/loader/cache/backend implementations, the 100 invoice DOCX/PDF files, their individual semantic references, or original full historical result artifacts. Whole-file hashes accompanying partial excerpts cannot independently validate the omitted source. Installed package versions, dirty-tree state, historical reference identity, and the retained test outcomes therefore remain packet-reported observations.

The only local computation was read-only packet byte/hash inspection. I ran no project tests, PDF parsing, benchmark, provider calls, model judges, reference generation, replay, or repository mutation. The packet’s reported 48 passing tests are not fresh execution evidence from this review, and they do not establish the new milestone’s correctness. external-review-packet