# Spec: Reconstruct a reproducible, practical document-parser evaluation

Alignment brief: `start-here.txt` in this work unit, commissioned by Stefan on
October 14, 2026, with practical parser selection confirmed and internal-benchmark
design emphasized in this conversation. Revision 3 incorporates Stefan's October 15 confirmation: assess whether public
benchmark documents and tasks fit meaningful business workloads, reuse matching
subsets where they do, and build internal evaluation only where needed. It adds
an executable ParseBench comparison. Revision 2 incorporated the returned
`fable-01.md` and `gpt-01.md` reviews, with specific dispositions recorded in
`review-dispositions.txt`. Both recommend bounded revision. This specification
does not claim that reconstruction or public release has occurred. The original
review packet remains unchanged; Git preserves its specification and plan.

## Objective

An engineering team can judge whether ParseBench covers its document distribution
and downstream task, select a relevant public subset when suitable, and establish
what internal evaluation is necessary when it is not. Reproducible comparisons and
retained project experience demonstrate the decision, supported by inspectable
references, failures, operating conditions and a versioned technical evidence export.

## Terms

Context: pdf-bench, document-parser-evaluation

| Term | Readings | Status | Basis |
|---|---|---|---|
| Reconstruction | A new report over old numbers; or repaired producing code and new reproducible evidence | resolved-by-author | The commission requires working code, a consequential comparison, and preserved historical evidence. |
| Shared inputs | Same document names; or identical input bytes for every compared parser | resolved-by-author | The commission requires a comparison on shared inputs. Document identity includes input hashes and rendition, not filenames alone. |
| Independent reference | Another parser's output; or source/annotation truth established before evaluated outputs | resolved-by-author | The commission requires independently specified truth and resolution of reconstructed invoice references. Evaluated output cannot define or repair its own reference. |
| Evidence tier | A permanent quality label for a corpus; or the claims a particular run can support | resolved-by-author | Preserve strong, directional, prototype, historical, and rerun-candidate evidence as the commission requests. Tier depends on run and claim. |
| Attempt and denominator | Successful rows only; or every planned input/parser pair with an explicit outcome | resolved-by-author | The commission requires failed, empty and timed-out attempts and metric denominators. Missing historical rows remain unknown, not assumed failures or successes. |
| Version | Wrapper version alone; or backend package, implementation, configuration and provider identity | resolved-by-author | The commission requires backend versions, cache behavior, and reconciliation of PDFsmith distribution/source disagreement. Unknown historical values remain unknown. |
| Fresh timing | Duration of any adapter call; or uncached parsing with the measured boundary declared | resolved-by-author | The commission requires cached latency to be resolved. Cache replay and failed-call default zero are not fresh parser latency. |
| Completion | A passing suite or smoke fixture; or reviewed reconstruction with executed comparison and inspectable export | resolved-by-author | The commission explicitly excludes closure on the earlier smoke experiment alone. |

## Why

The withdrawn benchmark has useful retained work, but its current descriptions
can imply reference independence and comparable performance that the producing
artifacts do not establish. Engineers need useful bounded conclusions, with the
conditions that change parser selection visible beside each result.

ParseBench changes the justification for this work. Its enterprise corpus and
semantic metrics already address much of the earlier motivation. PDF-Bench must
acknowledge that work and demonstrate an additional practical use rather than
claim novelty for enterprise documents or semantic correctness. Stefan confirmed
practical parser selection as the focus and emphasized teaching teams how to build
their own benchmarks. The report must explain decisions about corpus fit, reference
truth, task/grader design, failure accounting and interpretation through worked
examples, including mistakes from the retained work. A broad public benchmark does
not establish performance on a team's distribution or downstream task merely by
containing many pages. The material supports Applied AI's document-evaluation
consulting capability through demonstrated methods and evidence. It does not assert
that ParseBench lacks reproducibility or operational features.

## Acceptance criteria

1. Two self-contained external reviews, one from a strong GPT model and one from
   Claude, assess this specification and plan. Actual returned reports are retained
   with hashes and dispositions. Correctness blockers are resolved before the
   affected implementation starts. Optional extensions do not reset planning.
2. One authoritative run registry accounts for every result artifact discovered
   under the retained results inventory and the reviewed local evaluation. Each
   artifact is classified as a run, checkpoint, derived/merged export, diagnostic,
   or unrecognized artifact; none silently disappears. The registry generates the
   appendix and evidence export rather than competing with a second hand-maintained
   list. Provenance coverage is a count with an explicit denominator.
3. Each registered run links available config, document IDs and renditions, input
   and reference hashes, reference method, generating code, raw outputs, backend
   identity, cache policy, run date and metric definitions. Missing historical
   information has a named unknown and affected claims. Today's config or files
   are never asserted to be the bytes used historically without evidence.
4. SEC, controlled invoices, presentations, synthetic decks, arXiv, commercial and
   frontier pilots, and other retained families remain separately addressable.
   Existing results are not rewritten. Current report labels are reconciled with
   producing evidence, preserving useful diagnostic claims when stronger claims
   cannot be supported.
5. The SEC subset's pypdfium2-dependent selection and possible PDF/HTML content
   mismatch are disclosed and tested where evidence permits. That subset is not
   represented as a parser-independent sample or an exact visual reference.
6. The first consequential run uses all 100 retained invoice source documents as
   its fixed population, with pypdf and pdfplumber as the required local baseline
   parsers. Parsers receive the same frozen PDFs; only the grader receives
   qualified references. The illustrative decision is selecting a configured
   local pipeline for controlled born-digital invoice-to-record extraction. Selection
   and reference eligibility are established before parser execution. No document
   is removed because an evaluated parser performs poorly.
7. The invoice references identify invoice number, vendor, due date, displayed
   grand total and currency marker, and line-item records including their displayed
   headers and values from retained DOCX source
   content, with metadata used as a cross-check rather than an unquestioned oracle.
   They are distinct from the existing PDF-extracted reference directory. Source,
   metadata and PDF disagreement is recorded and resolved before a strong claim.
   When a source must be rendered again, it creates a separately identified new
   rendition and run; it never silently replaces a retained PDF.
8. A reference qualification record covers every source/PDF/reference combination
   and binds its decision to their hashes and the qualification-protocol hash.
   Changing any member invalidates the decision. PyMuPDF is an unscored mechanical
   text-presence instrument; it cannot establish associations or visible layout.
   Review all 182 retained rendered pages for clipping, overflow, continuation,
   and task-relevant field/record associations. Close-read mechanical misses and
   every observed template/complexity combination. Record exact pages and verdicts.
   Producer strings and timestamps are provenance clues, not proof of source/PDF
   identity. Truth means the facts visibly displayed, even if their arithmetic is
   wrong. Qualification cannot use either compared parser's score or silently
   correct document arithmetic. Any unresolved truth remains unavailable and
   visible in reference coverage against all 100 documents; it blocks a strong
   affected comparison. Rerendered documents have explicit new rendition identity.
9. A frozen invoice-specific contract precedes scored execution. Required fields
   are invoice number, vendor identity, due date, displayed grand total and printed
   currency marker. Records preserve description, quantity, displayed unit,
   displayed unit price and line total where those columns actually exist.
   Economy invoices have no separate unit-price column; embedded price/unit text
   stays in their description, and no price is imputed from arithmetic.
   Header aliases are Description->description, Quantity/Qty->quantity,
   Unit->unit, Unit Price/Rate->unit_price, and Amount->line_total. Missing-column
   applicability is fixed from source schemas
   before outputs, not chosen to improve grades. Match complete normalized records
   as a multiset, preserving duplicate multiplicity and missing/extra counts.
   No fuzzy assignment repairs wrong associations. Use Decimal strings, preserving
   signs, currency markers and unit meaning; never score source metadata floats as
   exact truth. Keep original surfaces beside canonical values. Numeric dates use
   the documented synthetic source MM/DD/YYYY convention; unsupported/ambiguous
   representations return ambiguity instead of consulting reference metadata.
   Extraction takes only parser output and the fixed public schema, without
   document-ID lookup, source/metadata/reference access or answer constants.
   Persist prediction bytes before grading. An isolated subprocess test removes
   all answer-bearing files and proves predictions depend on parser output rather
   than gold labels, values or record counts. Development fixtures are the smoke
   variants and at most ten declared retained IDs chosen by source structure;
   freeze the extractor before scoring. Later changes require a new protocol and
   comparable regrading. A parser-independent faithful-input control measures
   extraction on supported representations, not a universal extractor ceiling.
   Inspect parser disagreements and a stratified sample of shared failures, with
   at least 40 reviewed failures if more than 40 exist. Classify reference gaps,
   lost/misassociated parser content, unsupported extractor representations and
   evaluation defects, permitting mixed/unknown causes. A parser dropping an
   eligible record scores unsuccessful recovery, not reference unavailability.
10. Before execution or capability filtering, atomically write and hash exactly
    200 unique planned primary input/pipeline pairs plus separately marked corrupt,
    empty-output and enforced-timeout controls. Retries have separate attempt IDs
    and cannot satisfy the primary count. Record parse, prediction and grading
    outcomes separately. Parse outcomes distinguish success_content, success_empty,
    parser_failure, enforced_timeout, incompatible, initialization_failure and
    not_started; whitespace-only output is empty. Timeout comes from its enforcing
    mechanism and typed exception, never an error-message substring. A metric or
    grader exception is an evaluation failure, not a parser failure or reference
    gap. Reject unknown required metrics before any attempt. Planned pairs absent
    from the terminal journal remain incomplete. Old empty status stays unknown
    when raw output bytes are absent. Stop timed-out work before finalizing output.
11. Primary document task success is correct required fields and all records
    divided by the frozen reference-eligible document count, including parser
    failures/timeouts/empty outputs as zero task outcomes. Field micro-accuracy
    divides correct eligible fields by all eligible expected fields; record recall
    and precision report matched/expected and matched/predicted multiplicities;
    record F1 is twice the matched count divided by expected plus predicted counts,
    with unavailable zero-denominator precision explicit. Document-macro scores
    and record micro-scores are named separately. Required evaluation failures
    invalidate an affected aggregate rather than dropping difficult documents.
    Every
    quality metric also reports its exact eligible and scored document IDs and
    numerator/denominator. A paired comparison uses identical IDs; any common
    successful subset is a secondary diagnostic with its selection disclosed.
    Unequal-subset means remain inspectable diagnostics, never the primary ranking.
    An asymmetric failure/timeout on an eligible document and an all-failed parser
    must leave the primary population and denominators unchanged.
12. Parser/backend package versions, PDFsmith distribution and declared source
    versions, source revision/dirty-state information, implementation hashes,
    dependency snapshot, options, extractor, grader and normalizer identity are
    recorded. A disagreement in PDFsmith metadata is explained or explicitly
    unresolved with actual implementation identity preserved. This project does
    not change PDFsmith's API or release metadata on its owner's behalf.
13. New measurements distinguish fresh execution, cached replay and checkpoint
    reuse. The scored run uses the actual PdfsmithAdapter with cache mode bypass,
    proving both reads and writes are disabled. Normal reuse includes actual backend
    package/source/dependency identity and canonical output-affecting options or is
    disabled until safe. Do not invent options for no-argument local constructors.
    Parsed-output identity is input/parser identity; prediction identity adds the
    extractor/schema; grade identity adds qualified truth and grader/normalizer.
    Corrected references allow explicit regrading, not reuse of old grades. A changed
    option, backend identity, input or reference cannot silently reuse an unrelated
    checkpoint or output. Historical durations with unknown cache provenance are
    marked unsuitable for current latency comparisons.
    Any reusable checkpoint validates full protocol/population identity, membership
    and unique pairs before importing rows/counters; old formats remain readable,
    but incomplete identity prevents verified resumption. Attempt output namespaces
    include run, input and pipeline identity, and retain the exact returned bytes
    that were graded rather than a guessed path or mutable cache link.
14. Successful and failed started-call durations use a monotonic clock with declared
    boundaries and error-path accounting; unavailable
    historical failure duration is null. Fresh timing includes declared cold/import
    effects. A single execution yields observations, not an advertised latency
    ranking. Any later latency comparison requires repeats, warmup policy, hardware
    and resource context, and correctly configured comparable work.
15. Invalid reference generation, JSON serialization, validation, or publication of
    a run bundle leaves prior valid artifacts byte-for-byte intact. A failed new
    operation retains useful diagnostics under an explicitly incomplete run and
    cannot register a partial bundle as complete. A deliberate I/O/serialization
    failure reproduces that contract through the actual producing pipeline.
    Write only into a new run-owned incomplete directory; validate artifact hashes,
    outcome consistency and exact pair membership; write the completion manifest
    last, then finalize the directory and atomically replace the registry pointer.
    Readers verify manifest hashes and required outputs, not only a status flag.
    A fully accounted parser failure is compatible with completion; a missing
    required output from a successful attempt is not. Preserve valid registry
    bytes on errors and interruption. Power-loss durability is not claimed.
16. Regression checks fail when the actual producing code emits each identified
    defect, then pass after repair. Checks cover selection, reference/output
    separation, cache/options identity, checkpoint compatibility, denominator
    accounting, empty outputs, timeout classification, output collisions and
    atomic export preservation. Existing CLI and readable historical result formats
    continue to work. Focused tests and lint run before checkpoint closure.
17. A second execution of the frozen run protocol produces the same input/reference
    hashes, per-document normalized predictions/outcomes and task aggregates, or
    records a precise nondeterminism explanation. Duration equality is not required.
    Offline regrading runs with parser imports, original checkout/reference paths,
    network and ambient caches unavailable, using only the retained output/prediction,
    truth and frozen grading dependencies. Fresh relocated execution separately uses
    retrievable immutable parser source/package artifacts and declared dependencies;
    source hashes alone are not a dependency package. Bundle-relative paths and
    best-effort Git metadata preserve replay outside a checkout. A different
    implementation is reported as a mismatch, not identical reproduction.
18. The generated report/export lets a visitor find a document-family/task result,
    inspect failures and example outputs, identify why an alternative parser changes
    the outcome, and reproduce or regrade it. Each numerical statement resolves to
    run ID, immutable artifact/hash and JSON pointer, metric and denominator,
    evidence tier, and supported/unsupported interpretation. The report identifies
    how extractor behavior affects the comparison rather than attributing every
    failure to the parser.
19. OCR/scans, complex tables/charts, decks and academic papers have bounded follow-on
    protocols with input selection, reference needs, task, parser eligibility,
    acceptance and spending gate. They are not implied coverage of the first run.
    ParseBench reuse is assessed against pinned code/data, license and interface
    requirements; neither its aggregate scores nor this project's historical scores
    are presented as results measured in this reconstruction.
20. The report contains a worked internal-benchmark design example: a declared
    use case and document distribution; why the inputs fit or fail to fit it;
    alternatives for establishing references; a task and fixed extractor/grader;
    concrete examples of how selection, reference noise and missing failures change
    conclusions; and instructions for applying the protocol to a team's permitted
    documents. These instructions reuse the existing benchmark surface and avoid
    creating a speculative general-purpose framework. The report distinguishes
    demonstrated decisions, historical lessons and untested recommendations.
21. The editorial handoff identifies the relationship to the retained article
    `what-llm-and-agent-benchmarks-measure`: public benchmark scores are conditional
    on data, configuration and scoring, and internal evaluation requires an explicit
    use-case contract. It supplies usable findings/examples rather than rewriting
    that manuscript or promising a website change. Consulting relevance follows
    from the demonstrated evaluation work; no causal business-impact claim is made.

22. The first milestone includes a reproducible comparison on a frozen ParseBench
    subset chosen after the coverage assessment, initially targeting 30 content-
    faithfulness cases and 20 table cases. Freeze exact case IDs,
    document/page counts, source strata and hashes fixed before parser execution.
    Selection uses source/reference attributes, never candidate-parser performance.
    Suitable local parsers run on identical bytes; upstream deterministic evaluators
    and declared normalization score the outputs rather than a reimplementation
    labelled as ParseBench. Pin code, data, annotation and evaluator versions and
    report any adaptation. Retain failures, missing/unsupported outputs and exact
    metric denominators. The scored dimensions remain separate; this subset is
    not a reproduction of the full five-dimension leaderboard. No paid parser or
    judge/normalization call is authorized. Verify dataset access/source rights and
    dependency compatibility before execution; a failed integration is reported
    precisely rather than silently substituting a different metric.
23. The report compares decisions informed by the ParseBench subset with the
    custom invoice task, explaining which capabilities and error types transfer,
    which references/metrics can be reused, and which use-case-specific data and
    acceptance rules remain necessary. Explain material agreement, disagreement
    or inability to compare; a ranking reversal is not required. Assess the related
    ExtractBench schema/value/record contract as prior art. The contribution is the
    worked decision about whether a public benchmark represents the use case,
    whether a matching subset suffices, or whether additional internal evaluation
    is needed. A custom benchmark is not presumed necessary.

24. Before selecting the ParseBench run subset, assess the pinned full annotation
    inventory and inspect source documents across its declared domains, document
    families and capability dimensions. Map meaningful business workloads to
    document properties and downstream tasks, with counts and traceable examples.
    Distinguish present, partially represented, not observed and unknown coverage;
    document-type names alone do not prove task coverage. Any proposed gap must
    concern a consequential workload and survive inspection of relevant examples
    and upstream evaluation rules. Do not manufacture marginal omissions to justify
    this project. Recommend using ParseBench directly or a matching subset when
    it fits. Additional internal data/tasks require a stated mismatch. No percentage
    of all business use cases is asserted without a defined representative workload
    population and weights. Record source and annotation rights separately from
    code licensing. Assessment uncertainty stays visible and can motivate targeted
    inspection rather than a claim of absence.

## In scope

- Benchmark-design lessons and a worked internal-evaluation protocol grounded in
  actual preserved and newly executed evidence, supporting practical parser
  selection and Applied AI's consulting work.
- An executable, pinned ParseBench content/table reference comparison within the
  first milestone, using upstream evaluators and shared local-parser inputs.
- Existing-code reconciliation, registry/appendix generation and reproducible
  evidence tooling, with preserving error behavior and actual-pipeline regressions.
- A consequential local structured-document comparison and project-local technical
  report suitable for later editorial and website integration.
- ParseBench-informed scope and reuse assessment, with a dated primary-source
  account separating its launch paper from current software/data.
- Bounded follow-on research protocols; progress, review dispositions and handoff.

## Out of scope

- A universal leaderboard, a claim to outperform ParseBench, or contemporary
  cloud/frontier results inferred from old runs.
- Paid calls, including judge/normalization calls or free-credit APIs without
  explicit provider/run and Stefan-approved spending authority.
- Source public-main merge/release, article publication, scheduling, production
  deployment, website CMS changes, or rewriting retained editorial manuscripts.
- New agents or chats, production/confidential documents, or changes to PDFsmith's
  separate API/packaging ownership.
- A new UI, generalized workflow framework, exhaustive new corpus collection or
  all-family rerun in the first engineering milestone.

## Constraints

- Work in this existing checkout and work unit. Preserve inherited staged/dirty
  work; do not reset, stash, replay a review-branch patch blindly, or switch another
  worker's checkout. Own changes must be reviewable apart from inherited changes.
- Local, unpaid execution first. Use uv, existing parser abstractions and atomic
  persistence. Extend inventory and story exports instead of maintaining a parallel
  benchmark database or new parser framework.
- Keep progress compact in `progress.txt`; version owned checkpoints according to
  verified repository visibility. This repository is PUBLIC as checked on October
  14, 2026. Public-main merge remains unapproved. No secrets or confidential
  evidence enter a review packet or public branch.
- Specifications and plans can be revised after review; raw retained evidence and
  original experimental checkpoints cannot be overwritten by those revisions.
- No minimum performance score is needed for a valid comparison. A tied or poor
  result is acceptable if the protocol and export meet the contract.

## Environment / prior art

- `PROJECT_ORIENTATION.md` and `.workspace/reference/pdfbench_benchmark_story_brief.md`
  establish the practical mission and preservation requirements.
- `.workspace/issues/2026-10-09-document-ai-public-reconstruction.md` specifies
  claim provenance, reproducibility and editorial boundaries.
- `pdf_bench/inventory.py` already inventories corpora/configs/results and flags
  missing configs/versions and inconsistent counts. `inventory_overrides.yaml`
  contains current classifications to reconcile, not trust blindly.
- `scripts/build_internal_benchmark_story.py` already generates the story JSON and
  appendix. Its hard-coded SLATE and means over each parser's available numeric
  rows need reconciliation with claims, common inputs and metric coverage.
- `pdf_bench/runner.py`, `loader.py`, `systems/pdfsmith_adapter.py` and
  `utils/caching.py` provide execution, aliasing, checkpoints and cached parsing.
  `persistence.py` contains the already reviewed atomic writer.
- `builders/generate_invoice_corpus.py`, `builders/invoice/`, and the retained
  `corpus/business/invoices/{docx,pdfs,metadata,ground_truth,ground_truth_backup}`
  provide 100 source documents and competing reference artifacts. LibreOffice is
  available, but source/PDF/reference alignment still requires qualification.
- Starting independently reviewed revision is
  `d9305d6100e5288fa2fc255e088bfd8e22664b98` on
  `codex/source-first-pdf-evaluation-2026-10-13`. Its changes are mirrored in this
  dirty checkout; checked-out base is `bf8285b4cf4e69295eda2391665d54d9077d4d0a`.
- The earlier run is `.workspace/work/2026-10-13-local-parser-evaluation/run-03/`.
  Its comparison SHA-256 is
  `1b7ca15e231de50ea303e34e9b9ef20c759ad09533687605ad2f3c8129f7f242`.
  The coordinator reports 48 focused passing tests for that bounded checkpoint;
  that is prior evidence, not a fresh run or review of this reconstruction plan.
- External prior art: [ParseBench launch](https://www.llamaindex.ai/blog/parsebench),
  [paper v3](https://arxiv.org/html/2604.08538v3),
  [code snapshot](https://github.com/run-llama/ParseBench/tree/d423e529ae329317bcd33c650b367acfb60e6620),
  [dataset snapshot](https://huggingface.co/datasets/llamaindex/ParseBench/tree/2805a1d940f95a203e0ae4b88be9934f7765b3fc).
- Related retained editorial work is
  `/home/stefan/applied-ai/content-marketing/topics/evaluation-and-verification/publications/what-llm-and-agent-benchmarks-measure/{brief.md,draft.md}`.
  Website integration is owned through the existing specification at
  `/home/stefan/applied-ai/website/.workspace/work/2026-10-13-project-restoration/spec.md`.

## Existing surface (must not break)

- Original corpora, source/reference versions, raw results, parser outputs and
  historical run chronology remain available with their existing bytes.
- Existing BenchmarkRunner, CLI config/aliases, inventory and result loading
  remain usable. New fields distinguish unknown old values from measured new ones.
- The atomic persistence repair and reviewed local experiment remain preserved.
- Editorial artifacts under content-marketing and website production remain owned
  by their existing conversations. This owner supplies exact exports and limits.
- No unrelated inherited change is included in an owned checkpoint by accident.

## Open questions

- Positioning is resolved by Stefan's October 14 replies: practical parser selection
  and instruction in building use-case-specific internal benchmarks. External
  reviewers may challenge whether the proposed demonstration serves that goal;
  full ParseBench replication is not the default reconstruction scope.
- Returned reviews are retained with hashes and dispositions. Registry work and
  non-scored execution repairs can proceed. Strong scored-run claims remain gated
  on the frozen task protocol, complete rendition qualification, extraction isolation,
  eligible-failure regressions, and completed bundle/attempt validation.
- Reference qualification may find source/PDF disagreements. This owner resolves
  them by recorded source inspection and explicit new renditions, preserving the
  fixed population. An unresolved truth disagreement blocks strong affected
  scores, not preservation of the run's diagnostic evidence.
- ParseBench subset access/source rights and dependency compatibility require
  bounded checks before the first reference comparison. Broader OCR/model and
  other-dimension coverage remain follow-on work. No paid runs are assumed.
- Cloud/frontier comparison is deferred. Stefan must approve the exact inputs,
  provider/model/configuration and spend ceiling before those calls.

## Next actions

No new user decision is required. Paid comparisons and public release remain deferred.
