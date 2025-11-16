# Benchmark Configuration Guide

This document describes the YAML configuration schema for PDF-Bench benchmarks. Benchmark configurations control which documents, parsers, and metrics are used in a benchmark run.

## Quick Start

Create a benchmark configuration file (e.g., `benchmarks/my_benchmark.yaml`):

```yaml
name: My Benchmark
description: Description of what this benchmark tests
corpus_dir: corpus

document_filter:
  corpora:
    - synthetic
  max_documents: 10

parser_config:
  parsers:
    - pymupdf
    - marker

metric_config:
  metrics:
    - edit_similarity
    - chrf++
  aggregate: true

output_config:
  results_dir: results
  save_format: json
  generate_report: true
```

## Complete Schema

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable benchmark name |
| `description` | string | Yes | Benchmark description and purpose |
| `corpus_dir` | string | Yes | Path to corpus directory (usually "corpus") |
| `document_filter` | object | Yes | Document selection filters |
| `parser_config` | object | Yes | Parser configuration |
| `metric_config` | object | Yes | Metric configuration |
| `output_config` | object | Yes | Output and reporting configuration |
| `parallel_workers` | integer | No | Number of parallel workers (0=auto, 1=sequential, default: 0) |

### Document Filter

Controls which documents from the corpus are included in the benchmark.

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `corpora` | list[string] | List of corpora to include (`academic`, `business`, `synthetic`) | All |
| `domains` | list[string] | List of domains to include (`arxiv`, `gov-uk`, `sec-edgar`, `pandoc`, `libreoffice`) | All |
| `features` | list[string] | Documents must have ALL listed features (`tables`, `math`, `figures`, `code`, `lists`, `footnotes`, `multi-column`, `headers-footers`) | None |
| `exclude_doc_ids` | list[string] | Specific document IDs to exclude | None |
| `include_doc_ids` | list[string] | Specific document IDs to include (overrides other filters) | None |
| `max_documents` | integer \| null | Maximum number of documents to include | No limit |

**Examples:**

```yaml
# Include only synthetic documents with tables
document_filter:
  corpora:
    - synthetic
  features:
    - tables
```

```yaml
# Include first 5 documents from academic corpus
document_filter:
  corpora:
    - academic
  max_documents: 5
```

```yaml
# Include specific documents only
document_filter:
  include_doc_ids:
    - arxiv_1706_03762
    - syn-complex-001
```

### Parser Configuration

Specifies which parsers to benchmark and their options.

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `parsers` | list[string] | List of parser identifiers to benchmark | All available |
| `parser_options` | dict | Per-parser configuration options | {} |

**Available Parsers:**
- `pymupdf` - Fast baseline text extraction
- `pdfplumber` - Visual layout analysis with table extraction
- `marker` - GPU-accelerated ML parser
- `unstructured` - Element-based parsing with strategies
- `aws_textract` - AWS Textract (requires credentials)
- `azure_di` - Azure Document Intelligence (requires credentials)
- `google_docai` - Google Document AI (requires credentials)
- `databricks` - Databricks ai_parse_document (requires workspace)

**Example:**

```yaml
parser_config:
  # Run all 4 implemented parsers
  parsers:
    - pymupdf
    - pdfplumber
    - marker
    - unstructured
  # Configure unstructured to use fast strategy
  parser_options:
    unstructured:
      strategy: fast
```

### Metric Configuration

Specifies which metrics to compute.

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `metrics` | list[string] | List of metric identifiers to compute | Required |
| `aggregate` | boolean | Whether to compute aggregate scores across all documents | true |

**Available Metrics:**

**Text Metrics:**
- `edit_distance` - Normalized Levenshtein distance (0-1, higher is better)
- `edit_similarity` - 1 - edit_distance (0-1, higher is better)
- `character_error_rate` - Character-level error rate (0-1, lower is better)
- `chrf++` - Character n-gram F-score (0-100, higher is better)

**Structure Metrics:**
- `tree_edit_distance` - Tree edit distance on Markdown AST
- `tree_similarity` - 1 - normalized tree edit distance (0-1, higher is better)
- `element_f1` - F1 score for Markdown element types (headings, lists, etc.)

**Table Metrics:**
- `teds` - Table Edit Distance based Similarity (structure only)
- `teds_with_content` - TEDS including cell content
- `cell_content_f1` - Cell-by-cell F1 score
- `cell_accuracy` - Percentage of cells with exact match

**Math Metrics:**
- `latex_f1` - F1 score for LaTeX expressions
- `latex_accuracy` - Percentage of LaTeX expressions with exact match

**Example:**

```yaml
metric_config:
  # Comprehensive evaluation
  metrics:
    - edit_similarity
    - chrf++
    - tree_similarity
    - element_f1
    - teds
    - latex_f1
  aggregate: true
```

### Output Configuration

Controls how results are saved and reported.

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `results_dir` | string | Directory to save results | `results` |
| `save_format` | string | Output format: `json`, `csv`, or `both` | `json` |
| `generate_report` | boolean | Whether to generate HTML report | `true` |
| `report_path` | string \| null | Custom path for HTML report (auto-generated if null) | `null` |
| `save_predictions` | boolean | Whether to save parser predictions to disk | `false` |
| `verbose` | boolean | Show detailed progress output | `true` |

**Example:**

```yaml
output_config:
  results_dir: results
  save_format: both  # Save as both JSON and CSV
  generate_report: true
  save_predictions: true  # Save predictions for manual inspection
  verbose: true
```

## Example Configurations

### MVP All Parsers Benchmark

Comprehensive benchmark for all parsers on synthetic corpus:

```yaml
name: MVP All Parsers Benchmark
description: >
  Comprehensive benchmark evaluating all 4 implemented parsers on the
  complete synthetic corpus with all metrics.

corpus_dir: corpus

document_filter:
  corpora:
    - synthetic

parser_config:
  parsers:
    - pymupdf
    - pdfplumber
    - marker
    - unstructured
  parser_options:
    unstructured:
      strategy: fast

metric_config:
  metrics:
    - edit_distance
    - chrf++
    - tree_similarity
    - element_f1
    - teds
    - latex_f1
  aggregate: true

output_config:
  results_dir: results
  save_format: json
  generate_report: true
  save_predictions: true

parallel_workers: 0  # Auto-detect CPU count
```

### Quick Test Benchmark

Fast benchmark for development and testing:

```yaml
name: Quick Test Benchmark
description: Fast benchmark for development. 2 parsers, 3 documents, core metrics.

corpus_dir: corpus

document_filter:
  corpora:
    - synthetic
  max_documents: 3

parser_config:
  parsers:
    - pymupdf
    - marker

metric_config:
  metrics:
    - edit_similarity
    - chrf++
    - tree_similarity
    - element_f1
  aggregate: true

output_config:
  results_dir: results
  save_format: json
  generate_report: true
  save_predictions: false

parallel_workers: 1  # Sequential for debugging
```

### Specialized Benchmarks

**Tables Only:**

```yaml
name: Tables Benchmark
description: Focus on table extraction quality

corpus_dir: corpus

document_filter:
  features:
    - tables  # Only documents with tables

parser_config:
  parsers:
    - pymupdf
    - pdfplumber
    - marker
    - unstructured

metric_config:
  metrics:
    - edit_similarity
    - teds
    - teds_with_content
    - cell_content_f1
    - element_f1
  aggregate: true

output_config:
  results_dir: results
  save_format: json
  generate_report: true
```

**Math Only:**

```yaml
name: Math Benchmark
description: Focus on mathematical notation extraction

corpus_dir: corpus

document_filter:
  features:
    - math  # Only documents with math

parser_config:
  parsers:
    - pymupdf
    - marker
    - unstructured

metric_config:
  metrics:
    - edit_similarity
    - latex_f1
    - latex_accuracy
    - element_f1
  aggregate: true

output_config:
  results_dir: results
  save_format: json
  generate_report: true
```

## Validation

The configuration system validates all inputs:

```python
from pathlib import Path
from pdf_bench.config import load_config

# Load and validate configuration
config = load_config(Path("benchmarks/my_benchmark.yaml"))

# This will raise ValueError if invalid:
# - Missing required fields
# - Invalid parser names
# - Invalid metric names
# - Invalid corpus/domain/feature values
# - Invalid parallel_workers (<0)
# - Invalid save_format
# - Empty metrics list
# - etc.
```

## Python API

### Loading Configuration

```python
from pathlib import Path
from pdf_bench.config import load_config

config = load_config(Path("benchmarks/mvp_all.yaml"))
print(f"Benchmark: {config.name}")
print(f"Parsers: {config.parser_config.parsers}")
print(f"Metrics: {config.metric_config.metrics}")
```

### Creating Configuration Programmatically

```python
from pdf_bench.config import (
    BenchmarkConfig,
    DocumentFilter,
    ParserConfig,
    MetricConfig,
    OutputConfig,
    save_config,
)
from pathlib import Path

config = BenchmarkConfig(
    name="Custom Benchmark",
    description="Programmatically created benchmark",
    corpus_dir="corpus",
    document_filter=DocumentFilter(
        corpora=["synthetic"],
        max_documents=5
    ),
    parser_config=ParserConfig(
        parsers=["pymupdf", "marker"]
    ),
    metric_config=MetricConfig(
        metrics=["edit_similarity", "chrf++"]
    ),
    output_config=OutputConfig(
        save_format="both"
    ),
)

# Validate
config.validate()

# Save to file
save_config(config, Path("benchmarks/custom.yaml"))
```

### Converting Between Formats

```python
# Load from YAML
config = load_config(Path("benchmarks/mvp_all.yaml"))

# Convert to dictionary
data = config.to_dict()

# Reconstruct from dictionary
config2 = BenchmarkConfig.from_dict(data)

# Save with different name
config2.name = "Modified Benchmark"
save_config(config2, Path("benchmarks/modified.yaml"))
```

## Best Practices

1. **Start Small**: Use `max_documents` to test with a subset before running full benchmark
2. **Name Descriptively**: Use clear names that indicate what the benchmark tests
3. **Document Purpose**: Write detailed descriptions explaining goals and expected results
4. **Version Control**: Store benchmark configs in version control
5. **Specialized Configs**: Create focused configs for specific features (tables, math, etc.)
6. **Save Predictions**: Enable `save_predictions` when debugging parser quality issues
7. **Parallel Execution**: Use `parallel_workers: 0` for production, `1` for debugging
8. **Metric Selection**: Don't compute all metrics if you only need a subset (saves time)

## Command-Line Usage

(Note: CLI will be implemented in TASK-038 and TASK-042)

```bash
# Run benchmark from config
pdfbench run --config benchmarks/mvp_all.yaml

# Quick test
pdfbench run --config benchmarks/quick_test.yaml

# List available parsers
pdfbench list parsers

# Validate config without running
pdfbench validate benchmarks/my_config.yaml
```

## Troubleshooting

### Configuration Won't Load

**Error: "Missing required field: 'name'"**
- Solution: Ensure all required top-level fields are present

**Error: "Invalid parser 'xyz'"**
- Solution: Check parser name matches one of the valid parsers
- Run `pdfbench list parsers` to see available parsers

**Error: "Invalid metric 'abc'"**
- Solution: Check metric name against valid metrics list
- See "Available Metrics" section above

### Benchmark Runs Slowly

- Reduce `max_documents` for testing
- Use `parallel_workers: 0` for automatic parallelization
- Disable `save_predictions` if not needed
- Select fewer metrics
- Use `quick_test.yaml` as template

### No Documents Match Filter

- Check corpus exists in `corpus_dir`
- Verify corpus/domain/feature values are correct
- Remove restrictive filters temporarily
- Check `exclude_doc_ids` isn't too broad

## See Also

- [Document Metadata Schema](METADATA_SCHEMA.md) - Understanding document metadata
- [Contributing Guide](../CONTRIBUTING.md) - How to add parsers and metrics
- [README](../README.md) - Project overview and usage

## Version History

- **v0.1** (2024-11-15): Initial benchmark configuration schema
  - Document filtering by corpus, domain, features, doc IDs
  - Parser configuration with per-parser options
  - Metric configuration with aggregate support
  - Output configuration with multiple formats
  - Parallel execution support
  - 4 parsers: PyMuPDF, pdfplumber, Marker, Unstructured
  - 12 metrics across text, structure, tables, and math
