# PDF-Bench Leaderboard Proposals

Publication-ready leaderboard formats for different audiences and use cases.

**Date**: November 2025
**Benchmark Version**: 1.1 (with Frontier LLMs)
**Documents Evaluated**: 800+ across 6 corpora
**Last Updated**: 2025-11-30

---

## NEW: Frontier LLM Parser Leaderboard

### The Big Picture: LLMs vs Traditional Parsers

Frontier LLMs (GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5) can now parse PDFs directly via vision capabilities. How do they compare?

| Category | Best Parser | Edit Sim | Cost/Page | Use Case |
|----------|-------------|----------|-----------|----------|
| **Premium LLM** | GPT-5.1 | **92%** | ~$0.05 | Highest quality, low volume |
| **Premium LLM** | Gemini 3 Pro | 87% | ~$0.03 | Quality/cost balance |
| **Premium LLM** | Claude Sonnet 4.5 | 80% | ~$0.04 | Anthropic ecosystem |
| **Budget LLM** | LlamaParse | 78% | $0.003 | **Sweet spot** - LLM quality, 10x cheaper |
| **Budget LLM** | Gemini 2.0 Flash | 77% | ~$0.001 | Cheapest LLM option |
| **Open Source** | pypdfium2/pypdf | 78% | Free | Best free option |
| **Commercial API** | Azure Doc Intel | 88% | ~$0.0015 | Enterprise, forms |

### Key Finding: The 14-Point Premium Gap

**GPT-5.1 (92%) vs best open-source (78%) = 14 percentage points improvement**

Is it worth $0.05/page? Depends on:
- **High-value documents** (legal, financial): Yes
- **Bulk processing** (millions of pages): No - use open source or LlamaParse

### Frontier LLM Rankings (28 documents)

| Rank | Model | Edit Sim | ChrF++ | Tree Sim | Cost/Page |
|------|-------|----------|--------|----------|-----------|
| 1 | **GPT-5.1** | **92%** | **93.0** | 44% | ~$0.05 |
| 2 | Gemini 3 Pro | 87% | 86.2 | 43% | ~$0.03 |
| 3 | Claude Sonnet 4.5 | 80% | 81.7 | 44% | ~$0.04 |

### Budget LLM Rankings (30 documents)

| Rank | Model | Edit Sim | ChrF++ | Tree Sim | Cost/Page |
|------|-------|----------|--------|----------|-----------|
| 1 | **LlamaParse** | **78%** | **83.4** | **39%** | $0.003 |
| 2 | Gemini 2.0 Flash | 77% | 80.3 | 35% | ~$0.001 |
| 3 | GPT-4o-mini | 75% | 76.7 | 13% | ~$0.002 |
| 4 | Claude 3.5 Haiku | 68% | 69.7 | 33% | ~$0.002 |

### LLM Selection Guide

| If You Need | Choose | Why |
|-------------|--------|-----|
| Maximum quality, cost no object | **GPT-5.1** | 92% - best in class |
| Quality/cost balance | **Gemini 3 Pro** | 87% at ~$0.03/page |
| Budget LLM quality | **LlamaParse** | 78% at $0.003/page (10x cheaper than frontier) |
| Cheapest LLM option | **Gemini 2.0 Flash** | 77% at ~$0.001/page |
| Anthropic ecosystem | **Claude Sonnet 4.5** | 80% with Claude integration |

### Critical Insight: GPT-4o-mini's Structure Problem

GPT-4o-mini scores only **13% tree similarity** vs 35%+ for others. It extracts text well but destroys document structure. **Avoid for RAG pipelines** where structure matters.

### LlamaParse: The Sweet Spot

LlamaParse deserves special mention:
- **78% edit similarity** - matches best open-source parsers
- **$0.003/page** - 10x cheaper than frontier LLMs
- **Purpose-built for PDF** - not a general LLM doing PDF on the side
- **Free tier**: 1,000 pages/day for testing

For most use cases, LlamaParse offers the best quality/cost ratio.

---

## Overall Leaderboard (Combined Commercial + Open Source)

### Best Overall Performance

Top parsers by Edit Similarity across all document types:

| Rank | Parser | Type | Score | Best For |
|------|--------|------|-------|----------|
| 1 | Azure Document Intelligence | Commercial | 88.4% | Invoices, forms |
| 2 | Databricks Document AI | Commercial | 87.5%* | Structured markdown |
| 3 | PyPDFium2 | Open Source | 81.3% | General extraction |
| 4 | PyPDF | Open Source | 81.3% | Pure Python |
| 5 | PyPDF2 | Open Source | 81.2% | Legacy compatibility |
| 6 | Tika | Open Source | 81.0% | Enterprise systems |
| 7 | PyMuPDF | Open Source | 80.9% | Speed-critical |
| 8 | AWS Textract | Commercial | 76.9% | Full coverage |
| 9 | Google Document AI | Commercial | 75.6% | GCP integration |

*Format-agnostic score (normalized for markdown output)

### Key Finding

**The gap between best commercial and best open-source is only 7 percentage points** (88.4% vs. 81.3%). For many use cases, free open-source options provide competitive quality.

---

## Commercial Parser Leaderboard

### Overall Rankings

| Rank | Parser | Raw Score | Format-Agnostic | Coverage | Price/1K Pages |
|------|--------|-----------|-----------------|----------|----------------|
| 1 | **Azure** | 87.6% | **88.4%** | 200/200 | ~$1.50 |
| 2 | **Databricks** | 73.0% | **87.5%** | 64/200 | Volume |
| 3 | AWS Textract | 76.1% | 76.9% | 200/200 | ~$1.50 |
| 4 | Google Doc AI | 73.9% | 75.6% | 62/200 | ~$1.50 |

### By Document Type

| Parser | Invoices | Legal | HR/Resumes | Synthetic |
|--------|:--------:|:-----:|:----------:|:---------:|
| **Azure** | **90.6%** | 94.9% | 86.5% | 92.0% |
| Databricks | 58.9% | 93.7% | **89.3%** | **94.2%** |
| AWS | 69.2% | **94.6%** | 87.0% | 91.9% |
| Google | 57.2% | 92.2% | 86.1% | 93.5% |

### Selection Guide

| If You Need | Choose | Why |
|-------------|--------|-----|
| Best invoice processing | **Azure** | 90.6% on invoices (20+ points above competitors) |
| Best structure preservation | **Databricks** | Markdown output, 94.2% on synthetic |
| Full document coverage | **Azure** or **AWS** | 100% document processing rate |
| GCP ecosystem integration | **Google** | Native integration (accepts 30-page limit) |

---

## Open Source Parser Leaderboard

### Overall Rankings (353 Documents)

| Rank | Parser | Score | Speed | License |
|------|--------|-------|-------|---------|
| 1 | **PyPDFium2** | 81.3% | Fast | BSD-3 |
| 2 | **PyPDF** | 81.3% | Fast | BSD-3 |
| 3 | PyPDF2 | 81.2% | Fast | BSD-3 |
| 4 | Tika | 81.0% | Moderate | Apache-2 |
| 5 | Extractous | 81.0% | Fast | Apache-2 |
| 6 | PyMuPDF | 80.9% | **Ultra-fast** | AGPL |
| 7 | Kreuzberg | 79.1% | Fast | MIT |
| 8 | PyMuPDF4LLM | 78.6% | Fast | AGPL |
| 9 | Docling | 77.0% | Slow (GPU) | MIT |
| 10 | PdfPlumber | 74.5% | Fast | MIT |
| 11 | PdfMiner | 73.4% | Fast | MIT |
| 12 | Unstructured | 72.5% | Moderate | Apache-2 |
| 13 | Marker | 68.7% | Slow (GPU) | GPL-3 |

### By Document Type

| Document Type | Best Parser | Score | Worst Parser | Score |
|---------------|-------------|-------|--------------|-------|
| Legal Templates | PdfPlumber | 98.8% | Docling | 88.1% |
| Legal Contracts (CUAD) | PyMuPDF | 97.7% | PyPDF2 | 74.9% |
| HR/Resumes | Unstructured | 87.8% | Docling | 79.7% |
| Synthetic (controlled) | Docling | 88.8% | Extractous | 79.3% |
| Multi-Column | PyMuPDF | 93% | PdfPlumber | 56% |

### Speed vs. Accuracy Matrix

| Category | Parsers | Latency | Accuracy Range |
|----------|---------|---------|----------------|
| **Ultra-fast** | PyMuPDF | 1-10ms | 79-98% |
| **Fast** | PyPDFium2, PyPDF, Kreuzberg | 10-50ms | 74-98% |
| **Moderate** | Tika, Unstructured | 50-200ms | 72-98% |
| **GPU-heavy** | Docling, Marker | 1-10s | 68-89% |

### Selection Guide

| If You Need | Choose | Why |
|-------------|--------|-----|
| Maximum speed | **PyMuPDF** | 1-10ms per document, 80.9% accuracy |
| Best overall accuracy | **PyPDFium2** or **PyPDF** | 81.3% average |
| Multi-column documents | **PyMuPDF** | 93% on multi-column (PdfPlumber gets 56%) |
| Pure Python (no deps) | **PyPDF** | No C extensions |
| Enterprise deployment | **Tika** | Battle-tested, Apache ecosystem |
| LLM-optimized output | **PyMuPDF4LLM** | Markdown format for RAG |
| OCR capability | **Marker** | Only effective built-in OCR |

---

## Domain-Specific Leaderboards

### Invoice Processing

Critical for accounts payable automation:

| Rank | Parser | Score | Notes |
|------|--------|-------|-------|
| 1 | **Azure** | 90.6% | Specialized form recognition |
| 2 | Databricks* | 87.5% | Format-agnostic score |
| 3 | AWS | 69.2% | Full coverage |
| 4 | Google | 57.2% | Page limits affect large invoices |

*Tables remain challenging for all parsers (~50% ceiling)

### Legal Documents

For contract analysis and legal tech:

| Rank | Parser | Score | Notes |
|------|--------|-------|-------|
| 1 | **PdfPlumber** | 98.8% | Templates |
| 2 | **PyMuPDF** | 97.7% | Real contracts (CUAD) |
| 3 | AWS | 94.6% | Commercial option |
| 4 | Azure | 94.9% | Commercial option |

Legal documents are "solved" - simple, well-structured text yields high scores across all parsers.

### Resume/HR Documents

For recruiting and HR automation:

| Rank | Parser | Score | Notes |
|------|--------|-------|-------|
| 1 | **Databricks** | 89.3% | Best section detection |
| 2 | Unstructured | 87.8% | Good varied format handling |
| 3 | AWS | 87.0% | Reliable commercial option |
| 4 | Azure | 86.5% | Good structure preservation |

### OCR-Required Documents (Scanned/Image PDFs)

OmniDocBench English subset (252 documents):

| Rank | Parser | Score | Notes |
|------|--------|-------|-------|
| 1 | **Marker** | 72.8% | Only effective built-in OCR |
| 2 | Kreuzberg (OCR) | ~51%* | Requires explicit config |
| 3 | Unstructured (OCR) | ~45%* | Basic OCR only |
| - | Others | <1% | No OCR capability |

*Estimated with OCR enabled

**Key Insight**: For scanned documents, Marker is the only open-source option with effective built-in OCR. Commercial APIs all handle OCR well.

---

## Format Sensitivity Leaderboard

Reveals how output format affects benchmark scores:

| Parser | Raw Score | Normalized | Delta | Interpretation |
|--------|-----------|------------|-------|----------------|
| **Databricks** | 73.0% | **87.5%** | **+14.5%** | Markdown hurts raw score |
| Google | 73.9% | 75.6% | +1.6% | Light formatting |
| AWS | 76.1% | 76.9% | +0.8% | Plain text output |
| Azure | 87.6% | 88.4% | +0.8% | Plain text output |

**Critical Discovery**: Traditional edit distance metrics penalize parsers for helpful formatting. Databricks adds markdown headers (`## PROFESSIONAL SUMMARY`) which improves readability but hurts character-level similarity scores.

---

## Speed Leaderboard

Processing time per document (CPU, single-threaded):

| Rank | Parser | Avg Latency | Throughput |
|------|--------|-------------|------------|
| 1 | **PyMuPDF** | 1-5ms | ~200 docs/sec |
| 2 | Kreuzberg | 5-10ms | ~100 docs/sec |
| 3 | PyPDFium2 | 10-20ms | ~50 docs/sec |
| 4 | PyPDF | 20-30ms | ~35 docs/sec |
| 5 | PdfPlumber | 30-50ms | ~25 docs/sec |
| 6 | Tika | 100-200ms | ~7 docs/sec |
| 7 | Unstructured | 150-300ms | ~5 docs/sec |
| 8 | Docling | 1-5s (GPU) | ~0.5 docs/sec |
| 9 | Marker | 2-10s (GPU) | ~0.2 docs/sec |

**Note**: Commercial API latency depends on network and API load, typically 0.5-3s per document.

---

## Reliability Leaderboard

Document processing success rate:

| Rank | Parser | Success Rate | Failure Mode |
|------|--------|--------------|--------------|
| 1 | Azure | 100% (200/200) | None observed |
| 2 | AWS | 100% (200/200) | None observed |
| 3 | PyMuPDF | 99.5%+ | Rare corrupt PDFs |
| 4 | PyPDF | 99%+ | Some encrypted PDFs |
| 5 | Databricks | 68% (68/100) | API returns None |
| 6 | Google | 62% (62/100) | 30-page limit |
| 7 | Marker | ~85% | Complex documents fail |

---

## Leaderboard Summary Table

Quick reference for parser selection:

| Use Case | Best Choice | Alternative | Avoid |
|----------|-------------|-------------|-------|
| **General extraction** | PyPDFium2 | PyPDF | Marker |
| **Speed-critical** | PyMuPDF | Kreuzberg | Docling |
| **Invoice processing** | Azure | Databricks | Google |
| **Legal contracts** | PyMuPDF | AWS | - |
| **Multi-column** | PyMuPDF | Kreuzberg | PdfPlumber |
| **OCR required** | Marker | Commercial APIs | Most others |
| **RAG/LLM prep** | PyMuPDF4LLM | Databricks | - |
| **Budget-conscious** | PyPDFium2 | PyPDF | Commercial |
| **Maximum accuracy** | Azure | Databricks* | Marker |

*With format normalization

---

## Methodology Notes

### Scoring
- **Edit Similarity**: Primary metric, character-level accuracy
- **Format-Agnostic**: Strips markdown/formatting before comparison
- **Token Recall**: Word-level extraction completeness

### Corpora
- Synthetic: 31 controlled test documents
- CUAD: 75 real legal contracts
- Invoices: 100 generated business documents
- Legal Templates: 108 contract templates
- HR/Resumes: 34 documents
- OmniDocBench: 252 English documents

### Limitations
- Ground truth format affects raw scores
- API availability varies (Databricks/Google have coverage gaps)
- OCR testing limited to Marker due to configuration complexity

---

*Generated from PDF-Bench v1.0 - November 2025*
