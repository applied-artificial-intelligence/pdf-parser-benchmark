# PDF-Bench Methodology

A comprehensive guide to our evaluation methodology, metrics, corpus design, and the reasoning behind our benchmark choices.

## Overview

PDF-Bench evaluates PDF-to-Markdown parsers using multiple complementary metrics across diverse document types. This document explains what we measure, how we measure it, and why we made specific design choices.

---

## 1. Evaluation Metrics

### 1.1 Text Quality Metrics

**Edit Similarity** (Primary metric)
- Normalized Levenshtein distance: `1.0 - (edit_distance / max_length)`
- Range: 0.0 (completely different) to 1.0 (identical)
- Measures character-level accuracy after normalization
- Intuitive interpretation: "88% of characters match"

**ChrF++**
- Character n-gram F-score with word n-gram bonus
- More sophisticated than simple edit distance
- Standard metric in machine translation evaluation
- Range: 0-100

**Character Error Rate (CER)**
- `edit_distance / len(ground_truth)`
- Standard OCR evaluation metric
- Can exceed 1.0 for very poor extractions

### 1.2 Structure Metrics

**Tree Similarity**
- Parses markdown to Abstract Syntax Tree
- Computes tree edit distance on document structure
- Measures heading hierarchy, list nesting, document organization
- Critical for evaluating structural preservation

**Element F1**
- Counts document elements by type (headings, paragraphs, lists, tables, code blocks)
- Computes precision, recall, F1 per element type
- Answers: "Did the parser find all headers? All tables?"

### 1.3 Table Metrics

**TEDS (Tree Edit Distance-based Similarity)**
- Gold standard for table structure evaluation
- Converts tables to tree representation
- Measures structural correctness: rows, columns, cells, spanning
- From PubTabNet benchmark (Zhong et al.)

**Cell Content F1**
- Compares table cell contents
- Precision/recall/F1 on cell data extraction

### 1.4 What We Don't Measure (Yet)

| Aspect | Status | Impact |
|--------|--------|--------|
| Reading order | Not measured | Critical for multi-column |
| Semantic correctness | Not measured | Medium |
| Layout preservation | Not measured | Low priority |

---

## 2. Text Normalization

Before computing metrics, we normalize both ground truth and parser output to focus on substantive differences rather than superficial formatting variations.

### Applied Normalizations

1. **Unicode NFC**: Canonical character composition
2. **Whitespace**:
   - CRLF/CR to LF
   - Tabs to spaces
   - Multiple spaces to single space
   - Trim leading/trailing whitespace per line
   - Collapse multiple blank lines
3. **Quotes**: Smart quotes to straight quotes

### Why Normalization Matters

PDFs may use different Unicode encodings for the same character. Extractors produce different whitespace patterns. Without normalization, parsers are penalized for superficial differences that don't affect downstream use.

---

## 3. Corpus Design

### 3.1 Ground Truth Strategy

We use **DOCX-to-PDF conversion** for synthetic and business corpora:

1. Create documents programmatically with python-docx
2. Extract structure directly from DOCX internals (no parsing needed)
3. Convert DOCX to PDF with LibreOffice headless
4. Result: Perfect ground truth matching semantic structure

**Why this works:**
- Source truth is the programmatic structure, not parser output
- LibreOffice conversion is deterministic
- Can generate unlimited variations
- Full control over complexity and features

### 3.2 Corpus Categories

| Corpus | Documents | Ground Truth | Purpose |
|--------|-----------|--------------|---------|
| **Synthetic** | 31 | Markdown source | Systematic feature testing |
| **CUAD Contracts** | 75 | PDF text layer | Real-world legal documents |
| **Invoices** | 100 | Markdown source | Business document testing |
| **HR/Resumes** | 34 | Markdown source | Varied formatting |
| **Legal Templates** | 108 | Markdown source | Formal structure testing |
| **OmniDocBench** | 252 | Text extraction | Scanned/image documents |

**Total: 800+ documents**

### 3.3 Why Custom Corpora?

**Anticipated question**: "Why generate your own corpus when established benchmarks exist?"

**Answer**: We complement external benchmarks, not replace them.

1. **Perfect ground truth**: We KNOW synthetic corpus is correct (Markdown to PDF to Markdown)
2. **Controlled testing**: Each document tests specific features (tables, lists, columns)
3. **Business relevance**: Generated documents match real use cases
4. **Rapid iteration**: Can generate 100 documents in 60 seconds

**External benchmarks we incorporate:**
- **CUAD**: Real legal contracts from SEC filings
- **OmniDocBench**: Diverse document types including scanned pages

### 3.4 What Failed (Lessons Learned)

**HTML-to-Markdown Ground Truth (FAILED)**

We attempted to use HTML as ground truth for PDF parsing:
- GOV.UK: HTML pages formatted for web, not matching PDF content
- SEC EDGAR: Too many XBRL/XML artifacts

**Why it failed:**
- HTML and PDF are fundamentally different formats
- Version mismatches between HTML and PDF
- Navigation structure in HTML doesn't exist in PDF

**Lesson**: Use native PDF sources or structured formats (DOCX, LaTeX) for ground truth.

---

## 4. Parser Coverage

### 4.1 Open Source Parsers (13)

| Parser | Approach | Key Strength |
|--------|----------|--------------|
| docling | ML layout analysis | Structure preservation |
| marker | Vision models + LLM | Complex layouts |
| pymupdf | Direct PDF parsing | Speed |
| pymupdf4llm | PyMuPDF + LLM formatting | LLM-ready output |
| pdfplumber | Coordinate analysis | Table extraction |
| unstructured | ML classification | Document chunking |
| kreuzberg | Rust + OCR | Speed + accuracy |
| pdfminer | Pure Python | No dependencies |
| pypdf | Pure Python | Simplicity |
| pypdf2 | Legacy support | Compatibility |
| pypdfium2 | Google PDFium | Reliability |
| extractous | Rust bindings | Performance |
| tika | Apache ecosystem | Format support |

### 4.2 Commercial Parsers (3+)

| Parser | Provider | Status |
|--------|----------|--------|
| AWS Textract | Amazon | Tested |
| Azure Document Intelligence | Microsoft | Tested |
| Google Document AI | Google | Tested |
| Databricks | Databricks | Implemented, needs API key |
| Landing.AI | Landing AI | Implemented, needs API key |

---

## 5. Key Findings

### 5.1 Parser Performance Tiers

Based on synthetic corpus evaluation:

**Tier 1: Excellent (80%+)**
- PyPDFium2, Kreuzberg

**Tier 2: Very Good (75-80%)**
- PyPDF, PyPDF2, PyMuPDF, Extractous

**Tier 3: Good (70-75%)**
- Marker, Tika

**Tier 4: Fair (65-70%)**
- PyMuPDF4LLM, PDFMiner, Unstructured

### 5.2 Critical Observations

**Multi-Column Documents**
- Reading order is THE differentiator
- Best: PyMuPDF (89-97%), Kreuzberg (88-93%)
- Worst: PdfPlumber (44-67%)

**Table Extraction**
- All parsers struggle with complex tables (54-78%)
- Merged cells, multi-level headers remain challenging
- PdfPlumber has excellent table API but lower overall accuracy

**OCR Documents**
- Marker leads with ~77% edit similarity
- Docling-OCR achieves ~69%
- Kreuzberg at ~51% (faster but less accurate)

### 5.3 Speed vs Accuracy Trade-offs

| Parser | Speed | Accuracy | Notes |
|--------|-------|----------|-------|
| PyMuPDF | 0-3ms | 78% | Fastest |
| Marker | 6-20s | 73-88% | Depends on LLM |
| Docling | 1-7s | 51-80% | Varies by document |

---

## 6. Metric Interpretation Guide

### What Different Scores Mean

| Score | Interpretation | Typical Issues |
|-------|----------------|----------------|
| 90%+ | Excellent | Minor whitespace/formatting |
| 80-90% | Good | Some structure loss |
| 70-80% | Acceptable | Missing elements, order issues |
| 60-70% | Poor | Significant content loss |
| <60% | Unusable | Fundamental extraction failures |

### Why Scores Differ by Corpus

The same parser can score very differently on different corpora:

- **Synthetic**: Tests specific features, clean PDFs
- **CUAD**: Dense legal text, multi-page, few tables
- **Invoices**: Tables, numbers, structured data
- **OmniDocBench**: Scanned pages, varied quality

**Recommendation**: Test parsers on documents matching your use case.

---

## 7. Reproducing Results

### Running Benchmarks

```bash
# Full corpus benchmark
uv run python -m pdf_bench.runner benchmarks/full_corpus_353docs.yaml

# Specific corpus
uv run python -m pdf_bench.runner benchmarks/cuad_75docs.yaml --parsers docling marker

# View results
cat results/full_corpus_353docs.json | python -m json.tool
```

### Adding Custom Documents

1. Place PDFs in `corpus/custom/pdfs/`
2. Place ground truth markdown in `corpus/custom/ground_truth/`
3. Create metadata YAML files in `corpus/custom/metadata/`
4. Create benchmark config referencing your corpus
5. Run benchmark

---

## 8. References

### Metrics

- **TEDS**: Zhong et al., "Image-based Table Recognition: Data, Model, and Evaluation" (PubTabNet, 2019)
- **ChrF++**: Popovic, "chrF: character n-gram F-score for automatic MT evaluation" (2015)
- **Edit Distance**: Standard Levenshtein distance

### Benchmarks

- **OmniDocBench**: Comprehensive document parsing benchmark
- **DocLayNet**: IBM document layout analysis (80K pages)
- **PubTabNet**: Table structure recognition (568K tables)
- **CUAD**: Contract Understanding Atticus Dataset
- **FinTabNet**: Financial table extraction (112K tables)

### Academic Papers

- The READOC benchmark for PDF-to-Markdown evaluation
- DocParser: Hierarchical structure extraction
- HRDoc: Multi-page hierarchy benchmark

---

## 9. Limitations and Future Work

### Current Limitations

1. **Reading order**: Not explicitly measured for multi-column documents
2. **Semantic correctness**: Number/date extraction not separately evaluated
3. **Layout preservation**: Visual formatting not measured
4. **Statistical significance**: Confidence intervals not reported

### Planned Improvements

1. Reading order metric for multi-column documents
2. Expanded corpus (financial statements, government forms)
3. Integration of additional external benchmarks
4. Per-metric confidence intervals

---

*This methodology document is versioned with the benchmark. Last updated: 2025-11-23*
