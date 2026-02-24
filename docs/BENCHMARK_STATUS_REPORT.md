# PDF-Bench Status Report: Ground Truth Migration & Next Steps

*February 2026*

---

## 1. What We Have Done

### Original Approach (Pre-Migration)

We built a benchmarking suite evaluating **26 parsers** across **816 documents** in 6 corpora (synthetic, CUAD contracts, invoices, legal templates, HR documents, OmniDocBench, arXiv papers). The suite uses 6 metrics (edit similarity, ChrF++, CER, tree similarity, element F1, TEDS) and has accumulated **7,500+ individual evaluations** across 39 result files.

For arXiv papers, we used **ar5iv HTML** (rendered LaTeX) converted to Markdown as ground truth. This introduced significant artifacts: CSS class annotations (`.ltx_creator`, `.ltx_tag`), verbose internal anchor links, and structural noise that inflated ground truth files by 60-80% and uniformly suppressed all parser scores.

### Current Approach (Pandoc LaTeX Ground Truth)

We replaced ar5iv with a **LaTeX-to-Pandoc pipeline** for 4 of 5 arXiv papers:

1. Download LaTeX source from arXiv
2. Flatten multi-file projects with `latexpand`
3. Extract `\begin{document}...\end{document}` body (bypasses preamble macro loops)
4. Convert with `pandoc -f latex -t markdown`

**Results**: Ground truth files shrank 62-82% and scores roughly doubled on affected papers. For paper 2302.14852, edit similarity jumped from 0.21 to 0.46 (pypdfium2), confirming ar5iv artifacts were the dominant noise source.

### Current Academic Benchmark (5 Papers, 4 Parsers)

We ran 4 parsers (pypdfium2, pymupdf, marker, docling) on 5 arXiv papers with Pandoc ground truth. All 20/20 tasks succeeded after fixing:

- **Marker multiprocessing bug**: `parallel_workers` must be `1` (top-level YAML, not nested) to avoid daemon-subprocess conflicts
- **Stale ground truth**: One paper still had ar5iv content at the Pattern 1 path

| Parser | Edit Sim | ChrF++ | LaTeX F1 | Element F1 | Speed |
|--------|----------|--------|----------|------------|-------|
| **marker** | **0.426** | **66.5** | **0.167** | **0.509** | 298s avg |
| docling | 0.387 | 61.3 | 0.006 | 0.477 | 46s avg* |
| pypdfium2 | 0.398 | 61.0 | 0.006 | 0.447 | <1s |
| pymupdf | 0.395 | 60.9 | 0.006 | 0.377 | <1s |

*Docling times from previous uncached run; current run used cache.

**Key finding**: Marker is the only parser that meaningfully recovers LaTeX formulas (LaTeX F1: 0.167 vs ~0.006 for others).

---

## 2. What We Found

### Pandoc Ground Truth Is a Clear Win

| Metric | ar5iv Ground Truth | Pandoc Ground Truth | Improvement |
|--------|-------------------|---------------------|-------------|
| Edit Similarity (avg) | 0.21 | 0.46 | +119% |
| ChrF++ (avg) | 22.1 | 42.0 | +90% |
| Signal quality | Low (artifacts dominate) | High (clean Markdown) | Qualitative |

The improvement is consistent across all parsers, confirming ar5iv artifacts were suppressing scores equally rather than revealing parser differences.

### Marker Stands Out on Academic Papers

Marker's deep learning pipeline (layout detection, OCR, text recognition, table recognition) gives it a meaningful edge on academic papers with complex layouts, equations, and tables. It's the only parser to achieve non-trivial LaTeX F1 scores and leads on Element F1 (0.509).

The trade-off is speed: 178-705 seconds per paper vs. sub-second for text-extraction parsers. This is inherent to running 5 neural network models per document on GPU.

### One Paper Resists Automated Conversion

Paper 2303.18223 (LLM Survey, 144 pages, 785KB LaTeX) uses non-standard macros (`\ignore{}`, `\paratitle{}`, `\ifCLASSOPTION`), bare brace groups for paragraph scoping, and deeply nested custom environments. Multiple automated fix attempts failed. This paper still uses ar5iv ground truth.

---

## 3. What's Missing and Why It Matters

### Gap 1: The current report shows only 4 of 26 available parsers

**Why**: The `academic_5docs.yaml` config was written to test only 4 parsers (pypdfium2, pymupdf, marker, docling). This was a focused re-validation after the ground truth migration, not a full benchmark.

**Previous coverage**: We have historical results with up to 16 parsers on arXiv papers (`arxiv_10docs_fresh.json`) and 13 parsers on CUAD contracts. The full corpus benchmark (`full_corpus_353docs.json`) tested 10 open-source parsers. Commercial APIs and frontier LLMs were tested in separate runs.

**What's needed to restore full parser coverage**:

| Parser Category | Count | Requirements | Est. Cost (5 papers) |
|-----------------|-------|-------------|---------------------|
| Open-source text extraction | 9 | Already installed | $0 |
| Open-source ML (marker, docling) | 2 | GPU, `parallel_workers: 1` | $0 |
| Native (tika, marker_ollama) | 2 | Java, Ollama | $0 |
| Commercial OCR APIs | 4 | API keys, billing | ~$0.04 (26 pages) |
| Frontier LLMs | 8 | API keys | ~$1.30 (26 pages) |

**Recommendation**: Re-run with all 25 working parsers. Total cost for 5 papers (~450 pages): under $2 for commercial APIs + LLMs. The blocking issue is only configuration (adding parsers to the YAML list and ensuring `parallel_workers: 1` for marker compatibility).

### Gap 2: Dataset is heavily weighted toward academic papers

The Pandoc ground truth pipeline only works for LaTeX-sourced documents. Our corpus diversity breaks down as:

| Domain | Documents | Ground Truth Method | Ground Truth Quality |
|--------|-----------|-------------------|---------------------|
| arXiv academic | 5 (Pandoc) + ~460 (ar5iv) | Pandoc from LaTeX / ar5iv HTML | High (Pandoc) / Low (ar5iv) |
| CUAD contracts | 75 | PDF text layer extraction | Medium (no structure) |
| Invoices | 100 | Generated from DOCX templates | High (known source) |
| Legal templates | 108 | Generated from DOCX templates | High (known source) |
| HR documents | 34 | Generated from DOCX templates | High (known source) |
| OmniDocBench | 252 | Text extraction from images | Low (OCR baseline) |
| Synthetic | 31 | Generated from DOCX templates | High (known source) |

**The problem**: Business documents (invoices, legal, HR) have high-quality ground truth but were generated from Word templates. They test DOCX-to-PDF-to-Markdown fidelity, not real-world PDF parsing challenges (scanned docs, mixed layouts, embedded tables, multi-column). Academic papers test real-world complexity but only cover one document type.

### Gap 3: No PowerPoint-sourced documents

Slide decks converted to PDF are a common real-world use case (board presentations, technical talks, product briefs). They exercise parsers differently from text documents:

- Multi-column layouts with arbitrary positioning
- Charts and diagrams with embedded text
- Sparse text with large whitespace regions
- Bullet hierarchies and table-in-slide layouts
- Reading order ambiguity

No current corpus covers this.

### Gap 4: Frontier model results are stale

The current frontier LLM results reference models from mid-2025. Since then:
- **GPT-5.1** and **Gemini 3 Pro** are available (tested in `frontier_premium_300p.json`)
- **Claude Sonnet 4.5** was tested but Claude Opus 4.6 is now available
- Model IDs have shifted (some old aliases in PARSER_ALIASES are broken)

---

## 4. Recommended Next Steps

### Priority 1: Restore Full Parser Coverage on Pandoc Ground Truth (1-2 hours)

**Action**: Update `academic_5docs.yaml` to include all 25 working parsers and re-run.

```yaml
parser_config:
  parsers:
    # Open-source text extraction (9)
    - pypdf
    - pdfplumber
    - pymupdf
    - pymupdf4llm
    - pdfminer
    - pypdfium2
    - unstructured
    - kreuzberg
    - extractous
    # Open-source ML (2)
    - docling
    - marker
    # Native (2)
    - tika
    - marker_ollama
    # Commercial APIs (4) - requires API keys
    - aws_textract
    - azure
    - google
    - llamaparse
    # Frontier LLMs (6+) - requires API keys
    - anthropic-haiku
    - anthropic-sonnet
    - openai-mini
    - openai-4o
    - gemini-flash
    - gemini-pro
```

**Estimated time**: ~2 hours (marker/docling are slow; LLMs need API calls).
**Estimated cost**: <$2 for API-based parsers on 5 papers.
**Blocker**: Must use `parallel_workers: 1` for marker compatibility.

### Priority 2: Expand arXiv Paper Set (2-3 days)

**Target**: 25-50 papers with Pandoc ground truth, sampled for diversity.

**Selection criteria** (cross-discipline, cross-layout):

| Category | Papers | Why | Example Sources |
|----------|--------|-----|-----------------|
| Math-heavy (equations) | 5-8 | Tests formula extraction | math.AG, math.CO, hep-th |
| Table-heavy (benchmarks) | 5-8 | Tests table structure recovery | cs.CL, cs.CV (leaderboard papers) |
| Figure-heavy (diagrams) | 5-8 | Tests figure/caption handling | cs.CV, physics.optics |
| Two-column (IEEE/ACM) | 5-8 | Tests column merging | cs.*, IEEE proceedings |
| Single-column (NeurIPS/JMLR) | 5-8 | Tests standard layout | stat.ML, JMLR format |
| Long documents (>50 pages) | 3-5 | Tests scalability | Surveys, technical reports |

**Process per paper**:
1. Download LaTeX source from arXiv
2. Verify `latexpand` succeeds (reject if multi-file resolution fails)
3. Extract document body, convert with Pandoc
4. Validate output is non-trivial (>1KB, has structure)
5. Create metadata YAML

**Expected yield**: ~70% of attempted papers will convert cleanly. Budget 40-70 attempts for 25-50 usable papers.

**Rejection criteria**: Custom macros that break Pandoc, missing LaTeX source, image-only papers, non-English.

### Priority 3: Add PowerPoint-to-PDF Corpus (1-2 weeks)

**Approach**: Extend the existing DOCX builder pattern to PPTX.

**Implementation plan**:

1. **Create `builders/pptx/` module** with:
   - `slide_templates.py` — Define 8-10 slide layout types (title, bullets, table, chart, two-column, image+caption, comparison, timeline)
   - `data_generators.py` — Generate realistic content (business metrics, product roadmaps, quarterly results)
   - `pptx_builder.py` — Assemble slides using `python-pptx`

2. **Ground truth representation**:
   ```markdown
   # Slide 1: Quarterly Results

   ## Revenue Summary

   | Quarter | Revenue | Growth |
   |---------|---------|--------|
   | Q1 2025 | $12.3M | +15% |
   | Q2 2025 | $14.1M | +22% |

   Key takeaway: Record growth driven by enterprise segment.

   ---

   # Slide 2: Product Roadmap
   ...
   ```

   Each slide becomes a section. Tables are Markdown tables. Charts become their data table representation. Reading order follows slide layout (title → subtitle → body → notes).

3. **Generation targets**:
   - 50 slide decks, 5-20 slides each
   - 5 visual themes (corporate, startup, academic, government, creative)
   - Mix of content types per deck
   - Export to PDF via LibreOffice headless

4. **Evaluation mapping**:
   - **Text accuracy**: Compare extracted text against source PPTX text runs
   - **Structure**: Slide boundaries → section headers; bullet hierarchies preserved
   - **Tables**: Source table structure matches extracted tables
   - **Reading order**: Spatial layout → expected reading sequence

**Dependencies**: `python-pptx` (pure Python, no external deps), LibreOffice headless (already used for DOCX).

### Priority 4: Modernize Frontier Model Coverage (1 day)

**Update parser registry** for current model landscape:

| Model | Current Registry Entry | Status | Action |
|-------|----------------------|--------|--------|
| Claude Opus 4.6 | Not registered | New | Add `pdfsmith-anthropic-opus` |
| Claude Sonnet 4.6 | `pdfsmith-anthropic-sonnet` | Stale model ID | Update to `claude-sonnet-4-6` |
| GPT-5.1 | `pdfsmith-openai-5` | Working | Keep |
| Gemini 3 Pro | `pdfsmith-gemini-pro` | Working | Keep |
| Gemini 2.0 Flash | `pdfsmith-gemini-flash` | Working | Keep |
| GPT-4o | `pdfsmith-openai-4o` | Working | Keep |
| Gemini 1.5 Pro | Alias exists | Deprecated (404) | Remove |

**Cost for full frontier run** (5 papers, ~450 pages): ~$10-15.
**Cost for expanded set** (50 papers, ~2,000 pages): ~$50-100.

---

## 5. Strategic Recommendation

**Do both arXiv expansion AND synthetic business docs, but sequence them.**

### Phase 1 (This Week): Quick Wins
1. Re-run all 25 parsers on existing 5 papers with Pandoc ground truth
2. Update frontier model IDs in loader.py
3. Begin arXiv paper selection (identify 50 candidates)

### Phase 2 (Next 1-2 Weeks): arXiv Expansion
1. Convert 25-50 arXiv papers to Pandoc ground truth
2. Run full parser suite on expanded set
3. Publish updated benchmark results

### Phase 3 (Weeks 3-4): Synthetic Business + PPT
1. Build PPTX corpus generator (extends existing DOCX pattern)
2. Generate 50 slide deck PDFs with ground truth
3. Optionally expand DOCX corpus with more complex layouts
4. Run full parser suite on combined corpus

### Why This Sequence

- **arXiv expansion is faster**: The pipeline exists, we just need to select and convert papers. This gives us a credible 50-paper academic benchmark within days.
- **PPTX requires new tooling**: Building the generator takes 1-2 weeks. The payoff is high (unique contribution — no public benchmark tests slide deck parsing) but the lead time is longer.
- **Both together create a strong benchmark**: 50 arXiv papers + 50 PPTX decks + existing 273 DOCX-based business docs = ~370 documents with high-quality ground truth across 3 generation methods.

### What NOT to do

- **Don't chase "real" business PDFs**: The ground truth problem is unsolvable for real business documents without manual annotation, which doesn't scale. Synthetic generation with known source is the right approach.
- **Don't expand OmniDocBench**: The ground truth quality is low (OCR baseline) and the documents are mostly Chinese. Focus efforts where ground truth is reliable.
- **Don't test deprecated models**: Remove Gemini 1.5 Pro, old GPT-4 variants, and other discontinued models from configs.

---

## Appendix: File Inventory

### Modified During Ground Truth Migration
- `benchmarks/academic_5docs.yaml` — Added include_doc_ids, fixed parallel_workers
- `corpus/academic/ground_truth/2302.13971.md` — Pandoc (was ar5iv)
- `corpus/academic/ground_truth/2303.08774.md` — Pandoc (was ar5iv)
- `corpus/academic/ground_truth/2303.17564.md` — Pandoc (was ar5iv)
- `corpus/academic/sample/2302.13971.md` — Pandoc (was ar5iv)
- `corpus/academic/sample/2302.14852.md` — Pandoc (was ar5iv)
- `corpus/academic/sample/2303.08774.yaml` — New metadata
- `corpus/academic/sample/2303.17564.yaml` — New metadata
- `corpus/academic/sample/2303.18223.yaml` — New metadata

### Key Result Files
- `results/academic_5docs_pandoc.json` — Current 4-parser, 5-paper results (20/20 success)
- `results/full_corpus_353docs.json` — Previous 10-parser full benchmark
- `results/arxiv_10docs_fresh.json` — Previous 16-parser arXiv benchmark
- `results/frontier_premium_300p.json` — Frontier LLM comparison
- `results/commercial_200docs.json` — Commercial API comparison
