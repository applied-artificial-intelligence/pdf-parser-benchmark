# ParseBench fit assessment

Assessment date: October 15, 2026. No candidate parser was run or scored for this assessment.

ParseBench contains substantial material relevant to business document parsing. For a team processing financial reports, insurance material, contracts or presentation pages, the appropriate starting point is to inspect and run its relevant cases. Our earlier project rationale cannot depend on those categories being absent. Whether a selected parser satisfies a particular business process still requires a task and acceptance rule that the public score actually measures.

This assessment recommends reusing ParseBench's data and native evaluation for relevant parsing capabilities. It does not establish that a company needs a new corpus. The controlled invoice exercise demonstrates how to evaluate a specified extraction task; it is not evidence that ParseBench lacks transactional documents.

## Evidence and acquisition

The code revision is `d423e529ae329317bcd33c650b367acfb60e6620`; the dataset revision is `2805a1d940f95a203e0ae4b88be9934f7765b3fc`. The [pinned dataset card](https://huggingface.co/datasets/llamaindex/ParseBench/blob/2805a1d940f95a203e0ae4b88be9934f7765b3fc/README.md) and [pinned evaluator repository](https://github.com/run-llama/ParseBench/tree/d423e529ae329317bcd33c650b367acfb60e6620) describe the public benchmark. Its April launch article is a dated account, not a substitute for inspecting the current pinned files.

`parsebench-snapshot.json` records every annotation-file SHA256 and all source-file metadata returned by the paginated dataset API. `parsebench-inventory.json` groups every annotation row by dimension and exact source path, retaining line ranges, rule types, tags and upstream inference identities. Both files are in this work unit. Reproduction uses the acquisition/inventory commands below; downloaded originals stay under ignored `data_exports/parsebench/objects/`.

Independent enumeration of those bytes gives:

| Evaluation group | Group/input cases | Annotation rows |
|---|---:|---:|
| Charts | 568 | 4,864 |
| Tables | 503 | 503 |
| Content faithfulness | 506 | 141,322 |
| Semantic formatting | 476 | 5,997 |
| Visual grounding/layout | 500 | 16,325 |

These are 2,553 group/input cases over 2,078 distinct input paths and 2,060 source content identities. The text groups share 507 inputs. Some source bytes also repeat across group directories. The source tree contains one additional unannotated asset, `docs/text/text_sparse__anex.pdf`. A rule row, input path, physical page and original document are different units. The upstream card reports 1,211 original documents and 2,078 pages; this inventory does not independently establish original-document lineage or the page count of every input. Its 2,078 input-path count should not silently become a verified original-document count.

The content group has 170 inputs tagged simple, 119 OCR, 97 multicolumn, 47 multilingual, 33 miscellaneous, 14 dense, 13 handwriting and 13 sparse. Preserve upstream spelling `handwritting` in machine-readable records. The card's illustrative sparse count is 14; this pinned content annotation set contains 13. Some difficulty labels overlap. Tags describe source properties, not a sampled distribution of business workloads.

## What was inspected

`parsebench-inspection-selection.json` declares selection before parsing: two SHA256(path)-ordered inputs per upstream text tag and hard table/layout stratum, plus named business-document candidates. Charts have no easy/hard tags, so chart inspection uses three explicit candidates. Filenames select candidates but do not classify them. The resulting sample is 43 inputs, each containing one physical PDF page. Several pages display a two-page spread or multiple slides.

Every rendered page was visually reviewed, with text layers as auxiliary evidence. `parsebench-inspection-artifacts.json` binds each source SHA256 to its page/render hashes. `parsebench-inspection-observations.json` records each visible document form and the limits of that observation. `parsebench-assessment.json` joins the evidence and leaves uninspected inputs unknown. The sample establishes presence and examples, not prevalence or exhaustive annotation correctness. No translation-quality claim follows from visually identifying multilingual layouts.

| Meaningful workload | Inspected source evidence | What the public evaluation can help select | Remaining fit question |
|---|---|---|---|
| Financial reports and filings | Apple repurchase/subsidiary tables; bank regulation discussion; corporate reconciliation tables; Aviva remuneration charts | Text, table structure and header/value associations, chart data and page layout | Do the selected cases match the team's report types, units, footnotes and required errors? Whole-report extraction must retain its actual context. |
| Insurance and regulated documents | Auto-rating factors, medical-payment rules, provider-network dot matrix, Russian insurance guidance | Dense rules, lists, marked text, tables, localization and multilingual parsing properties | Parsing accuracy does not itself score a coverage decision, premium calculation or provider-network lookup with the team's acceptance rule. |
| Agreements, government rules and forms | Draft asset-purchase agreement with deletions; settlement formula/table; scanned procurement clauses; signed/notarized page; completed handwritten declaration | Text recovery, meaningful formatting, table association, scanned/handwritten content | Can the required legal field or clause be recovered with its operative status and needed cross-references? These inspected excerpts do not establish full-contract task accuracy. |
| Operational and transactional records | Construction change order; synthetic crew timesheet; job-description checkboxes | Field-like layouts, row/column structure and symbol preservation | Are actual supplier forms, record schemas, scan quality and missing-field costs represented? No claim that all invoices are absent follows from this sample. |
| Presentations and technical material | Walmart and ConocoPhillips earnings slides; private-credit investment deck; six-slide handout; ICML formatting example | Tables/charts, content order and technical page layout | Does the task require slide-level boundaries, speaker notes or facts spread across a complete deck? These page examples establish presence, not a full-deck outcome. |

Three filename checks changed the classification: `text_simple__bill.pdf` contains a legislative summary, `text_simple__contract2.pdf` contains a financial-report excerpt, and `Automated-Invoice__p3.pdf` describes an invoice workflow. The file `synthetic_invoce_page1.pdf` is a crew timesheet. Conversely, operational forms and insurance content occur under generic filenames. Missing domain labels cannot prove their absence.

## What the metrics establish

The pinned loader groups rules by `(category, pdf path)` and shares text inference between content and formatting groups. A case can hold many rules. Chart IDs can repeat across different inputs, so a global rule-ID count is incorrect. The inspection tooling preserves group, source path and rule ID together.

Upstream evaluation distinguishes textual content, meaningful formatting, tabular structure/records, chart data and grounding. These are useful parsing outcomes. A schema-specific business result must separately define such questions as which date is the due date, which party is the vendor, which amount includes tax, and whether a record remains attached to the correct header. Matching a task may mean reusing existing annotations and metrics; it does not automatically require creating another benchmark. The related [ExtractBench](https://github.com/run-llama/ExtractBench/tree/0e7647997211867060a645ac82deb9f7bc4a3b3f) should be assessed for schema-guided extraction before proposing new generic field/record infrastructure.

The case-oriented public loader operates on supplied input files. In the inspected sample, long reports/contracts are represented by excerpts, spreads or handouts, rather than their complete original files. That is useful for local parsing capabilities. It does not measure our hypothetical whole-document transaction-completion rate, inter-document reconciliation or the team's business acceptance thresholds. This is a boundary of the reported measurement, not proof that the public benchmark is deficient at its stated task.

## Decision for this reconstruction

Use a matched ParseBench subset for an explicit born-digital report/table parsing question, with exact inputs frozen before parser outputs and native upstream content/table evaluators. Preserve both simple and structurally demanding suitable inputs and state exclusions such as OCR capability. A two-local-parser exercise is not a result for all five dimensions or a substitute for the public leaderboard.

Keep the 100 controlled invoices as a separate worked task with independently qualified source truth. They let us demonstrate field/row association errors, fixed failure denominators and the effect of scoring choices. They do not estimate performance across real suppliers, and they do not justify creating an invoice benchmark merely because invoice filenames were not found here.

For a business evaluation, first specify the documents and decisions involved, then inspect matching public cases and rules. Use them directly where suitable. Add permitted internal documents or task annotations only for a demonstrated mismatch, such as a different supplier/scan distribution or a required field/relationship the chosen public rules do not score. Record the mismatch and its effect on the selection decision. No defined weighted population supports an estimate that ParseBench covers 80%, or any other percentage, of business use cases.

The next scored protocol will freeze its public subset after this assessment. Parser scores are not yet available. A tie, poor local performance or inability to integrate the native metric remains a valid recorded outcome.

## Licensing and limits

The pinned code license and dataset-card metadata declare Apache 2.0. The annotation schema has no per-source original-publication URL, document-family, language or license fields. This assessment records the dataset source link and content identity; it does not claim independent copyright clearance for every underlying publication. Original PDFs and full annotations are not redistributed on this branch. Reduced annotation test fixtures retain Apache licensing and attribution. No paid parser or judge call was made.

## Reproduce the inventory and inspection

The executable `reproduce_parsebench_assessment.sh` in this work unit acquires the pinned data, rebuilds the inventory, renders the same selected inputs and validates observations against their source hashes in a fresh output directory. Run it from the existing repository environment:

```bash
bash /home/stefan/applied-ai/pdf-bench/.workspace/work/2026-10-13-benchmark-rebuild/reproduce_parsebench_assessment.sh
```

For a new investigation, use new manifest/output paths instead of overwriting a completed assessment. Acquisition validates the full annotation/source inventory before atomically replacing a manifest. Inventory generation validates retained byte hashes before replacing its output. The visual observations are a dated inspection record, not an automatic consequence of running the rendering script.

## Next actions

No user decision is needed. Paid comparisons and public-main publication remain outside the approved scope.
