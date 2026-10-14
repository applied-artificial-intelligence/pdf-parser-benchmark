# Spec: Reconstruct a reproducible, practical document-parser evaluation

Alignment brief: `start-here.txt` in this work unit, commissioned by Stefan on
October 14, 2026, with practical parser selection confirmed and internal-benchmark
design emphasized in this conversation. This specification describes the proposed end state. It does
not claim that the reconstruction, external specification review, or public
release has occurred. The commission authorizes this specification, plan, and
review packet without a second exhaustive alignment interview.

## Objective

An engineering team can use demonstrated benchmark-design decisions to build an
internal document-parser evaluation for its own use case, reproduce our declared
document-family/task comparison, and inspect the references, failures, operating
conditions and claim limits through a technical report and versioned evidence export.

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
   parsers. Every parser receives the same frozen PDFs and references. Selection
   and reference eligibility are established before parser execution. No document
   is removed because an evaluated parser performs poorly.
7. The invoice references identify invoice number, vendor, due date, totals and
   line-item records including their headers and values from retained DOCX source
   content, with metadata used as a cross-check rather than an unquestioned oracle.
   They are distinct from the existing PDF-extracted reference directory. Source,
   metadata and PDF disagreement is recorded and resolved before a strong claim.
   When a source must be rendered again, it creates a separately identified new
   rendition and run; it never silently replaces a retained PDF.
8. A reference qualification record covers all 100 sources and PDF renditions,
   including visibility, truncation, content alignment and pagination concerns.
   Qualification cannot use a compared parser's score as its inclusion rule.
   Rendered spot checks cover each region, source template and complexity present,
   and every detected disagreement. Any unresolved reference makes its task score
   unavailable and remains visible in the fixed-population coverage denominator.
   The milestone cannot claim a strong 100-document comparison while such gaps
   remain unresolved.
9. A fixed downstream extractor is declared, versioned and held constant across
   parsers. Its input is exclusively the actual parser output. Exact field and
   header/value associations, missing and extra records, and document task success
   are reported separately from text similarity. It cannot read reference values
   while extracting. Numeric/date normalization is specified and cannot equate
   different amounts, dates or headers. Unsupported table forms have explicit
    unavailable status when the reference contract itself cannot describe them,
    not manufactured scores. A parser that drops an eligible table has failed the
    recovery task; its capability cannot remove that task from the denominator.
10. The run contains at least 200 planned primary attempts, plus separately marked
    corrupt, empty-output and enforced-timeout controls. It records success with
    content, success with empty content, parser failure, timeout, and any attempt
    that could not start. Interrupted execution records incomplete work rather
    than reporting completion. Controls do not inflate the primary population.
11. Coverage and task success use the fixed reference-eligible population, retaining
    parser failures/timeouts/empty outputs as unsuccessful task outcomes. Every
    quality metric also reports its exact eligible and scored document IDs and
    numerator/denominator. A paired comparison uses identical IDs; any common
    successful subset is a secondary diagnostic with its selection disclosed.
    No aggregate ranks parsers on different scored subsets without that disclosure.
12. Parser/backend package versions, PDFsmith distribution and declared source
    versions, source revision/dirty-state information, implementation hashes,
    dependency snapshot, options, extractor, grader and normalizer identity are
    recorded. A disagreement in PDFsmith metadata is explained or explicitly
    unresolved with actual implementation identity preserved. This project does
    not change PDFsmith's API or release metadata on its owner's behalf.
13. New measurements distinguish fresh execution, cached replay and checkpoint
    reuse. Cache identity includes all output-affecting backend/options/source
    information, or the run explicitly bypasses both reads and writes. A changed
    option, backend identity, input or reference cannot silently reuse an unrelated
    checkpoint or output. Historical durations with unknown cache provenance are
    marked unsuitable for current latency comparisons.
14. Successful and failed call durations have declared boundaries; unavailable
    historical failure duration is null. Fresh timing includes declared cold/import
    effects. A single execution yields observations, not an advertised latency
    ranking. Any later latency comparison requires repeats, warmup policy, hardware
    and resource context, and correctly configured comparable work.
15. Invalid reference generation, JSON serialization, validation, or publication of
    a run bundle leaves prior valid artifacts byte-for-byte intact. A failed new
    operation retains useful diagnostics under an explicitly incomplete run and
    cannot register a partial bundle as complete. A deliberate I/O/serialization
    failure reproduces that contract through the actual producing pipeline.
16. Regression checks fail when the actual producing code emits each identified
    defect, then pass after repair. Checks cover selection, reference/output
    separation, cache/options identity, checkpoint compatibility, denominator
    accounting, empty outputs, timeout classification, output collisions and
    atomic export preservation. Existing CLI and readable historical result formats
    continue to work. Focused tests and lint run before checkpoint closure.
17. A second execution of the frozen run protocol produces the same input/reference
    hashes and deterministic task aggregates, or records a precise nondeterminism
    explanation. Offline regrading of retained parser outputs reproduces aggregates
    without parsing or paid calls. A relocation exercise checks that the replay does
    not depend on workstation-specific absolute paths or live PDFsmith checkout.
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

## In scope

- Benchmark-design lessons and a worked internal-evaluation protocol grounded in
  actual preserved and newly executed evidence, supporting practical parser
  selection and Applied AI's consulting work.
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
- External reviews are not yet returned. Stefan submits the packet; this owner
  retains/disposes reports and resolves correctness blockers. This blocks substantial
  reconstruction implementation, not the review deliverables.
- Reference qualification may find source/PDF disagreements. This owner resolves
  them by recorded source inspection and explicit new renditions, preserving the
  fixed population. An unresolved truth disagreement blocks strong affected
  scores, not preservation of the run's diagnostic evidence.
- Current OCR/model availability, ParseBench dependency compatibility and licenses
  require bounded checks in follow-on work. No downloads or paid runs are assumed.
- Cloud/frontier comparison is deferred. Stefan must approve the exact inputs,
  provider/model/configuration and spend ceiling before those calls.

## Next actions

Stefan submits the completed review packet to GPT and Claude and returns both
reports before affected reconstruction implementation begins.
