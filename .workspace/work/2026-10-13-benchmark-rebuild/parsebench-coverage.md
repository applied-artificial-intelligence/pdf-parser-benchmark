# Public benchmark assessment for parsing and structured extraction

Assessment revised October 19, 2026. Retained source inspection is complete for mechanical
properties of the full pinned input population. Visual review covers 221 distinct
inputs. All benchmark and GPU execution is paused. Retained parser outputs are
not a completed full-population comparison.

## Recommendation

Select components against a defined collection, downstream task, quality threshold
and total cost. Consult public results before commissioning another comparison.
ParseBench directly addresses the text, tables, charts,
meaningful formatting and localization dimensions for which this project
previously struggled to construct references. Building another general-purpose
corpus of synthetic invoices is not justified by this assessment. The current
deliverable is a [practical evaluation guide](benchmark-design-guide.md), using
this inventory and retained experiments to explain benchmark fit and design.

Use OmniDocBench when formula recognition and its document/layout/language slices
matter. Use ExtractBench for schema-guided information extraction and inspect
ExtractBench Pro for document-specific interpretation, calculation and visual
relationships. Additional internal examples
need a demonstrated mismatch with the relevant public documents or acceptance
criteria. None of this establishes that one public score captures every business
workload, or that any benchmark is the uniquely best choice for all tasks.

## What the complete inventory establishes

The dataset revision is `2805a1d940f95a203e0ae4b88be9934f7765b3fc`; the evaluator
revision is `d423e529ae329317bcd33c650b367acfb60e6620`. Every annotation file and
annotated input was acquired and checked against its pinned LFS or Git identity.
The [full workload index](parsebench-workload-index.csv) is a filterable inventory
of all inputs, source hashes, formats, dimensions, difficulty tags, text-layer
properties, candidate families and visual observations. Its
[structured version](parsebench-workload-index.json) retains the content snippets
behind automatic classification candidates. Original sources remain outside Git.

| Capability group | Group/input cases | Annotation rows |
|---|---:|---:|
| Text recovery and reading order | 506 | 141,322 |
| Tables | 503 | 503 |
| Charts | 568 | 4,864 |
| Meaningful formatting | 476 | 5,997 |
| Visual grounding/layout | 500 | 16,325 |
| Total | 2,553 | 169,011 |

There are 2,078 input paths and 2,060 distinct acquired SHA256 identities. The
text groups share inputs, and some identical source bytes occur in different
folders. Cases, rule rows, input files and independent original documents are
different counting units.

The files comprise 2,036 PDFs and 42 images: 23 JPEGs and 19 PNGs. The images all
belong to the grounding group. There are 2,038 physical PDF pages plus the 42
images, or 2,080 page-like units. One PDF, `docs/text/text_ocr__012-25.pdf`, contains
three pages; all other inputs contain one page or image. The three-page Spanish
regulatory resolution was inspected on all pages, and its content annotations
include material from its final page. It is not merely an unannotated appendix.
The upstream headline count of 2,078 pages should therefore be distinguished from
our independently measured physical pages and image units. The upstream count of
1,211 original documents remains upstream-reported; original-document lineage was
not independently reconstructed.

Of the inputs, 141 have no extractable text layer and 168 contain fewer than 100
extracted characters. Every one of those 168 sparse inputs was reviewed visually,
including the two additional pages of the three-page input. Missing text can mean
a scan, an image, a pictorial instruction page or a nearly blank page. It cannot
by itself identify the document family or establish that OCR is needed.

The [source measurement](parsebench-source-coverage.json),
[annotation inventory](parsebench-inventory.json) and
[sparse-input observations](coverage-sparse-review-observations.json) retain the
individual evidence. `parsebench-source-coverage-v1.json` preserves the exact
original coverage bytes bound to the first full-run plans; its older page total
includes images and must not be described as a PDF-only total.

## Documents and representativeness

Source review confirms financial statements, regulatory and insurance tables,
contracts, signed legal documents, government correspondence, employment and
administrative forms, corporate memoranda, earnings presentations, technical
publications, newspapers and handwritten material. Scanned administrative and
legal forms occur under filenames that do not reveal their contents. Blank notes,
cover pages and a photographed classroom poster also occur. They test parsing
properties but are not equally informative for every business decision.

The workload index separates three facts: a capability group, automatic
content-based family candidates, and observed visual form. Keyword matches are
retrieval aids with retained snippets, not certified domain labels. They overlap,
and 1,041 inputs have no candidate under the declared English keyword rules.
Those inputs are not classified as irrelevant or absent from business use.
Visual observations cover 221 distinct inputs; the remaining forms are explicitly
unreviewed. We do not turn missing metadata into a coverage claim.

The table population is concentrated in insurance-related sources. In particular,
193 of the 503 table input paths contain SERFF in their published names. That is
a reproducible source-name count, supported by inspected insurance examples,
not an independently verified estimate of all insurance documents in the corpus.
Multiple pages also come from the same reports and filing bundles. Treating every
page as an independent business-document draw would overstate diversity.

The published tags identify OCR, handwriting, multilingual, dense, multicolumn,
simple and sparse text cases, and easy/hard tables and layouts. Tags overlap.
They describe challenge coverage, not real production frequencies. No weighted
population supports an assertion that ParseBench covers 80%, or any other share,
of all business use cases. A team should select and weight relevant slices using
its actual volumes and failure consequences.

## What the ground truth measures

| Requirement | ParseBench reference and score | Interpretation and boundary |
|---|---|---|
| Recover text and its order | Word/sentence/digit content rules, unwanted/repeated content rules and reading-order constraints; native content-faithfulness score | Useful for omissions, hallucinations and order. A mean of 0.90 is not a claim that 90% of pages are entirely correct. |
| Recover tables | Ground-truth HTML; GriTS and TableRecordMatch composite | Tests structure and header/value associations. It does not directly implement every workflow's all-records-correct acceptance rule. |
| Recover charts | Annotated label/value data points, with declared numeric tolerances | Tests selected chart facts. It is not pixel-perfect figure reconstruction or a test of every possible claim in a diagram. |
| Preserve meaningful formatting | Bold, strikeout, superscript/subscript, heading hierarchy and other formatting rules | Measures supported semantic distinctions. Some available rule metrics, including italic/underline/highlight, are excluded from the headline formatting score. LaTeX-related rules do not replace a dedicated formula-recognition benchmark. |
| Preserve localization and attribution | Region, class, content and order annotations; native grounding evaluation | Tests where an extracted element came from. It does not measure recreation of an entire editable page or the correctness of every figure's meaning. |

The upstream dataset describes machine-assisted annotation followed by human
verification. We verified reference availability and inspected examples, not all
169,011 annotations against the original source. The pinned JSONL rows do not
carry per-rule verification flags; their absence cannot independently confirm or
refute the documented review process. Annotation errors remain possible, as in
any benchmark, but this review has not established a systematic reference defect
that warrants replacing ParseBench.

An overall mean across five dimensions assigns weights to capabilities. A team
that never extracts chart data should not inherit that weighting automatically.
Conversely, a parser that returns readable text while losing table associations
cannot be selected on text similarity alone. The five dimensions should remain
visible beside any combined score.

## Where other public evaluation is useful

[OmniDocBench](https://github.com/opendatalab/OmniDocBench) documents page/block
attributes, text, table, layout, reading-order and formula references, including
LaTeX and formula-specific evaluation. Its documented document and language slices
complement ParseBench's enterprise-oriented parsing tasks. Formula-heavy technical
papers are a concrete reason to inspect that evaluation rather than generate new
formula truth here. This is a contract assessment, not a new executed OmniDocBench
comparison.

[ExtractBench](https://github.com/run-llama/ExtractBench) documents 370 inputs and
4,869 pages across short, medium and long documents, with schema-guided values,
record alignment and evidence/grounding. Its documented tasks include complete
long lists, finding requested facts in long documents and dense forms. The README
reports 325 real and 45 synthetic sources across eight business domains. These
figures are upstream-reported, not independently re-enumerated in this assessment.
They make it inappropriate to claim that public benchmarks generally omit
long-document extraction or business forms.

The primary-source READMEs were acquired at pinned revisions with hashes
in [the contract source record](benchmark-contract-sources.json). This does not
upgrade the older static ExtractBench implementation review into a current run.
The old source-level missing/null discrepancy is tied to its old revision; it is
not a claim about the present leaderboard.

### ExtractBench Pro

The [pinned Pro dataset card](https://huggingface.co/datasets/llamaindex/ExtractBenchPro/blob/4ae1ffe48696297a8f6c9153034b3914fc7763d0/README.md)
reports 100 synthetic documents, 2,622 pages, 86 document types and 144,141 expected
values. Document length ranges from 1 to 83 pages. Its challenge counts are:

| Challenge | Documents |
|---|---:|
| Document conventions | 22 |
| Organization-specific vocabulary | 14 |
| Counting rules | 12 |
| Drawn relationships | 20 |
| Charts inside documents | 25 |
| Long chart sheets | 7 |

The examples require interpreting document rules, calculating requested values
and following visual relationships. They extend the original extraction task,
using the same schema/field-rule format and evaluator. The upstream construction
sets fictional facts before rendering. It supplies repeatable references, while
synthetic conditions and deliberate challenge selection limit prevalence claims
about a customer's documents.

The [October 15 announcement](https://www.llamaindex.ai/blog/introducing-extractbench-pro)
adds perfect-document value F1 to value and grounded F1 reporting. Perfect value
F1 does not by itself require correct grounding. The announcement also states a
30-minute per-document limit and zero value/grounding scores for failed or timed-out
documents. Those are published evaluation conditions, not local measurements.

The extension changes gap assessment. Internal jargon, rules elsewhere in a
document, derived counts and diagram relationships already occur in public
evaluation. Any additional evaluation must identify the actual mismatch with
required documents, schemas, acceptance rules or deployment. An engineering label
alone does not establish a missing public capability.

This revision reads the pinned card, shared README and announcement. It does not
acquire or inspect the 100 PDFs, audit every expected value, execute the shared
evaluator or reproduce published system scores. Pro's counts and generation
method remain upstream-reported, distinct from the mechanically enumerated
ParseBench population. The [source record](benchmark-contract-sources.json)
retains the dataset revision and card hash.

### Release history, maturity and claims in the brief

Primary announcements date ParseBench to April 13, ExtractBench to August 11 and
Pro to October 15, 2026. Pro is the recent extension; the original ExtractBench
was not first released days before this assessment. Open data, code and declared
metrics make the contracts inspectable. They do not establish independent
reference validation or a permanent ranking of changing provider configurations.

ParseBench has five headline dimensions. Reading order and heading hierarchy
appear within existing dimensions; the source does not establish separate overall
scores for cross-page flow or tables-of-contents navigation. The pinned 147-row
leaderboard contains no provider named OpenParse. No claim about that parser's
rank is carried into the guide. Comparisons must name the actual entry and revision.

These checks support reuse of substantial public evidence. They establish no
business-wide coverage percentage, current universal winner or reason to rebuild
the public benchmarks. A targeted customer acceptance comparison remains a
different question from reproducing a general leaderboard.

## Related tools and operating evidence

### OpenDocRouter

The [official SDK](https://github.com/run-llama/opendocrouter-py/tree/84c5420a3b824a0b2d306bba6583da92460a0f05)
and public OpenAPI document expose model listing, uploads and model-selected
parsing through one client. This is an access interface, not a benchmark or
evidence that providers return equivalent output. The public API description
specifies PDF/image parsing to Markdown. No authenticated request, upload,
inference, billing experiment or model-catalog comparison was performed here.
The SDK snapshot and the OpenAPI source identity are recorded for inspection.

A common API can reduce integration effort. A routed comparison must still
identify the selected model/configuration, preprocessing, representation,
failures and price boundary. Routing/fallback policies require evaluation as
the actual combination selected for deployment.

### Confidence and total cost

LlamaIndex's [September 16 confidence guidance](https://www.llamaindex.ai/blog/what-makes-an-extraction-confidence-score-useful)
already describes precision-targeted cutoffs, separate validation data and
rechecking under changing document conditions. The guide adopts that evaluation
principle without transferring a provider's example cutoff to a customer's work.
Scores on returned values do not account for never-returned required values.
Whole-document acceptance and final reviewed-output accuracy remain separate.

Candidate cost must include review workload, failed/retried work, operating
effort and quality requirements beside processing charges. The revised guide's
cost table is hypothetical; it contains no current provider price comparison.
Cold versus initialized-model timing and application-to-result elapsed time
are declared measurement choices. This source review adds no local latency,
throughput, confidence calibration, serving-cost or GPU-utilization measurement.

### Retained local execution limitations

The retained [PDFSmith revision](https://github.com/applied-artificial-intelligence/pdfsmith/tree/48de187103ffd5e0932ee3bb550affc58314a346/src/pdfsmith/backends)
starts fresh subprocesses for the relevant backends. Docling creates a converter
per extraction; Marker recreates models and owned inference processes with CPU
execution and zero GPU offload configured; Unstructured loads spaCy per call.
The benchmark also starts per-document outer workers. Keeping only those outer
workers alive would not establish inner-model reuse. These are source observations,
not measured reload fractions, warm speedups or general properties of the underlying
SDKs. Exact file hashes remain in guide-evidence.json. The prior helper-process
cleanup is recorded in execution-stop-20261017.json; it is not a throughput result.

## What requires internal work

Additional evaluation is warranted when an important workload is demonstrably
unrepresented, the reference does not score the required fact/relationship, or
the operating contract changes the decision. Examples include a team's actual
scan degradation and document mix, an all-fields-and-records acceptance threshold,
or required evidence links and image assets in the delivered output. First check
whether existing ParseBench/OmniDocBench/ExtractBench/Pro cases and annotations supply
that need. A different acceptance threshold may need a different aggregate rather
than a new corpus.

The retained invoices remain a controlled example of reference qualification and
scoring choices. They are not evidence that ParseBench lacks invoices, and their
few layouts do not estimate performance on real suppliers. No new synthetic
invoice generation is part of this recommendation.

## Consequence for the PDFSmith comparison

The local registry contains 19 backend families: eleven local and eight requiring
commercial services. Model aliases are configurations, not additional independent
parser implementations. All eleven local integrations have now returned actual
public-input output in readiness probes, after isolated dependency/model repairs.
Full-population executions use explicit configurations and retain every planned
input and failure. There are 7,922 completed attempts retained in the eleven
primary runs. All execution is now paused, including the overnight queue.
The full-population comparison and prepared 208-input screen are deferred;
neither is a prerequisite for the guide. No full-population winner is asserted.

The current PDFSmith API returns Markdown without a grounding sidecar. Its
published image-capable-backend set is also empty in the frozen source snapshot.
The 42 grounding image inputs are therefore input-contract incompatibilities;
the missing coordinates affect grounding even on PDF inputs. Native grounding
failure/zero-padding must be labelled as unsupported output, not a finding that
Docling, Marker or another underlying SDK cannot locate elements. An application
requiring coordinates cannot choose through this Markdown-only comparison alone.

The pinned public leaderboard already reports configurations overlapping several
local families. Repeating those runs needs an unanswered decision that published
evidence cannot resolve, such as a consequential configuration or output-contract
difference. A new experiment requires a specified comparison and fresh resource
authorization. Paid providers remain uncalled and require an exact configuration
and approved spend ceiling before execution.

## Next actions

No user action is required for this assessment or the guide. All benchmark and GPU
work remains paused; paid runs and public-main merge remain unapproved.
