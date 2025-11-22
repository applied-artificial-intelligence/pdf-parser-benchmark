# Synthetic Corpus - Systematic Expansion

## Overview
Expanded corpus with 31 documents (904KB) testing specific parser challenges.

## Document Categories

### Original Pandoc-Generated (01-08)
- 01_basic.pdf - Simple text and headings
- 02_lists.pdf - Various list types  
- 03_tables.pdf - Table structures
- 04_math.pdf - Mathematical notation (FAILED - LaTeX issues)
- 05_complex.pdf - Mixed content
- 06_docx_simple.pdf - DOCX-generated simple report
- 07_docx_tables.pdf - DOCX table-heavy document
- 08_docx_multicolumn.pdf - DOCX multi-column layout

### Tables Category (09-14) - 6 documents
Tests table extraction progressively from simple to complex:
- 09: Simple 3x4 grid
- 10: Merged columns (colspan)
- 11: Wide table (7 columns)
- 12: Multiple tables in one document
- 13: Complex multi-level headers
- 14: Financial statement with formatting

### Lists Category (15-20) - 6 documents
Tests list detection and nesting:
- 15: Simple bullets
- 16: Numbered list
- 17: Two-level nesting
- 18: Three-level nesting
- 19: Mixed numbered/bullets
- 20: Lists with paragraphs

### Multi-column Category (21-26) - 6 documents
Tests reading order challenges:
- 21: Two-column text
- 22: Three-column layout
- 23: Mixed full-width and columns
- 24: Newsletter style
- 25: Academic paper format
- 26: Marketing brochure

### Mixed Content (27-32) - 6 documents
Real-world complexity with tables + lists + headings:
- 27: Business report
- 28: Technical documentation
- 29: Policy document
- 30: Meeting minutes
- 31: Research summary
- 32: Comprehensive annual report

## Testing Strategy

Each category tests specific parser capabilities:

**Tables**: Structure detection, merged cells, wide tables, boundaries
**Lists**: Item detection, nesting levels, mixed types
**Multi-column**: Reading order (down then across), section transitions
**Mixed**: Real-world complexity, content separation

## Ground Truth

All documents have perfect ground truth because:
1. Documents created programmatically with python-docx
2. Structure extracted from DOCX internals
3. LibreOffice conversion ensures reproducibility
4. Markdown ground truth matches semantic structure

## Benchmark Metrics

Run `python run_benchmark.py corpus/synthetic` to test:
- PyMuPDF (text-based)
- PDFPlumber (text-based)  
- Marker (GPU vision)
- Unstructured (OCR + layout)

Expected results:
- **Simple docs**: >95% similarity
- **Tables**: 70-90% (tests structure)
- **Lists**: 80-95% (tests nesting)
- **Multi-column**: 50-80% (hardest - reading order)
- **Mixed**: 70-90% (real-world)

## Usage

```bash
# Generate documents
uv run python builders/generate_systematic_corpus.py

# Convert to PDF
uv run python builders/convert_systematic_to_pdf.py

# Run benchmark
python run_benchmark.py corpus/synthetic
```
