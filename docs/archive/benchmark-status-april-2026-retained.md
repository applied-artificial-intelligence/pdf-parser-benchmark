# PDF-Bench Status Report: Practical Benchmark Framing

*April 2026*

---

## Current Position

PDF-Bench should be presented as a practical parser-evaluation project, not as a single universal leaderboard. The point of the benchmark is to show why PDF parser comparison is difficult and how to make useful decisions anyway.

The repo contains a broad history of corpus building, parser runs, commercial/frontier experiments, synthetic document generation, SEC filing work, presentation/deck attempts, and academic-paper ground-truth work. These should not be flattened into either "all publishable" or "all unusable." The useful structure is evidence tiers.

Current inventory snapshot:

- 12 corpora total; 11 classified as valid internal.
- 85 benchmark configs; 42 classified as valid internal.
- 99 result artifacts; 16 classified as valid internal, 8 draft, 75 archive-only.

---

## Evidence Tiers

### Tier 1: Stronger Comparison Tracks

These are the cleanest current comparison tracks and can support direct tables in the briefing.

| Track | Result file | Docs | Parsers | Use |
| --- | --- | ---: | ---: | --- |
| SEC filings subset | `results/sec_filings_47docs.json` | 47 | 12 | Real business-report baseline; born-digital text/order comparison. |
| Controlled invoices | `results/invoices_100docs_fresh.json` | 100 | 6 | Source-first structured business sanity track. |

### Tier 2: Directional And Diagnostic Tracks

These tracks remain useful and should be discussed, but not treated as the same evidentiary class as Tier 1.

| Track | Result file | Docs | Parsers | Use |
| --- | --- | ---: | ---: | --- |
| SEC full-corpus screen | `results/sec_filings_screen_all.json` | 320 | 1 | Coverage and GT screening, not parser ranking. |
| Legacy presentations | `results/presentations_30docs.json` | 30 | 12 | Slide/deck stress signals; ground truth and source quality uneven. |
| Investor deck prototype | `results/business_synthetic_investor_decks_subset_refresh.json` | 10 | 4 | Source-first deck generation prototype. |
| arXiv technical papers | `results/arxiv_10docs_fresh.json` | 10 | 16 | Technical parser stress track with LaTeX-derived GT. |
| Frontier/commercial pilots | `results/frontier_unified_30docs.json`, `results/frontier_premium_300p.json` | 28-30 | 3-4 | Cost/quality hypotheses; prompt/config audit required before headline claims. |

### Tier 3: Historical Runs

These artifacts should remain part of the project history and can explain what we learned, but they should not drive headline claims without rerun/repair.

| Artifact | Status | Why it matters |
| --- | --- | --- |
| `results/full_corpus_353docs.json` | Draft | Broad early comparison; failed tasks and mixed assumptions. |
| `results/comprehensive_278docs_all_parsers.json` | Draft | Useful history; confusing scope/name mismatch and failed tasks. |
| `results/hr_34docs.json` | Draft | Prior HR/resume evidence; failed tasks. |
| `results/invoices_100docs.json` | Draft | Superseded by cleaner invoice fresh run. |
| `results/sec_filings_30docs_oss_remaining.json` | Draft | Superseded by 47-doc SEC comparison. |

---

## Practical Public Framing

The briefing should not say "we have the final universal PDF parser leaderboard." It should say:

- PDF parser benchmarking is hard because ground truth is rare, document types fail differently, parser outputs vary, metrics disagree, and paid parser configuration matters.
- We built PDF Bench and PDF Smith to make this mess operationally manageable.
- Some tracks support direct comparison now; other tracks are directional, prototype, or historical.
- The useful output is a parser-selection workflow: match corpus, ground truth, parser family, metrics, cost, and downstream task.
- SEC filings show that many open-source parsers can be viable on born-digital business reports.
- Controlled invoices show that structured business documents can produce much wider parser differences.
- Presentations/decks are a high-value gap, not something to pretend away.
- arXiv remains a technical stress track, useful but separate from business marketing.
- Commercial/frontier models should be benchmarked through small inspected runs before scaling spend.

---

## Current Content Source

The content-marketing source has been restored to this broader practical framing:

- `../content-marketing/content/briefings/pdf-parsing/draft.md`
- `../content-marketing/content/website-staging/insights/pdf-parsing/index.md`
- `../website/content/export/insights/pdf-parsing-benchmark.md`

---

## Reproducible Commands

Generate the current result slate:

```bash
uv run python scripts/build_internal_benchmark_story.py
```

Generate the current inventory snapshot:

```bash
uv run python -m pdf_bench.main inventory --repo-root . --output data_exports/inventory_latest.json
```

Run targeted checks:

```bash
uv run ruff check scripts/build_internal_benchmark_story.py
uv run pytest tests/test_inventory.py tests/test_business_suite.py
```
