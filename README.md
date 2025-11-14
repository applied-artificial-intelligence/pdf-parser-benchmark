# PDF-Bench

Open-source benchmarking suite for PDF-to-Markdown conversion.

## Overview

PDF-Bench provides a comprehensive framework for evaluating the quality of PDF-to-Markdown conversion tools and services. It includes:

- **Synthetic Corpus**: 8 validated test documents with ground truth (Phase 2 ✅)
- **Baseline Parser**: PyMuPDF-based reference implementation
- **Metrics Framework**: Edit distance, structural analysis, table/math evaluation (in development)
- **Caching System**: Hash-based result caching for performance
- **Metadata Schema**: Comprehensive document metadata in YAML format

**Status**: MVP in development (Phase 2/11 complete)

## Synthetic Corpus

The synthetic corpus contains 8 validated documents designed to test various PDF parsing capabilities:

### Documents

| ID | Name | Type | Pages | Features | Size |
|----|------|------|-------|----------|------|
| 01 | basic | Pandoc | ~3-4 | Headings, paragraphs, basic formatting | 109KB |
| 02 | lists | Pandoc | ~3-4 | Ordered, unordered, nested lists | 123KB |
| 03 | tables | Pandoc | ~5-6 | 13 labeled tables (GFM + HTML) | 131KB |
| 04 | math | Pandoc | ~5-6 | 25+ LaTeX equations | 182KB |
| 05 | complex | Pandoc | ~8-10 | All Pandoc features combined | 257KB |
| 06 | docx_simple | DOCX | 10 | Business report, 14 variables | 39KB |
| 07 | docx_tables | DOCX | 7 | Financial tables (5 labeled) | 83KB |
| 08 | docx_multicolumn | DOCX | 7 | Multi-column academic layout | 65KB |

**Total**: 8 documents, ~50-60 pages, 989KB

All documents include:
- PDF file (generated from Markdown or DOCX)
- Ground truth Markdown file
- Metadata YAML file with hashes
- Validation passing (100% pass rate)

### Corpus Builder Usage

#### Regenerate Pandoc Documents (01-05)

```bash
# Build all Pandoc documents from Markdown sources
cd builders
uv run python build_synthetic.py
```

Requirements: pandoc 2.x+, XeLaTeX, Eisvogel template

#### Regenerate DOCX Documents (06-08)

```bash
# Step 1: Create DOCX templates
uv run python builders/create_docx_templates.py

# Step 2: Generate corpus from templates
uv run python builders/generate_docx_corpus.py
```

Requirements: python-docx-template, LibreOffice

#### Validate Corpus

```bash
# Run comprehensive validation
uv run python scripts/validate_corpus.py

# Checks: YAML schema, file existence, hashes, Markdown syntax, PDF parseability
# Report saved to: TASK-017-validation-report.md
```

### Known Limitations

**Current Corpus**:
- Small sample size (8 documents) - not statistically significant for production
- No images/figures - text-only documents
- No footnotes/endnotes
- English only
- Born-digital PDFs only (no scanned documents)

**Planned Expansion** (Phases 6-8):
- GOV.UK corpus: 20-30 real-world documents
- SEC EDGAR corpus: 10-20 financial filings
- arXiv corpus: 30-50 academic papers with images/math
- **Target**: ~100 documents for production benchmarks

See `TASK-018-manual-review.md` for detailed quality assessment.

## Installation

```bash
pip install pdf-bench
```

## Quick Start

```bash
pdfbench version
```

## Development

This project uses `uv` for dependency management.

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy .
```

### Project Structure

```
pdf-bench/
├── pdf_bench/           # Main package
│   ├── systems/         # Parser implementations (BaseParser, PyMuPDFParser)
│   ├── metrics/         # Evaluation metrics (edit_distance)
│   └── utils/           # Utilities (caching, metadata, normalization)
├── corpus/              # Document corpora
│   ├── synthetic/       # 8 synthetic documents (Phase 2 ✅)
│   ├── academic/        # arXiv papers (Phase 8)
│   └── business/        # GOV.UK, SEC filings (Phases 6-7)
├── builders/            # Corpus generation scripts
│   ├── build_synthetic.py      # Pandoc MD→PDF pipeline
│   ├── build_docx.py           # DOCX→PDF pipeline
│   ├── create_docx_templates.py
│   └── generate_docx_corpus.py
├── scripts/             # Utility scripts
│   └── validate_corpus.py      # Corpus validation
└── tests/               # Test suite (294 tests, 92% coverage)
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pdf_bench --cov-report=html

# Run specific test file
uv run pytest tests/test_systems/test_pymupdf.py -v
```

**Current Status**: 294 tests passing, 92% coverage

## License

MIT
