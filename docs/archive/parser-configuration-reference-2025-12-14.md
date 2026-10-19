# Historical parser configuration survey (December 14, 2025)

Archived on October 14, 2026 from
`/home/stefan/projects/pdf-bench/docs/PARSER_CONFIGURATION_REFERENCE.md`.
Original SHA-256: `d0c32e8688431c5a2ed262f399edaa2f7302c7357c8d383b2e9361c13f047b9f`.
The original survey follows unchanged below this notice.

This is historical research, not the current PDF-Bench/PDFsmith configuration
contract. Model lists, prices, limits, performance estimates and capabilities have
not been reverified. Listed upstream API options are not necessarily accepted by
the installed backend constructors. In the October 14 checkout, the pypdf and
pdfplumber PDFsmith constructors accept no configuration arguments; pdfplumber's
backend extracts tables as well as text. Use `pdf_bench/loader.py` and the actual
installed PDFsmith backend source to establish supported benchmark options.
The presets and package commands below are retained as historical examples.

# PDFSmith Parser Configuration Reference

**Purpose**: Complete configuration reference for all 19 PDF parsing backends.
**Last Updated**: 2025-12-14
**Review Cadence**: Check each parser's changelog monthly for breaking changes.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Open Source Parsers (11)](#open-source-parsers)
3. [Commercial Document APIs (5)](#commercial-document-apis)
4. [LLM Vision APIs (3)](#llm-vision-apis)
5. [Benchmark Configuration Presets](#benchmark-configuration-presets)
6. [Version Tracking](#version-tracking)

---

## Quick Reference

### All 19 Backends

| # | Backend | Type | Docs URL | Image Input | OCR | JSON Output |
|---|---------|------|----------|-------------|-----|-------------|
| 1 | docling | Open Source | https://docs.docling.ai | ✓ | ✓ | ✓ |
| 2 | marker | Open Source | https://github.com/VikParuchuri/marker | ✗ | ✓ | ✓ |
| 3 | pymupdf4llm | Open Source | https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/ | ✗ | ✗ | ✗ |
| 4 | kreuzberg | Open Source | https://github.com/Getso/kreuzberg | ✓ | ✓ | ✓ |
| 5 | unstructured | Open Source | https://docs.unstructured.io | ✗ | ✓ | ✓ |
| 6 | pdfplumber | Open Source | https://github.com/jsvine/pdfplumber | ✗ | ✗ | ✓ |
| 7 | pymupdf | Open Source | https://pymupdf.readthedocs.io | ✗ | ✓ | ✓ |
| 8 | pypdf | Open Source | https://pypdf.readthedocs.io | ✗ | ✗ | ✗ |
| 9 | pdfminer | Open Source | https://pdfminersix.readthedocs.io | ✗ | ✗ | ✗ |
| 10 | pypdfium2 | Open Source | https://pypdfium2.readthedocs.io | ✗ | ✗ | ✗ |
| 11 | extractous | Open Source | https://extractous.com | ✓ | ✓ | ✓ |
| 12 | aws_textract | Commercial | https://docs.aws.amazon.com/textract/ | ✓ | ✓ | ✓ |
| 13 | azure_di | Commercial | https://learn.microsoft.com/azure/ai-services/document-intelligence/ | ✓ | ✓ | ✓ |
| 14 | google_docai | Commercial | https://cloud.google.com/document-ai/docs | ✓ | ✓ | ✓ |
| 15 | databricks | Commercial | https://docs.databricks.com/sql/language-manual/functions/ai_parse_document | ✓ | ✓ | ✓ |
| 16 | llamaparse | Commercial | https://docs.llamaindex.ai/llamaparse/ | ✓ | ✓ | ✓ |
| 17 | openai | LLM Vision | https://platform.openai.com/docs/guides/vision | ✓ | ✓ | ✓ |
| 18 | anthropic | LLM Vision | https://docs.anthropic.com/claude/docs/vision | ✓ | ✓ | ✓ |
| 19 | gemini | LLM Vision | https://ai.google.dev/gemini-api/docs | ✓ | ✓ | ✓ |

---

## Open Source Parsers

### 1. Docling (IBM)

**Package**: `docling`
**Weight**: Heavy (~8-16GB RAM)
**Best For**: Highest quality extraction, academic documents

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `do_ocr` | bool | False | 20-50% accuracy on scanned; 6-10x slower |
| `do_table_structure` | bool | True | Critical for TEDS scores |
| `num_threads` | int | 4 | Memory/parallelization tradeoff |
| `device` | str | "auto" | "auto", "cpu", "cuda", "mps" |
| `ocr_languages` | list | ["eng"] | OCR language codes |
| `generate_page_images` | bool | False | Extract page images |
| `generate_picture_images` | bool | False | Extract embedded pictures |
| `images_scale` | float | 1.0 | Image scaling factor |

#### Output Formats
```python
result.document.export_to_markdown()
result.document.export_to_html()
result.document.export_to_json()
result.document.export_to_doctags()
```

#### Environment Variables
```bash
DOCLING_OCR=true
DOCLING_NUM_THREADS=2
DOCLING_DEVICE=cuda
OMP_NUM_THREADS=2
MKL_NUM_THREADS=2
```

#### Config File
Location: `.pdfsmith/docling.yaml` or `~/.config/pdfsmith/docling.yaml`
```yaml
do_ocr: false
do_table_structure: true
num_threads: 2
device: auto
```

---

### 2. Marker

**Package**: `marker-pdf`
**Weight**: Heavy (GPU recommended)
**Best For**: Academic papers, LaTeX-heavy content

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `force_ocr` | bool | False | Required for scanned docs |
| `use_llm` | bool | False | +5-10% text, +15-20% structure; 80-90% slower |
| `output_format` | str | "markdown" | "markdown", "json", "html", "chunks" |
| `page_range` | str | None | "1-5,10" format |
| `workers` | int | auto | Parallel workers |
| `ocr_engine` | str | "surya" | "surya" or "tesseract" |
| `extract_images` | bool | True | Image extraction |
| `languages` | list | ["en"] | Language detection |
| `batch_size` | int | 4 | Batch processing |

#### CLI Flags
```bash
marker_single input.pdf \
  --page_range "1-5,10" \
  --force_ocr \
  --use_llm \
  --output_format json \
  --workers 4
```

#### Output Formats
- `markdown`: Plain markdown string
- `json`: Tree structure with coordinates, hierarchy
- `html`: HTML markup
- `chunks`: Page-level chunks for RAG

#### Environment Variables
```bash
MARKER_USE_LLM=false
MARKER_BATCH_SIZE=2
MARKER_FORCE_OCR=true
```

---

### 3. PyMuPDF4LLM

**Package**: `pymupdf4llm`
**Weight**: Medium
**Best For**: Fast, deterministic, LLM-optimized output

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `pages` | list[int] | None | Zero-indexed page selection |
| `page_chunks` | bool | False | Return list of page dicts |
| `write_images` | bool | False | Extract images to PNG; 20-40% slower |
| `image_path` | str | None | Image output directory |

#### Usage
```python
import pymupdf4llm

# Single string
markdown = pymupdf4llm.to_markdown("input.pdf")

# Per-page chunks
pages = pymupdf4llm.to_markdown("input.pdf", page_chunks=True)
```

#### Limitations
- No OCR support
- No table extraction
- Markdown output only

---

### 4. Kreuzberg

**Package**: `kreuzberg`
**Weight**: Medium (Rust-based)
**Best For**: Fast OCR, multilingual, multiple OCR backends

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `force_ocr` | bool | False | Force OCR on text PDFs |
| `extract_tables` | bool | True | Table extraction |
| `extract_images` | bool | False | Image extraction |
| `ocr_backend` | str | "tesseract" | "tesseract", "easyocr", "paddleocr" |
| `target_dpi` | int | 150 | OCR resolution; higher = better/slower |
| `enable_quality_processing` | bool | False | Post-processing |

#### OCR Backend Configs
```python
from kreuzberg import ExtractionConfig, TesseractConfig, EasyOCRConfig

# Tesseract
config = ExtractionConfig(
    ocr_backend="tesseract",
    ocr_config=TesseractConfig(language="eng+deu")
)

# EasyOCR
config = ExtractionConfig(
    ocr_backend="easyocr",
    ocr_config=EasyOCRConfig(languages=["en", "de"])
)
```

#### Image Input Support
```python
result = kreuzberg.extract_file_sync("scan.png")  # Direct image support
```

---

### 5. Unstructured

**Package**: `unstructured`
**Weight**: Medium
**Best For**: Document processing pipelines, element-based extraction

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `strategy` | str | "auto" | "auto", "fast", "hi_res", "ocr_only" |
| `ocr_languages` | list | ["eng"] | Tesseract language codes |
| `include_page_breaks` | bool | True | Page boundary markers |
| `infer_table_structure` | bool | True | Table detection |
| `extract_images_in_pdf` | bool | False | Extract images |
| `extract_image_block_types` | list | [] | ["Image", "Table", "Figure"] |

#### Strategy Characteristics
- `"fast"`: No OCR, <1GB RAM, 1-3s/doc
- `"hi_res"`: Full OCR, table detection, 10-30s/doc
- `"ocr_only"`: Force OCR on all pages
- `"auto"`: Automatic selection

#### Output
Returns list of Element objects with categories:
- Title, Header, Paragraph, Text
- Table (with structure)
- List, ListItem
- Image, Figure, Caption

---

### 6. pdfplumber

**Package**: `pdfplumber`
**Weight**: Light
**Best For**: Tables, low-level PDF object access

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `layout` | bool | False | Preserve spatial layout |
| `x_tolerance` | int | 3 | Horizontal grouping |
| `y_tolerance` | int | 3 | Vertical grouping |

#### Table Extraction Settings
```python
tables = page.extract_tables(table_settings={
    "vertical_strategy": "lines",      # or "text", "explicit"
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "edge_min_length": 3,
    "min_words_vertical": 3,
    "min_words_horizontal": 1,
})
```

#### Output Formats
- Text (plain or layout-preserved)
- CSV (via CLI)
- JSON (via CLI)
- Table data structures

---

### 7. PyMuPDF (fitz)

**Package**: `pymupdf`
**Weight**: Light
**Best For**: Fast, comprehensive, many output formats

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `output_format` | str | "text" | See formats below |
| `clip` | rect | None | Restrict to region |
| `flags` | int | varies | Text extraction flags |
| `sort` | bool | False | Sort by position |

#### Output Formats
```python
page.get_text("text")      # Plain text
page.get_text("blocks")    # Block-level
page.get_text("words")     # Word-level
page.get_text("dict")      # Full structure
page.get_text("json")      # JSON string
page.get_text("html")      # HTML
page.get_text("markdown")  # Markdown
page.get_text("xml")       # XML
```

#### OCR Support
```python
textpage = page.get_textpage_ocr(
    language="eng",
    dpi=300,
    full=True,
)
```

#### Table Extraction
```python
tables = page.find_tables(
    horizontal_strategy="lines",
    vertical_strategy="lines",
    snap_tolerance=3,
)
```

---

### 8. pypdf

**Package**: `pypdf`
**Weight**: Light (pure Python)
**Best For**: Simple extraction, lightweight

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `extraction_mode` | str | "plain" | "plain" or "layout" |
| `layout_mode_space_vertically` | bool | True | Vertical spacing |
| `layout_mode_scale_weight` | float | 1.0 | Horizontal scale |
| `orientations` | tuple | (0,) | Text orientations |

#### Limitations
- No OCR
- No table extraction
- Text output only

---

### 9. pdfminer.six

**Package**: `pdfminer.six`
**Weight**: Light
**Best For**: Layout analysis, CJK support

#### Configuration Options (LAParams)

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `line_overlap` | float | 0.5 | Same-line threshold |
| `char_margin` | float | 2.0 | Character spacing |
| `word_margin` | float | 0.1 | Word spacing |
| `line_margin` | float | 0.5 | Paragraph grouping |
| `boxes_flow` | float/None | 0.5 | Text ordering; None = disable |
| `detect_vertical` | bool | False | Vertical text (CJK) |
| `all_texts` | bool | False | Include figure text |

#### Output Formats
- Text
- HTML
- XML
- hOCR

---

### 10. pypdfium2

**Package**: `pypdfium2`
**Weight**: Light
**Best For**: Chrome's PDF engine, fast extraction

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| strategy | str | "bounded" | "bounded" (Unicode) or "range" (UCS-2) |

#### Text Extraction
```python
textpage = page.get_textpage()
text = textpage.get_text_bounded()  # Full Unicode
text = textpage.get_text_range()    # Faster, UCS-2 only
```

#### Limitations
- No OCR
- No table detection
- Minimal configuration

---

### 11. Extractous

**Package**: `extractous`
**Weight**: Medium (Rust-based)
**Best For**: Speed (~25x faster), built-in OCR

#### Configuration Options

| Option | Type | Default | Impact |
|--------|------|---------|--------|
| `language` | str | "eng" | OCR language (ISO 639-2) |
| `timeout` | int | 30 | OCR timeout seconds |

#### Usage
```python
from extractous import Extractor, TesseractOcrConfig

extractor = Extractor()
extractor.set_ocr_config(
    TesseractOcrConfig().set_language("deu")
)
text, metadata = extractor.extract_file_to_string("input.pdf")
```

#### Image Input Support
```python
text, metadata = extractor.extract_file_to_string("scan.png")
```

---

## Commercial Document APIs

### 12. AWS Textract

**Documentation**: https://docs.aws.amazon.com/textract/

#### API Parameters

| Parameter | Type | Values |
|-----------|------|--------|
| `FeatureTypes` | list | `TABLES`, `FORMS`, `QUERIES`, `SIGNATURES`, `LAYOUT` |
| `QueriesConfig` | list | Query objects with `Text`, `Alias`, `Pages` |
| `Pages` | str | `"1-3"`, `"1-1"`, `"4-*"` |

#### Limits
- Sync: 10 MB, 1 page (PDF/TIFF)
- Async: 500 MB, 3,000 pages

#### Pricing
- Text detection: $0.065/page (first 1M)
- Form/Table: $0.065/page additional per feature

---

### 13. Azure Document Intelligence

**Documentation**: https://learn.microsoft.com/azure/ai-services/document-intelligence/

#### API Parameters

| Parameter | Type | Values |
|-----------|------|--------|
| `pages` | str | "1,3,5-10" |
| `locale` | str | "en-US" |
| `features` | list | `keyValuePairs`, `queryFields`, `ocrHighResolution`, `formulas` |
| `outputContentFormat` | str | Format specification |
| `output` | str | "pdf" (searchable) or JSON |

#### Add-On Features
- Formula extraction (LaTeX)
- Font extraction
- Barcode extraction
- Query fields (max 20)

#### Limits
- Free: 500 pages/month, 2 pages/request
- Paid: 2,000 pages/file

---

### 14. Google Document AI

**Documentation**: https://cloud.google.com/document-ai/docs

#### API Parameters

| Parameter | Type | Values |
|-----------|------|--------|
| `languageHints` | list | BCP-47 codes, e.g., `"en-t-i0-handwrit"` |
| `processorName` | str | Processor resource path |

#### Processor Types
- OCR (200+ languages)
- Form Parser
- Layout Parser
- Invoice, Bank Statement, W2, etc.

#### Limits
- Sync: 15 pages
- Batch: 200 pages/document

---

### 15. Databricks Document Understanding

**Documentation**: https://docs.databricks.com/sql/language-manual/functions/ai_parse_document

#### Function Parameters

```sql
ai_parse_document(
  content BINARY,
  version => '2.0',
  imageOutputPath => '/path/in/volume',
  descriptionElementTypes => '*'  -- '', 'figure', or '*'
)
```

#### Output
- VARIANT JSON with pages, elements, metadata
- Tables as HTML (v2.0)
- Element types: Text, Tables, Figures, Headers, Footers, etc.

---

### 16. LlamaParse

**Documentation**: https://docs.llamaindex.ai/llamaparse/

#### Tier System

| Tier | Credits/Page | Best For |
|------|--------------|----------|
| `fast` | ~1 | Simple docs |
| `cost_effective` | 3 | Mixed content |
| `agentic` | 10 | Complex docs |
| `agentic_plus` | 90 | Maximum accuracy |

#### Configuration (V2 API)

```json
{
  "parse_options": {
    "tier": "agentic_plus",
    "version": "latest"
  },
  "output_options": {
    "markdown_table_multiline_separator": " § ",
    "page_separator": "\n---\n",
    "tables_as_spreadsheet": {"enable": true},
    "extract_layout": {"enable": true}
  },
  "page_ranges": ["1-5", "10-15"],
  "crop_box": {"top": 0.0, "bottom": 1.0, "left": 0.0, "right": 1.0}
}
```

#### Output Formats
- Markdown
- JSON
- XLSX
- PDF

---

## LLM Vision APIs

### 17. OpenAI Vision

**Documentation**: https://platform.openai.com/docs/guides/vision

#### Models
- GPT-4o, GPT-4o-mini
- GPT-4.1, GPT-4.1-mini
- o4-mini (reasoning)

#### Image Parameters

| Parameter | Values | Impact |
|-----------|--------|--------|
| `detail` | `low`, `high`, `auto` | Resolution/tokens |

- `low`: 512×512, 85 tokens
- `high`: Full res + tiles, 170 tokens/tile

#### Generation Parameters

| Parameter | Range | Recommendation |
|-----------|-------|----------------|
| `temperature` | 0-2 | 0.0 for extraction |
| `max_tokens` | int | **Must set** for vision |
| `top_p` | 0-1 | Alternative to temperature |

#### Structured Output
```json
{
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "ExtractedData",
      "schema": {...},
      "strict": true
    }
  }
}
```

---

### 18. Anthropic Claude Vision

**Documentation**: https://docs.anthropic.com/claude/docs/vision

#### Models
- Claude 3.5 Sonnet (best vision)
- Claude 3.5 Haiku
- Claude Opus 4.1

#### Image Parameters

| Parameter | Values | Impact |
|-----------|--------|--------|
| `source.type` | `base64`, `url` | Input method |
| `cache_control.ttl` | `5m`, `1h` | Caching |

#### Limits
- 100 images per request
- 32 MB total, 8000×8000 px per image

#### Structured Output (Beta)
```json
{
  "output_format": {
    "type": "json",
    "json_schema": {...}
  }
}
```
Header: `anthropic-beta: structured-outputs-2025-11-13`

---

### 19. Google Gemini Vision

**Documentation**: https://ai.google.dev/gemini-api/docs

#### Models
- Gemini 3 Pro
- Gemini 2.5 Flash
- Gemini 2.5 Pro

#### Image Parameters

| Parameter | Values | Tokens |
|-----------|--------|--------|
| `media_resolution` | `low` | 280 |
| | `medium` | 560 |
| | `high` | 1120 |
| | `ultra_high` | ~1792+ |

#### PDF Support
- Up to 1000 combined pages per request
- Upload via Files API with status polling

#### Structured Output
```json
{
  "generation_config": {
    "response_mime_type": "application/json",
    "response_schema": {...}
  }
}
```

---

## Benchmark Configuration Presets

### Fast Preset
```yaml
docling:
  do_ocr: false
  do_table_structure: false
marker:
  force_ocr: false
  use_llm: false
unstructured:
  strategy: fast
pdfplumber:
  layout: false
pdfminer:
  boxes_flow: null
pymupdf:
  output_format: text
```

### Balanced Preset (Default)
```yaml
docling:
  do_ocr: false
  do_table_structure: true
marker:
  force_ocr: false
  use_llm: false
unstructured:
  strategy: auto
  infer_table_structure: true
pdfplumber:
  layout: false
pdfminer:
  boxes_flow: 0.5
```

### Best Quality Preset
```yaml
docling:
  do_ocr: true
  do_table_structure: true
  device: cuda
marker:
  force_ocr: true
  use_llm: true
  output_format: json
unstructured:
  strategy: hi_res
  infer_table_structure: true
pdfplumber:
  layout: true
pymupdf:
  use_ocr: true
  ocr_dpi: 300
```

### OCR Benchmark Preset
```yaml
docling:
  do_ocr: true
marker:
  force_ocr: true
kreuzberg:
  force_ocr: true
  ocr_backend: tesseract
  target_dpi: 300
unstructured:
  strategy: ocr_only
pymupdf:
  use_ocr: true
  ocr_dpi: 300
extractous:
  ocr_config:
    language: eng
```

---

## Version Tracking

### Check Script
```bash
#!/bin/bash
pip index versions docling
pip index versions marker-pdf
pip index versions pymupdf4llm
pip index versions kreuzberg
pip index versions unstructured
pip index versions pdfplumber
pip index versions pymupdf
pip index versions pypdf
pip index versions pdfminer.six
pip index versions pypdfium2
pip index versions extractous
```

### Breaking Changes to Watch

| Parser | Watch For |
|--------|-----------|
| docling | Pipeline options restructuring, VLM integration |
| marker | Output format changes, LLM integration |
| kreuzberg | OCR backend API changes |
| unstructured | Strategy options, element types |
| pymupdf | License changes (AGPL), API deprecations |
| llamaparse | Tier changes, credit costs |
| LLM APIs | Model deprecations, pricing changes |

---

## References

### Open Source
- Docling: https://github.com/DS4SD/docling
- Marker: https://github.com/VikParuchuri/marker
- PyMuPDF: https://github.com/pymupdf/PyMuPDF
- Kreuzberg: https://github.com/Getso/kreuzberg
- Unstructured: https://github.com/Unstructured-IO/unstructured
- pdfplumber: https://github.com/jsvine/pdfplumber
- pypdf: https://github.com/py-pdf/pypdf
- pdfminer.six: https://github.com/pdfminer/pdfminer.six
- pypdfium2: https://github.com/pypdfium2-team/pypdfium2
- extractous: https://github.com/yobix-ai/extractous

### Commercial
- AWS Textract: https://docs.aws.amazon.com/textract/
- Azure Document Intelligence: https://learn.microsoft.com/azure/ai-services/document-intelligence/
- Google Document AI: https://cloud.google.com/document-ai/docs
- Databricks: https://docs.databricks.com/sql/language-manual/functions/ai_parse_document
- LlamaParse: https://docs.llamaindex.ai/llamaparse/

### LLM Vision
- OpenAI Vision: https://platform.openai.com/docs/guides/vision
- Anthropic Claude: https://docs.anthropic.com/claude/docs/vision
- Google Gemini: https://ai.google.dev/gemini-api/docs
