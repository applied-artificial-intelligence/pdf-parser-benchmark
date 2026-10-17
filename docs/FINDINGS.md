# Historical findings and publication framing

Historical record. For current source-verified findings, use `PROJECT_ORIENTATION.md`
and the reconstruction report identified by `docs/BENCHMARK_STATUS_REPORT.md`.
The labels and recommendations below describe the retained historical artifact;
they are not current publication approval or current parser recommendations.

**Date**: November 2025
**Historical status label**: Ready for Publication (not current approval)
**Total Documents**: 800+ across 6 corpora
**Parsers Evaluated**: 13 open-source + 5 commercial

---

## Executive Summary

PDF-Bench is an open-source benchmarking suite for evaluating PDF-to-text/markdown conversion quality. This document consolidates all key findings from extensive benchmarking of 18 parsers across 800+ documents.

### Top-Line Findings

1. **No single parser dominates all document types** - Parser selection should be driven by document characteristics
2. **Format-agnostic metrics reveal hidden performance** - Databricks gains +14.5 percentage points when output format is normalized
3. **Document complexity determines accuracy ceiling** - Simple legal text: 98%, Invoices: 50-90%, Academic papers: 30%
4. **Commercial vs. open-source gap is narrower than expected** - Best open-source (81.3%) vs. best commercial (88.4%) = 7pt gap
5. **OCR remains a differentiator** - Only Marker handles image-based PDFs effectively among open-source options

---

## 1. Why We Built This Benchmark

### The Problem with Existing Benchmarks

Existing PDF parsing benchmarks suffer from three critical limitations:

| Limitation | Impact | Examples |
|------------|--------|----------|
| **Image-focused** | Irrelevant for born-digital business documents | PubLayNet, DocLayNet, DocBank |
| **Academic-only** | Don't reflect enterprise document diversity | PubMed/arXiv-sourced datasets |
| **Manual annotation** | Small scale, imperfect, expensive to extend | OmniDocBench (981 pages) |

### Our Solution: Source-Derived Ground Truth

We adopted a **DOCX-to-PDF pipeline** that provides perfect ground truth:

1. Create documents programmatically using `python-docx`
2. Extract structure directly from OpenXML internals
3. Convert to PDF with LibreOffice headless
4. Result: Ground truth matches semantic structure exactly

**Why this matters**: We can *know* a heading's level from its style tag. We can *know* a table's merged-cell structure. We can *know* list nesting depth. This eliminates annotation compromises that other benchmarks must make.

### Target Use Case: RAG Systems

This benchmark evaluates parsers for Retrieval-Augmented Generation (RAG) applications where:
- Simple text extraction is insufficient
- Parsing failures cause "garbage in, garbage out" in downstream LLMs
- Hierarchical structure affects chunking quality
- Reading order determines context coherence

---

## 2. The Evaluation Framework

### Multi-Layer Evaluation Stack

Following established document intelligence research, we evaluate across multiple layers:

| Layer | Task | Metric | Benchmark Dataset |
|-------|------|--------|-------------------|
| **L1** | Physical Layout | mAP | DocLayNet (reference) |
| **L2** | Semantic Labeling | F1 | Element F1 |
| **L3** | Reading Order | Edit Distance | Synthetic multi-column |
| **L4** | Table Structure | TEDS | Invoice corpus |
| **L5** | End-to-End | Edit Similarity | All corpora |

### Metrics Used

| Metric | What It Measures | When to Use |
|--------|------------------|-------------|
| **Edit Similarity** | Character-level text accuracy | General quality (primary) |
| **Edit Similarity Normalized** | Content accuracy ignoring format | Cross-parser comparison |
| **Token Recall** | Word extraction completeness | Content extraction |
| **ChrF++** | Character n-gram F-score | Alternative text quality |
| **TEDS** | Table structure accuracy | Table-heavy documents |
| **Tree Similarity** | Document hierarchy preservation | Structured documents |

### Format-Agnostic Metrics (Key Innovation)

**Critical Discovery**: Standard edit distance metrics penalize parsers for helpful formatting.

| Parser | Raw Score | Format-Agnostic | Delta |
|--------|-----------|-----------------|-------|
| Azure | 87.6% | 88.4% | +0.8% |
| **Databricks** | 73.0% | **87.5%** | **+14.5%** |
| AWS | 76.1% | 76.9% | +0.8% |
| Google | 73.9% | 75.6% | +1.6% |

**Insight**: Databricks outputs markdown headers (`## PROFESSIONAL SUMMARY`) which penalizes edit distance but correctly extracts content. Format-agnostic metrics reveal its true performance.

---

## 3. Corpora and Rationale

### Corpus Summary

| Corpus | Documents | Ground Truth Method | Purpose |
|--------|-----------|---------------------|---------|
| **Synthetic** | 31 | DOCX-to-PDF (perfect) | Controlled feature testing |
| **Invoices** | 100 | DOCX-to-PDF (perfect) | Table extraction |
| **Legal Templates** | 108 | DOCX-to-PDF (perfect) | Hierarchical structure |
| **HR/Resumes** | 34 | DOCX-to-PDF (perfect) | Varied layout handling |
| **CUAD Contracts** | 75 | PDF text layer | Real-world legal |
| **OmniDocBench** | 252 | External benchmark | OCR, diverse formats |

### Synthetic Corpus Design

**Purpose**: Systematic, controlled testing of specific parser capabilities

| Category | Documents | Features Tested |
|----------|-----------|-----------------|
| Basic Text | 7 | Paragraphs, headings, basic lists |
| Tables | 6 | Simple grids, merged cells, multi-level headers |
| Lists | 6 | Bullets, numbered, nested (2-3 levels) |
| Multi-Column | 6 | Two/three columns, mixed layouts |
| Mixed Content | 6 | Reports, meeting minutes, annual reports |

**Key Findings by Category**:
- **Tables (09-14)**: Best PyPDFium2 (79%), Worst Docling (53%)
- **Multi-Column (21-26)**: Best PyMuPDF (93%), Worst PdfPlumber (56%)
- **Lists (15-20)**: All parsers >90%, minimal differentiation

### Business Document Rationale

Based on OCR market research and enterprise automation trends:

| Category | Rationale | Our Coverage |
|----------|-----------|--------------|
| **Finance/AP** | BFSI = 21.3% of OCR market | 100 invoices |
| **HR/Recruiting** | 99% of Fortune 500 use ATS | 34 resumes |
| **Legal** | High corporate volume | 183 documents (CUAD + templates) |

---

## 4. Commercial Parser Leaderboard

### Overall Rankings (200-doc benchmark)

| Rank | Parser | Raw Score | Format-Agnostic | Coverage | Notes |
|------|--------|-----------|-----------------|----------|-------|
| **1** | **Azure Document Intelligence** | **87.6%** | **88.4%** | 200/200 | Best overall |
| **2** | **Databricks** | 73.0% | **87.5%** | 64/200 | Excellent with normalization |
| **3** | AWS Textract | 76.1% | 76.9% | 200/200 | Full coverage |
| **4** | Google Document AI | 73.9% | 75.6% | 62/200 | 30-page limit |
| **5** | Landing AI | 83.4%* | N/A | 3/200 | *Limited data |

### Performance by Document Type

| Parser | Invoices | Legal | HR | Synthetic |
|--------|----------|-------|-----|-----------|
| **Azure** | **90.6%** | 94.9% | 86.5% | 92.0% |
| AWS | 69.2% | **94.6%** | 87.0% | 91.9% |
| Databricks | 58.9% | 93.7% | **89.3%** | **94.2%** |
| Google | 57.2% | 92.2% | 86.1% | 93.5% |

### Key Commercial Insights

1. **Azure dominates invoices** (90.6% vs. 57-69% for competitors) - specialized form recognition training
2. **All excel on legal contracts** (92-95%) - well-structured text is straightforward
3. **Databricks leads on synthetic** (94.2%) - best structure preservation with markdown output
4. **Coverage varies significantly** - Google and Databricks miss documents due to API limitations

### Pricing Context

| Service | Free Tier | Paid Rate |
|---------|-----------|-----------|
| Azure | 500 pages/month | ~$1.50/1K pages |
| AWS | 1000 pages/month | ~$1.50/1K pages |
| Google | 1000 pages/month | ~$1.50/1K pages |
| Databricks | Account-based | Volume pricing |
| Landing AI | ~300 pages | ~$3.50/1K pages |

---

## 5. Open-Source Parser Leaderboard

### Overall Rankings (353 documents)

| Rank | Parser | Avg Score | Speed | Notes |
|------|--------|-----------|-------|-------|
| **1** | **PyPDFium2** | **81.3%** | Fast | Google's PDF library |
| **2** | **PyPDF** | **81.3%** | Fast | Pure Python |
| **3** | **PyPDF2** | **81.2%** | Fast | Legacy compatible |
| **4** | **Tika** | **81.0%** | Moderate | Enterprise-grade |
| **5** | **Extractous** | **81.0%** | Fast | Rust-based |
| **6** | **PyMuPDF** | **80.9%** | Ultra-fast | Speed king |
| 7 | Kreuzberg | 79.1% | Fast | OCR support |
| 8 | PyMuPDF4LLM | 78.6% | Fast | LLM-optimized |
| 9 | Docling-fast | 77.0% | Slow | GPU-accelerated |
| 10 | PdfPlumber | 74.5% | Fast | Table specialist |
| 11 | PdfMiner | 73.4% | Fast | PDF internals |
| 12 | Unstructured | 72.5% | Moderate | ETL focus |
| 13 | Marker | 68.7% | Slow | Many failures |

### Performance by Document Type

| Document Type | Best Parser | Score | Worst Parser | Score |
|---------------|-------------|-------|--------------|-------|
| Legal Templates | PdfPlumber | 98.8% | Docling | 88.1% |
| CUAD Contracts | PyMuPDF | 97.7% | PyPDF2 | 74.9% |
| HR Documents | Unstructured | 87.8% | Docling | 79.7% |
| Synthetic | Docling | 88.8% | Extractous | 79.3% |
| Multi-Column | PyMuPDF | 93% | PdfPlumber | 56% |

### Speed vs. Accuracy Tradeoffs

| Category | Parsers | Speed | Accuracy |
|----------|---------|-------|----------|
| Ultra-fast | PyMuPDF, Kreuzberg | 1-10ms | 79-98% |
| Fast | PdfPlumber, PyPDF | 10-50ms | 74-98% |
| Moderate | Tika, Unstructured | 50-200ms | 72-98% |
| GPU-heavy | Docling, Marker | 1-10s | 68-89% |

---

## 6. OmniDocBench Results (OCR Benchmark)

### Context

OmniDocBench is a comprehensive benchmark from CVPR 2025 covering diverse document types. The English subset (252 documents) includes scanned/image-based PDFs requiring OCR.

### Results

| Parser | Edit Similarity | Documents | Notes |
|--------|-----------------|-----------|-------|
| **Marker** | **72.8%** | 124 | Only effective OCR parser |
| Kreuzberg | ~1% | 124 | OCR disabled by default |
| Docling | 0.7% | 122 | Needs explicit OCR config |
| Tika | 0.5% | 124 | No built-in OCR |
| Unstructured | 0.4% | 124 | Basic OCR only |

**Key Insight**: For image-based PDFs, only Marker provides effective built-in OCR among open-source options. Other parsers require explicit OCR configuration or external OCR preprocessing.

---

## 7. Domain-Specific Recommendations

### For Invoice Processing

| Priority | Parser | Score | Rationale |
|----------|--------|-------|-----------|
| 1 | Azure Document Intelligence | 90.6% | Specialized form recognition |
| 2 | Databricks | 87.5%* | Good with format normalization |
| 3 | AWS Textract | 69.2% | Wide coverage, lower accuracy |

*Format-agnostic score

### For Resume Parsing

| Priority | Parser | Notes |
|----------|--------|-------|
| 1 | Azure | Best section detection |
| 2 | Databricks | Good structure with markdown |
| 3 | Layout-aware (Marker, Docling) | Complex format handling |

### For Legal Contracts

| Priority | Parser | Notes |
|----------|--------|-------|
| 1 | AWS Textract | Best on dense text |
| 2 | PyMuPDF | Fast and accurate |
| 3 | Azure | Good structure preservation |

### For Multi-Column Documents

| Priority | Parser | Score | Notes |
|----------|--------|-------|-------|
| 1 | PyMuPDF | 93% | Excellent reading order |
| 2 | Kreuzberg | 91% | Fast with good accuracy |
| **Avoid** | PdfPlumber | 56% | Struggles with column detection |

### For OCR Needs

| Priority | Parser | Notes |
|----------|--------|-------|
| 1 | Marker | Only effective built-in OCR |
| 2 | Commercial APIs | All have good OCR |
| 3 | Kreuzberg (OCR mode) | Requires explicit config |

---

## 8. Key Technical Insights

### 1. Document Complexity Determines Accuracy Ceiling

| Complexity | Example | Typical Accuracy |
|------------|---------|------------------|
| Simple | Legal templates | ~98% |
| Moderate | CUAD contracts, HR docs | ~88-97% |
| Complex | Invoices with tables | ~50-90% |
| Very Complex | Academic papers (2-col) | ~30% |
| OCR Required | Scanned documents | 0-73% |

### 2. Table Extraction Remains Hard

All parsers hit a ~50% ceiling on invoice table extraction because:
- PDF tables are not semantically marked
- Text extraction loses spatial relationships
- No parser reliably reconstructs table structure

### 3. Reading Order is Subtle

Multi-column documents expose critical reading order failures:
- Down-then-across vs. across-then-down
- PdfPlumber fails dramatically (56%)
- PyMuPDF handles it best (93%)

### 4. Output Format Matters for Evaluation

Parsers output different formats (plain text, markdown, HTML). Raw edit similarity penalizes structure-aware parsers. Format-agnostic metrics provide fairer comparison.

### 5. GPU Parsers Don't Always Win

Despite higher resource requirements:
- Docling averages 77% vs. PyPDFium2 at 81%
- Marker has many failures on complex documents
- Simple, fast parsers often perform best

---

## 9. Methodology Notes

### Ground Truth Sources

| Corpus | Method | Quality |
|--------|--------|---------|
| Synthetic/Business | DOCX extraction | Perfect |
| CUAD | PDF text layer | Good (depends on PDF encoding) |
| OmniDocBench | External annotations | Variable |

### Normalization Applied

Before metric computation:
1. Unicode NFC normalization
2. Whitespace standardization (CRLF→LF, tabs→spaces)
3. Quote normalization (smart quotes→straight)
4. Multiple blank line collapse

### Limitations

1. **Ground truth format affects scores** - PyMuPDF plain text favors plain-text parsers
2. **API failures affect coverage** - Databricks (64/200), Google (62/200) vs. Azure/AWS (200/200)
3. **Single metric cannot capture all quality dimensions** - Use multiple metrics for full picture

---

## 10. Repository Structure

### Core Files

```
pdf_bench/
├── runner.py           # Benchmark orchestration
├── loader.py           # Document loading
├── metrics/            # All evaluation metrics
└── systems/            # Parser adapters (18 parsers)

corpus/
├── synthetic/          # 31 generated test documents
├── business/           # Invoices, legal, HR
└── academic/           # OmniDocBench, sample papers

benchmarks/             # YAML benchmark configurations
results/                # JSON benchmark results
docs/                   # Documentation
```

### Running Benchmarks

```bash
# Full benchmark
uv run python -m pdf_bench.runner benchmarks/full_corpus_353docs.yaml

# Specific parsers
uv run python -m pdf_bench.runner benchmarks/cuad_75docs.yaml --parsers pymupdf marker

# Commercial parsers (requires API keys in .env)
uv run python -m pdf_bench.runner benchmarks/commercial_200docs.yaml
```

---

## 11. Publication Angles

### Potential Article Topics

1. **"The Hidden Cost of PDF Parsing Metrics"** - How format sensitivity distorts parser comparisons
2. **"Which PDF Parser Should You Use? It Depends."** - Domain-specific recommendations
3. **"Why Manual Annotation Doesn't Scale"** - The case for synthetic benchmarks
4. **"Commercial vs. Open-Source PDF Parsing in 2025"** - Detailed comparison
5. **"The Multi-Column Problem"** - Reading order challenges and solutions
6. **"Tables in PDFs: Why Everyone Struggles"** - Analysis of the 50% ceiling

### Key Messages for Decision Makers

1. **No one-size-fits-all** - Choose parser based on document type
2. **Free options are competitive** - 7pt gap from best commercial to best open-source
3. **Speed doesn't mean inaccuracy** - PyMuPDF is both fastest and highly accurate
4. **Beware misleading benchmarks** - Output format affects scores significantly
5. **Test on your documents** - Benchmark results vary by domain

---

## Appendix: Results Files

### Main Benchmark Results

| File | Description |
|------|-------------|
| `commercial_200docs.checkpoint.json` | Commercial parser results (1100+ results) |
| `full_corpus_353docs.json` | Open-source parser results |
| `cuad_75docs_all_parsers.json` | Legal contracts comparison |
| `omnidocbench_english_ocr.json` | OCR benchmark results |

### By Corpus

| Corpus | Results File |
|--------|--------------|
| Synthetic | `synthetic_missing_parsers.json` |
| Invoices | `invoices_100docs_fresh.json` |
| Legal | `legal_108docs.json` |
| HR | `hr_34docs.json` |
| CUAD | `cuad_75docs_all_parsers.json` |
| OmniDocBench | `omnidocbench_english_ocr.json` |

---

*Last Updated: November 2025*
