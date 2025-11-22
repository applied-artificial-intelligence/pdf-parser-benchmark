# 273-Document Comprehensive Benchmark Results

**Date**: 2025-11-21
**Benchmark**: 273 documents × 10 parsers = 2,730 runs
**Success Rate**: 2,723/2,730 (99.7%)
**Results File**: `results/full_corpus_353docs.json`

---

## Executive Summary

Expanded benchmark across **four business domains** with 273 documents reveals **domain-specific parser performance varies dramatically**. While earlier 31-doc synthetic tests showed docling leading, the full corpus benchmark tells a more nuanced story:

### Top-Line Results

| Metric | Winner | Score | Note |
|--------|--------|-------|------|
| **Overall Text** | pypdfium2/pypdf | 78.3% | Fast, 100% reliable |
| **Legal Docs** | pypdfium2/pypdf/pymupdf/pdfplumber | 98.8% | Near-perfect on contracts |
| **Invoices** | kreuzberg/pypdfium2/pypdf | 49.9% | All parsers struggle |
| **HR/Resumes** | unstructured | 87.8% | Marginal lead |
| **Table Structure (TEDS)** | pdfplumber | 93.4% | Consistent table winner |

### Key Finding: Domain Matters More Than Parser

**Invoice documents** expose parser limitations - even top performers drop from 98.8% (legal) to 49.9% (invoices), a **49 percentage point gap** within the same parser.

---

## Corpus Composition

| Domain | Documents | Description |
|--------|-----------|-------------|
| Legal (Synthetic) | 108 | Contracts, NDAs, licensing agreements |
| Invoices | 100 | Commercial invoices with tables |
| HR/Resumes | 34 | Professional resumes |
| Synthetic Tests | 31 | Tables, lists, columns, mixed layouts |
| **Total** | 273 | |

*Note: CUAD (75 real SEC contracts) excluded - PDFs available but ground truth requires additional processing*

---

## Complete Parser Rankings

### Overall Performance (Sorted by Edit Similarity)

| Rank | Parser | Edit Sim | chrF++ | CER | TEDS | Success |
|------|--------|----------|--------|-----|------|---------|
| 1 | pypdfium2 | **78.3%** | 90.5 | 21.7% | - | 100% |
| 2 | pypdf | 78.3% | 90.4 | 21.7% | - | 100% |
| 3 | extractous | 77.5% | 90.4 | 22.5% | - | 100% |
| 4 | pymupdf | 77.3% | 90.5 | 22.7% | - | 100% |
| 5 | kreuzberg | 74.9% | 87.5 | 25.1% | - | 100% |
| 6 | pymupdf4llm | 74.7% | 86.1 | 26.8% | 84.8% | 100% |
| 7 | docling | 71.3% | 87.5 | 32.2% | 84.5% | **97.4%** |
| 8 | pdfplumber | 70.4% | 91.6 | 43.0% | **93.4%** | 100% |
| 9 | pdfminer | 68.2% | 89.1 | 31.8% | - | 100% |
| 10 | unstructured | 66.5% | 87.4 | 34.5% | - | 100% |

### Domain-Specific Performance (Edit Similarity %)

| Parser | Synthetic | Legal | Invoices | HR/Resumes | Variance |
|--------|-----------|-------|----------|------------|----------|
| pypdfium2 | 87.5 | **98.8** | 49.9 | 87.3 | 18.5% |
| pypdf | 87.4 | **98.8** | 49.9 | 87.3 | 18.5% |
| extractous | 82.9 | 98.5 | 49.2 | **87.7** | 18.4% |
| pymupdf | 85.4 | **98.8** | 47.7 | 87.3 | 19.2% |
| kreuzberg | **87.5** | 90.3 | **49.9** | 87.3 | **16.7%** |
| pymupdf4llm | 85.0 | 96.9 | 43.5 | 85.2 | 20.1% |
| docling | 87.4 | 86.0 | 46.6 | 85.9 | 16.9% |
| pdfplumber | 67.4 | **98.8** | 33.8 | 87.3 | 24.5% |
| pdfminer | 72.0 | 98.5 | 27.1 | 86.8 | 27.7% |
| unstructured | 73.3 | 98.7 | 21.7 | **87.8** | 29.7% |

---

## Key Insights

### 1. The Invoice Problem

**All parsers struggle with invoices** - the best achieves only 49.9% edit similarity:

```
Legal Contracts:  98.8% (best)
HR/Resumes:       87.8%
Synthetic Tests:  87.5%
Invoices:         49.9% (worst)
```

**Why invoices are hard**:
- Complex table layouts with merged cells
- Mixed content (logos, text, numbers)
- Variable formats across vendors
- Dense information in small spaces

**Implication**: For invoice processing pipelines, **post-processing or specialized models are required**.

### 2. Legal Documents Are "Solved"

Multiple parsers achieve **98.8% accuracy** on legal contracts:
- pypdfium2, pypdf, pymupdf, pdfplumber all tie at 98.8%

This makes sense:
- Legal documents are highly structured
- Consistent formatting across documents
- Minimal visual complexity
- Text-heavy, few tables

**Recommendation**: For legal document extraction, use fastest reliable parser (pypdfium2 or pymupdf).

### 3. Parser Consistency Varies

**Most consistent** (lowest cross-domain variance):
- kreuzberg: 16.7% variance
- docling: 16.9% variance

**Least consistent** (highest cross-domain variance):
- unstructured: 29.7% variance
- pdfminer: 27.7% variance

Consistent parsers maintain performance across document types; inconsistent ones may excel in one domain but fail in others.

### 4. TEDS (Table Structure) Remains Specialized

Only 3 parsers report TEDS scores:
- **pdfplumber: 93.4%** (table extraction specialist)
- pymupdf4llm: 84.8%
- docling: 84.5%

Most text extraction parsers don't attempt table structure recognition.

---

## Metric Correlations

| Metric Pair | Correlation | Interpretation |
|-------------|-------------|----------------|
| edit_similarity ↔ CER | **-0.978** | Near-perfect inverse (expected) |
| edit_similarity ↔ chrF++ | **0.739** | Strong positive |
| edit_similarity ↔ tree_similarity | 0.174 | Weak - text quality ≠ structure |
| edit_similarity ↔ element_f1 | 0.386 | Moderate |
| tree_similarity ↔ TEDS | -0.137 | No relationship |

**Key Finding**: **Text extraction quality (edit_similarity) does not predict structure preservation (tree_similarity)**. Parsers optimized for text accuracy may not preserve document structure.

---

## Metric Distributions

| Metric | Mean | Std Dev | Min | Max |
|--------|------|---------|-----|-----|
| edit_similarity | 0.737 | 0.272 | 0.032 | 0.989 |
| chrF++ | 89.1 | 10.3 | 3.9 | 100.0 |
| CER | 0.282 | 0.304 | 0.011 | 1.166 |
| tree_similarity | 0.352 | 0.134 | -0.286 | 1.000 |

---

## Recommendations by Use Case

### Contract Intelligence / Legal
**Recommended**: pypdfium2, pymupdf
- 98.8% accuracy, 100% reliability, fast
- No need for advanced parsers on this domain

### Invoice Processing
**Recommended**: Custom solution required
- No parser exceeds 50% accuracy
- Consider: OCR + LLM post-processing
- Or: Specialized invoice ML models

### Resume/HR Document Processing
**Recommended**: unstructured or extractous
- 87.8% and 87.7% respectively
- Similar performance across parsers

### RAG/LLM Applications Needing Structure
**Recommended**: docling or pymupdf4llm
- Better structure preservation (61%+ vs 30% average)
- Trade-off: docling has 2.6% failure rate

### Table-Heavy Documents
**Recommended**: pdfplumber
- 93.4% TEDS score
- Purpose-built for table extraction

---

## Comparison with Previous 31-Doc Benchmark

| Metric | 31-Doc (Synthetic) | 273-Doc (Full Corpus) |
|--------|--------------------|-----------------------|
| Top parser | docling (87.4%) | pypdfium2 (78.3%) |
| Average accuracy | 83.2% | 73.7% |
| Docling success rate | 77% | 97.4% |
| Best TEDS | pdfplumber (93.4%) | pdfplumber (93.4%) |

**Why the difference?**
1. 31-doc was synthetic-only (easier)
2. 273-doc includes invoices (harder)
3. Docling improved reliability from 77% to 97.4%
4. Real-world documents expose parser weaknesses

---

## Next Steps

1. **CUAD Integration**: Process 75 real SEC contracts to add ground truth
2. **Invoice Deep Dive**: Analyze what specifically causes invoice extraction failures
3. **OmniDocBench Comparison**: Compare these results against academic benchmark
4. **Commercial Parser Evaluation**: Test Azure Document Intelligence, AWS Textract, Google Document AI
