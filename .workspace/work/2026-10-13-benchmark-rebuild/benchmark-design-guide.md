# Choosing a PDF parser: when public benchmarks are enough

Use public benchmarks to identify credible parser candidates. Check whether their
documents, required outputs and scoring rules support your decision before
collecting new references or running another comparison. Additional evaluation
earns its cost when it can resolve an important uncertainty about the workflow.

That is the useful purpose of PDF-Bench today. Our original work struggled with
ground truth, inconsistent references and comparisons that measured different
things. ParseBench now provides much of the public parsing evaluation we needed.
Our contribution is to explain how to use that evidence and how to avoid the
mistakes in our own attempts. We have not established a consequential coverage
deficit that justifies a replacement general-purpose corpus.

This guide uses public sources and retained PDF-Bench evidence reviewed on
October 17, 2026. No parser, native evaluator or GPU experiment was run to produce
it. The [evidence record](guide-evidence.json) identifies the sources and limits
behind its factual examples.

## The output you need determines the comparison

"Parse this PDF" can describe several different jobs. A searchable document needs
readable text and usable boundaries. A table extraction needs the association
between each value, row and header. A chart extraction needs values attached to
the right labels. A review interface may need source coordinates for every fact.
An invoice workflow needs the requested fields and complete line records in a
declared schema.

These requirements overlap, but success on one does not establish success on the
others. A parser can preserve every word in two adjacent address blocks while
merging the supplier and recipient. A downstream extractor then has the words
without a reliable way to assign the parties. A readable Markdown document can
also omit the coordinates needed by an evidence viewer.

Before comparing scores, describe the decision in terms of the delivered output:
which facts and associations must survive, which mistakes require review, and
which interface receives the result. Privacy, supported file types and operating
limits constrain the candidate set too. They should be established before
spending time on a parser that cannot be deployed in the intended setting.

For a document-search application, a parsing benchmark can support a judgement
about text and reading order. It does not establish retrieval relevance or the
correctness of answers generated later. Keep the parsing decision and the
downstream application evaluation distinct, then inspect where failures pass
between them.

## Start with the public evidence that answers your task

ParseBench evaluates text faithfulness, tables, chart facts, meaningful formatting
and visual grounding. Its references and evaluation code address several of the
hardest parts of constructing a parsing comparison. Its
[published leaderboard](https://github.com/run-llama/ParseBench/blob/d423e529ae329317bcd33c650b367acfb60e6620/leaderboard.csv)
also provides results that a new project should consult before repeating work.
The checked snapshot contains 147 configuration rows, including pypdf, PyMuPDF,
PyMuPDF4LLM and a Docling-based entry. Configuration rows are not independent
parser families. A family name alone does not establish equivalence to a particular
local wrapper, model version or hosted service.

Different public benchmarks answer different questions:

| Decision | Public evidence to inspect | What still needs matching |
|---|---|---|
| Recover page text, tables, chart facts, meaningful formatting or source regions | [ParseBench](https://github.com/run-llama/ParseBench) and its dimension-specific results | Relevant document conditions, required representations and the particular capability score |
| Return schema-guided fields, repeated records and supporting evidence from documents | [ExtractBench](https://github.com/run-llama/ExtractBench/tree/56b8fdd91b2cf3648caf75c717c68441ecf4d43f) | Applicable document types, schema semantics, completeness and grounding requirements |
| Parse technical or varied document layouts where formulas and language slices matter | [OmniDocBench](https://github.com/opendatalab/OmniDocBench/tree/f133a71e9e91c3621c7ce8994200a7b394a06eb3) | Relevant formula, text, layout, table and language conditions |

ExtractBench explicitly includes schema-guided extraction, repeated structures
and source evidence, with short, medium and long document slices. OmniDocBench
documents formula references and formula-specific evaluation alongside other
parsing elements. Long-document extraction and formula recognition therefore
need a review of existing public evidence before they become reasons to create
new truth. These are assessments of their documented contracts; we did not run
either benchmark for this guide.

Published results can support a shortlist without another local run. A new run
may be useful when the required configuration is untested, the relevant slice is
not separately reported, or integration changes the available output. It should
answer that question explicitly. Adding another aggregate for an already reported
configuration is a weak contribution by itself.

## Judge the documents as well as the benchmark description

An industry label is a starting point for inspection. Within financial reports,
for example, narrative paragraphs, image-only pages, dense tables and earnings
charts place different demands on a parser. Two corpora labelled "finance" may
exercise very different capabilities.

Our retained ParseBench assessment accounts for **2,078 input paths** and
**2,553 capability-group cases**, with **2,060 distinct file hashes**. Shared inputs
and duplicate bytes explain why these are different counts. The inputs comprise
2,036 PDFs and 42 images. They are predominantly individual page inputs; one PDF
contains three pages. Input files and test cases should not be presented as a
count of independent, complete business documents. The
[filterable workload inventory](parsebench-workload-index.csv) exposes source
paths, hashes, dimensions, challenge tags, text-layer properties and observations.
The [coverage assessment](parsebench-coverage.md) explains the counting units.

Mechanical properties were measured across the full pinned source population.
Visual observations cover **221 distinct inputs**, including all 168 inputs with
fewer than 100 mechanically extracted characters. Source review found reports,
contracts, administrative forms, correspondence, presentations, technical
material and other forms. It did not certify every reference or classify every
document into a complete business taxonomy.

That distinction prevents a common mistake. Our keyword-based family suggestions
leave many inputs unidentified. An absent keyword label means the classifier did
not identify a family. It does not prove the benchmark lacks that family. A sparse
text layer also identifies a review candidate, not necessarily a difficult scan:
covers, pictorial instructions and nearly blank pages can contain little text.

Source concentration matters too. Of the 503 table input paths, 193 contain SERFF
in their published names. This is a source-name count, not a verified estimate of
all insurance content. It prompts a practical question: do these table forms
resemble the forms that matter to the reader's decision? Multiple pages from the
same report or template also should not be treated as independent observations
of layout diversity. The [source measurement](parsebench-source-coverage.json)
retains the underlying rows.

A useful fit judgement names the important document conditions, points to
matching public examples, and records what remains unexamined. It does not assign
a percentage of all business use cases without a defined population and weighting.
We found no basis for such a percentage here, and no systematic reference defect
that warrants replacing ParseBench. Upstream reports machine-assisted annotation
followed by human verification. Our inspection is a separate, bounded review,
not independent verification of every annotation.

## Translate metric scores into acceptance decisions

The five ParseBench dimensions should remain visible when interpreting an overall
result. Their usefulness depends on the required output:

| Required behaviour | What the parsing evidence addresses | Additional acceptance question |
|---|---|---|
| Preserve text and reading order | Content and order rules | Are the particular omissions or misordered passages consequential to this workflow? |
| Preserve tables | Structure and header/value association | Must every required record be correct, or is partial recovery useful? |
| Recover chart information | Annotated label/value data points | Does the task need those facts, other chart facts, or an image asset? |
| Preserve meaningful formatting | Supported formatting distinctions | Which distinctions affect interpretation in this application? |
| Link output to its source | Region, class and content attribution | Does the delivered interface expose usable coordinates and page identity? |

These descriptions summarize the pinned evaluator contracts documented in the
[coverage assessment](parsebench-coverage.md#what-the-ground-truth-measures).
Chart fact recovery does not establish recreation of a figure's appearance or
understanding of every diagram. A parser can preserve useful table text while
failing a metric that requires table structure. That result needs interpretation
in terms of the delivered representation.

An average content-faithfulness score of 0.90 is not evidence that exactly 90% of
pages are wholly correct. A mean over rules or case scores is a different quantity
from the proportion of documents with no critical error. Likewise, a team that
does not extract charts should not automatically adopt an overall score's chart
weight. A team whose decisions depend on chart values cannot ignore that dimension
because text recovery looks good.

A relevant public subset can clarify these questions, but a subset score must
name its selection and denominator. The full published leaderboard remains a
different population. There is no defensible shortcut from "our subset scored
higher" to "our configuration beat the published system." A fixed 10% sample is
a resource choice, not a universal justification for sample size. Its usefulness
depends on the decision and the important conditions it includes. A small screen
with no observed critical errors does not establish a rare-error rate.

## A retained example: changing success changes the preferred pipeline

One controlled PDF-Bench experiment used generated invoices, source-qualified
references and a fixed downstream extractor. The references covered five required
fields and complete line records. A document passed only when its required fields
and records passed the declared task criteria. The documents came from six source
template/complexity cells; 100 filled documents were not 100 independent layouts.
Qualification included coding-agent visual review, not independent human
adjudication. The [reference checkpoint](invoice-reference-checkpoint.json)
records that scope.

The retained result illustrates why acceptance must be specified before reading
a leaderboard:

| Configured pipeline | Complete invoices | Matched / expected / predicted line records | Record F1 |
|---|---:|---:|---:|
| pypdf plus the fixed extractor | 84/100 | 668 / 696 / 698 | 0.958393 |
| pdfplumber plus the fixed extractor | 55/100 | 677 / 696 / 691 | 0.976208 |

These values are from the
[retained summary](invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c/summary.json),
whose input/output identity is bound by its
[completion manifest](invoice-comparison-evidence/run-9f0739f0bd464c6b9b3dbe1c86b6731c/completion.json).
Complete-document acceptance favoured the configured pypdf pipeline. Line-record
F1 favoured the configured pdfplumber pipeline. Neither is a current recommendation
for arbitrary supplier invoices or an isolated measurement of the parser alone.

Inspection of the failures explained part of the difference. Some representations
retained line-item values but merged party columns, preventing the extractor from
assigning the vendor. Other failures involved descriptions split across lines or
information outside the extractor's preferred table representation. The
[failure audit](invoice-failure-audit.json) reviewed all 61 failed task pairs using
retained outputs and prior source qualification. It attributes interacting causes;
its categories are not mutually exclusive.

The practical lesson is to inspect the parser output, the downstream prediction
and the reference separately. A low end-to-end result may expose a parser loss,
an extractor limitation or an interaction between them. A comparison of a
configured pipeline should name all those components. The invoice experiment is
useful evidence about evaluation design, not the principal reason for PDF-Bench
or a claim about real-vendor performance.

## References and selection can manufacture a winner

Reference truth must describe the rendition actually evaluated. HTML from a
filing, a later revision of a document, or a source template can contain information
that is absent or differently arranged in the PDF. A generated source makes facts
accessible, but it does not establish that the rendered page displays all of them.
Source-to-PDF agreement still needs qualification.

Our retained SEC configuration selected documents using one parser's similarity
threshold, and some annual-report PDFs could differ from their filing-HTML
references. Those observations limit what the retained comparison establishes.
They do not prove every old score is wrong. The
[historical registry](retained-evidence/bundle-a6fe94d9e8eb41b785e8f55786f02f4e/registry.json)
preserves these reference and selection uncertainties alongside the artifacts.

The invoice evidence provides a directly inspectable counterexample. On the full
fixed population, the line-record F1 ordering was 0.958393 versus 0.976208. Keeping
only the 84 invoices that the pypdf pipeline completed changes those scores to
1.000000 versus 0.995671. The ordering reverses. The
[selection-bias demonstration](invoice-selection-bias-demonstration.json) retains
the selected IDs and arithmetic. That deliberately biased subset is an illustration,
not a replacement result. It also cannot reconstruct the historical SEC
counterfactual, because the other parsers were not run on all excluded documents.

A new comparison should therefore select inputs independently of the evaluated
outputs, retain failures in their planned denominators, and compare alternatives
on the same bytes. A failed parser call, an empty answer, a timeout and a missing
evaluation result need distinct records. An evaluator exception makes the affected
evaluation incomplete; dropping the difficult document would change the population.

Ambiguous source facts require an explicit policy as well. Unknown, absent and
unreadable values need not mean the same thing. Repeated descriptions may represent
separate records, so collapsing them into a set can lose real items. Normalizing
dates, currency and whitespace should follow the task, while preserving distinctions
whose loss would change an operational decision. Evaluated outputs must not be
used to rewrite their own expected answers.

## The interface and execution path are part of the evidence

The evaluated system includes its adapter and output contract. In the frozen
PDFSmith snapshot we inspected, the benchmark adapter receives Markdown without
a coordinate sidecar. A workflow requiring source boxes cannot obtain them from
that interface alone, even if an underlying SDK can produce them. This is an
interface limitation established by
[adapter source](../../../pdf_bench/systems/pdfsmith_adapter.py), not a new
grounding score or a finding that the underlying SDK lacks localization.

The same care applies to operating measurements. Our benchmark starts a fresh
outer process for each document. Several PDFSmith backends then start another
interpreter internally. At the
[inspected PDFSmith revision](https://github.com/applied-artificial-intelligence/pdfsmith/tree/48de187103ffd5e0932ee3bb550affc58314a346/src/pdfsmith/backends),
Docling creates a new converter on each extraction. Marker recreates its models
and owned inference processes, explicitly selecting CPU execution and zero GPU
offload layers. Unstructured loads spaCy in each extraction. These source
properties explain why keeping only the outer benchmark worker alive would not
establish model reuse.

Disk-cached weights do not mean models remain initialized in memory. A timer
called "parse time" can still include loading performed inside the backend's parse
method. Cold-call latency, warm-call latency, batch throughput and an output-cache
hit are different operating measurements. A useful comparison declares which one
matches deployment, separates startup and steady-state work, and records device,
concurrency, thread limits and contention. We have not measured a warm speedup or
the fraction of time attributable to reloading in these retained runs.

Cleanup needs evidence too. Four Marker helper processes remained after the
earlier benchmark parents had stopped. The
[stop receipt](execution-stop-20261017.json) records their later termination.
In that execution, checking the parents alone was insufficient to establish
resource release. An interrupted benchmark must account for owned helper processes
as well as its top-level jobs.

No operating-speed winner follows from these observations. They identify work
that belongs before a performance comparison. Local inference also has hardware,
energy and operating costs even when there is no metered API bill; those costs
were not measured here. Evaluation expenditure should be recorded separately
from the expected serving cost of the chosen pipeline.

## What an internal evaluation needs to add

Additional evaluation starts with a sentence describing what current evidence
cannot decide. "We process PDFs" is too broad. "These accepted documents must
return every required record with its source evidence, within our operating
limits" identifies a testable contract. The remaining question is whether existing
public inputs, annotations and metrics already support that contract.

Sometimes the answer is an existing slice or a different aggregate over retained
case results. Sometimes the task belongs in a schema-guided extraction benchmark.
When the real uncertainty concerns the team's scan quality, required schema,
document packets or integration, additional internal examples may be warranted.
Those are candidate mismatches to verify, not blanket claims that public
benchmarks omit them.

The design should make several choices visible before new outputs exist:

- The eligible document population and the conditions that could change the
  decision, including important failure cases. Production weighting and deliberate
  stress coverage should be reported separately.
- The required delivered representation and reference facts, including how a
  reviewer resolves ambiguity without consulting evaluated answers.
- The acceptance criteria for critical fields, associations, complete records,
  surplus output, missing values and source evidence. Useful partial credit can
  coexist with a stricter document-acceptance rate.
- The frozen configurations, comparable input bytes, failure outcomes and operating
  limits. A provider, model, extractor or option change creates a different comparison.
- The decision the result could change and the evidence needed to stop. A small
  difference concentrated in uncertain references warrants investigation before
  adding more indiscriminate runs.

Paired comparisons on shared inputs make disagreements inspectable. Results by
meaningful document condition help distinguish broad behaviour from a few repeated
templates. Uncertainty should respect the available source identity: many rules
on the same page, or pages from one document, do not supply the same independent
evidence as unrelated documents. Where original-document lineage is unknown,
report that limit instead of implying precision from the rule count.

An integration check can remain necessary even when published quality evidence
is sufficient for the shortlist. It establishes that the chosen configuration
accepts the actual inputs and returns the required representation in its deployment.
That bounded acceptance work does not require recreating a public research
leaderboard.

## The useful contribution of PDF-Bench

PDF-Bench's current contribution is this explanation, the inspectable coverage
inventory and retained examples of how evaluation choices change conclusions.
The older academic, presentation, synthetic-deck and commercial pilots remain
available as directional, prototype or historical evidence. Their limitations
travel with the claims they can support. They do not become current rankings
because a newer guide cites them.

For a team choosing a parser, the useful outcome is a documented candidate choice,
the evidence supporting it, the uncertainty that could change it, and any additional
acceptance test justified by that uncertainty. A consulting engagement can deliver
that assessment and the required reference/acceptance design. It can also conclude
that existing public evidence is adequate and that no new benchmark is needed.

New PDF-Bench experiments should follow the same rule. Each needs an unanswered
decision, a specified comparison and an acceptable resource budget. The prepared
full and sampled parser plans are not results and do not create an obligation
to run them. Benchmark and GPU execution remains paused.
