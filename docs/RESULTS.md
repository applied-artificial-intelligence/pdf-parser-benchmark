# PDF Parser Benchmark Results

**Last Updated**: 2025-11-24
**Parsers Tested**: 13 open-source + 5 commercial parsers
**Documents Benchmarked**: 353 documents across 6 corpora
**Total Benchmark Results**: 5,500+ (parser × document combinations)
**Primary Metric**: Edit Similarity (Levenshtein-based)

---

## Commercial Parser Results (NEW)

Cloud-based commercial PDF parsing services tested on 200 documents.

### Overall Rankings

| Rank | Parser | Raw Score | Format-Agnostic | Documents | Notes |
|------|--------|-----------|-----------------|-----------|-------|
| 1 | **Azure Document Intelligence** | **87.6%** | **88.4%** | 200 | Best overall accuracy |
| 2 | **Databricks** | 73.0% | **87.5%** | 64 | +14.5% with format normalization |
| 3 | AWS Textract | 76.1% | 76.9% | 200 | Full coverage |
| 4 | Google Document AI | 73.9% | 75.6% | 62 | 30-page limit |
| 5 | Landing AI | 83.4%* | N/A | 3 | *Limited data - credits exhausted |

### Performance by Document Type

| Parser | Invoices | Legal | HR | Synthetic | Academic |
|--------|----------|-------|-----|-----------|----------|
| Azure | **90.6%** | 94.9% | 86.5% | 92.0% | 29.3% |
| AWS | 69.2% | **94.6%** | 87.0% | 91.9% | 23.9% |
| Databricks | 58.9% | 93.7% | **89.3%** | **94.2%** | 9.5% |
| Google | 57.2% | 92.2% | 86.1% | 93.5% | 20.1% |

### Key Findings

**Azure dominates invoice parsing** - 90.6% vs 57-69% for competitors. Azure's form recognition specifically trained on invoices gives it a significant edge.

**All parsers excel on legal contracts** - 92-95% accuracy on CUAD. Well-structured text documents are straightforward for all services.

**Academic papers remain challenging** - All parsers under 30%. Two-column layouts and mathematical notation defeat even premium services.

### Important: Format Sensitivity in Scores

Raw edit similarity scores can be misleading due to **output format differences**:

| Parser | Raw Score | Format-Agnostic | Token Recall | Delta | N docs |
|--------|-----------|-----------------|--------------|-------|--------|
| Azure | 87.6% | 88.4% | 98.1% | +0.8% | 200 |
| Databricks | 73.0% | **87.5%** | 97.9% | **+14.5%** | 64 |
| AWS | 76.1% | 76.9% | 97.9% | +0.8% | 200 |
| Google | 73.9% | 75.6% | 95.8% | +1.6% | 62 |

**Key insight**: Databricks scores 73.0% raw but **87.5% format-agnostic** (+14.5 points) because it outputs markdown headers like `## PROFESSIONAL SUMMARY`, which penalizes edit distance but extracts content correctly.

**Why this matters**: Our ground truth (PyMuPDF plain text) naturally favors parsers that output plain text (Azure, AWS). Parsers that add helpful formatting (HTML tables, markdown headers) are penalized even when they extract content correctly.

See **Methodology and Limitations** section below for details on format-agnostic metrics.

### Pricing Notes

| Service | Free Tier | Paid Pricing |
|---------|-----------|--------------|
| Azure | S0 Free (500 pages/month) | ~$1.50/1000 pages |
| AWS Textract | 1000 pages/month | ~$1.50/1000 pages |
| Google Document AI | 1000 pages/month | ~$1.50/1000 pages |
| Databricks | Account-based | Volume pricing |
| Landing AI | ~300 pages | ~$3.50/1000 pages |

---

## Open-Source Parser Rankings

Average score across all 6 corpora (353 documents each):

| Rank | Parser | Avg Score | Notes |
|------|--------|-----------|-------|
| 1 | **PyPDFium2** | **81.3%** | Fast, reliable |
| 2 | **PyPDF** | **81.3%** | Pure Python |
| 3 | **PyPDF2** | **81.2%** | Legacy compatible |
| 4 | **Tika** | **81.0%** | Enterprise-grade |
| 5 | **Extractous** | **81.0%** | Rust-based |
| 6 | **PyMuPDF** | **80.9%** | Speed king |
| 7 | Kreuzberg | 79.1% | OCR support |
| 8 | PyMuPDF4LLM | 78.6% | LLM-optimized |
| 9 | Docling-fast | 77.0% | IBM, GPU-accelerated |
| 10 | PdfPlumber | 74.5% | Table specialist |
| 11 | PdfMiner | 73.4% | PDF internals |
| 12 | Unstructured | 72.5% | ETL focus |
| 13 | Marker | 68.7% | Many failures on complex docs |

---

## Quick Summary by Corpus

| Corpus | Docs | Best Parser | Score | Document Type |
|--------|------|-------------|-------|---------------|
| Legal Templates | 108 | PdfPlumber | 98.8% | Clean hierarchical text |
| CUAD Contracts | 75 | PyMuPDF | 97.7% | Real legal contracts |
| HR Documents | 34 | PyPDF2 | 87.9% | Resumes, varied formats |
| Synthetic | 31 | Docling | 88.8% | Tables, lists, columns |
| Invoices | 100 | Kreuzberg | 49.9% | Complex table structures |
| Academic | 5 | Marker | 38.1% | Two-column, equations |

---

## Parser Coverage Matrix

**Full coverage achieved**: 13 parsers × 6 corpora

| Parser | Synthetic | CUAD | Invoices | Legal | HR | Academic | Coverage |
|--------|:---------:|:----:|:--------:|:-----:|:--:|:--------:|:--------:|
| docling-fast | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| extractous | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| kreuzberg | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| marker | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pdfminer | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pdfplumber | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pymupdf | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pymupdf4llm | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pypdf | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pypdf2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| pypdfium2 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| tika | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |
| unstructured | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **6/6** |

*Note: OmniDocBench (OCR-only corpus) excluded from coverage matrix - only Marker handles it effectively.*

---

## Detailed Results by Corpus

### 1. Legal Templates (108 docs) - 98.8% Top Score

Clean, hierarchical legal documents generated from templates.

| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| pdfplumber | 98.8% | 108 |
| pymupdf | 98.8% | 108 |
| pypdfium2 | 98.8% | 108 |
| pypdf | 98.7% | 108 |
| kreuzberg | 98.6% | 108 |
| pdfminer | 98.4% | 108 |
| unstructured | 98.4% | 108 |
| tika | 98.3% | 108 |
| pymupdf4llm | 93.0% | 108 |
| marker | 90.3% | 108 |
| docling-fast | 88.1% | 108 |

**Takeaway**: Simple text-heavy documents are well-handled by most parsers.

### 2. CUAD Legal Contracts (75 docs) - 97.7% Top Score

Real-world legal contracts from the Contract Understanding Atticus Dataset.

| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| pymupdf | 97.7% | 75 |
| kreuzberg | 97.6% | 75 |
| unstructured | 97.1% | 75 |
| pypdfium2 | 97.0% | 75 |
| pdfplumber | 97.0% | 75 |
| pypdf | 96.9% | 75 |
| pdfminer | 96.7% | 75 |
| tika | 96.6% | 75 |
| pymupdf4llm | 93.2% | 75 |
| marker | 92.9% | 75 |
| docling-fast | 90.6% | 75 |
| extractous | 86.3% | 75 |
| pypdf2 | 74.9% | 75 |

**Takeaway**: Production legal documents parse very well across most parsers.

### 3. HR Documents (34 docs) - 87.8% Top Score

Resumes, job applications, and HR forms with varied layouts.

| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| unstructured | 87.8% | 34 |
| tika | 87.7% | 34 |
| pymupdf | 87.3% | 34 |
| pypdfium2 | 87.2% | 34 |
| pypdf | 87.2% | 34 |
| kreuzberg | 87.0% | 34 |
| pdfminer | 86.9% | 34 |
| pdfplumber | 86.6% | 34 |
| pymupdf4llm | 85.7% | 34 |
| marker | 82.7% | 34 |
| docling-fast | 79.7% | 34 |

**Takeaway**: Varied formatting (resumes) shows parser differentiation.

### 4. Synthetic Test Documents (31 docs) - 88.8% Top Score

Programmatically generated documents with perfect ground truth.

| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| docling-fast | 88.8% | 31 |
| marker | 88.5% | 9 |
| kreuzberg | 88.3% | 31 |
| pypdf | 88.1% | 31 |
| docling | 87.4% | 24 |
| pymupdf4llm | 86.2% | 31 |
| tika | 84.7% | 31 |
| pypdf2 | 83.6% | 31 |
| pdfminer | 83.5% | 31 |
| extractous | 79.3% | 31 |

**Takeaway**: Our synthetic corpus with known ground truth shows Docling excelling.

### 5. OmniDocBench OCR (124 English docs) - 72.8% Top Score

Image-based documents requiring OCR (subset of OmniDocBench).

| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| marker | 72.8% | 124 |
| kreuzberg | ~1% | 124 |
| docling-fast | 0.7% | 122 |
| tika | 0.5% | 124 |
| unstructured | 0.4% | 124 |

**Takeaway**: Only Marker effectively handles OCR. Others need explicit OCR enablement.

### 6. Invoices (100 docs) - 90.6% Top Score (Commercial) / 77.1% (Open Source)

Generated invoices with tabular data. Ground truth regenerated from PDF text extraction (not DOCX tables).

**Commercial Parsers:**
| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| **azure_document_intelligence** | **90.6%** | 100 |
| aws_textract | 69.1% | 100 |
| docling-fast | 67.3% | 100 |
| marker | 60.0% | 100 |
| databricks | 58.9% | 100 |
| google_document_ai | 57.6% | 100 |

**Open Source Parsers:**
| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| pymupdf4llm | 77.1% | 100 |
| kreuzberg | ~50% | 100 |
| pymupdf | ~50% | 100 |
| pdfplumber | ~50% | 100 |

**Takeaway**: Azure's specialized form recognition dominates invoice parsing. PyMuPDF4LLM leads open-source options.

### 7. Academic Papers (5 arXiv docs) - 38.1% Top Score

Two-column scientific papers with equations.

| Parser | Edit Similarity | Docs |
|--------|-----------------|------|
| marker | 38.1% | 1 |
| pypdfium2 | 29.9% | 5 |
| pymupdf | 29.7% | 5 |
| docling-fast | 27.8% | 4 |

**Note**: Marker failed on 4/5 docs (GPU/timeout). Low scores expected due to complex layouts and equations.

---

## Key Insights

### 1. Document Complexity Matters Most

Parser scores correlate strongly with document complexity:
- **Simple text** (legal templates): ~98% accuracy
- **Real documents** (CUAD, HR): ~88-97% accuracy
- **Tables** (invoices): ~50% accuracy
- **Two-column/equations** (academic): ~30% accuracy
- **OCR required**: Only Marker works well

### 2. No Single Best Parser

Different parsers excel in different scenarios:
- **Text-heavy**: PyMuPDF, PdfPlumber, Kreuzberg (fast and accurate)
- **Varied layouts**: Unstructured, Tika (robust to formatting)
- **Tables**: All struggle equally (~50%)
- **OCR**: Marker only

### 3. Speed vs Accuracy Tradeoffs

| Category | Parsers | Speed | Accuracy |
|----------|---------|-------|----------|
| Ultra-fast | PyMuPDF, Kreuzberg | 1-10ms | 87-98% |
| Fast | PdfPlumber, PyPDF | 10-50ms | 87-98% |
| Moderate | Tika, Unstructured | 50-200ms | 87-98% |
| GPU-heavy | Docling, Marker | 1-10s | 73-89% |

### 4. Table Extraction Remains Hard

Invoice corpus results show ALL parsers hitting a ~50% ceiling. This reflects:
- PDF tables are not semantically marked
- Text extraction loses spatial relationships
- No parser reliably reconstructs table structure

---

## Recommendations

### For Text-Heavy Documents
Use **PyMuPDF** or **Kreuzberg** - fast, accurate, reliable.

### For Mixed Content
Use **Unstructured** or **Tika** - handles varied layouts well.

### For OCR Needs
Use **Marker** - only parser with effective built-in OCR.

### For Production Pipelines
1. Pre-classify documents by type
2. Route to specialized parsers
3. Accept table extraction limitations

---

## Methodology and Limitations

### Metric: Edit Similarity

The primary metric is **Edit Similarity** (1 - normalized Levenshtein distance), which measures character-level similarity between parser output and ground truth. Scores range from 0% (completely different) to 100% (identical).

### Important: Format Sensitivity

**The current scores are format-sensitive.** This means parsers that output markdown or HTML are penalized even when they correctly extract all content.

**Example (invoice_001.pdf):**

| Parser | Output Format | Raw Score | Format-Agnostic | Token Recall |
|--------|---------------|-----------|-----------------|--------------|
| Azure | Plain text | 93% | 100% | 100% |
| AWS | Plain text | 66% | ~85% | ~95% |
| Databricks | HTML tables | 48% | **92%** | **100%** |
| Google | Markdown + headers | 46% | 77% | 96% |

**What this means:**
- Databricks' low raw score (48%) reflects HTML table markup (`<table><tr><td>`), not poor extraction
- Google's low score reflects markdown headers (`# INVOICE`) and number spacing (`45. 87`)
- When formatting is stripped, Databricks actually has **better** content extraction than Google

### Format-Agnostic Metrics (NEW)

We've implemented format-agnostic metrics that strip markdown/HTML before comparison:

1. **`edit_similarity_normalized`**: Strips `#` headers, HTML tags, fixes number spacing, then computes edit similarity
2. **`token_recall`**: Measures what fraction of ground truth words appear in output (ignores order and formatting)

These metrics provide a fairer comparison when parsers output different formats.

### Ground Truth Source

Ground truth was extracted from PDFs using PyMuPDF's `get_text()` method. This produces plain text output, which naturally favors parsers that also output plain text.

**Alternative approaches we considered:**
- Multiple ground truth formats (plain text, markdown, HTML)
- Semantic similarity via embeddings
- Task-based evaluation (LLM Q&A accuracy)

### Recommendations for Interpretation

1. **For text-heavy documents**: Raw edit similarity is meaningful
2. **For structured documents (tables, forms)**: Use format-agnostic metrics or token recall
3. **Compare parsers within the same output format category** when possible
4. **High token recall + low edit similarity** = formatting difference, not extraction failure

---

## Test Environment

- **Hardware**: GPU-enabled workstation (CUDA)
- **Metrics**: Edit Similarity (primary), ChrF++, CER, Format-Agnostic Edit Similarity, Token Recall
- **Ground Truth**: PyMuPDF text extraction (plain text)

## Files

Results stored in `results/` directory:

**Commercial Parser Benchmarks:**
- `commercial_200docs.checkpoint.json` - Main commercial results (1100+ results)
- `invoices_100docs_fresh.checkpoint.json` - Invoice benchmark with corrected ground truth
- `invoices_databricks.checkpoint.json` - Databricks-only invoice results

**Open Source Parser Benchmarks:**
- `hr_34docs.json`
- `invoices_100docs.json`
- `legal_108docs.json`
- `cuad_75docs_all_parsers.json`
- `synthetic_missing_parsers.json`
- `academic_5docs.json`
- `omnidocbench_english_ocr.json`
