**Disposition: REVISE (bounded), not BLOCK.** The spec and plan are sound in direction and already name most of the real defects. Issue 1 (registry) and the non-scored parts of Issue 4 can start now. The scored invoice comparison (Issues 2–3–5) should not start until four contract gaps are closed on paper: the line-item/normalization contract, an extractor-attribution control, the qualification instrument, and the attempt ledger. These are 1–2 days of specification plus one cheap pre-run inventory, not open research.

**What I inspected and did not execute.** I read the full 4,002-line packet: start-here, review-context, spec, plan, manifest, baseline checks, nine retained track summaries, the smoke comparison pack, and all code excerpts. I did not access the repository, run any test, execute any parser, download ParseBench, or make paid calls. I ran one web search to cross-check the ParseBench figures. Everything below about runtime behavior is inference from the excerpts and recorded artifacts, labeled as such.

---

## A. Blockers for the scored run (resolve before Issues 2–3–5)

**1. The task contract is unspecified where it matters most: line-item identity, matching, and normalization. (AC 7, 9, 11; Issues 2–3)**

Evidence: the only existing grader is `grade_fields` (local_evaluation.py 141–154): five scalar labels, exact string equality on a `^Label:` regex, no line items. Metadata stores totals as `float(tax_result.total)` (generate_invoice_corpus.py 299–301) and records only `line_item_count`, not items. The DOCX text extractor assumes the first row is a header and iterates `row.cells`, which in python-docx repeats merged cells (107–121). Date generation uses `datetime.now()` and module-level `random` (data_generators.py 193–194), so regional date surface forms in the DOCX are unknown until inventoried.

Failure scenarios: a parser emits `Total: 1,275.40` and is scored wrong against `1275.40`; a float `1234.5` in metadata is compared to the rendered `1,234.50`; a DD/MM region renders `03/04/2026` and the blind extractor has no licensed way to choose; two identical line items collapse to one; a totals table with no header row becomes a "record".

Acceptance change to AC 9: a frozen, hashed task-contract document must exist before execution, specifying (a) each reference field stores both the semantic value and the exact rendered surface string from the DOCX; the grader accepts the whitespace-normalized surface string or the canonical form and nothing else; (b) amounts compare as `Decimal` with declared scale, never float; (c) a line-item record is the ordered tuple (description, quantity, unit price, line total), matched as a multiset after normalization, with missing/extra counted separately and document success = all fields and all records; (d) a pre-run inventory across all 100 DOCX of tables per document, header string sets, merged cells, and page spans, with any structure outside the contract marked unavailable before any parser runs. Exact matching is enough for synthetic data; do not add fuzzy or Hungarian matching.

**2. Without a ceiling control and a failure taxonomy, the fixed extractor's limits will be booked against the parsers. (AC 9, 18; Issues 3, 6)**

Evidence: in the smoke, pypdf scored 0/5 on `columns` although every value token was present (technical-report 37–42). That is a legitimate pipeline result, but the plan has no mechanism to say how much of the 100-document result is extractor rather than parser.

Failure scenario: pdfplumber renders the line-item table with multiple spaces; the extractor expects pipe separators; zero records are recovered; the report says "pdfplumber fails line-item recovery" when the parser output was correct.

Acceptance change to AC 9/18: (a) extractor ceiling control — run the frozen extractor over a parser-independent linearization of every reference (a fixed format written from the reference JSON); the recovered fraction is the extractor's ceiling and is reported per field and record type beside parser scores; (b) every document-level task failure (or a stratified sample of at least 40 if more) is hand-labeled as parser-dropped-content / parser-misordered / extractor-unsupported-representation / reference-gap, with counts in the report; (c) the extractor's development inputs are declared — the smoke variants plus a listed set of at most ten retained IDs — and it is frozen by hash before the run. Blindness at runtime is necessary but not sufficient; the author knows the templates, and the report should say so as a teaching point rather than imply otherwise.

**3. Qualification must name its instrument, and stratified visual review is not enough at this corpus size. (AC 8; Issue 2)**

Evidence: Issue 2 says "inspect source and rendered PDFs" without saying with what. If disagreement detection reads pypdf or pdfplumber text, qualification is parser-dependent in a weaker form of the SEC mistake.

Failure scenario: LibreOffice clips the last column of a wide table on one unsampled document; both parsers miss line totals; the report concludes neither parser recovers line items for that layout cell.

Acceptance change to AC 8: (a) a mechanical presence check of every reference value in the PDF text layer for all 100 documents, using a non-compared instrument (PyMuPDF 1.26.6 is installed; pdftotext is an alternative), declared as qualification-only; (b) a batch-provenance check that the retained PDF came from the retained DOCX — DOCX core-properties timestamps versus PDF CreationDate/Producer, with the LibreOffice producer string recorded; (c) a full rasterized thumbnail pass of all pages for truncation and overflow — at ~100–200 pages this is cheaper than arguing about sampling — plus close reading of every mechanical miss and at least one document per template×complexity cell; (d) any re-rendered document is flagged as a mixed-rendition item, because today's LibreOffice differs from the historical converter and a parser difference on those documents is confounded with converter version.

**4. The attempt ledger does not exist before execution, and three status paths are wrong in the retained code. (AC 10, 16; Issue 4)**

Evidence: skipped parser/document pairs are counted and printed, never recorded (runner.py 316–326); timeout is inferred from the substring `"exceeded"` (local_evaluation.py 183–184); the adapter writes and returns a path for empty markdown (pdfsmith_adapter.py 157–162), the runner marks it success, the smoke recorded the raster output as `status: success` with SHA-256 `e3b0c442…` (the hash of the empty string), and the current test enshrines that (`test_local_evaluation.py` 67–68).

Failure scenario: a worker-pool crash after 150 pairs leaves no record for the remaining 50, and nothing can prove 200 were planned; a backend raising "rate limit exceeded" is classified as a timeout while a real `TimeoutError` with other text is classified as failure.

Acceptance change to AC 10: the planned-pair manifest (200 primary plus controls) is written and hashed before execution; terminal status comes from a closed enum set by mechanism — timeout only from the enforcing wrapper's exception type, `success_empty` when the stripped output is empty, `not_started` for pairs absent from the journal; ledger minus journal equals incomplete. Historical rows cannot be reclassified unless raw outputs were retained; the registry must record "empty-status unknown" for them.

**5. The scored run must go through the real adapter with an explicit cache mode. (AC 13; Issue 4)**

Evidence: `PdfsmithAdapter.parse` always consults `.cache` relative to CWD (142–147); the key is name + pdfsmith `__version__` + 16 hex of the input (caching.py 109–111) and omits backend package versions and kwargs. The smoke avoided this by using `FreshLocalParser`, a side wrapper (`fresh-pdfsmith-*`), so the reviewed experiment never exercised the production adapter.

Failure scenario: pypdf is upgraded; the key is unchanged; a cached output is attributed to the new version. Or: the 100-document run again uses the wrapper, the adapter is never repaired, and the "existing surface" and the evidence diverge.

Acceptance change to AC 13: the scored run uses `PdfsmithAdapter` with a recorded `cache_mode ∈ {read-write, bypass}`; the key includes backend package `version()`, a hash of canonicalized kwargs, and the PDFsmith source SHA already in the manifest. If no output-affecting option exists for the two local backends, say so and test the version dimension only; do not fabricate an option.

## B. Significant findings (fix within the milestone; not blocking start)

**6. Relocation replay will crash before testing anything.** `run_comparison` calls `git rev-parse` and `git status` via `check_output` (local_evaluation.py 242–247); outside a checkout that raises `CalledProcessError`. `invoices_100docs_fresh.yaml` hardcodes `corpus_dir: /home/stefan/...`; the investor-deck result references `/tmp/business_synthetic_investor_decks_subset.yaml`; PDFsmith is editable with disagreeing metadata, so `pip install pdfsmith==0.2.0` cannot reproduce it. AC 17 change: bundle-relative paths, best-effort revision capture recording "unavailable", and replay that verifies `pdfsmith_source_sha256` and backend versions and reports a mismatch as "different implementation", not as an error.

**7. Use the real inconsistencies in retained artifacts as red fixtures.** The packet contains three that a registry must flag without fabrication: `sec_filings_commercial_5docs` declares success 14, failure 13, total 15 (actual rows 15; 14+13≠15); `sec_filings_screen_all` is named "All 89 Documents" but declares 320 documents and 320 rows; the first invoice cloud row's 0.000294 s is consistent with the runner timing the `parser.parse` call around a cache hit (runner.py 202–204, adapter 142–147). The 0.048 s for pypdfium2 on a full annual report (sec_filings_47docs first row) looks like the same thing; that is inference, not established.

**8. The SEC reference is a different filing, not just a noisy rendering.** `sec_filings_47docs.yaml` 3–5 benchmarks ARS annual-report PDFs against 10-K iXBRL HTML. An ARS is frequently not the 10-K. The 0.90 pypdfium2 threshold therefore selected for ARS≈10-K content overlap and against pypdfium2 failures simultaneously. The SLATE's "tier_1_stronger_comparison … strong for text/order" cannot stand; the registry should demote to historical/directional with this reason. Note also that the "selection changes ranking" counterexample cannot be computed from retained data — `sec_filings_screen_all` has pypdfium2 only — so the worked example must demonstrate selection effects on the new run (e.g., apply a hypothetical "drop documents where parser A scores < x" rule and show the paired result shift), and present the SEC case as the rule, not the counterfactual.

**9. Reference-description count is three, not two.** The yaml says PDF-extracted, the SLATE says source-first, and the retained builder extracts from DOCX with paragraphs before tables (generate_invoice_corpus.py 274–278). Which of `ground_truth` and `ground_truth_backup` is which is unknown. Issue 2's comparison of versions is right; it should also hash both directories against a fresh `extract_ground_truth_from_docx` output to test whether either is byte-reproducible from the retained DOCX.

**10. Multi-file atomicity: use the simplest pattern.** Write all artifacts into `run-dir.incomplete/`, validate, write a hashed `manifest.json` last with the existing atomic writer, then rename the directory. Registry acceptance requires manifest present and hashes verified. No transaction log.

## C. Audit of the proposed red/green checks

- Issue 1 (uneven coverage, SEC disagreement): good — use the real artifacts in finding 7.
- Issue 2 ("introduce a real generator/converter defect"): a mutated DOCX is an injected input, not a converter defect; acceptable for testing the qualifier if labeled as such. The real evidence is the qualifier's counts over the actual 100 documents. Do not rerun the seedless, `datetime.now()`-dependent generator to recreate anything.
- Issue 3 (reordered labels, transposed headers): these are mutations of parser output, fine for grader tests, but the extractor and grader share an author and likely a normalization function, so grader tests must use hand-written literal predictions, and extractor tests must use real outputs (smoke `columns` is a genuine case). Make blindness structural: run the extractor in a subprocess with reference files moved or unreadable.
- Issue 4 (stale cache via real option; checkpoint reuse via real runner): good, with the caveat in finding 5. The "enforced delayed backend" is a fabricated backend; it tests the mechanism, not a parser, and should be labeled a control.
- Issue 4 (serializer/I-O injection): the existing `test_bad_metric_produced_by_runner…` monkeypatches `METRIC_FUNCTIONS` and exercises the real writer; adequate. Note it also asserts `success_count == 1` on a row with a garbage metric, which is the AC 10 defect in miniature.
- Issue 5 (second fresh run, offline regrade): keep; cheap.

## D. Representativeness and milestone sufficiency

A hundred synthetic invoices are 100 fills of a small number of layout cells (template_style × complexity), all rendered by one producer from python-docx. The effective sample for parser-versus-layout behavior is the number of distinct cells, not 100. The report must state that count and present results per cell; the 100 are not 100 independent layout trials, and no confidence interval should pretend otherwise. This is a teaching point, not a defect.

The milestone does demonstrate reference truth, grader design, failure accounting, and interpretation. Its weakest teaching element is the parser pair: pypdf and pdfplumber are both text-layer extractors, so the result will mostly turn on line ordering. Optional but high-value: add pymupdf4llm (0.2.2, installed, no download) as a third parser. It emits Markdown tables, which makes the "representation versus extractor" question real and bounded (300 attempts). Not required by the spec; recommend it.

## E. ParseBench positioning and reuse

Positioning is correct: acknowledge, don't claim novelty on enterprise documents or semantic metrics, don't replicate. Secondary sources corroborate the packet's figures — about 2,078 human-verified pages from about 1,211 enterprise documents with 169,011 rule-based tests across five dimensions, purely rule-based with no LLM-as-judge, and an overall score that is the unweighted mean across the five dimensions. That unweighted mean is itself a design choice a team should not inherit, which fits the article's thesis. Reuse: GTRM/TableRecordMatch belongs to the tables follow-on track only; it needs their annotation format, so it has no place in the invoice milestone. Still unverified from primary sources: the paper-v3 document count (1,180) versus README (1,211), the README's deterministic-default/opt-in-paid-normalization claim, dataset-source rights for the enterprise documents, and dependency compatibility.

## F. Unsupported or inconsistent claims in the packet

- technical-report 82–83: "Ruff formatting and focused lint passed" versus baseline `ruff format --check .` reporting 19 files to reformat and 183 lint findings. Scope "focused" explicitly or correct the report.
- `sec_filings_47docs.yaml` 4–5: "ensuring ground truth noise < 10%" — the threshold bounds parser error plus reference mismatch jointly; the packet already says this, the yaml still asserts it.
- Findings 7 and 8 above (summary arithmetic, "All 89", ARS versus 10-K).
- `build_documents` labels the smoke corpus `domain="pandoc"` (local_evaluation.py 84); cosmetic, but it will surface in the registry.

## G. Complexity to remove or keep bounded

Disable checkpoint reuse for the scored run and add only a manifest-hash guard rather than a general checkpoint-compatibility validator. Change the cache key scheme and let old entries become unreachable; do not migrate or invalidate historical cache contents. Relocation is `cp -r` to another directory and run; no dependency-declaration framework. Exact multiset matching for line items; no fuzzy matching. Keep the common-success subset in the appendix only. The premises/claims matrices and `closure check: ok` verify document structure, not evidence; treat them as process hygiene, never as a passing check.

## H. Still unverified and outside this review

Whether raw parser outputs for historical runs are retained (determines whether offline regrading and empty-status reclassification of old rows are possible at all); the actual DOCX template date and header surface forms; what kwargs PDFsmith's pypdf and pdfplumber backends accept; whether the runner's `results_dir` is per-parser (local_evaluation.py 181 assumes `results_dir/parser/doc_id.md` while the adapter writes `input_path.stem`, so same-stem inputs or doc_id≠stem will mis-hash); and the GPT review required by AC 1, which this report does not substitute for. No runtime experiment, historical reconstruction, or external review has passed on the strength of this document.