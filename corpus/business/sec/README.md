# SEC EDGAR Filings Corpus

Production-ready corpus of SEC EDGAR filings for PDF-to-Markdown benchmarking.

## Overview

This corpus contains **20 SEC filings** from major U.S. public companies, selected to provide comprehensive coverage of financial document types and complexity levels for benchmarking PDF-to-Markdown conversion systems.

## Corpus Statistics

- **Total documents**: 20 filings
- **HTML files**: 20 (695.80 KB total)
- **PDF files**: 1 (30.30 MB - JPMorgan Chase)
- **Markdown ground truth**: 20 files (14.78 KB total)
- **License**: Public Domain (US Government Works)
- **Source**: [SEC EDGAR](https://www.sec.gov/edgar)

## Selection Methodology

Documents were selected to provide:

1. **Industry Diversity** (10 industries):
   - Technology (Apple, Microsoft, Amazon, Intel, NVIDIA)
   - Finance (JPMorgan Chase, Goldman Sachs)
   - Automotive (Tesla)
   - Retail (Walmart, Costco)
   - Healthcare/Pharmaceuticals (Johnson & Johnson, Pfizer)
   - Energy (Exxon Mobil)
   - Consumer Goods (Procter & Gamble, Coca-Cola)
   - Aerospace/Manufacturing (Boeing)

2. **Filing Type Variety**:
   - **14 Annual Reports (10-K)**: Full-year financial statements
   - **6 Quarterly Reports (10-Q)**: Interim financial statements

3. **Company Size Range**:
   - Large-cap and mega-cap companies
   - Market leaders in their respective industries

4. **Recent Filings**:
   - 2023-2024 filings
   - Reflects current SEC formatting standards

5. **Table Complexity**:
   - Financial statements (balance sheets, income statements)
   - Segment reporting
   - Revenue breakdowns
   - Geographic data
   - Multi-level headers
   - XBRL-formatted tables

## Directory Structure

```
corpus/business/sec/
├── html/              # HTML filings (20 files, 695.80 KB)
├── pdfs/              # PDF versions (1 file, 30.30 MB)
├── ground_truth/      # Markdown ground truth (20 files, 14.78 KB)
├── metadata/          # Per-document metadata (20 YAML files)
├── corpus_metadata.yaml
├── build_results.json
└── README.md
```

## Document List

### Annual Reports (10-K)

| ID | Company | Industry | Pages | Complexity | Fiscal Year |
|----|---------|----------|-------|------------|-------------|
| sec_001 | Apple Inc. | Technology | 92 | High | 2024 |
| sec_002 | Microsoft Corporation | Technology | 86 | High | 2024 |
| sec_003 | Tesla, Inc. | Automotive | 128 | High | 2023 |
| sec_004 | Amazon.com, Inc. | Technology/Retail | 87 | High | 2023 |
| sec_005 | JPMorgan Chase & Co. | Finance | 312 | High | 2023 |
| sec_006 | Walmart Inc. | Retail | 72 | Medium | 2024 |
| sec_007 | Johnson & Johnson | Healthcare/Pharma | 93 | High | 2023 |
| sec_008 | Exxon Mobil Corporation | Energy | 101 | High | 2023 |
| sec_009 | The Procter & Gamble Company | Consumer Goods | 97 | Medium | 2024 |
| sec_010 | The Boeing Company | Aerospace/Mfg | 118 | High | 2023 |
| sec_011 | The Goldman Sachs Group, Inc. | Finance/Investment Banking | 286 | High | 2023 |
| sec_012 | The Coca-Cola Company | Consumer Goods/Beverages | 87 | Medium | 2023 |
| sec_013 | Intel Corporation | Technology/Semiconductors | 104 | High | 2023 |
| sec_014 | Costco Wholesale Corporation | Retail/Wholesale | 55 | Medium | 2024 |

### Quarterly Reports (10-Q)

| ID | Company | Industry | Pages | Complexity | Quarter |
|----|---------|----------|-------|------------|---------|
| sec_015 | Apple Inc. | Technology | 54 | Medium | Q2 2024 |
| sec_016 | Tesla, Inc. | Automotive | 78 | High | Q3 2024 |
| sec_017 | Amazon.com, Inc. | Technology/Retail | 59 | Medium | Q2 2024 |
| sec_018 | Walmart Inc. | Retail | 48 | Medium | Q1 2025 |
| sec_019 | Pfizer Inc. | Healthcare/Pharma | 94 | High | Q3 2024 |
| sec_020 | NVIDIA Corporation | Technology/Semiconductors | 60 | High | Q2 2025 |

## Ground Truth Generation

Markdown ground truth was generated from HTML filings using:

1. **SEC-specific HTML parsing**:
   - Handles SEC's viewer format
   - Strips navigation and non-content elements
   - Preserves document structure

2. **Financial table extraction**:
   - Three-tier complexity classification (simple/medium/complex)
   - Simple tables → GitHub Flavored Markdown
   - Medium/complex tables → HTML preservation
   - XBRL tag detection and stripping
   - Multi-level header handling
   - Merged cell support (rowspan/colspan)

3. **Currency normalization**:
   - Remove dollar signs: `$1,234` → `1234`
   - Remove commas: `1,234,567` → `1234567`
   - Convert accounting negatives: `($123)` → `-123`

4. **SEC-specific formatting**:
   - Metadata extraction (company, CIK, filing date)
   - Footnote handling (superscript notation)
   - Signature block extraction
   - Table of contents generation

## Known Characteristics

### PDF Availability

**Note**: Only 1 of 20 filings (5%) has an official PDF version available from SEC EDGAR.

- **sec_005** (JPMorgan Chase 10-K): PDF available (30.30 MB)
- **All others**: HTML-only filings (no official PDF from SEC)

This is typical for SEC EDGAR filings in recent years, as the SEC primarily hosts HTML/XBRL formats. For benchmarking purposes:

- Use HTML→Markdown conversion as ground truth
- Test parsers that can handle HTML input
- For PDF-based parsers, you may need to generate PDFs from HTML using tools like wkhtmltopdf or similar

### Table Complexity

SEC filings contain highly complex financial tables:

- **Multi-level headers**: Column headers spanning multiple rows
- **Merged cells**: Extensive use of rowspan/colspan
- **XBRL tags**: Embedded semantic tags for financial data
- **Nested tables**: Tables within table cells
- **Footnote references**: Superscript markers linked to footnotes
- **Currency formatting**: Parentheses for negatives, comma separators

### Limitations

1. **HTML viewer format**: Files are from SEC's HTML viewer, not raw XBRL
2. **Limited PDF coverage**: Only 1 PDF available (5% of corpus)
3. **Currency context loss**: Dollar signs removed during normalization
4. **Table simplification**: Some complex tables preserved as HTML
5. **Metadata extraction**: Basic metadata only (title, CIK)

## Usage

### Validation

Validate corpus integrity:

```bash
python builders/validate_sec_corpus.py
```

Expected output:
```
✓ VALIDATION PASSED - All files present and valid
Total filings:             20
Metadata files:            20/20
HTML files:                20/20
PDF files:                 1/20
Markdown ground truth:     20/20
```

### Rebuilding Corpus

To rebuild or update the corpus:

```bash
# Download HTML, PDFs, and convert to Markdown
python builders/build_sec_corpus.py --skip-existing

# Or download only (no conversion)
python builders/download_sec_corpus.py --skip-existing

# Or convert only (if HTML already downloaded)
python builders/convert_sec_corpus.py \
    --input corpus/business/sec/html/ \
    --output corpus/business/sec/ground_truth/
```

### Integration with PDF-Bench

The corpus integrates seamlessly with PDF-Bench:

```python
from pdf_bench.loader import load_benchmark_config

# Use in benchmark configuration
config = load_benchmark_config("benchmarks/sec_only.yaml")
```

Example benchmark config (`benchmarks/sec_only.yaml`):

```yaml
name: "SEC EDGAR Benchmark"
description: "Benchmark on SEC financial filings"

documents:
  filter:
    category: business
    subcategory: sec_edgar

parsers:
  - pymupdf
  - marker
  - unstructured

metrics:
  - edit_distance
  - teds  # Table accuracy
  - element_f1
```

## Metadata Schema

Each filing has a YAML metadata file in `metadata/<id>.yaml`:

```yaml
id: sec_001
company_name: Apple Inc.
cik: "0000320193"
filing_type: 10-K
filing_date: "2024-11-01"
accession_number: "0000320193-24-000123"
industry: Technology
fiscal_year: 2024
fiscal_year_end: "2024-09-28"
pages: 92
complexity: high
license: Public Domain (US Government Works)
source_url: https://www.sec.gov/Archives/edgar/...
category: business
subcategory: sec_edgar
document_type: 10-K
html_file: html/sec_001.html
html_size: 36482
ground_truth_file: ground_truth/sec_001.md
ground_truth_size: 762
notes: Comprehensive financial tables including revenue by product/geography...
```

## License

All documents are **Public Domain (US Government Works)** under 17 U.S.C. § 105.

- SEC EDGAR filings are official U.S. government publications
- No copyright restrictions
- Free to use for commercial and non-commercial purposes
- Attribution to SEC appreciated but not required

## Source & Attribution

- **Source**: [SEC EDGAR](https://www.sec.gov/edgar)
- **Accessed**: November 2024
- **User-Agent Compliance**: All downloads comply with SEC's User-Agent policy

## Citation

If you use this corpus in research, please cite:

```bibtex
@dataset{sec_edgar_corpus_2024,
  title={SEC EDGAR Filings Corpus for PDF-to-Markdown Benchmarking},
  author={{PDF-Bench Contributors}},
  year={2024},
  publisher={PDF-Bench},
  url={https://github.com/pdf-bench/pdf-bench},
  note={20 SEC EDGAR filings from major U.S. public companies (2023-2024)}
}
```

## Contact

For questions or issues with this corpus:
- Open an issue: [GitHub Issues](https://github.com/pdf-bench/pdf-bench/issues)
- Corpus version: 1.0
- Last updated: November 2024
