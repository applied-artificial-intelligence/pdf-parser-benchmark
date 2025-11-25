# PDF-Bench Test Corpora

Comprehensive collection of PDF documents for benchmarking parser performance across diverse document types.

**Total Documents**: 800+ across 6 corpus categories
**Ground Truth Methods**: DOCX-to-PDF (synthetic/business), Text extraction (external)
**Benchmark Status**: 560+ documents fully benchmarked

---

## Overview

PDF-Bench uses a multi-corpus approach combining synthetic documents (perfect ground truth) with real-world documents from established datasets.

### Corpus Summary

| Corpus | Documents | Status | Ground Truth | Benchmarked |
|--------|-----------|--------|--------------|-------------|
| **Synthetic** | 31 | Complete | Markdown source | Yes (all parsers) |
| **CUAD Contracts** | 75 | Complete | PDF text layer | Yes (13 parsers) |
| **Invoices** | 100 | Complete | Markdown source | In progress |
| **Legal Templates** | 108 | Complete | Markdown source | In progress |
| **HR/Resumes** | 34 | Complete | Markdown source | Yes (11 parsers) |
| **OmniDocBench** | 252 (English) | Complete | Text extraction | Yes (4 OCR parsers) |

**Total**: 800+ documents across 6 corpora

---

## 1. Synthetic Corpus (31 Documents)

**Purpose**: Systematic, controlled testing of specific parser capabilities

### Design Philosophy

The synthetic corpus uses **DOCX-to-PDF conversion** to achieve perfect ground truth:
1. Create documents programmatically with python-docx
2. Extract structure directly from DOCX internals
3. Convert DOCX to PDF with LibreOffice headless
4. Result: Ground truth matches semantic structure exactly

### Document Categories

| Category | Documents | Features Tested |
|----------|-----------|-----------------|
| Basic Text | 7 | Paragraphs, headings, basic lists |
| Tables | 6 | Simple grids, merged cells, multi-level headers |
| Lists | 6 | Bullets, numbered, nested (2-3 levels) |
| Multi-Column | 6 | Two/three columns, mixed layouts, newsletter |
| Mixed Content | 6 | Reports, meeting minutes, annual reports |

### Key Findings by Category

**Tables (09-14)**:
- Best: PyPDFium2 (78.57%), PyPDF, Kreuzberg
- Worst: PDFMiner (54.55%), Docling (53.01%)
- Challenge: Merged cells and complex headers

**Multi-Column (21-26)**:
- Best: PyMuPDF (89-97%), Kreuzberg (88-93%)
- Worst: PdfPlumber (44-67%), Unstructured (42-65%)
- Challenge: Reading order (down-then-across vs across-then-down)

**Lists (15-20)**:
- All parsers perform well (>90%)
- Best: PdfPlumber (97.71%), Unstructured (97.98%)

### Files

- PDFs: `corpus/synthetic/pdfs/*.pdf`
- Ground truth: `corpus/synthetic/ground_truth/*.md`
- Metadata: `corpus/synthetic/metadata/*.yaml`

---

## 2. CUAD Legal Contracts (75 Documents)

**Purpose**: Real-world legal document parsing from SEC filings

### Source

**CUAD (Contract Understanding Atticus Dataset)**:
- Published by The Atticus Project
- 510 contracts from SEC EDGAR filings
- We use a 75-document subset for manageable benchmark runtime

### Document Characteristics

| Characteristic | Value |
|----------------|-------|
| Average pages | 15-50 |
| Format | Dense legal text, numbered clauses |
| Tables | Minimal |
| Multi-column | Single column only |
| Complexity | High (legal terminology, cross-references) |

### Ground Truth

Uses **PDF text layer extraction** (not OCR):
- PyMuPDF extracts embedded text
- Normalized and cleaned for comparison
- Quality depends on original PDF encoding

### Use Cases

- Testing dense text extraction
- Evaluating numbered section handling
- Legal document parsing accuracy

### Files

- PDFs: `corpus/business/cuad/pdfs/*.pdf`
- Ground truth: `corpus/business/cuad/ground_truth/*.md`
- Metadata: `corpus/business/cuad/metadata/*.yaml`

---

## 3. Business Invoices (100 Documents)

**Purpose**: Table extraction and structured data parsing

### Generation Method

Uses DOCX templates with Jinja2 and python-docx:
1. Template-based invoice generation
2. Randomized vendor/customer data (Faker library)
3. Variable line item counts (1-15 items)
4. LibreOffice DOCX-to-PDF conversion

### Document Variants

| Variant | Count | Features |
|---------|-------|----------|
| Simple | 30 | 1-3 line items, basic layout |
| Standard | 40 | 5-8 line items, tax calculations |
| Complex | 30 | 10+ items, discounts, shipping |

### Key Features Tested

- **Tables**: Line item grids with headers
- **Key-value pairs**: Invoice number, dates, totals
- **Numerical accuracy**: Currency, percentages, calculations
- **Layout**: Headers, footers, company logos

### Expected Performance

- Table-focused parsers (PdfPlumber, PyPDFium2) expected to excel
- Structure-aware parsers (Docling, Marker) for layout preservation
- TEDS metric particularly relevant

### Files

- PDFs: `corpus/business/invoices/pdfs/*.pdf`
- Ground truth: `corpus/business/invoices/ground_truth/*.md`
- Metadata: `corpus/business/invoices/metadata/*.yaml`
- Builder: `builders/generate_invoice_corpus.py`

---

## 4. Legal Templates (108 Documents)

**Purpose**: Hierarchical structure and formal document formatting

### Document Types

| Type | Count | Features |
|------|-------|----------|
| Employment Agreements | 40 | Standard contract structure |
| Non-Disclosure Agreements | 25 | Concise, defined terms |
| Service Contracts | 20 | Scope of work, deliverables |
| Terms of Service | 15 | Long-form, numbered sections |
| Other Legal | 8 | Mixed legal formats |

### Key Features Tested

- **Hierarchical numbering**: 1.1, 1.1.1, 1.1.1.1 patterns
- **Defined terms**: Capitalized term conventions
- **Cross-references**: "See Section 4.2" patterns
- **Complex clauses**: Multi-paragraph subsections
- **Legal formatting**: ALL CAPS headers, indentation

### Expected Performance

- Structure-aware parsers should preserve numbering
- Tree similarity metric particularly relevant
- Element F1 for heading/section detection

### Files

- PDFs: `corpus/business/legal/pdfs/*.pdf`
- Ground truth: `corpus/business/legal/ground_truth/*.md`
- Metadata: `corpus/business/legal/metadata/*.yaml`
- Builder: `builders/build_legal_corpus.py`

---

## 5. HR Documents/Resumes (34 Documents)

**Purpose**: Section extraction and varied formatting handling

### Resume Formats

| Format | Count | Layout |
|--------|-------|--------|
| Chronological | 15 | Traditional reverse-chronological |
| Functional | 10 | Skills-focused organization |
| Combination | 5 | Mixed format |
| Academic CV | 4 | Extended format with publications |

### Industries Represented

Technology, Finance, Healthcare, Education, Manufacturing, Retail, Consulting

### Key Features Tested

- **Section detection**: Contact, Summary, Experience, Education, Skills
- **Lists**: Bullet points for responsibilities and achievements
- **Varied fonts**: Bold, italic, different sizes
- **Two-column layouts**: Some modern resume formats

### Expected Performance

- Layout-aware parsers should handle format variations
- Element F1 for section detection
- Tree similarity for organizational structure

### Files

- PDFs: `corpus/business/hr/pdfs/*.pdf`
- Ground truth: `corpus/business/hr/ground_truth/*.md`
- Metadata: `corpus/business/hr/metadata/*.yaml`
- Builder: `builders/build_hr_corpus.py`

---

## 6. OmniDocBench (252 English Documents)

**Purpose**: Diverse real-world documents including scanned/image-based PDFs

### Source

**OmniDocBench** (CVPR 2025):
- Comprehensive document parsing benchmark
- 1,355 total pages across 9 document types
- We use the 252-document English subset

### Document Types

| Type | Included | Notes |
|------|----------|-------|
| Academic papers | Yes | Two-column, equations |
| Financial reports | Yes | Tables, charts |
| Textbooks | Yes | Mixed content |
| Books | Yes | Various layouts |
| Research reports | Yes | Technical documents |
| Newspapers | Limited | Complex multi-column |
| Slides | Limited | Visual-heavy |
| Handwritten | Excluded | OCR challenge (Chinese) |
| Exam papers | Limited | Mixed content |

### Ground Truth

**Text extraction** from OmniDocBench JSON annotations:
- Original format includes polygon coordinates
- We extract text content as ground truth
- Some information loss vs. full OmniDocBench evaluation

### OCR vs. Text-Based Parsing

OmniDocBench documents are primarily **image-based** (scanned or screenshot):
- Standard text extraction parsers return empty/minimal output
- OCR-capable parsers (Marker, Docling-OCR, Kreuzberg-OCR) required
- Benchmark results reflect OCR quality, not just parsing

### Benchmark Results (OCR Parsers)

| Parser | Edit Similarity | Notes |
|--------|-----------------|-------|
| Marker | ~77% | Best overall |
| Docling (OCR) | ~69% | Good structure preservation |
| Kreuzberg (OCR) | ~51% | Fast but less accurate |
| Unstructured (OCR) | ~45% | Basic OCR |

### Files

- PDFs: `corpus/academic/omnidocbench/pdfs/*.pdf`
- Ground truth: `corpus/academic/omnidocbench/ground_truth/*.md`
- Metadata: `corpus/academic/omnidocbench/metadata/*.yaml`
- Builder: `builders/convert_omnidocbench.py`

---

## Ground Truth Methodology

### DOCX-to-PDF Pipeline (Synthetic + Business)

The DOCX-to-PDF approach provides **perfect ground truth** because:

1. **Source of truth is programmatic**: We create the document structure in code
2. **No parsing required**: Extract directly from DOCX XML internals
3. **Deterministic conversion**: LibreOffice produces consistent PDFs
4. **Full control**: Can test any feature combination

```python
# Example: Ground truth extraction
from docx import Document

doc = Document('template.docx')
for para in doc.paragraphs:
    if para.style.name.startswith('Heading'):
        level = int(para.style.name[-1])
        print(f"{'#' * level} {para.text}")
    else:
        print(para.text)
```

### Text Extraction (CUAD, OmniDocBench)

For documents where we don't control creation:
- Extract embedded text layer (if available)
- Use OCR output from established benchmark
- Quality varies with source document

### Failed Approaches (Lessons Learned)

**HTML-to-Markdown** (FAILED):
- Tried GOV.UK, SEC EDGAR HTML as ground truth
- HTML and PDF are fundamentally different formats
- Navigation elements, version mismatches cause problems
- **Lesson**: Don't use HTML as PDF ground truth

**LaTeX-to-PDF** (Limited success):
- Works for academic papers with LaTeX source
- Complex: Compilation issues, package dependencies
- Limited to equation-heavy documents

---

## Domain Performance Analysis

Parser performance varies significantly by document type. This section shows how the same parser can excel in one domain while struggling in another.

### Why Domain Matters

| Document Type | Key Challenge | Best Parser Traits |
|--------------|---------------|-------------------|
| **Invoices** | Table extraction, number accuracy | Table-aware, structured output |
| **Resumes/HR** | Section detection, varied layouts | Layout analysis, heading detection |
| **Legal** | Dense text, hierarchical numbering | Text fidelity, structure preservation |
| **Multi-column** | Reading order | Layout models, column detection |

### Commercial Parser Performance by Domain

Based on 540+ documents across 4 commercial parsers:

| Domain | Best Performer | Score | Worst Performer | Score | Gap |
|--------|---------------|-------|-----------------|-------|-----|
| **Synthetic** | Azure | 92% | Google | 78% | 14pts |
| **Invoices** | Azure | 89% | AWS | 71% | 18pts |
| **HR/Resumes** | Azure | 88% | AWS | 74% | 14pts |
| **Legal (CUAD)** | AWS | 82% | Databricks | 69% | 13pts |

**Key Insight**: No single parser dominates all domains. Azure leads for structured business documents, while AWS performs better on dense legal text.

### Open Source Parser Performance by Domain

Based on 353+ documents across 13 open source parsers:

| Domain | Top 3 Parsers | Worst Performer |
|--------|--------------|-----------------|
| **Synthetic** | PyPDFium2 (80%), Kreuzberg (79%), PyPDF (78%) | Docling (51%) |
| **Multi-column** | PyMuPDF (93%), Kreuzberg (91%), Extractous (88%) | PdfPlumber (56%) |
| **Tables** | PyPDFium2 (79%), PyPDF (77%), Kreuzberg (76%) | PDFMiner (55%) |
| **Lists** | PdfPlumber (98%), Unstructured (98%), PyMuPDF (96%) | Docling (88%) |

### Domain-Specific Recommendations

**For Invoice Processing:**
1. Azure Document Intelligence (88.6%) - Best overall accuracy
2. Databricks (87.5% format-agnostic) - Good with format normalization
3. AWS Textract (76.5%) - Wide coverage, lower accuracy

**For Resume Parsing:**
1. Azure Document Intelligence - Best section detection
2. Databricks - Good structure with markdown output
3. Any layout-aware parser (Marker, Docling) for complex formats

**For Legal Contracts:**
1. AWS Textract - Best on dense text
2. Azure Document Intelligence - Good structure preservation
3. PyMuPDF - Fast and accurate for text extraction

**For Multi-Column Documents:**
1. PyMuPDF (93%) - Excellent reading order
2. Kreuzberg (91%) - Fast with good accuracy
3. AVOID: PdfPlumber (56%) - Struggles with column detection

---

## Business Document Priority Framework

Based on OCR market research and enterprise automation trends:

### Tier 1: Highest Volume & Value

| Category | Document Types | Market Data |
|----------|----------------|-------------|
| **Finance/AP** | Invoices, Receipts, POs | BFSI = 21.3% of OCR market |
| **HR/Recruiting** | Resumes, Applications | 99% of Fortune 500 use ATS |
| **Legal** | Contracts, NDAs | High corporate volume |
| **KYC/Identity** | ID documents, Utility bills | 65M docs in 2024 (+41% YoY) |

### Tier 2: Industry-Specific

- Healthcare: CMS-1500, UB-04 claims
- Banking: Loan applications, tax forms
- Logistics: Bills of lading, packing slips
- Insurance: Claims forms, policies

### Current Coverage

- Finance: **100 invoices** (complete)
- HR: **34 resumes** (complete)
- Legal: **108 templates** + **75 real contracts** (complete)
- Others: Expansion planned

---

## Usage

### Loading a Specific Corpus

```bash
# Run benchmark on synthetic corpus only
uv run python -m pdf_bench.runner benchmarks/synthetic_31docs.yaml

# Run on CUAD contracts
uv run python -m pdf_bench.runner benchmarks/cuad_75docs.yaml

# Run on all business documents
uv run python -m pdf_bench.runner benchmarks/business_all.yaml
```

### Adding Custom Documents

1. Create directory structure:
   ```
   corpus/custom/
   ├── pdfs/
   │   └── document.pdf
   ├── ground_truth/
   │   └── document.md
   └── metadata/
       └── document.yaml
   ```

2. Create metadata YAML:
   ```yaml
   doc_id: custom_001
   pdf_file: document.pdf
   ground_truth_file: document.md
   domain: custom
   features:
     - tables
     - multi_column
   ```

3. Create benchmark config referencing your corpus

---

## External Benchmarks Reference

PDF-Bench incorporates or references these established benchmarks:

| Benchmark | Focus | Documents | Use in PDF-Bench |
|-----------|-------|-----------|------------------|
| **CUAD** | Legal contracts | 510 | 75-doc subset included |
| **OmniDocBench** | Diverse documents | 1,355 | English subset included |
| **DocLayNet** | Layout analysis | 80,863 | Reference only |
| **PubTabNet** | Table structure | 568K tables | TEDS metric source |
| **FinTabNet** | Financial tables | 112K | Planned expansion |

---

## Quality Assurance

### Validation Checks

All corpora undergo:
1. **Source validation**: Ground truth extracted from structured source
2. **Format verification**: All PDFs readable by target parsers
3. **Metadata completeness**: Required fields present
4. **Sample inspection**: Manual review of representative documents

### Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| OmniDocBench Chinese docs excluded | By design | Focus on English subset |
| Some OmniDocBench images low quality | Accepted | Reflects real-world conditions |
| CUAD multi-page extraction | Known | Per-document scoring |

---

## Future Expansion

### Planned Additions

| Corpus | Documents | Priority | Status |
|--------|-----------|----------|--------|
| Financial Reports | 50+ | High | Planned |
| Government Forms | 50+ | Medium | Planned |
| Healthcare Documents | 30+ | Low | Blocked (HIPAA) |
| Technical Manuals | 30+ | Medium | Planned |

### Target: 1000+ Documents

Current: 800+ documents
Goal: 1000+ documents across 10+ categories

---

## References

### Builder Scripts

- `builders/generate_systematic_corpus.py` - Synthetic corpus
- `builders/download_cuad_corpus.py` - CUAD contracts
- `builders/generate_invoice_corpus.py` - Invoice generation
- `builders/build_legal_corpus.py` - Legal templates
- `builders/build_hr_corpus.py` - Resume generation
- `builders/convert_omnidocbench.py` - OmniDocBench conversion

### Documentation

- [METHODOLOGY.md](METHODOLOGY.md) - Evaluation methodology
- [METRICS.md](METRICS.md) - Metric explanations
- [PARSERS.md](PARSERS.md) - Parser comparison

---

*Last Updated: 2025-11-23*
