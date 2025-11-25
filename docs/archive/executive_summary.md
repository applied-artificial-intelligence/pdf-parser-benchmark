# PDF Parser Benchmark: Executive Summary

## Overview

We evaluated **10 open-source PDF parsers** across **273 business documents** representing contract intelligence, invoice processing, and HR document workflows.

**Total benchmark runs**: 2,730
**Success rate**: 99.7%

---

## Key Findings

### 1. Domain Determines Performance

Parser effectiveness varies dramatically by document type:

| Document Type | Best Accuracy | Implication |
|---------------|---------------|-------------|
| **Legal Contracts** | 98.8% | Multiple parsers work well |
| **HR Documents** | 87.8% | Good performance across tools |
| **Invoices** | 49.9% | All parsers underperform |

**Business Impact**: Parser selection should be document-type specific, not based on generic benchmarks.

### 2. Invoice Processing Requires Specialized Solutions

No open-source parser exceeds 50% accuracy on invoices. This is an industry-wide limitation affecting all document processing pipelines that handle vendor invoices.

**Recommendation**: For invoice processing, evaluate specialized ML models (LayoutLM, Donut) or commercial APIs rather than generic PDF parsers.

### 3. Text Accuracy Does Not Equal Structure Quality

Parsers achieve 74% text extraction accuracy but only 35% structure preservation—a 50% gap.

**Business Impact**: For RAG systems, semantic search, or document classification that depends on document hierarchy, text accuracy benchmarks are insufficient predictors of quality.

---

## Recommendations by Use Case

| Use Case | Recommended Parser | Expected Accuracy |
|----------|-------------------|-------------------|
| Contract Intelligence | pypdfium2, pymupdf | 98.8% |
| Invoice Processing | Custom solution | <50% with generic parsers |
| Resume Processing | unstructured | 87.8% |
| Table Extraction | pdfplumber | 93.4% (TEDS) |
| RAG Applications | docling | 61% structure preservation |

---

## Top Performers

### Best Overall Text Accuracy
1. **pypdfium2** - 78.3% (100% reliability)
2. **pypdf** - 78.3% (100% reliability)
3. **extractous** - 77.5%

### Best Table Extraction
1. **pdfplumber** - 93.4% TEDS score

### Best Structure Preservation
1. **docling** - 61.2% tree similarity
2. **pymupdf4llm** - 60.8%

---

## Bottom Line

- **Contract intelligence**: Solved problem—use fast, reliable parsers (pypdfium2)
- **Invoice processing**: Requires custom solutions beyond generic PDF parsing
- **Parser selection**: Test on representative samples of your actual documents

---

**Full Technical Report**: [docs/blog/01_comprehensive_evaluation.md](blog/01_comprehensive_evaluation.md)
**Methodology**: 273 documents, 6 metrics, ground truth from source conversions
**Last Updated**: November 2025
