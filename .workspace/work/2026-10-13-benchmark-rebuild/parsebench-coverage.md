# ParseBench coverage and the PDF-Bench decision

Assessment updated October 17, 2026. Source inspection is complete for mechanical
properties of the full pinned input population. Visual review covers 221 distinct
inputs. All benchmark and GPU execution is paused. Retained parser outputs are
not a completed full-population comparison.

## Recommendation

Consult ParseBench's published results before commissioning another parser
comparison. It directly addresses the text, tables, charts,
meaningful formatting and localization dimensions for which this project
previously struggled to construct references. Building another general-purpose
corpus of synthetic invoices is not justified by this assessment. The current
deliverable is a [practical evaluation guide](benchmark-design-guide.md), using
this inventory and retained experiments to explain benchmark fit and design.

Use OmniDocBench when formula recognition and its document/layout/language slices
matter. Use ExtractBench when the decision concerns schema-guided information
extraction, repeated records or long-document tasks. Additional internal examples
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

The current primary-source READMEs were acquired at pinned revisions with hashes
in [the contract source record](benchmark-contract-sources.json). This does not
upgrade the older static ExtractBench implementation review into a current run.
The old source-level missing/null discrepancy is tied to its old revision; it is
not a claim about the present leaderboard.

## What requires internal work

Additional evaluation is warranted when an important workload is demonstrably
unrepresented, the reference does not score the required fact/relationship, or
the operating contract changes the decision. Examples include a team's actual
scan degradation and document mix, an all-fields-and-records acceptance threshold,
or required evidence links and image assets in the delivered output. First check
whether existing ParseBench/OmniDocBench/ExtractBench cases and annotations supply
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
