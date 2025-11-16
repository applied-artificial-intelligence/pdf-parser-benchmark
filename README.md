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

### Basic Installation

```bash
# Install core package
pip install pdf-bench

# Or with uv
uv pip install pdf-bench
```

### Parser Installation

PDF-Bench supports multiple PDF parsers. Each parser has different dependencies and capabilities.

#### PyMuPDF (Recommended - Baseline)

Fast, simple text extraction. No additional dependencies required.

```bash
pip install pymupdf
```

**Best for**: Quick benchmarking, simple documents, baseline comparisons

#### pdfplumber

Visual layout analysis with excellent table extraction.

```bash
pip install pdfplumber
```

**Best for**: Documents with tables, forms, visual layouts

#### Marker (ML-Based)

High-quality ML-based parsing with GPU acceleration support.

```bash
pip install marker-pdf

# Optional: GPU support (CUDA required)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Best for**: Complex documents, academic papers, production quality

**Note**: First run downloads ML models (~1-2GB). GPU highly recommended for performance.

#### Unstructured

Element-based parsing with extensive document type support.

```bash
pip install unstructured[pdf]

# Additional dependencies for full features
pip install unstructured[local-inference]
```

**Best for**: Document classification, element extraction, enterprise workflows

### Quick Start

```bash
# Check installation
pdfbench version

# Run quick benchmark (2 parsers, 3 documents)
pdfbench run benchmarks/quick_test.yaml

# Generate HTML report
pdfbench report results/quick_test.json
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

## Parser Details

### Comparison Matrix

| Feature | PyMuPDF | pdfplumber | Marker | Unstructured |
|---------|---------|------------|--------|--------------|
| **Speed** | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡ Slow (GPU: ⚡⚡) | ⚡⚡ Medium |
| **Quality** | Basic | Good | Excellent | Very Good |
| **Tables** | ❌ No | ✅✅✅ Excellent | ✅✅ Very Good | ✅✅ Very Good |
| **Math/LaTeX** | ❌ No | ❌ No | ✅✅ Very Good | ✅ Basic |
| **Structure** | ❌ Plain text | ✅ Basic | ✅✅✅ Excellent | ✅✅ Very Good |
| **GPU Support** | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Setup Complexity** | ✅ Simple | ✅ Simple | ⚠️ Complex | ⚠️ Medium |
| **Dependencies** | Minimal | Minimal | Heavy (~2GB models) | Medium |

### PyMuPDF Parser

**Type**: Baseline / Fast text extraction
**Library**: PyMuPDF (fitz)

**Capabilities**:
- Fast text extraction (100+ pages/second)
- Minimal memory footprint
- Reliable and stable
- Built-in caching

**Limitations**:
- No structure preservation (headings, lists, etc.)
- No table extraction
- No math/LaTeX support
- Plain text output only

**Example Usage**:
```python
from pdf_bench.systems.pymupdf import PyMuPDFParser
from pathlib import Path

parser = PyMuPDFParser()
result = parser.parse(
    pdf_path=Path("document.pdf"),
    output_dir=Path("output")
)
print(f"Parsed to: {result}")
```

**Best Use Cases**:
- Quick baseline benchmarks
- Simple text-heavy documents
- Performance-critical applications
- Text search/indexing

### pdfplumber Parser

**Type**: Visual layout analysis
**Library**: pdfplumber

**Capabilities**:
- Excellent table extraction (best in class)
- Visual bounding box analysis
- Column detection
- Form field extraction
- Page layout preservation

**Limitations**:
- No ML-based content understanding
- No math/LaTeX extraction
- Limited handling of complex layouts
- Slower than PyMuPDF

**Example Usage**:
```python
from pdf_bench.systems.pdfplumber_parser import PdfPlumberParser
from pathlib import Path

parser = PdfPlumberParser()
result = parser.parse(
    pdf_path=Path("financial_report.pdf"),
    output_dir=Path("output")
)
```

**Best Use Cases**:
- Financial reports with tables
- Forms and structured documents
- Data extraction from PDFs
- Layout-sensitive documents

### Marker Parser

**Type**: ML-based / High quality
**Library**: marker-pdf (Meta)

**Capabilities**:
- State-of-the-art quality
- Excellent structure preservation
- Math/LaTeX extraction
- Table extraction
- GPU acceleration
- Multi-column support

**Limitations**:
- Large model downloads (~1-2GB first run)
- Slow without GPU (10-30 sec/page)
- High memory usage
- Complex setup

**Setup Requirements**:
```bash
# Basic installation
pip install marker-pdf

# GPU support (recommended)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# First run downloads models to ~/.cache/marker/
```

**Example Usage**:
```python
from pdf_bench.systems.marker import MarkerParser
from pathlib import Path

parser = MarkerParser()
result = parser.parse(
    pdf_path=Path("academic_paper.pdf"),
    output_dir=Path("output")
)
```

**Best Use Cases**:
- Academic papers
- Complex multi-column documents
- Documents with math/equations
- Production-quality extraction

### Unstructured Parser

**Type**: Element-based / Enterprise
**Library**: unstructured

**Capabilities**:
- Element-level extraction
- Document classification
- Multi-format support
- Metadata extraction
- Chunking strategies
- Enterprise features

**Limitations**:
- Complex API
- Many optional dependencies
- Slower than simple parsers
- Overkill for simple documents

**Setup Requirements**:
```bash
# Basic PDF support
pip install unstructured[pdf]

# Full features (local inference)
pip install unstructured[local-inference]

# Optional: Detectron2 for better table extraction
pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git"
```

**Example Usage**:
```python
from pdf_bench.systems.unstructured_parser import UnstructuredParser
from pathlib import Path

parser = UnstructuredParser()
result = parser.parse(
    pdf_path=Path("mixed_content.pdf"),
    output_dir=Path("output")
)
```

**Best Use Cases**:
- Enterprise document pipelines
- Multi-format document processing
- Document classification
- RAG (Retrieval Augmented Generation) pipelines

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pdf_bench --cov-report=html

# Run specific test file
uv run pytest tests/test_systems/test_pymupdf.py -v

# Run parser integration tests
uv run pytest tests/test_systems/test_parser_integration.py -v
```

**Current Status**: 900+ tests passing, good coverage

## License

MIT
