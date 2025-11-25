# Parser Configuration Guide

PDF-Bench supports configurable parsers to handle different document types and resource constraints. This guide covers how to configure parsers, especially those with significant resource requirements like Docling.

## Configuration Sources

Configuration is loaded from multiple sources, in order of precedence:

1. **Explicit options** - Passed directly in benchmark YAML or constructor
2. **Environment variables** - `PARSER_OPTION` format (e.g., `DOCLING_OCR=true`)
3. **Project config** - `.pdfbench/<parser>.yaml` in working directory
4. **User config** - `~/.config/pdfbench/<parser>.yaml`
5. **Built-in defaults**

## Docling Configuration

Docling is a high-quality PDF parser from IBM that uses deep learning models. It has two main operating modes:

### Fast Mode (Default)

- **OCR disabled** - Text extracted from PDF structure only
- **Memory**: ~2-4GB RAM
- **Speed**: ~2-5 seconds per document
- **Best for**: Text-based PDFs, contracts, reports

### OCR Mode

- **OCR enabled** - Uses EasyOCR for scanned documents
- **Memory**: ~8-12GB RAM
- **Speed**: ~30-60 seconds per document
- **GPU strongly recommended**
- **Best for**: Scanned documents, images, mixed content

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `do_ocr` | `false` | Enable OCR for scanned documents |
| `do_table_structure` | `true` | Enable table structure extraction |
| `num_threads` | `4` | Number of CPU threads |
| `device` | `auto` | Device selection: auto, cpu, cuda, mps |
| `ocr_languages` | `["en"]` | Languages for OCR (ISO 639-1 codes) |
| `table_mode` | `fast` | Table extraction mode: fast, accurate |
| `generate_page_images` | `false` | Generate page images for visual grounding |
| `images_scale` | `1.0` | Image scale factor |

### Configuration Methods

#### 1. Benchmark YAML (Recommended for benchmarks)

```yaml
parser_config:
  parsers:
    - docling
    - pymupdf
  parser_options:
    docling:
      do_ocr: true
      num_threads: 8
      device: cuda
```

#### 2. Environment Variables

```bash
# Enable OCR
export DOCLING_OCR=true

# Use CPU only
export DOCLING_DEVICE=cpu

# Run benchmark
uv run python -m pdf_bench.main run benchmarks/cuad_75docs.yaml
```

#### 3. Config File

Create `.pdfbench/docling.yaml` in your project:

```yaml
# Project-specific Docling configuration
do_ocr: false
do_table_structure: true
num_threads: 4
device: auto
```

Or `~/.config/pdfbench/docling.yaml` for user defaults.

### Parser Variants

PDF-Bench provides two pre-configured Docling variants:

| Parser ID | Mode | Use Case |
|-----------|------|----------|
| `docling` | Fast (no OCR) | Text-based PDFs, general use |
| `docling-ocr` | OCR enabled | Scanned documents, images |

Use in benchmark YAML:

```yaml
parser_config:
  parsers:
    - docling      # Fast mode
    - docling-ocr  # OCR mode
```

## Resource Requirements Summary

| Parser | Memory | Speed | GPU |
|--------|--------|-------|-----|
| `docling` (fast) | 2-4GB | 2-5 sec/doc | Optional |
| `docling-ocr` | 8-12GB | 30-60 sec/doc | Recommended |
| `marker` | 4-8GB | 10-30 sec/doc | Recommended |
| `pymupdf` | <1GB | <1 sec/doc | No |
| `pdfplumber` | <1GB | 1-2 sec/doc | No |

## Troubleshooting

### Out of Memory with Docling

1. Disable OCR: `DOCLING_OCR=false`
2. Reduce threads: `DOCLING_THREADS=2`
3. Use CPU mode: `DOCLING_DEVICE=cpu`
4. Process fewer documents in parallel

### Slow Processing

1. Enable GPU if available: `DOCLING_DEVICE=cuda`
2. Increase threads: `DOCLING_THREADS=8`
3. Disable unnecessary features: `do_table_structure: false`

### Checking Configuration

```python
from pdf_bench.loader import PARSER_REGISTRY

parser = PARSER_REGISTRY['docling']()
print(f"OCR: {parser._do_ocr}")
print(f"Device: {parser._device}")
print(f"Config source: {parser._config_source}")
```
